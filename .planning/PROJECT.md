# TOITURELV Cortex

## What This Is

A web application for TOITURELV's team to test and validate their roofing price estimation ML model. Users input job details, get AI-powered estimates with reasoning from similar historical cases, and provide feedback to improve the model over time. Laurent reviews estimates and enters his actual prices, building a dataset for continuous model improvement.

## Core Value

**Accurate price estimates with explainable reasoning** — the team can see why the AI suggests a price (similar past jobs) and track how accurate it's becoming.

## Requirements

### Validated

- ✓ Data pipeline transforms C-Cube exports into ML-ready datasets — existing
- ✓ ML models trained (GradientBoosting, v4) with ~59% R², 56% within ±20% — existing
- ✓ CBR embeddings generated (8,132 cases, 384-dim) — existing
- ✓ CLI prediction interface works — existing

### Active

- [ ] FastAPI backend serves ML model predictions
- [ ] Pinecone stores and queries CBR embeddings
- [ ] OpenRouter LLM adds reasoning to estimates
- [ ] Next.js admin app with estimate form (6 inputs)
- [ ] Review queue for Laurent to enter actual prices
- [ ] Analytics dashboard (accuracy, confidence trends, material mix)
- [ ] Supabase stores feedback for batch review
- [ ] Simple password authentication

### Out of Scope

- Auto-updating model from feedback — future milestone, design for it but don't build
- Client-facing interface — internal tool only for now
- Mobile app — web responsive is sufficient
- Real-time C-Cube integration — manual data export workflow continues

## Context

**Business:** TOITURELV is a Quebec roofing company. They have 10K+ historical quotes in their C-Cube system. The ML model predicts job prices based on sqft, category (Bardeaux/Élastomère/Other/Service Call), and complexity factors.

**Technical:**
- Trained models exist as .pkl files
- 8,132 CBR case embeddings ready for Pinecone upload
- No backend/frontend code exists yet — greenfield for web layer

**Users:**
- TOITURELV team enters job details to get estimates
- Laurent (owner/estimator) reviews all estimates and enters final prices
- Feedback accumulates for periodic model retraining

## Constraints

- **Deployment**: Railway (FastAPI) + Vercel (Next.js) + Pinecone + Supabase
- **LLM**: OpenRouter with configurable model (start with Mistral)
- **Auth**: Simple shared password for v1
- **Data**: Use existing trained models and embeddings, don't retrain

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Supabase over Railway Postgres | Built-in table UI for reviewing feedback | — Pending |
| Store feedback for batch review | Simpler than auto-update, gives control | — Pending |
| All 6 model inputs in form | Full control over predictions | — Pending |
| OpenRouter for LLM | Easy to swap models | — Pending |

---
*Last updated: 2026-01-18 after initialization*
