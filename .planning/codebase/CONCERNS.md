# Codebase Concerns

**Analysis Date:** 2026-01-18

## Tech Debt

**Hardcoded File Paths:**
- Issue: All Python scripts use absolute paths like `/Users/aymanbaig/Desktop/cortex-data/`
- Files: `cortex-data/master_data_pipeline_v4_fixed.py`, `cortex-data/comprehensive_analysis.py`, `cortex-data/deep_insights_analysis.py`, `cortex-data/validate_clients.py`
- Impact: Code cannot run on any other machine, deployment impossible without refactor
- Fix approach: Use relative paths, environment variables, or config file for `DATA_PATH`

**Multiple Script Versions Without Cleanup:**
- Issue: Multiple versions of same scripts exist (v2, v3, v4) without clear indication of which is current
- Files: `cortex-data/train_cortex.py`, `cortex-data/train_cortex_v2.py`, `cortex-data/train_cortex_v3.py`, `cortex-data/train_cortex_v4.py`, `cortex-data/master_data_pipeline_v2.py`, `cortex-data/master_data_pipeline_v3.py`, `cortex-data/master_data_pipeline_v4.py`, `cortex-data/master_data_pipeline_v4_fixed.py`
- Impact: Unclear which script is production-ready, risk of running outdated code
- Fix approach: Archive old versions to `archive/` directory, keep only latest production script

**Duplicate Discovery Scripts:**
- Issue: Two discovery scripts with unclear differences
- Files: `cortex-data/discover.py`, `cortex-data/discover 2.py`
- Impact: Confusion about which to use, possible inconsistent data processing
- Fix approach: Consolidate into single script or remove duplicates

**Global Warnings Suppression:**
- Issue: All Python scripts use `warnings.filterwarnings('ignore')` globally
- Files: All `.py` files in `cortex-data/`
- Impact: Silently ignores potentially important deprecation/future warnings, hides data issues
- Fix approach: Use targeted warning suppression only where necessary, log warnings to file

**Model Version Mismatch:**
- Issue: `predict_final.py` loads v3 models while v4 models also exist
- Files: `cortex-data/predict_final.py` references `cortex_model_global.pkl`, `cortex_model_Bardeaux.pkl`, `cortex_config_v3.json`
- Impact: Unclear which model version is intended for production use
- Fix approach: Create single unified prediction interface, document which model version to use

**Bare Except Clauses:**
- Issue: Multiple `except:` without specifying exception type
- Files: `cortex-data/master_data_pipeline_v4_fixed.py` lines 38, 77; `cortex-data/discover.py` line 19
- Impact: Catches all exceptions including KeyboardInterrupt, hides actual errors
- Fix approach: Use specific exception types (ValueError, TypeError, etc.)

## Known Bugs

**2022 Labor Data Anomaly:**
- Symptoms: 2022 labor hours show median of ~1.3 hours vs normal 20-30 hours
- Files: `cortex-data/master_quotes_valid.csv`, `cortex-data/master_quotes_labor_reliable.csv`
- Trigger: Viewing labor statistics for 2022 data
- Workaround: Created separate `master_quotes_labor_reliable.csv` that excludes 2022 data; labor-dependent analyses should use this file

**Broken Quote Materials CSV:**
- Symptoms: Pipeline v4 explicitly skips `Quote Materials_clean.csv` due to data corruption
- Files: `cortex-data/Quote Materials_clean.csv`, `cortex-data/master_data_pipeline_v4_fixed.py`
- Trigger: Loading materials data for aggregation
- Workaround: Uses existing v3 master_quotes.csv for material aggregations instead of reprocessing

**Low Square Footage Coverage:**
- Symptoms: Only ~33% of quotes have sqft data despite text extraction attempts
- Files: `cortex-data/master_quotes.csv`, `cortex-data/master_data_pipeline_v4_fixed.py`
- Trigger: Running sqft-dependent analyses or ML models
- Workaround: Models use available data; confidence scoring accounts for missing sqft

## Security Considerations

**No Secrets Management:**
- Risk: Project specification mentions API keys (Pinecone, OpenRouter) with no .env file present
- Files: `Project docs/TOITURELV-CORTEX-SPEC.md` references `PINECONE_API_KEY`, `OPENROUTER_API_KEY`
- Current mitigation: No backend/frontend code exists yet; keys not in repository
- Recommendations: Create `.env.example` template, add `.env` to `.gitignore`, use environment variables in deployment

**Sensitive Client Data in CSV:**
- Risk: Raw quote data with client_id, building_id, project_id in plain CSV files
- Files: `cortex-data/master_quotes.csv`, `cortex-data/master_quotes_valid.csv`, all `_clean.csv` files
- Current mitigation: Files are local only, not in web-accessible location
- Recommendations: Encrypt sensitive data at rest, implement access controls, consider PII anonymization for development

**No Input Validation:**
- Risk: Scripts read CSV files without validating data types or sanitizing inputs
- Files: All pipeline and analysis scripts
- Current mitigation: Scripts are run locally by trusted users
- Recommendations: Add input validation for any user-facing or API-based data ingestion

## Performance Bottlenecks

**Inefficient Row-by-Row Operations:**
- Problem: Multiple uses of `df.apply()` with row-wise lambda functions
- Files: `cortex-data/master_data_pipeline_v4_fixed.py` lines 148-152, `cortex-data/train_cortex_v4.py` line 31
- Cause: `df.apply(axis=1)` iterates row-by-row, not vectorized
- Improvement path: Use vectorized pandas operations, numpy where possible

