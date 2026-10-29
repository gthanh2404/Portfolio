-- db/schema.sql — the whole schema of the notes app. Safe to run more than once.
CREATE TABLE IF NOT EXISTS notes (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  body text NOT NULL CHECK (length(body) > 0),
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS notes_created_at_idx ON notes (created_at DESC);
-- Supabase publishes an automatic REST API for tables in "public". We do not use it.
-- RLS on + no policies = that API sees nothing. The app connects as the table
-- owner, which bypasses RLS, so the app is not affected.
ALTER TABLE notes ENABLE ROW LEVEL SECURITY;
