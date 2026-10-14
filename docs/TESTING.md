# InsightIQ — Quality Assurance & Test Verification Report

This document records the automated testing architecture, verification procedures, and actual test execution outputs across backend and frontend test suites.

---

## 1. Automated Test Architecture

```
InsightIQ/
├── backend/tests/
│   ├── __init__.py
│   └── test_backend.py        # 28 Pytest test cases covering API, KPIs, cleaning, SQL AST, ML, exports, security headers, metadata, multi-dataset registration, domain verification, and deletion safety
└── frontend/src/__tests__/
    ├── setupTests.ts
    └── App.test.tsx           # 3 Vitest component & filter interaction test cases
```

---

## 2. Test Execution Commands

### Run Backend Test Suite
```bash
PYTHONPATH=. backend/venv/bin/pytest backend/tests/test_backend.py -v
```

### Run Frontend Unit Tests
```bash
cd frontend && npm test -- --run
```

### Run Frontend Production Type-Check & Build
```bash
cd frontend && npm run build
```

---

## 3. Verified Backend Test Execution Output

```
============================= test session starts ==============================
platform darwin -- Python 3.14.3, pytest-9.1.1, pluggy-1.6.0 -- /Users/mukeshpramanik/Desktop/InsightIQ/backend/venv/bin/python3.14
cachedir: .pytest_cache
rootdir: /Users/mukeshpramanik/Desktop/InsightIQ
plugins: anyio-4.15.1
collected 28 items

backend/tests/test_backend.py::test_health_check PASSED                  [  3%]
backend/tests/test_backend.py::test_list_datasets PASSED                 [  7%]
backend/tests/test_backend.py::test_kpi_calculations_and_formulas PASSED [ 10%]
backend/tests/test_backend.py::test_kpi_zero_denominator_safety PASSED   [ 14%]
backend/tests/test_backend.py::test_formula_injection_defense PASSED     [ 17%]
backend/tests/test_backend.py::test_canonical_mapping_inference PASSED   [ 21%]
backend/tests/test_backend.py::test_data_cleaning_pipeline PASSED        [ 25%]
backend/tests/test_backend.py::test_sql_lab_allowed_query PASSED         [ 28%]
backend/tests/test_backend.py::test_sql_lab_rejects_disallowed_dml PASSED [ 32%]
backend/tests/test_backend.py::test_sql_lab_rejects_multiple_statements PASSED [ 35%]
backend/tests/test_backend.py::test_sql_lab_rejects_unauthorized_tables PASSED [ 39%]
backend/tests/test_backend.py::test_safe_mape_calculation PASSED         [ 42%]
backend/tests/test_backend.py::test_forecasting_pipeline PASSED          [ 46%]
backend/tests/test_backend.py::test_rfm_segmentation PASSED              [ 50%]
backend/tests/test_backend.py::test_csv_export_endpoint PASSED           [ 53%]
backend/tests/test_backend.py::test_pdf_export_endpoint PASSED           [ 57%]
backend/tests/test_backend.py::test_eda_analysis_sample_dataset PASSED   [ 60%]
backend/tests/test_backend.py::test_eda_empty_dataset PASSED             [ 64%]
backend/tests/test_backend.py::test_eda_missing_and_constant_numeric_columns PASSED [ 67%]
backend/tests/test_backend.py::test_security_headers PASSED              [ 71%]
backend/tests/test_backend.py::test_health_check_metadata PASSED         [ 75%]
backend/tests/test_backend.py::test_upload_and_temp_file_cleanup PASSED  [ 78%]
backend/tests/test_backend.py::test_all_five_benchmark_datasets_registered PASSED [ 82%]
backend/tests/test_backend.py::test_sales_revenue_analytics_suite PASSED [ 85%]
backend/tests/test_backend.py::test_customer_analytics_rfm_suite PASSED  [ 89%]
backend/tests/test_backend.py::test_ecommerce_analytics_forecasting_suite PASSED [ 92%]
backend/tests/test_backend.py::test_hr_analytics_suite PASSED            [ 96%]
backend/tests/test_backend.py::test_built_in_datasets_protected_from_deletion PASSED [100%]

======================== 28 passed in 1.68s =========================
```

---

## 4. Verified Frontend Test Execution Output

```
> insightiq-frontend@1.0.0 test
> vitest run --run

 RUN  v2.1.9 /Users/mukeshpramanik/Desktop/InsightIQ/frontend

 ✓ src/__tests__/App.test.tsx (3)
   ✓ InsightIQ UI Component Suite (3)
     ✓ renders MetricCard with title, value, and formula note correctly
     ✓ renders FilterBar with options and handles interactions
     ✓ renders LoadingSpinner, ErrorAlert, and EmptyState components

 Test Files  1 passed (1)
      Tests  3 passed (3)
   Start at  10:57:20
   Duration  606ms
```

---

## 5. Verified Production Build Output (Code-Split & Chunk Optimized)

```
> insightiq-frontend@1.0.0 build
> tsc && vite build

vite v5.4.21 building for production...
✓ 2384 modules transformed.
dist/index.html                               1.32 kB │ gzip:   0.69 kB
dist/assets/index-B95wJvE5.css               29.63 kB │ gzip:   5.79 kB
dist/assets/FilterBar-EIMxqIt9.js             4.09 kB │ gzip:   1.05 kB
dist/assets/DatasetsPage-CLVBTA-X.js          4.47 kB │ gzip:   1.68 kB
dist/assets/ReportsPage-BEDw6vKo.js           4.55 kB │ gzip:   1.78 kB
dist/assets/InsightsPage-DZjar7QZ.js          4.76 kB │ gzip:   1.77 kB
dist/assets/SqlLabPage-BlRAV_lQ.js            7.28 kB │ gzip:   2.38 kB
dist/assets/SalesAnalyticsPage-DF-b4dyb.js    9.32 kB │ gzip:   3.05 kB
dist/assets/ForecastingPage-D7B8XrWj.js      10.41 kB │ gzip:   3.03 kB
dist/assets/SegmentationPage-BwgJ_dsk.js     11.95 kB │ gzip:   3.26 kB
dist/assets/EdaPage-Da948jBP.js              13.11 kB │ gzip:   3.26 kB
dist/assets/DataImportPage-D77ShMaC.js       15.60 kB │ gzip:   4.06 kB
dist/assets/OverviewDashboard-BBM14kMv.js    17.34 kB │ gzip:   4.65 kB
dist/assets/vendor-icons-BPL8kRKu.js         18.57 kB │ gzip:   3.80 kB
dist/assets/index-CQ701OVH.js                22.24 kB │ gzip:   6.62 kB
dist/assets/vendor-react-q4n69DWJ.js        163.71 kB │ gzip:  53.41 kB
dist/assets/vendor-charts-BxyvGKB3.js       434.53 kB │ gzip: 115.19 kB
✓ built in 1.38s
```
