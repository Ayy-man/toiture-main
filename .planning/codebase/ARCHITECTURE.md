# Architecture

**Analysis Date:** 2026-01-18

## Pattern Overview

**Overall:** Data Pipeline + ML Training Architecture (Pre-Application Phase)

**Key Characteristics:**
- Data science/ML project in exploratory phase, not yet a deployed application
- Batch processing pipelines that transform raw CSV exports into ML-ready datasets
- Multiple iterative model training scripts (v1-v4) with hyperparameter tuning
- Planned 3-tier web architecture (FastAPI backend + Next.js frontend + Pinecone vector DB) documented but not yet implemented
- Case-Based Reasoning (CBR) approach with embeddings for similarity search

## Layers

**Data Ingestion Layer:**
- Purpose: Parse and clean raw C-Cube CSV exports (transposed format)
- Location: `cortex-data/discover.py`
- Contains: CSV parsing logic for transposed data format, field extraction
- Depends on: Raw CSV files (`Quote*.csv`)
- Used by: Data pipeline layer

**Data Pipeline Layer:**
- Purpose: Transform raw data into ML-ready master datasets
- Location: `cortex-data/master_data_pipeline_v4.py`
- Contains: Data aggregation, feature extraction (sqft, pitch, layers), derived metrics calculation, anomaly flagging
- Depends on: Cleaned CSV files (`*_clean.csv`)
- Used by: Analysis and training layers
- Outputs: `master_quotes.csv`, `master_quotes_valid.csv`, `master_quotes_labor_reliable.csv`

**Analysis Layer:**
- Purpose: Generate business intelligence and data quality insights
- Location: `cortex-data/comprehensive_analysis.py`, `cortex-data/deep_analysis.py`
- Contains: Visualization generation (matplotlib), statistical analysis, executive summaries
- Depends on: `master_quotes_valid.csv`
- Used by: Human stakeholders for decision-making
- Outputs: PNG charts, TXT reports

**ML Training Layer:**
- Purpose: Train and optimize price prediction models
- Location: `cortex-data/train_cortex_v4.py` (latest), `cortex-data/train_cortex_v3.py`, `cortex-data/train_cortex_v2.py`
- Contains: Feature engineering, model training (GradientBoosting, RandomForest), hyperparameter tuning (GridSearchCV), cross-validation
- Depends on: `master_quotes_valid.csv`
- Used by: Prediction layer
- Outputs: `cortex_v4_bardeaux.pkl`, `cortex_v4_gb.pkl`, `cortex_v4_rf.pkl`, `cortex_config_v4.json`

**Prediction Layer:**
- Purpose: Load trained models and generate price estimates
- Location: `cortex-data/predict_final.py`
- Contains: Model loading, feature construction, confidence scoring
- Depends on: Trained model files (`.pkl`), config files (`.json`)
- Used by: CLI users (currently), planned web API

**CBR/Embeddings Layer (Prepared but not deployed):**
- Purpose: Store and retrieve similar historical cases via vector similarity
- Location: `cortex-data/cbr_cases.json`, `cortex-data/cbr_embeddings.npz`
- Contains: 8,132 case embeddings (384-dim from `paraphrase-multilingual-MiniLM-L12-v2`)
- Depends on: Master quote data
- Used by: Planned Pinecone upload, hybrid retrieval system

## Data Flow

**Raw Data to Predictions (Current State):**

1. Raw CSV export from C-Cube (transposed format) loaded via `discover.py`
2. Cleaned CSVs produced (`*_clean.csv`)
3. `master_data_pipeline_v4.py` aggregates materials, labor, subs, extracts features
4. `master_quotes_valid.csv` created with calculated fields (margins, $/sqft, complexity)
5. `train_cortex_v4.py` loads valid quotes, engineers features, trains models
6. Models saved as `.pkl` files with config in `cortex_config_v4.json`
7. `predict_final.py` loads models and provides CLI predictions

**Planned Production Flow (Not Yet Implemented):**

1. User submits roof specs via Next.js form
2. Next.js API route proxies to FastAPI backend
3. FastAPI queries Pinecone for similar historical cases
4. CBR engine combines structured filters + semantic ranking
5. LLM (Mistral 7B via OpenRouter) revises estimate with confidence
6. Response returned with estimate range, similar cases, reasoning

**State Management:**
- No runtime state management (batch processing)
- Model state persisted in `.pkl` files
- Configuration in `.json` files
- Embeddings in `.npz` (numpy compressed) and `.json` formats

## Key Abstractions

**Quote/Case:**
- Purpose: Represents a historical roofing job with pricing
- Examples: Records in `master_quotes_valid.csv`, cases in `cbr_cases.json`
- Pattern: Flat record with 50+ fields including derived metrics

**Prediction Result:**
- Purpose: Structured estimate output with confidence
- Examples: Return dict in `predict_final.py`
- Pattern: Dictionary with `estimate`, `range_low`, `range_high`, `model`, `confidence`

**Pipeline Step:**
- Purpose: Transform data through aggregation or calculation
- Examples: `materials_agg`, `labor_agg`, `sub_agg` in pipeline
- Pattern: pandas groupby → agg → merge onto master

## Entry Points

**Data Ingestion:**
- Location: `cortex-data/discover.py`
- Triggers: Manual execution for new C-Cube exports
- Responsibilities: Parse transposed CSV, extract records, save clean version

**Data Pipeline:**
- Location: `cortex-data/master_data_pipeline_v4.py`
- Triggers: Manual execution after new clean data available
- Responsibilities: Aggregate all data sources, calculate derived metrics, flag anomalies, export master files

**Model Training:**
- Location: `cortex-data/train_cortex_v4.py`
- Triggers: Manual execution to retrain models
- Responsibilities: Feature engineering, model selection, hyperparameter tuning, model persistence

**Prediction CLI:**
- Location: `cortex-data/predict_final.py`
- Triggers: CLI execution with sqft and category arguments
- Responsibilities: Load models, construct features, return estimate

**Planned Web Entry Points (From Spec):**
- Backend: `backend/app/main.py` (FastAPI) - Not yet created
- Frontend: `frontend/app/page.tsx` (Next.js) - Not yet created
- API Endpoint: `POST /estimate` - Specified but not implemented

## Error Handling

**Strategy:** Minimal error handling with warnings suppression

**Patterns:**
- `warnings.filterwarnings('ignore')` used throughout training scripts
- `pd.to_numeric(..., errors='coerce')` for type conversion failures
- `try/except` with basic fallback for encoding issues in CSV parsing
- No structured error logging or monitoring

## Cross-Cutting Concerns

**Logging:** Print statements with progress indicators (`[1/14]`, `✓` markers)

**Validation:**
- Anomaly flags in pipeline (`flag_anomalies` function)
- `is_valid_for_analysis` boolean filter in output
- Data quality checks (year range, margin bounds, price bounds)

**Configuration:**
- Hardcoded paths (`DATA_PATH = "/Users/aymanbaig/Desktop/cortex-data/"`)
- Model hyperparameters stored in `cortex_config_v4.json`
- Inflation factors embedded in code and config

**Authentication:** None (local scripts only)

---

*Architecture analysis: 2026-01-18*
