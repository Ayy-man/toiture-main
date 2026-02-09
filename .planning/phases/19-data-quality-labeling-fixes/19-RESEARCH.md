# Phase 19: Data Quality & Labeling Fixes - Research

**Created:** 2026-02-09
**Source:** Laurent feedback (Jan 21, 2026) + Sprint requirements (Feb 9, 2026)
**Deadline:** Feb 11, 2026 (HARD)

## Overview

This phase consolidates critical data quality and labeling fixes originally planned in Phase 12. Laurent identified three major issues:
1. Misleading "Revenue" labels (these are quotes, not invoiced revenue)
2. Corrupted 2022 labor cost data (1,512 records with unreliable labor quotes)
3. Missing square footage data causing model unreliability

## Requirements Breakdown

### DQ-01: Revenue Label Replacement
**Goal:** Change all instances of "Revenue"/"Revenu" to "Total Quote Value"/"Valeur totale des soumissions"

**Current State:**
- **Frontend i18n files:**
  - `/frontend/src/lib/i18n/en.ts` line 117: `revenuTotal: "Total Revenue"`
  - `/frontend/src/lib/i18n/fr.ts` line 117: `revenuTotal: "Revenu total"`
- **Component usage:**
  - `/frontend/src/components/apercu/metrics-cards.tsx` line 49: uses `t.apercu.revenuTotal`
  - `/frontend/src/app/(admin)/apercu/page.tsx` lines 31, 44: hardcoded "Revenu par annee" and "Revenu par categorie"
  - `/frontend/src/components/apercu/revenue-chart.tsx`: component name itself uses "Revenue"
- **Backend schemas:**
  - `/backend/app/schemas/dashboard.py`: Field names use `revenue` (lines 5, 10, 17, 22, 27, 32, 37)
  - `/backend/app/routers/dashboard.py`: Variable names use `revenue` and `total_revenue` throughout

**Impact Analysis:**
- 10+ files need changes (2 i18n, 5 frontend components, 2 backend schemas)
- Field names in TypeScript types match backend (total_revenue, revenue_by_year, revenue_by_category)
- Chart components reference "revenue" dataKey in Recharts

**Technical Decisions:**
1. **Keep backend field names as `revenue`** - changing database field names is risky and unnecessary
2. **Change all user-facing labels** to "Total Quote Value" / "Valeur totale des soumissions"
3. **Update TypeScript types** to use `quote_value` for clarity (with backend mapping)
4. **Rename component files** from "revenue-chart.tsx" to "quote-value-chart.tsx" for clarity

### DQ-02: Financial Chart Disclaimers
**Goal:** Add disclaimer to all financial charts stating these are quoted amounts, not invoiced revenue

**Current Charts:**
- `/frontend/src/app/(admin)/apercu/page.tsx`: 4 charts
  - Revenue by Year (line 29-39)
  - Revenue by Category (line 42-52)
  - Monthly Trend (line 55-65)
  - Top Clients (line 68-78)

**Implementation Options:**
1. Add disclaimer to each Card component (CardFooter or CardDescription)
2. Add disclaimer as page-level notice above all charts
3. Add tooltip on chart title with info icon

**Recommended:** Page-level disclaimer banner below KPI cards, above charts grid
- **EN:** "Note: All amounts shown represent quoted values, not invoiced revenue."
- **FR:** "Note : Tous les montants affichés représentent des valeurs de soumissions, et non des revenus facturés."

### DQ-03: 2022 Data Quality Flag
**Goal:** Flag 1,512 corrupted 2022 labor quotes and exclude from training

**Problem Context:**
- Laurent identified that 2022 labor cost data is unreliable
- Affects model training for labor predictions
- 1,512 records from year 2022 need to be flagged

**Database Changes Needed:**
- Add `data_quality_flag` column to `estimates` table in Supabase
  - Type: `text` or `jsonb` (to support multiple flags)
  - Nullable: yes (only flagged records have values)
  - Values: "labor_unreliable_2022", etc.
- Alternative: Add `quality_flags` JSONB array column for future extensibility

**Backend Changes:**
- Add migration or manual SQL to add column
- Bulk update query: `UPDATE estimates SET data_quality_flag = 'labor_unreliable_2022' WHERE EXTRACT(YEAR FROM created_at) = 2022`
- Modify training data queries to exclude flagged records

**Current Training Location:**
- Training happens offline in `/cortex-data/` directory (pre-application phase)
- No real-time training in production backend
- Models are pre-trained `.pkl` files loaded at runtime

**Action Required:**
1. Add column to Supabase estimates table
2. Flag 2022 records with SQL UPDATE
3. Document in training pipeline that 2022 labor data should be excluded
4. Future: Update `/cortex-data/train_cortex_v4.py` to filter on quality flags

### DQ-04: Square Footage Required Field
**Goal:** Make sqft mandatory on estimate forms (except Service Call category)

