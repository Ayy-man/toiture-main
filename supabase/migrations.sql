-- ============================================================================
-- TOITURES LV CORTEX — SUPABASE MIGRATIONS
-- ============================================================================
-- Run this ENTIRE file in Supabase Dashboard → SQL Editor
-- All statements are idempotent (safe to re-run)
-- Order matters: run top to bottom
-- ============================================================================


-- ============================================================================
-- 1. EXTENSIONS
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS pg_trgm;


-- ============================================================================
-- 2. ESTIMATES TABLE ALTERATIONS (Phase 19: Data Quality)
-- ============================================================================

-- Add data quality flag column for marking unreliable records
ALTER TABLE estimates ADD COLUMN IF NOT EXISTS data_quality_flag TEXT NULL;

-- Add estimator tracking column for compliance monitoring
ALTER TABLE estimates ADD COLUMN IF NOT EXISTS created_by TEXT NULL;

-- Add submission tracking column (Phase 23)
ALTER TABLE estimates ADD COLUMN IF NOT EXISTS submission_created boolean DEFAULT false;

-- Flag 2022 labor data as unreliable (1,512 records)
UPDATE estimates
SET data_quality_flag = 'labor_unreliable_2022'
WHERE EXTRACT(YEAR FROM created_at) = 2022
  AND data_quality_flag IS NULL;

-- Indexes for compliance queries
CREATE INDEX IF NOT EXISTS idx_estimates_created_by ON estimates(created_by);
CREATE INDEX IF NOT EXISTS idx_estimates_quality_flag ON estimates(data_quality_flag);


-- ============================================================================
-- 3. MATERIALS TABLE (Phase 20: Materials Database)
-- ============================================================================

CREATE TABLE IF NOT EXISTS materials (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(100),
    name TEXT NOT NULL,
    cost DECIMAL(10,2),
    sell_price DECIMAL(10,2),
    unit VARCHAR(50) NOT NULL,
    category VARCHAR(100),
    supplier VARCHAR(200),
    note TEXT,
    area_sqft DECIMAL(10,2) DEFAULT 0,
    length_ft DECIMAL(10,2) DEFAULT 0,
    width_ft DECIMAL(10,2) DEFAULT 0,
    thickness_ft DECIMAL(10,2) DEFAULT 0,
    item_type VARCHAR(20) DEFAULT 'material',
    ml_material_id INTEGER,
    review_status VARCHAR(20) DEFAULT 'approved',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_materials_category ON materials(category);
CREATE INDEX IF NOT EXISTS idx_materials_name_trgm ON materials USING gin(name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_materials_code ON materials(code) WHERE code IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_materials_review ON materials(review_status);
CREATE INDEX IF NOT EXISTS idx_materials_item_type ON materials(item_type);

COMMENT ON TABLE materials IS 'Laurent''s roofing materials inventory imported from LV Material List.csv';
COMMENT ON COLUMN materials.review_status IS 'approved = clean data, flagged = incomplete/labor, duplicate = near-duplicate detected';
COMMENT ON COLUMN materials.item_type IS 'material = physical item, labor = service/labor item';
COMMENT ON COLUMN materials.ml_material_id IS 'Links to ML model material IDs for future integration';


-- ============================================================================
-- 4. SUBMISSIONS TABLE (Phase 23: Submission Workflow)
-- ============================================================================

CREATE TABLE IF NOT EXISTS submissions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at timestamptz DEFAULT now() NOT NULL,
  updated_at timestamptz DEFAULT now() NOT NULL,

  -- Relationships
  estimate_id uuid,
  parent_submission_id uuid REFERENCES submissions(id) ON DELETE CASCADE,

  -- User tracking
  created_by text,
  approved_by text,

  -- Status workflow
  status text NOT NULL DEFAULT 'draft',
  finalized_at timestamptz,
  approved_at timestamptz,

  -- Client details
  client_name text,
  category text NOT NULL,
  sqft numeric(10,2),

  -- Upsell tracking
  upsell_type text,

  -- Pricing data
  pricing_tiers jsonb NOT NULL DEFAULT '[]'::jsonb,
  selected_tier text DEFAULT 'Standard',

  -- Line items (editable materials and labor)
  line_items jsonb NOT NULL DEFAULT '[]'::jsonb,

  -- Notes and audit trail
  notes jsonb DEFAULT '[]'::jsonb,
  audit_log jsonb DEFAULT '[]'::jsonb,

  -- Calculated totals
  total_materials_cost numeric(10,2) NOT NULL DEFAULT 0,
  total_labor_cost numeric(10,2) NOT NULL DEFAULT 0,
  total_price numeric(10,2) NOT NULL DEFAULT 0,

  -- Constraints
  CONSTRAINT valid_status CHECK (status IN ('draft', 'pending_approval', 'approved', 'rejected')),
  CONSTRAINT valid_tier CHECK (selected_tier IN ('Basic', 'Standard', 'Premium'))
);

CREATE INDEX IF NOT EXISTS idx_submissions_status ON submissions(status);
CREATE INDEX IF NOT EXISTS idx_submissions_created_at ON submissions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_submissions_parent_id ON submissions(parent_submission_id) WHERE parent_submission_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_submissions_estimate_id ON submissions(estimate_id) WHERE estimate_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_submissions_notes ON submissions USING GIN(notes);
CREATE INDEX IF NOT EXISTS idx_submissions_audit_log ON submissions USING GIN(audit_log);

-- Updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_submissions_updated_at ON submissions;
CREATE TRIGGER update_submissions_updated_at
  BEFORE UPDATE ON submissions
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();


-- ============================================================================
-- 5. SUBMISSIONS SEND COLUMNS (Phase 24: Export & Send)
-- ============================================================================

ALTER TABLE submissions ADD COLUMN IF NOT EXISTS send_status text DEFAULT 'draft';
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS scheduled_send_at timestamptz;
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS sent_at timestamptz;
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS recipient_email text;
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS email_subject text;
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS email_body text;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'valid_send_status'
  ) THEN
    ALTER TABLE submissions ADD CONSTRAINT valid_send_status
      CHECK (send_status IN ('draft', 'scheduled', 'sent', 'failed'));
  END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_submissions_send_status ON submissions(send_status);
CREATE INDEX IF NOT EXISTS idx_submissions_scheduled_send ON submissions(scheduled_send_at)
  WHERE send_status = 'scheduled';

COMMENT ON COLUMN submissions.send_status IS 'Send status: draft, scheduled, sent, failed';
COMMENT ON COLUMN submissions.scheduled_send_at IS 'Timestamp for scheduled send (null if not scheduled)';
COMMENT ON COLUMN submissions.sent_at IS 'Timestamp when email was successfully sent';
COMMENT ON COLUMN submissions.recipient_email IS 'Client email address for quote delivery';
COMMENT ON COLUMN submissions.email_subject IS 'Email subject line (cached from send request)';
COMMENT ON COLUMN submissions.email_body IS 'Email body HTML (cached from send request)';


-- ============================================================================
-- DONE — After running this file, execute the materials import:
--   cd backend && python -m app.scripts.import_materials
-- ============================================================================
