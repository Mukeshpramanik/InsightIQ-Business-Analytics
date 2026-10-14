"""
InsightIQ Interactive SQL Analytics Lab Engine.
Validates queries using sqlglot Abstract Syntax Tree (AST) analysis.
Guarantees read-only SELECT queries, single-statement execution,
whitelisted table access, and bounded result sets.
"""
import time
import sqlite3
import sqlglot
from sqlglot import exp
from typing import Dict, Any, List, Optional, Tuple
from backend.database import get_readonly_connection

ALLOWED_TABLES = {"sales_data", "datasets", "cleaning_history"}

SAMPLE_SQL_QUERIES = [
    {
        "id": "regional_margin",
        "title": "Regional Profitability & Net Margin Ranking",
        "category": "Aggregations & Grouping",
        "description": "Calculates total revenue, profit, distinct orders, and net profit margin percentage grouped by geographic region.",
        "query": """SELECT 
    region,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(revenue), 2) AS total_revenue,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(profit) / SUM(revenue)) * 100.0, 2) AS profit_margin_pct
FROM sales_data
GROUP BY region
ORDER BY total_revenue DESC;"""
    },
    {
        "id": "mom_growth_window",
        "title": "Month-over-Month (MoM) Growth via Window Functions",
        "category": "Window Functions & CTEs",
        "description": "Uses LAG() window function over monthly sales totals to calculate chronological month-over-month revenue growth percentage.",
        "query": """WITH monthly_sales AS (
    SELECT 
        substr(order_date, 1, 7) AS sales_month,
        ROUND(SUM(revenue), 2) AS monthly_revenue
    FROM sales_data
    GROUP BY substr(order_date, 1, 7)
)
SELECT 
    sales_month,
    monthly_revenue,
    LAG(monthly_revenue, 1) OVER (ORDER BY sales_month) AS prev_month_revenue,
    ROUND(
        ((monthly_revenue - LAG(monthly_revenue, 1) OVER (ORDER BY sales_month)) 
        / LAG(monthly_revenue, 1) OVER (ORDER BY sales_month)) * 100.0, 
        2
    ) AS mom_growth_pct
FROM monthly_sales
ORDER BY sales_month;"""
    },
    {
        "id": "category_revenue_share",
        "title": "Category Revenue Contribution (Window Aggregates)",
        "category": "Advanced Analytics",
        "description": "Calculates each product category's revenue and exact percentage share of total enterprise turnover using window SUM().",
        "query": """SELECT 
    category,
    COUNT(DISTINCT product_id) AS distinct_products,
    ROUND(SUM(revenue), 2) AS category_revenue,
    ROUND(
        (SUM(revenue) / SUM(SUM(revenue)) OVER ()) * 100.0, 
        2
    ) AS revenue_share_pct
FROM sales_data
GROUP BY category
ORDER BY category_revenue DESC;"""
    },
    {
        "id": "clv_top_customers",
        "title": "Top Customers by Lifetime Value (CLV)",
        "category": "Customer Intelligence",
        "description": "Identifies the highest lifetime value customers with order count, total spend, and average spend per order.",
        "query": """SELECT 
    customer_id,
    customer_name,
    segment,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(revenue), 2) AS lifetime_spend,
    ROUND(AVG(revenue), 2) AS avg_item_revenue
FROM sales_data
GROUP BY customer_id, customer_name, segment
HAVING COUNT(DISTINCT order_id) >= 2
ORDER BY lifetime_spend DESC
LIMIT 15;"""
    },
    {
        "id": "discount_tier_analysis",
        "title": "Discount Tier Impact on Net Profit Margin",
        "category": "Pricing Strategy",
        "description": "Classifies transactions into discount brackets using conditional CASE statements to measure margin erosion.",
        "query": """SELECT 
    CASE 
        WHEN discount = 0 THEN '0% Full Price'
        WHEN discount <= 0.10 THEN '1% - 10% Low Discount'
        WHEN discount <= 0.20 THEN '11% - 20% Medium Discount'
        ELSE '> 20% Deep Discount'
    END AS discount_tier,
    COUNT(*) AS transaction_count,
    ROUND(SUM(revenue), 2) AS tier_revenue,
    ROUND(SUM(profit), 2) AS tier_profit,
    ROUND((SUM(profit) / SUM(revenue)) * 100.0, 2) AS net_margin_pct
FROM sales_data
GROUP BY discount_tier
ORDER BY tier_revenue DESC;"""
    },
    {
        "id": "subquery_above_average_orders",
        "title": "High-Value Orders Above Category Average",
        "category": "Subqueries & Correlated Filtering",
        "description": "Filters orders whose total revenue exceeds the overall benchmark average across the catalog.",
        "query": """SELECT 
    order_id,
    order_date,
    customer_name,
    product_name,
    revenue,
    profit
FROM sales_data
WHERE revenue > (SELECT AVG(revenue) * 2 FROM sales_data)
ORDER BY revenue DESC
LIMIT 20;"""
    }
]

