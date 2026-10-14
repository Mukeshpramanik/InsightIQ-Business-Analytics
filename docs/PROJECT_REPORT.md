# InsightIQ — Final-Year Engineering Capstone Project Report

**Title:** InsightIQ: A Production-Grade Business Intelligence, Data Quality & Predictive Analytics Platform  
**Target Roles:** Data Analyst, Business Intelligence Engineer, Junior Data Scientist  
**Academic Year:** 2025–2026  
**Tech Stack:** Python 3 (FastAPI, Pandas, Scikit-learn, SQLite, sqlglot, ReportLab), React 18 (TypeScript, Vite, Tailwind CSS, Recharts)

---

## Abstract

Modern enterprises face significant challenges converting fragmented transactional sales data into validated, decision-grade business intelligence. Conventional enterprise BI tools often suffer from high license costs, opaque data cleaning transformations, vulnerability to spreadsheet injection, and a lack of integrated statistical validation for forward-looking projections. 

This project presents **InsightIQ**, an end-to-end, reproducible Business Intelligence and Predictive Analytics platform built from the ground up. InsightIQ automates data profiling, canonical schema mapping, Tukey's IQR outlier detection, and formula injection sanitization with a mathematically documented Data Quality Score. It provides a real-time executive dashboard calculating certified financial metrics (Revenue, Profit, AOV, Profit Margin) with zero-denominator safety and chronological baseline comparisons. Furthermore, the platform integrates autoregressive machine learning models with time-ordered train/test validation, deterministic RFM customer segmentation, a transparent rule-based insight engine, an AST-validated SQL lab, and automated ReportLab executive PDF generation. Automated test suites verify 100% mathematical accuracy across all modules without relying on external cloud APIs or paid dependencies.

---

## 1. Introduction

### 1.1 Problem Statement
Small-to-medium businesses and departmental analysts frequently rely on manual spreadsheets to calculate critical KPIs and forecast future demand. This manual paradigm leads to:
1. **Mathematical Errors:** Unhandled zero-denominators, erroneous growth comparisons without baselines, and misleading visual representations.
2. **Data Leakage in Forecasting:** Using future observations to train time-series models, resulting in artificial overconfidence and disastrous operational stockouts.
3. **Data Quality Blind Spots:** Hidden duplicate records, erratic date formats, and spreadsheet formula injection vulnerabilities (`=cmd|' /C calc'!A0`).
4. **Tool Fragmentation:** Shuffling data across disconnected tools for cleaning, SQL querying, clustering, and executive reporting.

### 1.2 Objectives
The primary objective of InsightIQ is to build a unified, resilient web platform that:
- Ingests raw sales CSVs, checks data quality, and cleans data idempotently.
- Computes certified business KPIs derived strictly from active dataset records.
- Delivers interactive statistical EDA (descriptive stats, histograms, box plots, correlation heatmaps).
- Predicts forward sales and order volumes using time-ordered machine learning with confidence bands and safe error metrics (MAE, RMSE, safe MAPE).
- Segments customer bases deterministically using RFM quintiles and unsupervised K-Means clustering.
- Surfaces actionable management recommendations via an audited analytical rule engine.
- Provides an interactive SQL Analytics Lab secured by Abstract Syntax Tree (AST) validation.

---

## 2. Methodology & Mathematical Formulations

### 2.1 Certified Business KPI Formulas
All metrics in InsightIQ are computed dynamically from active dataset transactions:

$$\text{Total Revenue} = \sum_{i=1}^{N} \Big(\text{Quantity}_i \times \text{Unit Price}_i \times (1 - \text{Discount}_i)\Big)$$

$$\text{Total Profit} = \sum_{i=1}^{N} \Big(\text{Revenue}_i - \text{COGS}_i - \text{Shipping Cost}_i\Big)$$

$$\text{Average Order Value (AOV)} = \begin{cases} \frac{\text{Total Revenue}}{\text{Count of Distinct Order IDs}}, & \text{Orders} > 0 \\ 0.0, & \text{Orders} = 0 \end{cases}$$

