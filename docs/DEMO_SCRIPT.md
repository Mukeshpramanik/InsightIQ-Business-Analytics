# InsightIQ — 5–7 Minute Interview & Project Demonstration Script

**Objective:** Conduct a crisp, confident, professional demonstration of InsightIQ showcasing full-stack competency, data engineering rigor, statistical validity, and business acumen.

---

## Minute 0:00 – 1:00 | Executive Overview & Financial Integrity
1. **Introduction:**
   - *"Welcome! This is InsightIQ — a production-grade Business Intelligence and Predictive Analytics platform I engineered as my final-year project."*
   - *"Unlike static UI dashboards, every number, filter, visualization, and ML model in InsightIQ is computed dynamically from the active SQLite database without hardcoding."*
2. **Dashboard Tour:**
   - Point out the **6 Executive KPI Cards**:
     - *Total Revenue ($2.70M), Total Profit ($701K), Profit Margin (25.94%), Total Orders (3,200), AOV ($844.99), Active Customers (350).*
   - Hover over the **Info icon** on Average Order Value or Profit Margin to demonstrate documented business formulas.
   - Change a filter (e.g., select Region = "West" or Category = "Technology").
   - Demonstrate how every card, area chart, category pie chart, and recent orders table updates instantly in real time.
   - Click **Reset Filters** to restore full dataset scope.

---

## Minute 1:00 – 2:15 | Data Ingestion, Profiling & Quality Engine
1. **Navigate to "Data Import & Quality"** in the sidebar.
2. **Demonstrate Automated Profiling:**
   - Click the button **"Load Demo Dataset (With Issues)"** at the top right.
   - Explain: *"This loads a real-world test dataset containing deliberate duplicates, missing discount values, trailing whitespace, and unformatted dates."*
   - Highlight the **Data Quality Score**: *"The engine calculates an objective 0-100 quality score using a documented mathematical penalty model."*
   - Point out the **Spreadsheet Formula Injection Defense**: *"Notice that text strings beginning with `=`, `+`, `-`, or `@` are sanitized with leading single quotes to prevent CSV injection vulnerabilities in Excel."*
3. **Execute Cleaning Pipeline:**
   - Review the column mapping suggestions (canonical synonym matching).
   - Click **"Apply Cleaning & Ingest Dataset"**.
   - Show the **Cleaning Audit Banner**: *"Rows deduplicated, nulls imputed via median, and quality score improved from Fair to Excellent."*

---

## Minute 2:15 – 3:30 | Exploratory Data Analysis (EDA) Workspace
1. **Navigate to "Exploratory EDA"**:
   - Highlight the **Parametric & Non-Parametric Summary Statistics Table**: Mean, Median, Std Dev, Min, 25%, 75%, Max, and Skewness coefficients.
   - Switch the histogram variable dropdown from `revenue` to `profit` or `discount` to show dynamic 10-bin frequency density.
2. **Tukey's IQR Outlier Analysis:**
   - Point out the 5-number summary and IQR fence calculations:
   - *"Here we clearly distinguish statistical outliers from data errors. The upper fence transactions represent legitimate enterprise bulk orders."*
3. **Pearson Correlation Heatmap & Bivariate Scatter:**
   - Show the correlation matrix table: highlight the strong positive relationship between revenue and profit, and the margin compression associated with deep discounts.
   - Hover over points in the scatter plot to display line-item order details.

---

## Minute 3:30 – 4:30 | Predictive Analytics & Sales Forecasting
1. **Navigate to "Sales Forecasting"**:
   - Select Target Metric: **Gross Sales Revenue ($)**, Granularity: **Monthly ('MS')**, Horizon: **6 Months Ahead**.
   - Select Model: **Scikit-Learn Ridge (Autoregressive)** and click **Run Model**.
2. **Explain Rigorous ML Methodology:**
   - *"A critical design rule in InsightIQ is the prevention of data leakage. We use a strictly time-ordered 80% train / 20% test split, never training on future observations."*
   - Point out the **Out-of-Sample Performance Cards**: MAE, RMSE, R2, and **Safe MAPE %**.
   - *"Notice our safe MAPE formula: periods with zero actual demand are tracked separately rather than dividing by zero."*
   - Hover over the forward projection showing the **95% Confidence Interval band**.
   - Click **"Download Forecast CSV"** to demonstrate immediate CSV report generation.

---

## Minute 4:30 – 5:30 | Customer Segmentation & Business Insights
1. **Navigate to "Customer Segmentation"**:
   - Explain the **RFM Framework**:
     - *Recency (days since last order), Frequency (distinct orders), Monetary (total spend).*
   - Showcase the **5 deterministic quintile groups**: *Champions, Loyal Customers, Potential Loyalists, At-Risk Customers, and Hibernating.*
   - Point out the strategic recommendation card for each group.
   - Toggle **"Enable K-Means ML Clustering"** to show unsupervised cluster assignment side-by-side with rule-based RFM.
2. **Navigate to "Business Insights"**:
   - Explain the transparent analytical rule engine:
     - *"No hallucinating chatbots or fake AI labels. These findings are derived from real mathematical conditions."*
   - Highlight the **Margin Drag Finding**: detects high-volume products contributing top-line sales but delivering sub-10% margins.
   - Highlight the **Customer Concentration (Pareto 80/20)** finding.

---

## Minute 5:30 – 7:00 | SQL Analytics Lab, PDF Export & Wrap-Up
1. **Navigate to "SQL Analytics Lab"**:
   - Click on the pre-built query: **"Month-over-Month (MoM) Growth via Window Functions"**.
   - Click **"Execute SQL"** — show sub-10ms query execution with `LAG() OVER ()`.
   - **Demonstrate AST Security:**
     - Type `DROP TABLE sales_data;` into the editor and click Execute.
     - Show the red warning banner: *"Rejected by AST Security Engine: Non-read operation 'DROP' is forbidden."*
     - Show that multi-statements (`SELECT 1; DROP TABLE sales_data;`) and unauthorized tables (`sqlite_master`) are also rejected.
2. **Navigate to "Reports & Export"**:
   - Click **"Download Executive PDF Report"**.
   - Open the generated PDF: show the professional ReportLab executive summary containing KPI tables, category performance, RFM distributions, and methodology disclaimers.
3. **Closing Statement:**
   - *"InsightIQ demonstrates end-to-end full-stack capabilities, data pipeline hygiene, rigorous predictive analytics, and secure SQL query execution ready for production deployment."*