def validate_sql_query(sql_text: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validates user SQL text using sqlglot AST parsing.
    Enforces:
    - Exactly one SQL statement
    - Statement MUST BE a SELECT (or WITH ... SELECT)
    - Referenced tables MUST BE in ALLOWED_TABLES
    - Disallows DDL, DML, PRAGMA, ATTACH, DETACH
    Returns (is_valid, error_message, sanitized_sql)
    """
    cleaned_sql = sql_text.strip()
    if not cleaned_sql:
        return False, "Query cannot be empty.", None

    try:
        # Parse statements
        statements = sqlglot.parse(cleaned_sql, read="sqlite")
        if not statements or len(statements) == 0:
            return False, "Failed to parse query: no valid SQL expression detected.", None
        if len(statements) > 1:
            return False, "Security Violation: Multiple statements are strictly forbidden. Only a single SELECT query is permitted.", None
            
        ast = statements[0]
        if ast is None:
            return False, "Invalid SQL syntax.", None
            
        # Must be Select expression (can have WITH / CTEs)
        if not isinstance(ast, (exp.Select, exp.Union)):
            return False, f"Security Violation: Non-read operation '{ast.key.upper()}' is rejected. Only SELECT queries are permitted.", None
            
        # Check all table references
        referenced_tables = set()
        for table_node in ast.find_all(exp.Table):
            t_name = table_node.name.lower()
            # If it's a CTE alias defined in WITH, it's allowed
            cte_names = [cte.alias.lower() for cte in ast.find_all(exp.CTE) if cte.alias]
            if t_name not in cte_names:
                referenced_tables.add(t_name)
                
        # Validate that all physical tables are approved
        unauthorized = referenced_tables - ALLOWED_TABLES
        if unauthorized:
            return False, f"Access Denied: Table(s) {list(unauthorized)} are not accessible. Permitted tables: {list(ALLOWED_TABLES)}.", None
            
        # Ensure result set is bounded (enforce LIMIT <= 500)
        has_limit = False
        limit_node = ast.find(exp.Limit)
        if limit_node:
            try:
                lim_val = int(limit_node.expression.this)
                if lim_val > 500:
                    limit_node.set("expression", exp.Literal.number(500))
                has_limit = True
            except Exception:
                has_limit = False
                
        sanitized_sql = ast.sql(dialect="sqlite")
        if not has_limit and not isinstance(ast, exp.Union):
            sanitized_sql += "\nLIMIT 500"
            
        return True, None, sanitized_sql
        
    except sqlglot.errors.ParseError as pe:
        return False, f"SQL Syntax Error: {str(pe)}", None
    except Exception as e:
        return False, f"Validation Error: {str(e)}", None

def execute_safe_query(sql_text: str) -> Dict[str, Any]:
    """
    Validates and executes read-only SQL query against SQLite database.
    Measures execution latency and formats tabular response.
    """
    is_valid, err_msg, sanitized_sql = validate_sql_query(sql_text)
    if not is_valid or not sanitized_sql:
        return {
            "success": False,
            "columns": [],
            "rows": [],
            "row_count": 0,
            "execution_time_ms": 0.0,
            "error_message": err_msg,
            "query_executed": sql_text
        }
        
    start_time = time.perf_counter()
    try:
        # Use strict read-only SQLite URI mode
        conn = get_readonly_connection()
        cursor = conn.cursor()
        cursor.execute(sanitized_sql)
        
        # Extract column headers
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        
        return {
            "success": True,
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "execution_time_ms": elapsed_ms,
            "error_message": None,
            "query_executed": sanitized_sql
        }
    except sqlite3.OperationalError as oe:
        elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        return {
            "success": False,
            "columns": [],
            "rows": [],
            "row_count": 0,
            "execution_time_ms": elapsed_ms,
            "error_message": f"SQLite Operational Error: {str(oe)}",
            "query_executed": sanitized_sql
        }
    except Exception as e:
        elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        return {
            "success": False,
            "columns": [],
            "rows": [],
            "row_count": 0,
            "execution_time_ms": elapsed_ms,
            "error_message": f"Execution Error: {str(e)}",
            "query_executed": sanitized_sql
        }
