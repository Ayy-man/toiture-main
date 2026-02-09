-- Phase 24: Add send tracking columns to submissions table
-- Run this migration in Supabase SQL editor after Phase 23's table creation

-- Add send tracking columns
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS send_status text DEFAULT 'draft';
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS scheduled_send_at timestamptz;
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS sent_at timestamptz;
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS recipient_email text;
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS email_subject text;
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS email_body text;

-- Add constraint for valid send statuses
-- Use DO block to avoid error if constraint already exists
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'valid_send_status'
  ) THEN
    ALTER TABLE submissions ADD CONSTRAINT valid_send_status
      CHECK (send_status IN ('draft', 'scheduled', 'sent', 'failed'));
  END IF;
END $$;

-- Index for querying scheduled submissions
CREATE INDEX IF NOT EXISTS idx_submissions_send_status ON submissions(send_status);
CREATE INDEX IF NOT EXISTS idx_submissions_scheduled_send ON submissions(scheduled_send_at)
  WHERE send_status = 'scheduled';

-- Comment columns for documentation
COMMENT ON COLUMN submissions.send_status IS 'Send status: draft, scheduled, sent, failed';
COMMENT ON COLUMN submissions.scheduled_send_at IS 'Timestamp for scheduled send (null if not scheduled)';
COMMENT ON COLUMN submissions.sent_at IS 'Timestamp when email was successfully sent';
COMMENT ON COLUMN submissions.recipient_email IS 'Client email address for quote delivery';
COMMENT ON COLUMN submissions.email_subject IS 'Email subject line (cached from send request)';
COMMENT ON COLUMN submissions.email_body IS 'Email body HTML (cached from send request)';
