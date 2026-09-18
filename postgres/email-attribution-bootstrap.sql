-- Durable email attribution columns used by the Executive Report.
-- Safe to apply repeatedly; live sender workflows also apply these guards.

ALTER TABLE "DAN_Release_Log" ADD COLUMN IF NOT EXISTS campaign_key TEXT;
UPDATE "DAN_Release_Log"
SET campaign_key = CASE
  WHEN campaign = 'brands' THEN 'dan_brands'
  WHEN campaign = 'dispensaries' THEN 'dan_dispensaries'
  ELSE 'dan_' || COALESCE(NULLIF(campaign, ''), 'unknown')
END
WHERE NULLIF(campaign_key, '') IS NULL;
CREATE INDEX IF NOT EXISTS dan_release_log_idx_campaign_key
  ON "DAN_Release_Log" (campaign_key, release_date);

ALTER TABLE "Emerald_Release_Log" ADD COLUMN IF NOT EXISTS campaign_key TEXT;
UPDATE "Emerald_Release_Log"
SET campaign_key = 'emerald_' || COALESCE(NULLIF(bucket, ''), 'unknown')
WHERE NULLIF(campaign_key, '') IS NULL;
CREATE INDEX IF NOT EXISTS emerald_release_log_idx_campaign_key
  ON "Emerald_Release_Log" (campaign_key, release_date);

ALTER TABLE partnership_release_log ADD COLUMN IF NOT EXISTS campaign_key TEXT;
UPDATE partnership_release_log
SET campaign_key = 'partnership_email'
WHERE NULLIF(campaign_key, '') IS NULL;
CREATE INDEX IF NOT EXISTS partnership_release_log_idx_campaign_key
  ON partnership_release_log (campaign_key, release_date);

ALTER TABLE newsletter_send_log ADD COLUMN IF NOT EXISTS campaign_key TEXT;
UPDATE newsletter_send_log
SET campaign_key = 'newsletter_' || week_key
WHERE NULLIF(campaign_key, '') IS NULL;
CREATE INDEX IF NOT EXISTS newsletter_send_log_idx_campaign_key
  ON newsletter_send_log (campaign_key, week_key);
