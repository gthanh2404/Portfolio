-- db/seed.sql — a few demo rows. Safe to run more than once: no duplicates.
INSERT INTO notes (body)
SELECT v.body
FROM (VALUES
  ('Session 14: this note lives in Supabase'),
  ('Region: Southeast Asia (Singapore)'),
  ('Free projects pause after 7 days without activity')
) AS v(body)
WHERE NOT EXISTS (SELECT 1 FROM notes n WHERE n.body = v.body);
