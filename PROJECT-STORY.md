# Toitures LV Cortex — Project Timeline

## Week 1: Dec 9-15 — Data Extraction

Laurent Vergniol's roofing company runs on C-Cube, a Quebec construction management tool. On December 14, six raw CSV exports landed — 155 MB of everything Toitures LV had ever quoted since 2020. Quote lines, materials, labor, subcontractors, company records. The data was in C-Cube's proprietary block-transposed format — not standard CSV rows, but grouped blocks that needed to be detected and unpivoted before you could even read them.

## Week 2-3: Dec 16-28 — Understanding the Problem

Quiet period. The data sat there while the scope of the project was being figured out. What does Laurent actually need? What can this data tell us? What's the product?

## Week 4: Dec 29 — Data Cleanup & Financial Intelligence

The real work started here. A `discover.py` script was written to auto-detect C-Cube's transposed block structure and parse it into clean CSVs. Six raw files became six `_clean.csv` files by late afternoon.

Then the analysis pipeline began — three versions of `master_data_pipeline` in a few hours, building up to a proper aggregation system. A 105-field data dictionary was written. Deep analysis scripts produced 10 chart sets covering every angle of the business:

- **8,293 valid quotes** across 2020-2025
- **$118.9M total revenue**, 27.1% margin
- **41.2% YoY growth** (2024 to 2025)
- Cost split: 46% materials, 50% labor
- 170 VIP clients, 1,487 repeat customers
- 323% seasonal revenue swing (peak vs trough)
- 2022 labor data flagged as unreliable (median 1.3 hrs vs normal 20-30)

An executive summary and deep insights report were produced — the kind of deliverables you'd give a business owner to say "here's what your data actually says."

## Week 5: Jan 1-4 — Holiday / Planning

New Year's break. The financial report was shared with Laurent and Amin during this window. The conversation shifted from "what does the data say" to "can we build a system that predicts quotes."

## Week 6: Jan 5-6 — ML Model Training & Data Recovery

The pipeline hit v4 — now handling French number formats (`1 000,00`), extracting square footage from quote descriptions, and filtering out bad records. The final `master_quotes.csv` was 48.8 MB of consolidated, clean data.

Then four generations of the Cortex pricing model were trained in one session:

- **v1**: Basic random forest — baseline
- **v2**: Separate labor/material models — better decomposition
- **v3**: Category-specific models (Bardeaux, Elastomere, etc.) — domain awareness
- **v4**: Ensemble (RF + gradient boosting + category-specific) — R²=0.59, MAE=$2,832

A square footage recovery effort found that only 33% of quotes had sqft data — a major gap. About 2,000 values were recovered from quote descriptions using regex extraction.

CBR (case-based reasoning) embeddings were generated — 8,132 quote cases vectorized for similarity search, preparing for the Pinecone integration.

## Week 7: Jan 7-12 — Architecture & Design

The architecture decisions were made. FastAPI + Next.js + Supabase + Pinecone + OpenRouter. The system would combine ML predictions (trained models), CBR (similar past quotes via vector search), and LLM reasoning (explain the estimate) into a hybrid quoting engine.

## Week 8: Jan 13-17 — Proposal & Spec Writing

The project proposal and the Data Intelligence Report were written. These were formal deliverables — the intelligence report packaged all the December analysis into a client-facing document. The proposal laid out what Cortex would be and how it would work.

## Week 9: Jan 18-19 — Backend & Frontend Foundation

With the proposal approved, development began. The backend came first — FastAPI with the trained ML models, Pinecone CBR integration, LLM reasoning via OpenRouter. Then the frontend — Next.js with shadcn/ui, estimate form, result display, authentication, feedback system, analytics dashboard, and deployment configs for Railway and Vercel. Material ID prediction models were also trained, adding the ability to predict which materials a job would need.

The admin dashboard followed — sidebar navigation, five tabs (Apercu, Historique, Clients, Estimateur with sub-views), KPI cards, charts, customer search. The entire application skeleton was standing.

## Week 10: Jan 20-26 — Infrastructure & Testing

The system was deployed to Railway (backend) and Vercel (frontend). Memory optimization work — lazy-loading ML models to fit Railway's constraints, smaller embedding models, OOM fixes. Streaming estimates were added for better UX. This was the "make it actually run in the cloud" week.

## Week 11: Jan 27 - Feb 1 — Hybrid Quoting & Polish

The core intelligence engine was built — hybrid quote generation combining ML + CBR + LLM with confidence scoring. The frontend got the full quote experience: invoice-style display, PDF export, complexity presets. A comprehensive UI overhaul brought shadcn v4 with the Lyra theme. The FR/EN language toggle was implemented across every component. Material names were finalized (150+ definitions).

Production-readiness fixes: CORS, Next.js security patch, lockfile regeneration, sidebar styling, duplicate i18n keys cleaned up.

## Week 12: Feb 2-4 — Pre-Launch QA

Final testing before going live. The system was shown to Steven (the estimator) and Laurent. Last-minute adjustments and environment configuration.

## Week 13: Feb 5 — Launch Day

Cortex went live. Steven started using it for real quotes. The first hours brought the classic launch-day fixes — CORS config, missing UI components, type errors that only surface with real data, embedding model timeout under production load. A feedback panel was added so Steven could rate estimates and flag issues. Performance monitoring went in to track what was slow. The formal system spec was written to document what was now deployed.

## Week 14: Feb 6-8 — User Feedback Collection

Steven and Laurent used the system for a full work week. Feedback was collected on what was missing, what was confusing, what was wrong. The dashboard labels said "revenue" when they meant "quote value." The complexity system was too rigid. The materials database wasn't searchable. There were no submission workflows — you could generate a quote but couldn't track it through approval and delivery.

## Week 15: Feb 9-10 — The Final Sprint

Everything learned from the first week of real usage was built in a concentrated push:

- **Phase 19**: Fixed dashboard labels, added data quality flags, compliance monitoring, estimator dropdown
- **Phase 20**: Materials database — imported 1,152 materials from LV's material list into Supabase with fuzzy search, built a searchable MaterialSelector component
- **Phase 21**: Rebuilt the complexity system from scratch — 6 tiers (0-100) with 8 weighted factors and a visual checklist
- **Phase 22**: Added 7 new estimation input fields (equipment type, access, stories, roof condition, etc.) with RadioGroup selectors
- **Phase 23**: Full submission workflow — draft/review/approved/sent/accepted/rejected pipeline, drag-and-drop editing, upsell suggestions, notes
- **Phase 24**: DOCX export for formal quotes, red flag system (5 categories of pricing anomalies), email service for sending quotes directly
- **Phase 25**: Dark mode, i18n cleanup (all hardcoded strings moved to translation keys), Recharts dark mode compatibility

Final polish: GST/QST tax lines on quotes, signature section, collapsible accordion form layout, compact tier selector cards. All SQL consolidated into a single idempotent migration file.

## Where It Stands Now (Feb 10, 2026)

Live in production. 25 phases complete. An AI-powered roofing estimation system that takes job parameters, predicts pricing using ML models trained on 8,293 historical quotes, finds similar past jobs via vector search, generates LLM-powered reasoning, suggests materials, flags pricing anomalies, exports DOCX quotes, and emails them to clients — all in French and English, with dark mode, running on Vercel + Railway + Supabase.
