# Phase 13: Hybrid Quote Generation - Context

**Gathered:** 2026-02-01
**Status:** Ready for planning

<domain>
## Phase Boundary

Generate full roofing quotes by running CBR (similar job retrieval) and ML (material/labor prediction) in parallel, then using an LLM to merge and reconcile outputs into a complete quote.

**Output includes:**
- Work items with names (from Quote Lines)
- Material IDs with quantities (849 unique IDs)
- Labor hours
- Total price with confidence score
- Three-tier pricing (Basic/Standard/Premium)

**Data sources:**
- CBR: 8,293 historical quotes, retrieves 5 most similar
- ML: Trained on 7,433 samples

</domain>

<decisions>
## Implementation Decisions

### CBR Data Extraction & Scaling
- Pull **full line-item breakdown** from similar jobs (work items + materials + quantities + labor)
- Use **category-specific scaling factors** when adjusting quantities to new job size (only if data shows actual differences; otherwise simple sqft ratio)
- Weight similar jobs by **recency × similarity** — more recent jobs weighted higher, multiplied by Pinecone similarity score
- When sqft missing from input or similar jobs: **use median sqft for that job_category** from training data

### ML Model Architecture
- Use **separate specialized models** (material classifier, quantity predictors, labor regressor) — then LLM reconciles
- Material prediction: return **fixed top 20** most likely materials regardless of confidence threshold
- Quantity prediction: use **category-based formulas** learned from data (e.g., sqft-based ratios per category)
- Work items: **retrieve from CBR** (91% coverage) rather than ML prediction

### Complexity Factors (Laurent's 6-factor system)
- ML uses **both** aggregate score (0-56) for main prediction AND individual factors for adjustments
- Individual factors:
  1. Access difficulty (0-10)
  2. Roof pitch/slope (0-8)
  3. Number of penetrations (0-10)
  4. Material removal complexity (0-8)
  5. Safety concerns (0-10)
  6. Timeline constraints (0-10)
- LLM receives **all 6 factors with values** for explainable reasoning

### LLM Merger Logic
- Priority: **Accuracy over speed** — take time to reason carefully
- Material conflicts: **trust CBR for common items** (appears in 3+/5 similar jobs), otherwise trust ML
- Quantity conflicts: **average CBR and ML** quantities
- Technical implementation details (prompt structure, context formatting): researcher determines

### Confidence Scoring
- Use **combined formula**: CBR/ML agreement + data completeness + CBR similarity scores
- Flag for Laurent's review: **below 50% confidence**

### Edge Cases
- No similar CBR jobs found: **ML only + low confidence flag** for review
- Service calls (labor only): **detect and route to separate flow** — not through full materials pipeline
- 2022 corrupted labor data: already handled in Phase 12 (excluded from training)

### Claude's Discretion
- Exact prompt structure for LLM merger
- Specific scaling formulas per category (determined by data analysis)
- Weight formula for recency × similarity
- Category-based quantity formulas (derived from training data)
- Performance optimizations (parallelization details)

</decisions>

<specifics>
## Specific Ideas

- Architecture: CBR and ML run in **parallel**, then LLM merges
- Target response time: **<5 seconds** for full quote
- Latency breakdown: ~500ms CBR + ~200ms ML + ~2-3s LLM
- Three-tier pricing (Basic/Standard/Premium) output required — implementation TBD in Phase 12 first
- The 849 material IDs have only 12.9% with product names — rest are IDs only
- Quote Lines have 91.2% coverage for work item names

</specifics>

<deferred>
## Deferred Ideas

- Feedback loop for model improvement (which source was right, what humans changed)
- Periodic retraining schedule
- Per-line-item confidence display
- Output format for C-Cube import / PDF generation

</deferred>

---

*Phase: 13-hybrid-quote-generation*
*Context gathered: 2026-02-01*