**Current Implementation:**
- `/frontend/src/lib/schemas.ts` line 29-32:
  ```typescript
  sqft: z.number()
    .positive("Square footage must be positive")
    .max(100000, "Square footage cannot exceed 100,000")
  ```
- Already validates positive and max, but doesn't handle Service Call exception

**Form Locations:**
1. **Prix tab:** `/frontend/src/components/estimate-form.tsx`
   - Uses `estimateFormSchema` from schemas.ts
   - Default value: 1500 (line 55)
2. **Soumission Complète tab:** `/frontend/src/components/estimateur/full-quote-form.tsx`
   - Uses `hybridQuoteFormSchema` from schemas/hybrid-quote.ts
   - Default value: 1500 (line 58)

**Implementation Strategy:**
1. Add conditional validation: if category != "Service Call", sqft is required
2. For Service Call: allow sqft to be optional or 0
3. Update form UI to show "(optional)" or disable sqft field when Service Call selected
4. Backend schema `/backend/app/schemas/estimate.py` already requires sqft > 0 - needs same conditional

**Backend Changes:**
- Modify `EstimateRequest` in `/backend/app/schemas/estimate.py`
- Add Pydantic validator that allows sqft=0 or None when category="Service Call"

### DQ-05: Square Footage Compliance Dashboard
**Goal:** Track sqft data entry compliance by estimator with alerts

**Requirements:**
1. Compliance dashboard showing sqft entry rate per estimator
2. Alert if compliance drops below 80%
3. Track which estimates are missing sqft data

**Current State:**
- No estimator/user tracking in current schema
- `estimates` table doesn't have `estimator_id` or `created_by` field
- No admin compliance dashboard exists

**Implementation Challenges:**
1. **No user system:** Current app uses shared password (AUTH-01), no individual logins
2. **No estimator field:** Database doesn't track who created each estimate
3. **Compliance tracking requires user identity**

**Recommended Approach:**
1. **Short-term (Sprint):**
   - Add `created_by` text field to estimates table (free-text name entry)
   - Add dropdown on estimate form: "Estimator: [Steven / Laurent / Other]"
   - Build compliance report page in admin dashboard
   - Show sqft completion rate overall and per estimator (last 30 days)
   - Add alert banner if completion rate < 80%

2. **Long-term (Future Phase):**
   - Implement proper user authentication (per-user accounts)
   - Track estimator_id as foreign key
   - Real-time compliance monitoring

**Dashboard Components Needed:**
- New admin tab: "Compliance" or add to Aperçu page
- Metric card: "Sqft Completion Rate" with color coding (green >80%, red <80%)
- Table: Estimator, Total Estimates, Sqft Completed, Completion Rate
- Filter: Last 7 days / 30 days / All time

## Technical Considerations

### Database Schema Changes

**Supabase Migration Needed:**
```sql
-- Add data quality flag column
ALTER TABLE estimates
ADD COLUMN data_quality_flag TEXT NULL;

-- Add estimator tracking
ALTER TABLE estimates
ADD COLUMN created_by TEXT NULL;

-- Flag 2022 labor data
UPDATE estimates
SET data_quality_flag = 'labor_unreliable_2022'
WHERE EXTRACT(YEAR FROM created_at) = 2022;

-- Create index for compliance queries
CREATE INDEX idx_estimates_created_by ON estimates(created_by);
CREATE INDEX idx_estimates_quality_flag ON estimates(data_quality_flag);
```

### Frontend Architecture

**Current Admin Dashboard Structure:**
- Layout: `/frontend/src/app/(admin)/layout.tsx`
- Sidebar: `/frontend/src/components/admin/app-sidebar.tsx`
- 4 tabs: Estimateur, Historique, Aperçu, Clients (+ Retours added in Phase 18)

**Tab Structure for Compliance:**
- Option 1: Add "Compliance" as 6th tab
- Option 2: Add compliance section to Aperçu page (below charts)
- **Recommended:** Option 2 - keep related metrics together

### Backend API Endpoints

**New Endpoints Needed:**
```
GET /dashboard/compliance
  Query params: start_date?, end_date?, estimator?
  Response: {
    overall_completion_rate: float,
    estimators: [
      {
        name: string,
        total_estimates: int,
        sqft_completed: int,
        completion_rate: float
      }
    ],
    alert: bool,  // true if < 80%
    time_period: string
  }
```

**Existing Endpoints to Modify:**
- `POST /estimate` - add created_by field
- `POST /estimate/hybrid` - add created_by field
- Both in `/backend/app/routers/estimate.py`

### i18n Strings Needed

