-- Phase 19: Data Quality & Labeling Fixes
-- Add data quality flag column for marking unreliable records
ALTER TABLE estimates ADD COLUMN IF NOT EXISTS data_quality_flag TEXT NULL;

-- Add estimator tracking column for compliance monitoring
ALTER TABLE estimates ADD COLUMN IF NOT EXISTS created_by TEXT NULL;

-- Flag 2022 labor data as unreliable (1,512 records)
UPDATE estimates
SET data_quality_flag = 'labor_unreliable_2022'
WHERE EXTRACT(YEAR FROM created_at) = 2022
  AND data_quality_flag IS NULL;

-- Create indexes for compliance queries
CREATE INDEX IF NOT EXISTS idx_estimates_created_by ON estimates(created_by);
CREATE INDEX IF NOT EXISTS idx_estimates_quality_flag ON estimates(data_quality_flag);
