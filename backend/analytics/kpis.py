"""
InsightIQ Business KPI and Dashboard Analytics Engine.
Calculates certified business metrics, growth rates, baseline comparisons,
and categorical aggregations from the active dataset.
"""
import sqlite3
import datetime
from typing import Dict, Any, List, Optional, Tuple
from backend.database import get_db_connection

def build_filter_where_clause(
    dataset_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    region: Optional[str] = None,
    category: Optional[str] = None,
    segment: Optional[str] = None,
    product: Optional[str] = None
) -> Tuple[str, List[Any]]:
    """Builds parameterized WHERE clause for sales_data queries."""
    conditions = ["dataset_id = ?"]
    params: List[Any] = [dataset_id]
    
    if start_date:
        conditions.append("order_date >= ?")
        params.append(start_date)
    if end_date:
        conditions.append("order_date <= ?")
        params.append(end_date)
    if region and region != "All":
        conditions.append("region = ?")
        params.append(region)
    if category and category != "All":
        conditions.append("category = ?")
        params.append(category)
    if segment and segment != "All":
        conditions.append("segment = ?")
        params.append(segment)
    if product and product != "All":
        conditions.append("product_name LIKE ?")
        params.append(f"%{product}%")
        
    return " WHERE " + " AND ".join(conditions), params