$$\text{Net Profit Margin (\%)} = \begin{cases} \frac{\text{Total Profit}}{\text{Total Revenue}} \times 100, & \text{Revenue} > 0 \\ 0.0, & \text{Revenue} = 0 \end{cases}$$

$$\text{Period Growth (\%)} = \begin{cases} \frac{\text{Current Period Revenue} - \text{Baseline Revenue}}{\text{Baseline Revenue}} \times 100, & \text{Baseline} > 0 \\ \text{null (suppressed)}, & \text{No Valid Baseline} \end{cases}$$

### 2.2 Data Quality Scoring Formula
InsightIQ calculates an objective quality score $S \in [0, 100]$:

$$S = \max\Big(0, \min\big(100, 100 - (P_{\text{missing}} + P_{\text{duplicate}} + P_{\text{outlier}} + P_{\text{mapping}} + P_{\text{type}})\big)\Big)$$

- $P_{\text{missing}} = \min\big(25, \frac{\text{Missing Cells}}{\text{Total Cells}} \times 100\big)$
- $P_{\text{duplicate}} = \min\big(20, \frac{\text{Duplicate Rows}}{\text{Total Rows}} \times 100\big)$
- $P_{\text{outlier}} = \min\big(20, \frac{\text{Outliers Identified}}{\text{Numeric Cells}} \times 150\big)$ via Tukey's $[Q_1 - 1.5\text{IQR}, Q_3 + 1.5\text{IQR}]$
- $P_{\text{mapping}} = \frac{\text{Unmapped Critical Fields}}{3} \times 20$ (evaluating `order_date`, `revenue`, `quantity`)
- $P_{\text{type}} = \min\big(15, \frac{\text{Format Anomalies}}{\text{Total Rows}} \times 100\big)$

### 2.3 Safe Error Metrics in Sales Forecasting
To evaluate out-of-sample forecast accuracy without numerical instability:

$$\text{MAE} = \frac{1}{M} \sum_{t=1}^{M} |y_t - \hat{y}_t|, \quad \text{RMSE} = \sqrt{\frac{1}{M} \sum_{t=1}^{M} (y_t - \hat{y}_t)^2}$$

$$\text{Safe MAPE (\%)} = \frac{100}{|\{t : y_t \neq 0\}|} \sum_{t: y_t \neq 0} \left|\frac{y_t - \hat{y}_t}{y_t}\right|$$

Periods where actual demand $y_t = 0$ are accounted for in a distinct metric (`zero_actuals_count`) rather than dividing by zero or producing infinite percentages.

---

## 3. Results & Acceptance Testing

The platform was tested across synthetic enterprise benchmark datasets spanning 3,200 orders across 24 continuous months.

| Evaluation Area | Expected Behavior | Actual System Result | Status |
|---|---|---|---|
| Startup & Seeding | Idempotent initial seed of 3,200 orders | 3,200 records loaded, seed fixed at 42 | **PASSED** |
| KPI Precision | Verified against independent analytical calculation | Margin: 25.94%, Revenue: $2,703,982.31 | **PASSED** |
| Zero Denominator Safety | Zero revenue/orders query returns 0.0, no 500 error | Handled safely via conditional SQLite logic | **PASSED** |
| Formula Injection Defense | Strips/prepends single quote to dangerous symbols | `=cmd...` sanitized to `'=cmd...` | **PASSED** |
| SQL AST Validation | Rejects DROP, DELETE, multi-statement, sys tables | Rejected with descriptive AST error messages | **PASSED** |
| Forecast Leakage | Strict chronological train/test split | Out-of-sample evaluated on final 20% | **PASSED** |
| PDF Export | Valid PDF byte stream with tables and styles | Valid `%PDF-1.4` generated via ReportLab | **PASSED** |

---

## 4. Conclusion & Interview Suitability

InsightIQ fulfills all academic requirements for a final-year computer science/data science capstone. Its adherence to defensive engineering, strict statistical methodology, clean frontend/backend separation, and auditable data contracts makes it directly applicable for technical interviews across Data Analyst, Business Analyst, and Junior Data Scientist candidate evaluations.
