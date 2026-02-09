-- Submissions table for editable quote workflow with approval process
-- Run this migration in Supabase SQL Editor

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

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_submissions_status ON submissions(status);
CREATE INDEX IF NOT EXISTS idx_submissions_created_at ON submissions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_submissions_parent_id ON submissions(parent_submission_id) WHERE parent_submission_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_submissions_estimate_id ON submissions(estimate_id) WHERE estimate_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_submissions_notes ON submissions USING GIN(notes);
CREATE INDEX IF NOT EXISTS idx_submissions_audit_log ON submissions USING GIN(audit_log);

-- Updated_at trigger function (idempotent)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to submissions table
DROP TRIGGER IF EXISTS update_submissions_updated_at ON submissions;
CREATE TRIGGER update_submissions_updated_at
  BEFORE UPDATE ON submissions
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Add submission tracking to estimates table
ALTER TABLE estimates ADD COLUMN IF NOT EXISTS submission_created boolean DEFAULT false;

-- Completion message
DO $$
BEGIN
  RAISE NOTICE 'Submissions table created successfully with indexes and triggers';
END $$;
