# 17-06 Summary: Feedback System

**Status:** Complete (code ready, needs deployment + Supabase table)
**Completed:** 2026-02-05

## Problem

No way to collect user feedback on estimates. Users couldn't indicate if an estimate was accurate or not.

## Solution

Added 👍/👎 feedback buttons to all estimate results with optional actual price and reason fields.

## Implementation

### Backend

**`backend/app/schemas/feedback.py`:**
Added new schemas:
```python
class QuickFeedbackRequest(BaseModel):
    estimate_id: str
    input_params: dict
    predicted_price: float
    predicted_materials: Optional[list] = None
    feedback: Literal["positive", "negative"]
    actual_price: Optional[float] = None
    reason: Optional[str] = None

class QuickFeedbackResponse(BaseModel):
    success: bool
    message: str
```

**`backend/app/routers/feedback.py`:**
Added new endpoint:
```python
@router.post("/quick", response_model=QuickFeedbackResponse)
def submit_quick_feedback(request: QuickFeedbackRequest):
    # Inserts into cortex_feedback table
```

### Frontend

**New component: `frontend/src/components/estimateur/feedback-panel.tsx`**
- Two large buttons: "Précise" (👍) and "Imprécise" (👎)
- Expandable form after selection:
  - Positive: optional actual price input
  - Negative: required actual price + required reason
- Loading state during submission
- Success confirmation: "Merci pour votre retour!"

**Updated `frontend/src/components/estimateur/quote-result.tsx`:**
- Added FeedbackPanel after QuoteActions
- Generates UUID for estimate tracking
- Passes inputParams, predictedPrice, predictedMaterials

**Updated `frontend/src/components/estimateur/full-quote-form.tsx`:**
- Passes form values as inputParams to QuoteResult

**Updated `frontend/src/components/estimate-form.tsx`:**
- Added FeedbackPanel to Prix tab results
- Tracks estimateId and submittedParams state

## Files Modified

- `backend/app/schemas/feedback.py`
- `backend/app/routers/feedback.py`
- `frontend/src/components/estimateur/feedback-panel.tsx` (new)
- `frontend/src/components/estimateur/quote-result.tsx`
- `frontend/src/components/estimateur/full-quote-form.tsx`
- `frontend/src/components/estimate-form.tsx`

## Supabase Table Required

```sql
CREATE TABLE cortex_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    estimate_id TEXT NOT NULL,
    input_params JSONB NOT NULL,
    predicted_price NUMERIC NOT NULL,
    predicted_materials JSONB,
    feedback TEXT NOT NULL CHECK (feedback IN ('positive', 'negative')),
    actual_price NUMERIC,
    reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_cortex_feedback_feedback ON cortex_feedback(feedback);
CREATE INDEX idx_cortex_feedback_created_at ON cortex_feedback(created_at);
```

## Verification

1. Go to Prix tab, submit estimate
2. See 👍/👎 buttons below result
3. Click thumbs up, optionally enter price, submit
4. See "Merci pour votre retour!"
5. Check Supabase cortex_feedback table for new row
6. Repeat for Soumission Complète tab
