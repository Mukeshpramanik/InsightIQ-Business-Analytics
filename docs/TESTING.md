# InsightIQ — Quality Assurance & Test Verification Report

This document records the automated testing architecture, verification procedures, and actual test execution outputs across backend and frontend test suites.

---

## 1. Automated Test Architecture

```
InsightIQ/
├── backend/tests/
│   ├── __init__.py
│   └── test_backend.py        # 16 Pytest test cases covering API, KPIs, cleaning, SQL AST, ML, exports
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
cd frontend && npm test
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
rootdir: /Users/mukeshpramanik/Desktop/InsightIQ
plugins: anyio-4.15.1
collected 16 items                                                             

backend/tests/test_backend.py::test_health_check PASSED                  [  6%]
backend/tests/test_backend.py::test_list_datasets PASSED                 [ 12%]
backend/tests/test_backend.py::test_kpi_calculations_and_formulas PASSED [ 18%]
backend/tests/test_backend.py::test_kpi_zero_denominator_safety PASSED   [ 25%]
backend/tests/test_backend.py::test_formula_injection_defense PASSED     [ 31%]
backend/tests/test_backend.py::test_canonical_mapping_inference PASSED   [ 37%]
backend/tests/test_backend.py::test_data_cleaning_pipeline PASSED        [ 43%]
backend/tests/test_backend.py::test_sql_lab_allowed_query PASSED         [ 50%]
backend/tests/test_backend.py::test_sql_lab_rejects_disallowed_dml PASSED [ 56%]
backend/tests/test_backend.py::test_sql_lab_rejects_multiple_statements PASSED [ 62%]
backend/tests/test_backend.py::test_sql_lab_rejects_unauthorized_tables PASSED [ 68%]
backend/tests/test_backend.py::test_safe_mape_calculation PASSED         [ 75%]
backend/tests/test_backend.py::test_forecasting_pipeline PASSED          [ 81%]
backend/tests/test_backend.py::test_rfm_segmentation PASSED              [ 87%]
backend/tests/test_backend.py::test_csv_export_endpoint PASSED           [ 93%]
backend/tests/test_backend.py::test_pdf_export_endpoint PASSED           [100%]

======================== 16 passed, 4 warnings in 1.46s ========================
```

---

## 4. Verified Frontend Test Execution Output

```
> insightiq-frontend@1.0.0 test
> vitest run

 RUN  v2.1.9 /Users/mukeshpramanik/Desktop/InsightIQ/frontend

 ✓ src/__tests__/App.test.tsx (3)
   ✓ InsightIQ UI Component Suite (3)
     ✓ renders MetricCard with title, value, and formula note correctly
     ✓ renders FilterBar with options and handles interactions
     ✓ renders LoadingSpinner, ErrorAlert, and EmptyState components

 Test Files  1 passed (1)
      Tests  3 passed (3)
   Start at  10:09:40
   Duration  476ms
```

---

## 5. Verified Production Build Output

```
> insightiq-frontend@1.0.0 build
> tsc && vite build

vite v5.4.21 building for production...
✓ 2382 modules transformed.
dist/index.html                   1.15 kB │ gzip:   0.63 kB
dist/assets/index-BqnsYMAP.css   28.77 kB │ gzip:   5.67 kB
dist/assets/index-BlTZ4IGr.js   733.46 kB │ gzip: 195.60 kB
✓ built in 1.45s
```

---

## 6. Coverage Summary & Mathematical Guarantees

1. **Formula Invariance:** Formula checks assert that $AOV = \frac{\text{Revenue}}{\text{Orders}}$ and $\text{Margin} = \frac{\text{Profit}}{\text{Revenue}} \times 100$ within $\pm 0.05$ rounding tolerance.
2. **Zero-Denominator Defense:** Empty subset queries return zero without throwing divide-by-zero exceptions.
3. **Formula Injection Sanitization:** Verifies leading `=`, `+`, `-`, `@` characters are safely neutralized.
4. **AST Read-Only Security:** Verifies that DDL, DML, multiple statements, and system catalog access (`sqlite_master`) are rejected before execution.
5. **PDF Compilation:** Verifies pure Python binary `%PDF` compilation with ReportLab.
