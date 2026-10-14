# InsightIQ — Business Intelligence & Predictive Analytics Platform

[![Python](https://img.shields.io/badge/Python-3.14%20%7C%203.11%2B-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61dafb?logo=react)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-3178c6?logo=typescript)](https://www.typescriptlang.org)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-38bdf8?logo=tailwindcss)](https://tailwindcss.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-28%20Backend%20%7C%203%20Frontend%20Passed-brightgreen)](docs/TESTING.md)

**InsightIQ** is a production-quality, responsive web application for exploratory data analysis, business intelligence, customer segmentation, automated data cleaning, and predictive sales forecasting. Built as a comprehensive engineering capstone project, it is specifically designed to demonstrate full-stack software engineering and data analytical rigor in **Data Analyst**, **Business Analyst**, and **Junior Data Scientist** technical evaluations.

---

## 1. Project Overview & Core Principles

Small-to-medium businesses and analytics teams frequently struggle with fragmented spreadsheets, unreliable growth metrics, opaque data quality issues, and predictive models plagued by data leakage. 

InsightIQ addresses these challenges with production-grade engineering principles:
1. **Never Uses Mock Data:** Every KPI card, trend chart, correlation heatmap, forecast interval, and business insight is computed directly from SQLite transactional records in real time.
2. **Eliminates Divide-by-Zero & False Growth:** Handles zero denominators safely and suppresses growth percentages when historical comparison baselines do not exist.
3. **Guarantees Zero Data Leakage:** Evaluates predictive models using strictly chronological 80/20 train/test splits.
4. **Protects Against Formula Injection:** Sanitizes uploaded and exported CSV files against spreadsheet formula execution (`=cmd|' /C calc'!A0`).
5. **Secures SQL Interactivity:** Enforces read-only SELECT execution in the SQL Analytics Lab using Abstract Syntax Tree (AST) query validation.
6. **Multi-Domain Benchmark Support:** Comes pre-loaded with 5 benchmark datasets totaling 16,000 transactional rows across B2B, Retail, Customer Loyalty, D2C E-Commerce, and HR Workforce domains.

---

## 2. Key Modules & Features

- **Executive BI Dashboard:** 6 core financial KPIs (Total Revenue, Total Profit, Profit Margin %, Total Orders, Average Order Value, Active Customers), Revenue/Profit area trends, Sales by Category, Regional distribution, Top/Bottom products, and recent order transactions with interactive filters.
- **Data Import & Quality Engine:** Drag-and-drop CSV upload, automated profiling, canonical column synonym mapper, Tukey IQR outlier detection, documented 0–100 Data Quality Score, formula injection defense, deduplication, median/mean imputation, and before/after comparison audit.
- **Exploratory Data Analysis (EDA):** Summary statistics table (Mean, Median, Std Dev, Min, 25%, 75%, Max, Skewness), dynamic 10-bin distribution histograms, Tukey's IQR box plot statistics, Pearson correlation heatmap matrix, and bivariate scatter plots.
- **Sales Analytics Deep Dive:** Month-over-Month (MoM) growth velocities, high-volume/low-margin product drag detection, category contribution, and paginated transaction drill-down.
- **Predictive Sales Forecasting:** Scikit-Learn Autoregressive Ridge Regression and Exponential Smoothing (EWMA) baselines, out-of-sample evaluated error metrics (MAE, RMSE, R2, and Safe MAPE %), with 95% confidence intervals and downloadable forecast CSVs.
- **Customer Segmentation (RFM + K-Means):** Deterministic 1–5 quintile scoring across Recency, Frequency, and Monetary dimensions. Classifies customers into 6 actionable segments (*Champions, Loyal, Potential Loyalists, At-Risk, Hibernating, New*) with unsupervised K-Means clustering.
- **Automated Business Insights:** Deterministic, transparent analytical rule engine generating actionable management findings with exact supporting numbers, calculation methodologies, and strategic recommendations.
- **Interactive SQL Analytics Lab:** Safe, read-only SQL execution against SQLite tables with an interview query catalog, AST syntax validator, latency timer, and sortable result grid.
- **Reports & Export Center:** Instant CSV downloads and automated high-resolution Executive PDF Report generation compiled with ReportLab.
- **Dataset Management:** Multi-dataset registration, metadata inspection, active dataset switching, domain tagging, and 1-click sample data restore.

---

## 3. Screenshots & Platform UI

```
+-------------------------------------------------------------------------------------------------------+
|  InsightIQ  |  [ Active: B2B Sales & Revenue Analytics v ]   (Restore Pristine Benchmark Data)       |
+-------------------------------------------------------------------------------------------------------+
|  Navigation    |  Executive KPI Cards                                                                |
|  - Dashboard   |  [ Total Revenue: $42.23M ]  [ Total Profit: $17.55M ]  [ Margin: 41.56% ]          |
|  - Data Import |  [ Total Deals: 2,800     ]  [ Avg Deal Size: $15,083 ] [ Accounts: 20   ]          |
|  - EDA         +-------------------------------------------------------------------------------------+
|  - Sales       |  Interactive Analytical Filters: Date Range | Region | Category | Segment            |
|  - Forecast    +---------------------------------------------------+---------------------------------+
|  - Segments    |  Revenue & Profit Growth Velocity (MoM Area)      |  Category Distribution (Bar)    |
|  - Insights    |  [~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~] |  Cloud Infrastructure:  48%     |
|  - SQL Lab     |  Forecast Projection (95% Confidence Band)        |  Cybersecurity:         28%     |
|  - Reports     |  [==== Historical ===|-- Predicted Model (Ridge)-] |  Enterprise Software:   24%     |
+-------------------------------------------------------------------------------------------------------+
```

| View | Module Description | Primary Components |
|---|---|---|
| **Executive Dashboard** | High-level performance overview and drill-downs | 6 KPI Cards, Recharts Area/Bar charts, FilterBar, Transactions Table |
| **Data Quality & Ingestion** | Automated data health inspection and cleaning | 0–100 Quality Score Gauge, Synonym Mapper, Outlier Auditing |
| **Exploratory Data Analysis** | Distribution profiling and bivariate correlation | Parametric stats table, Pearson Heatmap, IQR Box Plots, Histograms |
| **Sales Analytics** | Margin drag analysis and velocity monitoring | MoM growth calculations, Margin Drag Detector, Category Contribution |
| **Predictive Forecasting** | Machine learning autoregressive projections | Ridge Regression, EWMA, Safe MAPE calculation, 95% Confidence Bounds |
| **Customer RFM Segmentation**| Behavioral cohort clustering | 1–5 Quintile Scoring, K-Means clustering, Actionable Strategies |
| **SQL Analytics Lab** | Interactive read-only query workshop | AST SQL Parser (`sqlglot`), Query Catalog, Latency Timer, Data Table |
| **Executive Reports** | Formal PDF generation & CSV exports | ReportLab 2-page C-level PDF with embedded KPIs, summaries, and charts |

> *Tip: To capture actual screenshots for your repository, start the application locally with `./run_backend.sh` and `./run_frontend.sh`, take full-resolution captures of each page, and place them in `docs/screenshots/`.*

---

## 4. Multi-Domain Benchmark Datasets & Relational Schema

InsightIQ comes pre-configured with **5 production benchmark datasets** totaling **16,000 transactional rows** spanning 24 continuous months (2024-01-01 to 2025-12-31):

1. **Global Superstore Retail (`sample_superstore`):** 3,200 retail omnichannel transactions across Technology, Furniture, and Office Supplies.
2. **B2B Sales & Revenue (`sales_revenue_analytics`):** 2,800 enterprise sales pipeline contracts across Cloud Infrastructure, Cybersecurity, Enterprise Software, and Consulting.
3. **Customer Loyalty (`customer_analytics`):** 3,400 retail loyalty transactions across 300 member cohorts (Platinum VIP, Gold, Silver, Regular) with power-law repeat purchase frequency for rich RFM quintile segmentation.
4. **D2C E-Commerce (`ecommerce_analytics`):** 3,600 direct-to-consumer store orders across 450 shoppers tracking traffic acquisition channels (Organic, Paid Google, Social Ad, Email, Affiliate) with seasonal Q4 Black Friday/Cyber Week spikes.
5. **Workforce & HR Analytics (`hr_analytics`):** 3,000 monthly workforce allocation lines across 320 employees in Engineering, Sales, Operations, and Finance, tracking total compensation cost, FTE headcount, and net human capital return.

### Universal Relational Schema
All 5 domain datasets share the optimized `sales_data` relational schema:
- **B2B Enterprise:** `order_id` = Deal ID, `customer_id` = Account ID, `segment` = Client Tier, `category` = Product Line.
- **Customer Loyalty:** `order_id` = Receipt ID, `customer_id` = Loyalty ID, `segment` = Membership Tier.
- **D2C E-Commerce:** `segment` = Marketing Channel, `region` = Fulfillment Zone, `category` = Merchandise Category.
- **Workforce & HR:** `order_id` = Allocation ID, `customer_id` = Employee ID, `category` = Department, `revenue` = Value Output ($), `cost` = Compensation Cost ($), `profit` = Net Human Capital Return ($).

- **Fixed Random Seed:** `random.seed(42)` ensures mathematical reproducibility across all demo sessions.
- **Consistent Accounting Equations:**
  $$\text{Revenue} = \text{Quantity} \times \text{Unit Price} \times (1 - \text{Discount})$$
  $$\text{Profit} = \text{Revenue} - \text{COGS} - \text{Shipping Cost}$$

---

## 5. Technology Stack

### Backend
- **Framework:** Python 3 (FastAPI 0.110+)
- **Data Processing:** Pandas, NumPy
- **Machine Learning:** Scikit-learn (Ridge Regression, K-Means Clustering, StandardScaler)
- **Database:** SQLite (Relational transactional storage with index optimization, WAL mode, and connection pooling)
- **Validation:** Pydantic v2
- **SQL AST Parser:** `sqlglot`
- **PDF Generation:** ReportLab
- **Testing:** Pytest, HTTPX

### Frontend
- **Framework:** React 18 (TypeScript)
- **Build Tool:** Vite
- **Styling:** Tailwind CSS
- **Visualizations:** Recharts
- **Icons:** Lucide React
- **Routing:** React Router v6
- **Testing:** Vitest, React Testing Library, jsdom

---

## 6. Quick Start & Setup Instructions

### Prerequisites
- Python 3.10+ (Tested on Python 3.14 & 3.11)
- Node.js v18+ & npm
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/InsightIQ-Business-Analytics.git
cd InsightIQ-Business-Analytics
```

### Option A: Local Development (Recommended)

#### Start the Backend API (Port 8000)
```bash
./run_backend.sh
```
*Alternatively, manual command:*
```bash
python3 -m venv backend/venv
source backend/venv/bin/activate
pip install -r backend/requirements.txt
PYTHONPATH=. uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
*The backend automatically initializes the SQLite schema and seeds all 5 benchmark domain datasets (16,000 records) upon initial startup.*
- **API Health Check:** `http://127.0.0.1:8000/api/health`
- **Interactive Swagger Docs:** `http://127.0.0.1:8000/docs`

#### Start the Frontend Application (Port 5173)
In a separate terminal window:
```bash
./run_frontend.sh
```
*Alternatively, manual command:*
```bash
cd frontend
npm install
npm run dev
```
Open **`http://localhost:5173`** in your browser.

---

### Option B: Docker Compose (Zero Setup)
```bash
docker compose up -d --build
```
Access the application at `http://localhost` and API docs at `http://localhost:8000/docs`.

---

## 7. Automated Test Suite & QA Verification

InsightIQ includes comprehensive test suites covering all backend analytical contracts, zero-denominator safeguards, formula injection protection, SQL AST security, multi-domain dataset integrity, and frontend component rendering.

### Run Backend Tests (28 Tests)
```bash
PYTHONPATH=. backend/venv/bin/pytest backend/tests/test_backend.py -v
```
**Verified Results:**
- 28/28 tests passed in **1.62s**.
- Covers health checks, KPI formulas, AST query security, safe MAPE calculation, ML forecasting, RFM quintile segmentation, CSV/PDF exports, EDA statistics, multi-domain dataset registration, and dataset deletion safeguards.

### Run Frontend Unit Tests (3 Tests)
```bash
cd frontend && npm test -- --run
```
**Verified Results:**
- 3/3 tests passed in **689ms**.
- Covers MetricCard rendering, FilterBar interaction, and UI state handlers (Loading, Error, Empty states).

### Run Frontend Production Build & Type-Check
```bash
cd frontend && npm run build
```
**Verified Results:**
- TypeScript strict type-check: **0 errors**.
- Vite code-split bundle generated: **17 optimized chunks** (~1.4s).

---

## 8. API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | GET | System status and database records count |
| `/api/datasets` | GET | Catalog of available datasets |
| `/api/datasets/reset-sample` | POST | Reseeds default benchmark datasets |
| `/api/upload/preview` | POST | Profiles uploaded CSV and returns Data Quality Score |
| `/api/upload/clean` | POST | Applies cleaning transforms and ingests to SQLite |
| `/api/analytics/dashboard` | GET | Filtered executive KPIs and dashboard aggregations |
| `/api/analytics/eda` | GET | Descriptive statistics, histograms, and correlation matrix |
| `/api/analytics/sales` | GET | MoM sales growth, margin drag detection, and drill-down |
| `/api/analytics/forecast` | POST | Autoregressive Ridge / EWMA predictive forecasting |
| `/api/analytics/segmentation`| GET | RFM quintile segmentation and K-Means clusters |
| `/api/analytics/insights` | GET | Rule-based business findings and recommendations |
| `/api/sql-lab/samples` | GET | Curated library of business SQL queries |
| `/api/sql-lab/execute` | POST | AST-validated read-only SQL query execution |
| `/api/export/csv` | GET | Download filtered transactions as sanitized CSV |
| `/api/export/pdf` | GET | Download certified Executive Summary PDF report |

---

## 9. Project Documentation Directory

Detailed engineering guides and interview preparation materials are available in [`docs/`](docs/):
- [**`docs/DEPLOYMENT.md`**](docs/DEPLOYMENT.md): Production deployment guide covering Docker, Linux VPS/systemd/Nginx, SSL certificates, PaaS clouds, and backup strategies.
- [**`docs/ARCHITECTURE.md`**](docs/ARCHITECTURE.md): System architecture, data ingestion flows, and Mermaid diagrams.
- [**`docs/PROJECT_REPORT.md`**](docs/PROJECT_REPORT.md): Formal final-year academic capstone report structure.
- [**`docs/DEMO_SCRIPT.md`**](docs/DEMO_SCRIPT.md): 5–7 minute interview demonstration plan.
- [**`docs/INTERVIEW_PREPARATION.md`**](docs/INTERVIEW_PREPARATION.md): Technical decisions, SQL deep-dives, analytics concepts, and likely interviewer questions.
- [**`docs/TESTING.md`**](docs/TESTING.md): QA verification logs, commands, and actual execution outputs.

---

## 10. License

Developed for academic demonstration and interview evaluation. Released under the [MIT License](LICENSE).
