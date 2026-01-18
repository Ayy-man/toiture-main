# Technology Stack

**Analysis Date:** 2026-01-18

## Languages

**Primary:**
- Python 3.x - Data analysis, ML model training, prediction scripts, data pipelines

**Secondary:**
- TypeScript/JavaScript - Planned for Next.js frontend (not yet implemented)

## Runtime

**Environment:**
- Python 3.x (system Python or virtual environment)
- No `.nvmrc` or `.python-version` files detected

**Package Manager:**
- pip (implied) - No `requirements.txt` currently exists in repository
- npm/yarn planned for frontend - No `package.json` exists yet

**Lockfile:**
- Not present - No lockfiles detected

## Frameworks

**Core:**
- scikit-learn - Machine learning (GradientBoostingRegressor, RandomForestRegressor, Ridge, HuberRegressor, LabelEncoder)
- pandas - Data manipulation and CSV processing
- numpy - Numerical computing and array operations
- matplotlib - Data visualization and chart generation

**Testing:**
- Not configured - No test framework detected

**Build/Dev:**
- None currently - Scripts run directly with Python interpreter

## Key Dependencies

**Critical (Used in ML Training):**
- `sklearn.ensemble.GradientBoostingRegressor` - Primary prediction model
- `sklearn.ensemble.RandomForestRegressor` - Ensemble model component
- `sklearn.linear_model.Ridge` - Linear baseline model
- `sklearn.linear_model.HuberRegressor` - Robust regression
- `sklearn.preprocessing.LabelEncoder` - Category encoding
- `sklearn.model_selection.train_test_split` - Data splitting
- `sklearn.model_selection.cross_val_score` - Cross-validation
- `sklearn.model_selection.GridSearchCV` - Hyperparameter tuning
- `sklearn.metrics.*` - Model evaluation (MAE, R2, MAPE)

**Data Processing:**
- `pandas` - CSV reading, DataFrame operations, aggregations
- `numpy` - Numerical operations, log transforms, array manipulation
- `re` - Regular expressions for text extraction (sqft parsing)

**Visualization:**
- `matplotlib.pyplot` - Chart generation
- `matplotlib.ticker` - Axis formatting

**Serialization:**
- `joblib` - Model persistence (`.pkl` files)
- `json` - Configuration files

**Planned (Per Spec):**
- FastAPI - Backend API framework
- Pinecone - Vector database for CBR
- OpenRouter - LLM API for case revision
- Next.js 14 - Frontend framework
- sentence-transformers - Embedding generation (`paraphrase-multilingual-MiniLm-L12-v2`)

## Configuration

**Environment:**
- Hardcoded paths: `DATA_PATH = "/Users/aymanbaig/Desktop/cortex-data/"`
- No `.env` files present
- No environment variable configuration

**Planned Environment Variables (Per Spec):**
```
PINECONE_API_KEY=xxx
OPENROUTER_API_KEY=xxx
INDEX_NAME=toiturelv-cortex
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Build:**
- No build configuration files
- Scripts executed directly: `python3 train_cortex_v4.py`

**Model Configuration:**
- `cortex-data/cortex_config_v4.json` - Model features, hyperparameters, performance metrics
- `cortex-data/cortex_config_v3.json` - Previous version config with category mapping

## Platform Requirements

**Development:**
- Python 3.8+ with pip
- ~100GB+ disk space (large CSV files)
- macOS confirmed (hardcoded paths use `/Users/`)

**Production (Planned):**
- Railway - FastAPI backend deployment
- Vercel - Next.js frontend deployment
- Pinecone - Vector database (free tier: 8K vectors)
- OpenRouter - LLM API access

## Data Files

**Source Data (CSV):**
- `cortex-data/master_quotes_valid.csv` - Primary training data
- `cortex-data/master_quotes.csv` - Full quote dataset
- `cortex-data/master_quotes_labor_reliable.csv` - Labor-verified subset
- `cortex-data/Quote Lines_clean.csv` - Quote line items
- `cortex-data/Quote Materials_clean.csv` - Material records
- `cortex-data/Quote Sub Lines_clean.csv` - Subcontractor data
- `cortex-data/Quote Time Lines_clean.csv` - Labor time records
- `cortex-data/Quotes Data Export_clean.csv` - Raw quote export

**Model Artifacts (PKL):**
- `cortex-data/cortex_v4_bardeaux.pkl` - Tuned Bardeaux model
- `cortex-data/cortex_v4_gb.pkl` - GradientBoosting model
- `cortex-data/cortex_v4_rf.pkl` - RandomForest model
- `cortex-data/category_encoder_v4.pkl` - Category LabelEncoder

**CBR System (Planned):**
- `cortex-data/cbr_cases.json` - 8,293 structured cases
- `cortex-data/cbr_cases.jsonl` - Cases in JSONL format
- `cortex-data/cbr_embeddings.json` - 8,132 embeddings (JSON)
- `cortex-data/cbr_embeddings.npz` - Embeddings (NumPy compressed)

## Scripts Inventory

| Script | Purpose |
|--------|---------|
| `cortex-data/train_cortex_v4.py` | Latest model training with hyperparameter tuning |
| `cortex-data/predict_final.py` | CLI prediction interface |
| `cortex-data/master_data_pipeline_v4_fixed.py` | Data cleaning and feature extraction |
| `cortex-data/comprehensive_analysis.py` | Business analytics and visualization |
| `cortex-data/deep_insights_analysis.py` | Customer and profitability analysis |

## Current State vs Planned

| Component | Current | Planned |
|-----------|---------|---------|
| Data Pipeline | Complete | - |
| ML Models | Trained (v4) | - |
| CBR Embeddings | Generated locally | Upload to Pinecone |
| FastAPI Backend | Not started | Build `/estimate` endpoint |
| Next.js Frontend | Not started | Build form UI |
| Deployment | Local only | Railway + Vercel |

---

*Stack analysis: 2026-01-18*
