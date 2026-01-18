# Codebase Structure

**Analysis Date:** 2026-01-18

## Directory Layout

```
Toiture-P1/
├── .planning/              # GSD planning documents
│   └── codebase/           # Codebase analysis documents
├── Project docs/           # Business requirements and specifications
│   ├── Proposal Toiture.txt
│   ├── TOITURELV Data Intelligence Report.txt
│   └── TOITURELV-CORTEX-SPEC.md
└── cortex-data/            # Data files, scripts, and models
    ├── *.csv               # Raw and processed data files
    ├── *.py                # Python scripts (pipelines, training, analysis)
    ├── *.pkl               # Trained ML models
    ├── *.json              # Configuration and CBR case files
    ├── *.npz               # Compressed embeddings
    └── *.png               # Generated analysis charts
```

## Directory Purposes

**`.planning/`:**
- Purpose: GSD workflow planning and documentation
- Contains: Codebase analysis markdown files
- Key files: `codebase/ARCHITECTURE.md`, `codebase/STRUCTURE.md`

**`Project docs/`:**
- Purpose: Business context, requirements, and technical specifications
- Contains: Project proposal, data intelligence report, Cortex MVP spec
- Key files:
  - `TOITURELV-CORTEX-SPEC.md`: Complete technical specification for planned web application
  - `TOITURELV Data Intelligence Report.txt`: Business analysis from quote data

**`cortex-data/`:**
- Purpose: All data processing, ML training, and analysis code
- Contains: Python scripts, CSV data, trained models, config files
- Generated: Yes (analysis outputs, trained models)
- Committed: Partially (scripts yes, large CSVs/models typically gitignored)

## Key File Locations

**Entry Points:**
- `cortex-data/discover.py`: Initial CSV parsing and cleaning
- `cortex-data/master_data_pipeline_v4.py`: Main data transformation pipeline
- `cortex-data/train_cortex_v4.py`: Current model training script
- `cortex-data/predict_final.py`: CLI prediction interface

**Configuration:**
- `cortex-data/cortex_config_v4.json`: Model hyperparameters, features, performance metrics
- `cortex-data/cortex_config_v3.json`: Previous version config (category mappings)

**Trained Models:**
- `cortex-data/cortex_v4_bardeaux.pkl`: Tuned GradientBoosting model for Bardeaux category
- `cortex-data/cortex_v4_gb.pkl`: GradientBoosting ensemble component
- `cortex-data/cortex_v4_rf.pkl`: RandomForest ensemble component
- `cortex-data/category_encoder_v4.pkl`: LabelEncoder for job categories

**Core Data:**
- `cortex-data/master_quotes_valid.csv`: Primary ML training dataset (10K+ records)
- `cortex-data/master_quotes_labor_reliable.csv`: Subset excluding 2022 anomalous data
- `cortex-data/cbr_cases.json`: 8,293 structured cases for CBR system
- `cortex-data/cbr_embeddings.npz`: 8,132 vector embeddings (384-dim)

**Raw Data (from C-Cube):**
- `cortex-data/Quotes Data Export_clean.csv`: Main quotes data
- `cortex-data/Quote Materials_clean.csv`: Materials line items
- `cortex-data/Quote Lines_clean.csv`: Job line items
- `cortex-data/Quote Time Lines_clean.csv`: Labor entries
- `cortex-data/Quote Sub Lines_clean.csv`: Subcontractor entries

**Analysis Scripts:**
- `cortex-data/comprehensive_analysis.py`: 40-chart business analysis generator
- `cortex-data/deep_analysis.py`: Detailed pattern analysis
- `cortex-data/deep_insights_analysis.py`: Advanced insights generation

**Analysis Outputs:**
- `cortex-data/comprehensive_analysis.png`: 16-chart business dashboard
- `cortex-data/cortex_v4_analysis.png`: Model performance visualization
- `cortex-data/executive_summary.txt`: Key business metrics summary

## Naming Conventions

**Files:**
- Python scripts: `snake_case.py` (e.g., `train_cortex_v4.py`)
- Data files: `descriptive_name.csv` (e.g., `master_quotes_valid.csv`)
- Models: `model_name_version.pkl` (e.g., `cortex_v4_bardeaux.pkl`)
- Config: `model_config_version.json` (e.g., `cortex_config_v4.json`)
- Versioning: `_v1`, `_v2`, `_v3`, `_v4` suffixes for iterations

**Directories:**
- Lowercase with hyphens: `cortex-data`, `Project docs`
- Planning directories: `.planning/codebase/`

**Variables (in Python):**
- DataFrames: descriptive names (`master`, `bardeaux`, `materials_agg`)
- Features: snake_case (`sqft_final`, `complexity_score`, `price_per_sqft`)
- Constants: UPPER_CASE (`DATA_PATH`, `OUTPUT_PATH`)

## Where to Add New Code

**New Data Pipeline Feature:**
- Implementation: Modify `cortex-data/master_data_pipeline_v4.py` or create `v5`
- Follow pattern: Add extraction function, add to master merge, add to export columns

**New ML Model Experiment:**
- Implementation: Create `cortex-data/train_cortex_v5.py`
- Pattern: Copy v4 structure, modify feature sets or model types
- Save outputs: `cortex_v5_*.pkl`, `cortex_config_v5.json`

**New Analysis/Visualization:**
- Implementation: Add to `cortex-data/comprehensive_analysis.py` or create new script
- Pattern: Load `master_quotes_valid.csv`, generate charts, save to `cortex-data/`

**Web Application (When Building):**
- Backend: Create `backend/` directory per spec in `TOITURELV-CORTEX-SPEC.md`
- Frontend: Create `frontend/` directory per spec
- Structure: Follow `cortex-project/` layout in spec file

**Utilities/Helpers:**
- Shared extraction functions: Add to relevant pipeline script
- No separate utils module exists currently

## Special Directories

**`cortex-data/` (data directory):**
- Purpose: All project data, models, scripts, outputs
- Generated: Partially (models, outputs are generated)
- Committed: Scripts should be committed; large data files (CSV > 100MB, PKL) should be gitignored
- Note: Contains 80+ files including large datasets (>50MB each)

**`.git/`:**
- Purpose: Git version control
- Generated: Yes
- Committed: N/A (is the repository itself)

## Planned Structure (From Spec, Not Yet Created)

The `TOITURELV-CORTEX-SPEC.md` defines target structure:

```
cortex-project/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── routers/estimate.py  # /estimate endpoint
│   │   └── services/
│   │       ├── pinecone_client.py
│   │       ├── cbr_engine.py
│   │       └── llm_service.py
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── page.tsx
│   │   ├── components/
│   │   └── api/estimate/route.ts
│   └── package.json
├── data/                        # Move from cortex-data/
│   ├── cbr_cases.json
│   └── cbr_embeddings.json
└── docs/
```

This structure does not yet exist and should be created during implementation phase.

---

*Structure analysis: 2026-01-18*