def get_dashboard_kpis(
    dataset_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    region: Optional[str] = None,
    category: Optional[str] = None,
    segment: Optional[str] = None,
    product: Optional[str] = None
) -> Dict[str, Any]:
    """Computes headline KPIs and comparison period metrics."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    where_clause, params = build_filter_where_clause(
        dataset_id, start_date, end_date, region, category, segment, product
    )
    
    query = f"""
        SELECT 
            COALESCE(SUM(revenue), 0.0) as total_rev,
            COALESCE(SUM(profit), 0.0) as total_prof,
            COUNT(DISTINCT order_id) as total_ord,
            COUNT(DISTINCT customer_id) as total_cust,
            MIN(order_date) as min_date,
            MAX(order_date) as max_date
        FROM sales_data
        {where_clause}
    """
    cursor.execute(query, params)
    row = cursor.fetchone()
    
    total_rev = round(float(row["total_rev"]), 2)
    total_prof = round(float(row["total_prof"]), 2)
    total_ord = int(row["total_ord"])
    total_cust = int(row["total_cust"])
    act_min_date = row["min_date"]
    act_max_date = row["max_date"]
    
    # Safe KPI Formulas
    # Average Order Value = Total Revenue / Total Orders
    aov = round(total_rev / total_ord, 2) if total_ord > 0 else 0.0
    
    # Profit Margin = Total Profit / Total Revenue * 100
    profit_margin = round((total_prof / total_rev) * 100.0, 2) if total_rev > 0 else 0.0
    
    # Baseline comparison calculation (if explicit start_date and end_date are selected)
    prev_rev = None
    prev_prof = None
    rev_growth = None
    prof_growth = None
    has_baseline = False
    
    if start_date and end_date:
        try:
            d_start = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            d_end = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
            duration_days = (d_end - d_start).days
            
            if duration_days > 0:
                prev_end = d_start - datetime.timedelta(days=1)
                prev_start = prev_end - datetime.timedelta(days=duration_days)
                
                prev_where, prev_params = build_filter_where_clause(
                    dataset_id,
                    prev_start.isoformat(),
                    prev_end.isoformat(),
                    region, category, segment, product
                )
                
                cursor.execute(f"""
                    SELECT 
                        COALESCE(SUM(revenue), 0.0) as prev_rev,
                        COALESCE(SUM(profit), 0.0) as prev_prof,
                        COUNT(DISTINCT order_id) as prev_ord
                    FROM sales_data
                    {prev_where}
                """, prev_params)
                p_row = cursor.fetchone()
                
                if p_row and p_row["prev_ord"] > 0:
                    prev_rev = round(float(p_row["prev_rev"]), 2)
                    prev_prof = round(float(p_row["prev_prof"]), 2)
                    has_baseline = True
                    
                    if prev_rev > 0:
                        rev_growth = round(((total_rev - prev_rev) / prev_rev) * 100.0, 2)
                    if prev_prof != 0:
                        prof_growth = round(((total_prof - prev_prof) / abs(prev_prof)) * 100.0, 2)
        except Exception:
            has_baseline = False
            
    conn.close()
    
    return {
        "total_revenue": total_rev,
        "total_profit": total_prof,
        "total_orders": total_ord,
        "average_order_value": aov,
        "total_customers": total_cust,
        "profit_margin_pct": profit_margin,
        "prev_revenue": prev_rev,
        "prev_profit": prev_prof,
        "revenue_growth_pct": rev_growth,
        "profit_growth_pct": prof_growth,
        "has_comparison_baseline": has_baseline,
        "date_range": {
            "start": start_date or act_min_date,
            "end": end_date or act_max_date
        }
    }

def get_category_breakdown(
    dataset_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    region: Optional[str] = None,
    category: Optional[str] = None,
    segment: Optional[str] = None,
    product: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Category performance with revenue shares and profit margins."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    where_clause, params = build_filter_where_clause(
        dataset_id, start_date, end_date, region, category, segment, product
    )
    
    # Total revenue for calculating share
    cursor.execute(f"SELECT COALESCE(SUM(revenue), 0.0) FROM sales_data {where_clause}", params)
    grand_revenue = float(cursor.fetchone()[0])
    
    query = f"""
        SELECT 
            category,
            ROUND(SUM(revenue), 2) as cat_revenue,
            ROUND(SUM(profit), 2) as cat_profit,
            COUNT(DISTINCT order_id) as cat_orders
        FROM sales_data
        {where_clause}
        GROUP BY category
        ORDER BY cat_revenue DESC
    """
    cursor.execute(query, params)
    results = []
    
    for row in cursor.fetchall():
        rev = float(row["cat_revenue"])
        prof = float(row["cat_profit"])
        margin = round((prof / rev) * 100.0, 2) if rev > 0 else 0.0
        share = round((rev / grand_revenue) * 100.0, 2) if grand_revenue > 0 else 0.0
        
        results.append({
            "category": row["category"] or "Uncategorized",
            "revenue": rev,
            "profit": prof,
            "orders": int(row["cat_orders"]),
            "profit_margin": margin,
            "share_pct": share
        })
        
    conn.close()
    return results

def get_region_breakdown(
    dataset_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    region: Optional[str] = None,
    category: Optional[str] = None,
    segment: Optional[str] = None,
    product: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Regional distribution of sales, margins, and customers."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    where_clause, params = build_filter_where_clause(
        dataset_id, start_date, end_date, region, category, segment, product
    )
    
    query = f"""
        SELECT 
            region,
            ROUND(SUM(revenue), 2) as reg_revenue,
            ROUND(SUM(profit), 2) as reg_profit,
            COUNT(DISTINCT order_id) as reg_orders,
            COUNT(DISTINCT customer_id) as reg_customers
        FROM sales_data
        {where_clause}
        GROUP BY region
        ORDER BY reg_revenue DESC
    """
    cursor.execute(query, params)
    results = []
    
    for row in cursor.fetchall():
        rev = float(row["reg_revenue"])
        prof = float(row["reg_profit"])
        margin = round((prof / rev) * 100.0, 2) if rev > 0 else 0.0
        
        results.append({
            "region": row["region"] or "Other",
            "revenue": rev,
            "profit": prof,
            "orders": int(row["reg_orders"]),
            "customers": int(row["reg_customers"]),
            "profit_margin": margin
        })
        
    conn.close()
    return results

def get_trend_data(
    dataset_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    region: Optional[str] = None,
    category: Optional[str] = None,
    segment: Optional[str] = None,
    product: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Monthly or daily aggregation of revenue, profit, and order volume."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    where_clause, params = build_filter_where_clause(
        dataset_id, start_date, end_date, region, category, segment, product
    )
    
    # Group by Year-Month (e.g. 2024-01) for clean visual trends
    query = f"""
        SELECT 
            substr(order_date, 1, 7) as period,
            ROUND(SUM(revenue), 2) as period_rev,
            ROUND(SUM(profit), 2) as period_prof,
            COUNT(DISTINCT order_id) as period_orders
        FROM sales_data
        {where_clause}
        GROUP BY substr(order_date, 1, 7)
        ORDER BY period ASC
    """
    cursor.execute(query, params)
    results = []
    for row in cursor.fetchall():
        results.append({
            "period": row["period"],
            "revenue": float(row["period_rev"]),
            "profit": float(row["period_prof"]),
            "orders": int(row["period_orders"])
        })
        
    conn.close()
    return results

def get_product_rankings(
    dataset_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    region: Optional[str] = None,
    category: Optional[str] = None,
    segment: Optional[str] = None,
    product: Optional[str] = None
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Returns top 10 products by revenue and bottom 5 products by profit."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    where_clause, params = build_filter_where_clause(
        dataset_id, start_date, end_date, region, category, segment, product
    )
    
    # Top 10 by revenue
    top_query = f"""
        SELECT 
            product_name,
            category,
            ROUND(SUM(revenue), 2) as prod_rev,
            ROUND(SUM(profit), 2) as prod_prof,
            SUM(quantity) as prod_qty
        FROM sales_data
        {where_clause}
        GROUP BY product_name, category
        ORDER BY prod_rev DESC
        LIMIT 10
    """
    cursor.execute(top_query, params)
    top_products = []
    for r in cursor.fetchall():
        rev = float(r["prod_rev"])
        prof = float(r["prod_prof"])
        margin = round((prof / rev) * 100.0, 2) if rev > 0 else 0.0
        top_products.append({
            "product_name": r["product_name"],
            "category": r["category"],
            "revenue": rev,
            "profit": prof,
            "quantity": int(r["prod_qty"]),
            "profit_margin": margin
        })
        
    # Bottom 5 by profit
    bottom_query = f"""
        SELECT 
            product_name,
            category,
            ROUND(SUM(revenue), 2) as prod_rev,
            ROUND(SUM(profit), 2) as prod_prof,
            SUM(quantity) as prod_qty
        FROM sales_data
        {where_clause}
        GROUP BY product_name, category
        ORDER BY prod_prof ASC
        LIMIT 5
    """
    cursor.execute(bottom_query, params)
    bottom_products = []
    for r in cursor.fetchall():
        rev = float(r["prod_rev"])
        prof = float(r["prod_prof"])
        margin = round((prof / rev) * 100.0, 2) if rev > 0 else 0.0
        bottom_products.append({
            "product_name": r["product_name"],
            "category": r["category"],
            "revenue": rev,
            "profit": prof,
            "quantity": int(r["prod_qty"]),
            "profit_margin": margin
        })
        
    conn.close()
    return top_products, bottom_products

def get_recent_orders(
    dataset_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    region: Optional[str] = None,
    category: Optional[str] = None,
    segment: Optional[str] = None,
    product: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """Fetches recent order records with detailed line items."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    where_clause, params = build_filter_where_clause(
        dataset_id, start_date, end_date, region, category, segment, product
    )
    
    query = f"""
        SELECT 
            id, order_id, order_date, customer_name, segment, region, category,
            product_name, quantity, unit_price, discount, revenue, profit
        FROM sales_data
        {where_clause}
        ORDER BY order_date DESC, id DESC
        LIMIT ?
    """
    cursor.execute(query, params + [limit])
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results