**Large In-Memory DataFrames:**
- Problem: Loading entire 50MB+ CSV files into memory
- Files: `cortex-data/comprehensive_analysis.py`, `cortex-data/deep_insights_analysis.py`
- Cause: No chunked reading or streaming
- Improvement path: Use `pd.read_csv(chunksize=...)` for very large files, or use parquet format

**Unoptimized Model Training:**
- Problem: GridSearchCV with all combinations runs sequentially by default
- Files: `cortex-data/train_cortex_v4.py` line 269
- Cause: `n_jobs=-1` is set but no multiprocessing consideration for data size
- Improvement path: Consider using `HalvingGridSearchCV` or `RandomizedSearchCV` for faster iteration

## Fragile Areas

**Text Extraction Regular Expressions:**
- Files: `cortex-data/master_data_pipeline_v4_fixed.py` lines 41-60
- Why fragile: Complex regex patterns for French number parsing and sqft extraction
- Safe modification: Add unit tests for each regex pattern with known inputs/outputs
- Test coverage: None - patterns are untested

**Job Category Classification:**
- Files: `cortex-data/train_cortex_v3.py`, `cortex-data/train_cortex_v4.py`
- Why fragile: Hard-coded category list `['Bardeaux', 'Elastomere', 'Other', 'Service Call']`
- Safe modification: Make category list data-driven from actual categories in dataset
- Test coverage: None

**Inflation Factor Constants:**
- Files: `cortex-data/train_cortex_v4.py` line 30, `cortex-data/train_cortex_v3.py` line 21, `cortex-data/cortex_config_v3.json`, `cortex-data/cortex_config_v4.json`
- Why fragile: Hardcoded inflation factors `{2020: 1.97, 2021: 1.52, ...}` duplicated across files
- Safe modification: Centralize inflation factors in single config file, import everywhere
- Test coverage: None

**ML Model Feature Lists:**
- Files: `cortex-data/train_cortex_v3.py` lines 40-41, `cortex-data/train_cortex_v4.py` lines 115-121, `cortex-data/predict_final.py` lines 28-32
- Why fragile: Feature lists duplicated and can drift between training and prediction scripts
- Safe modification: Load feature list from config file, validate at prediction time
- Test coverage: None

## Scaling Limits

**File-Based Storage:**
- Current capacity: Local CSV files up to ~50MB each
- Limit: No database; cannot handle concurrent writes, queries limited by file I/O
- Scaling path: Migrate to PostgreSQL or similar for quote data; use vector DB (Pinecone) for embeddings as specified

**Single-Machine Processing:**
- Current capacity: All scripts run on single local machine
- Limit: Cannot parallelize across machines, limited by local CPU/RAM
- Scaling path: Containerize with Docker, deploy to cloud with horizontal scaling

**Embedding Storage:**
- Current capacity: 8,132 embeddings in JSON format (~67MB)
- Limit: JSON format is inefficient for large embedding sets
- Scaling path: Pinecone upload (planned per spec), or use `.npz` format (already exists)

## Dependencies at Risk

**Matplotlib Style Deprecation:**
- Risk: Uses `plt.style.use('seaborn-v0_8-whitegrid')` which may not exist in all matplotlib versions
- Impact: Visualization scripts fail on older matplotlib
- Migration plan: Use version check or fallback to standard style

**Scikit-learn API Changes:**
- Risk: Uses sklearn directly without pinning version
- Impact: Model files may be incompatible across sklearn versions
- Migration plan: Pin sklearn version in requirements.txt, add version metadata to .pkl files

**No Requirements File:**
- Risk: No `requirements.txt` or `pyproject.toml` in `cortex-data/`
- Impact: Unknown dependency versions, potential compatibility issues
- Migration plan: Create requirements.txt with pinned versions: pandas, numpy, sklearn, matplotlib, joblib

## Missing Critical Features

**No Automated Testing:**
- Problem: Zero test files, no test framework configured
- Blocks: CI/CD, confident refactoring, regression detection
- Location: Should be in `cortex-data/tests/`

**No Data Validation Layer:**
- Problem: No schema validation for incoming CSV data
- Blocks: Data quality assurance, error detection at ingestion

**No Logging Framework:**
- Problem: Uses `print()` statements for all output
- Blocks: Production monitoring, debugging in deployed environment

**No API Layer (Backend Not Built):**
- Problem: FastAPI backend specified but not implemented
- Blocks: Web integration, external system access to predictions
- Reference: `Project docs/TOITURELV-CORTEX-SPEC.md` defines full API spec

**No Frontend (Not Built):**
- Problem: Next.js frontend specified but not implemented
- Blocks: User interface for estimates
- Reference: `Project docs/TOITURELV-CORTEX-SPEC.md` defines full frontend spec

## Test Coverage Gaps

**All Code is Untested:**
- What's not tested: Every Python file in `cortex-data/`
- Files: 15+ Python scripts with zero test coverage
- Risk: Any change could introduce regression without detection
- Priority: HIGH - especially for `master_data_pipeline_v4_fixed.py`, `train_cortex_v4.py`, `predict_final.py`

**Critical Untested Functions:**
- `parse_french_number()` in `cortex-data/master_data_pipeline_v4_fixed.py`
- `extract_sqft()` in `cortex-data/master_data_pipeline_v4_fixed.py`
- `extract_dimensions()` in `cortex-data/master_data_pipeline_v4_fixed.py`
- `predict()` in `cortex-data/predict_final.py`

**ML Model Accuracy Validation:**
- What's not tested: Model predictions against known good values
- Files: All model `.pkl` files
- Risk: Model degradation goes unnoticed
- Priority: HIGH

---

*Concerns audit: 2026-01-18*