**English (`/frontend/src/lib/i18n/en.ts`):**
```typescript
apercu: {
  // Change:
  revenuTotal: "Total Quote Value",
  // Add:
  disclaimer: "Note: All amounts shown represent quoted values, not invoiced revenue.",
  sqftCompliance: "Sqft Data Entry",
  completionRate: "Completion Rate",
  estimatorName: "Estimator",
  totalEstimates: "Total Estimates",
  complianceAlert: "Warning: Sqft completion rate is below 80%",
}
```

**French (`/frontend/src/lib/i18n/fr.ts`):**
```typescript
apercu: {
  // Change:
  revenuTotal: "Valeur totale des soumissions",
  // Add:
  disclaimer: "Note : Tous les montants affichés représentent des valeurs de soumissions, et non des revenus facturés.",
  sqftCompliance: "Saisie des données de superficie",
  completionRate: "Taux de complétion",
  estimatorName: "Estimateur",
  totalEstimates: "Total estimations",
  complianceAlert: "Attention : Le taux de complétion de superficie est inférieur à 80%",
}
```

## Dependencies

**Before Starting:**
- Supabase access for schema changes (add columns)
- Decide on estimator tracking approach (text field vs future user system)

**During Implementation:**
- Frontend changes can proceed in parallel with backend
- Database migration must complete before backend API changes

**Blocking Issues:**
- None - all changes are additive (no breaking changes)
- Can deploy incrementally (labels first, then compliance dashboard)

## Risks & Mitigations

**Risk 1:** Changing field names breaks existing code
- **Mitigation:** Keep backend field names, only change display labels

**Risk 2:** 2022 data flag affects live estimates
- **Mitigation:** Flag only applies to training data, not production estimates

**Risk 3:** Compliance tracking without user system is hacky
- **Mitigation:** Use free-text estimator field as interim solution, plan proper auth for Phase 23+

**Risk 4:** Sqft validation breaks Service Call workflow
- **Mitigation:** Conditional validation based on category

## Success Metrics

**After Implementation:**
1. Zero instances of "Revenue"/"Revenu" visible to users
2. Disclaimer visible on all financial charts
3. 1,512 records flagged in database with `data_quality_flag = 'labor_unreliable_2022'`
4. Sqft field shows "(optional)" for Service Call category
5. Compliance dashboard shows sqft completion rate
6. Alert appears when completion rate < 80%
7. Estimator dropdown appears on estimate forms

## Files to Modify

**Frontend (10 files):**
- `/frontend/src/lib/i18n/en.ts` - update revenue labels
- `/frontend/src/lib/i18n/fr.ts` - update revenue labels
- `/frontend/src/app/(admin)/apercu/page.tsx` - add disclaimer, update chart titles
- `/frontend/src/components/apercu/metrics-cards.tsx` - update card title
- `/frontend/src/components/apercu/revenue-chart.tsx` - rename & update
- `/frontend/src/components/apercu/category-chart.tsx` - update
- `/frontend/src/components/apercu/trend-chart.tsx` - update
- `/frontend/src/lib/schemas.ts` - add conditional sqft validation
- `/frontend/src/lib/schemas/hybrid-quote.ts` - add conditional sqft validation
- `/frontend/src/components/estimate-form.tsx` - add estimator dropdown
- `/frontend/src/components/estimateur/full-quote-form.tsx` - add estimator dropdown

**Backend (4 files):**
- `/backend/app/schemas/estimate.py` - add conditional sqft validation
- `/backend/app/schemas/hybrid_quote.py` - add conditional sqft validation
- `/backend/app/schemas/dashboard.py` - add ComplianceReport schema
- `/backend/app/routers/dashboard.py` - add /dashboard/compliance endpoint

**Database:**
- Supabase estimates table - add columns (SQL migration)

**Documentation:**
- Update training pipeline docs to exclude 2022 data

## Plan Structure

Based on the complexity, break this into 3-5 focused plans:

| Plan | Title | Priority | Estimated Time |
|------|-------|----------|----------------|
| 19-01 | Revenue Label Replacement | HIGH | 2-3 hours |
| 19-02 | Financial Chart Disclaimers | MEDIUM | 1 hour |
| 19-03 | 2022 Data Quality Flag | HIGH | 1-2 hours |
| 19-04 | Sqft Required Field Logic | HIGH | 2-3 hours |
| 19-05 | Sqft Compliance Dashboard | MEDIUM | 3-4 hours |

**Total Estimated Time:** 9-13 hours
**Sprint Deadline:** Feb 11, 2026 (2 days)
**Feasibility:** Tight but achievable if focused

## Next Steps

1. Create 19-01-PLAN.md for revenue label replacement (start here - quick win)
2. Create 19-03-PLAN.md for 2022 data flagging (database work)
3. Create 19-04-PLAN.md for sqft validation (frontend + backend)
4. Create 19-02-PLAN.md for chart disclaimers (quick)
5. Create 19-05-PLAN.md for compliance dashboard (most complex, may be stretch goal)

---
*Research complete: 2026-02-09*