def get_filter_options(dataset_id: str) -> Dict[str, List[str]]:
    """Returns dynamic unique filter values for regions, categories, segments."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT region FROM sales_data WHERE dataset_id = ? AND region IS NOT NULL ORDER BY region", (dataset_id,))
    regions = [r[0] for r in cursor.fetchall()]
    
    cursor.execute("SELECT DISTINCT category FROM sales_data WHERE dataset_id = ? AND category IS NOT NULL ORDER BY category", (dataset_id,))
    categories = [r[0] for r in cursor.fetchall()]
    
    cursor.execute("SELECT DISTINCT segment FROM sales_data WHERE dataset_id = ? AND segment IS NOT NULL ORDER BY segment", (dataset_id,))
    segments = [r[0] for r in cursor.fetchall()]
    
    cursor.execute("SELECT MIN(order_date), MAX(order_date) FROM sales_data WHERE dataset_id = ?", (dataset_id,))
    date_row = cursor.fetchone()
    min_date = date_row[0] if date_row else "2024-01-01"
    max_date = date_row[1] if date_row else "2025-12-31"
    
    conn.close()
    
    return {
        "regions": ["All"] + regions,
        "categories": ["All"] + categories,
        "segments": ["All"] + segments,
        "min_date": [min_date],
        "max_date": [max_date]
    }
