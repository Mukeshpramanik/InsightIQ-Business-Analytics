# InsightIQ — Comprehensive Technical Interview Preparation Guide

This guide equips you to confidently answer technical, analytical, statistical, and architectural questions during Data Analyst, Business Analyst, and Junior Data Scientist interviews.

---

## 1. Project Explanation (Elevator Pitch)

### 30-Second Elevator Pitch
> *"I built InsightIQ — an enterprise-grade Business Intelligence and Predictive Analytics platform. It automates raw sales CSV ingestion with formula-injection defense, calculates certified financial metrics with zero-denominator safety, predicts forward demand using out-of-sample evaluated machine learning, and executes secure SQL queries via AST validation. It bridges the gap between raw database engineering and executive business decision-making."*

### Key Architectural Strengths to Highlight
1. **No Mock or Fabricated Numbers:** Every chart, card, and insight is computed directly from active SQLite transactional records.
2. **Strict Prevention of Data Leakage:** Time-series train/test splits are chronological; models never train on future observations.
3. **Defense-in-Depth Security:** Spreadsheet formula injection prevention on CSV exports and Abstract Syntax Tree (AST) query validation via `sqlglot` on user SQL.

---

## 2. Technical Decision Rationale

| Decision | Chosen Technology | Alternative Considered | Engineering Rationale |
|---|---|---|---|
| **Backend Framework** | **FastAPI** | Flask, Django | High-performance asynchronous execution, automatic Pydantic schema validation, and native OpenAPI documentation. |
| **Frontend Framework** | **React 18 + Vite** | Next.js, Vue | Lightweight client-side SPA with lightning-fast HMR, component reusability, and seamless Recharts charting integration. |
| **Database Engine** | **SQLite (WAL Mode)** | PostgreSQL, MySQL | Zero-configuration local persistence, fast analytical read performance, and engine-level read-only URI enforcement (`?mode=ro`). |
| **SQL Parser** | **sqlglot** | Regex / String Blacklists | String blacklists are easily bypassed via SQL comments or case variation. `sqlglot` inspects the true Abstract Syntax Tree (AST) to verify statement type and table whitelist. |
| **Forecasting Model** | **Ridge Regressor + Lags** | Prophet, ARIMA | ARIMA/Prophet introduce heavy C++ binary dependencies and external runtime quirks. Autoregressive Ridge with lag features provides transparent, explainable, and fast projections. |
| **PDF Generation** | **ReportLab** | Puppeteer / WeasyPrint | Pure Python PDF compilation without needing headless Chrome or system-level WebKit binaries. |

---

## 3. Core Business & Analytics Concepts

### Q: Why use Tukey's IQR Method instead of Z-Score for Outlier Detection?
**Answer:**
Z-score assumes the underlying data follows a Gaussian (normal) distribution and relies on the mean and standard deviation, both of which are heavily distorted by extreme values. Retail sales data is almost always right-skewed (Pareto distributed). Tukey's IQR method relies on medians and quartiles ($Q_1, Q_3$), which are non-parametric and robust against skewed data.

### Q: What is "Margin Drag" and how does InsightIQ detect it?
**Answer:**
Margin drag occurs when a product generates high gross revenue volume but delivers an abnormally low or negative net profit margin. In InsightIQ, the insight engine flags products that represent $>3\%$ of enterprise turnover but yield $<10\%$ profit margin, alerting management to renegotiate supplier terms or curtail excessive promotional discounting.

### Q: How is RFM Segmentation calculated and why use Quintiles?
**Answer:**
RFM scores customers on:
- **Recency:** Days since most recent transaction relative to the reference date.
- **Frequency:** Count of unique completed orders.
- **Monetary:** Total gross revenue spend.
We use deterministic quintile scoring (1 to 5) based on ranking (`pd.qcut(rank(method="first"))`). Quintiles guarantee balanced distribution across customer cohorts, preventing ties from skewing segment definitions.

### Q: How do you handle zero actual demand in MAPE calculation?
**Answer:**
The standard Mean Absolute Percentage Error formula $\frac{|y - \hat{y}|}{y}$ divides by actual value $y$. When $y = 0$, division by zero occurs, producing infinity. In InsightIQ, our `compute_safe_mape` function explicitly masks out $y = 0$ values, computes the error over non-zero observations, and reports the `zero_actuals_count` to ensure statistical transparency.

---

## 4. SQL Deep-Dive & Sample Interview Questions

### Q1: Write a SQL query to calculate Month-over-Month (MoM) revenue growth using window functions.
```sql
WITH monthly_totals AS (
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
FROM monthly_totals
ORDER BY sales_month;
```

### Q2: Write a query to find the top 20% of customers by lifetime spend (Pareto Principle).
```sql
WITH customer_spending AS (
    SELECT 
        customer_id,
        customer_name,
        SUM(revenue) AS lifetime_spend,
        NTILE(5) OVER (ORDER BY SUM(revenue) DESC) AS spend_quintile
    FROM sales_data
    GROUP BY customer_id, customer_name
)
SELECT 
    customer_id,
    customer_name,
    ROUND(lifetime_spend, 2) AS total_spend
FROM customer_spending
WHERE spend_quintile = 1
ORDER BY lifetime_spend DESC;
```

### Q3: How do you optimize analytical queries on large tables in SQLite?
1. **Composite Indexes:** Create multi-column indexes matching common filter and group patterns, e.g., `(dataset_id, order_date)` and `(dataset_id, region)`.
2. **Covering Indexes:** Include queried columns in index structures to avoid table b-tree lookups.
3. **EXPLAIN QUERY PLAN:** Inspect whether SQLite performs an indexed `SEARCH TABLE` vs an unindexed `SCAN TABLE`.
4. **Server-Side Aggregation:** Push `SUM`, `COUNT`, and `AVG` operations into the database engine rather than transferring millions of raw records over the wire to Python.

---

## 5. Likely Interviewer Questions & Model Answers

### Q: "What was the most challenging technical hurdle in this project, and how did you resolve it?"
**Answer:**
> *"The biggest challenge was preventing data leakage in the sales forecasting engine while maintaining continuous time series. Retail datasets often have missing trading days (e.g., weekends or holidays). If you compute lag features naively on raw order rows, `lag_1` refers to the previous transaction, not the previous day. I solved this by implementing a resample-and-fill aggregation step to establish uniform daily/monthly time series, followed by a strict chronological 80/20 train/test split. This ensured the model was validated solely on unseen future intervals."*

### Q: "How did you prevent SQL injection in the SQL Analytics Lab?"
**Answer:**
> *"Rather than relying on simplistic regex blacklists that can be bypassed with comments or capitalization tricks, I integrated `sqlglot` for Abstract Syntax Tree (AST) validation. The parser verifies that the AST is strictly a `Select` expression, asserts that only authorized tables (`sales_data`, `datasets`, `cleaning_history`) are referenced, enforces single-statement boundaries, and caps result sets with `LIMIT 500`. Furthermore, query execution runs against an SQLite URI opened with `mode=ro`, meaning the database engine itself rejects any write attempts at the OS level."*

### Q: "What is Spreadsheet Formula Injection, and how did you mitigate it?"
**Answer:**
> *"Spreadsheet Formula Injection (CSV Injection) occurs when an exported CSV contains fields starting with characters like `=`, `+`, `-`, or `@`. When opened in Microsoft Excel or Google Sheets, the spreadsheet treats the cell as a formula and executes external programs (e.g. `=cmd\|' /C calc'!A0`). I mitigated this in the data cleaning and export pipeline by checking text fields and prepending a single quote `'` to any cell starting with those characters, neutralizing formula execution."*
