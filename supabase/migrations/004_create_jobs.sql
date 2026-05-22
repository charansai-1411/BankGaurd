-- Create jobs table
CREATE TABLE IF NOT EXISTS jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    status TEXT NOT NULL CHECK (status IN ('PENDING', 'RUNNING', 'READY', 'FAILED')),
    agent_type TEXT NOT NULL,
    mode TEXT NOT NULL,
    report_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Enable Row-Level Security
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;

-- Allow all operations for simplicity in this system
CREATE POLICY select_jobs_policy ON jobs FOR SELECT USING (true);
CREATE POLICY insert_jobs_policy ON jobs FOR INSERT WITH CHECK (true);
CREATE POLICY update_jobs_policy ON jobs FOR UPDATE USING (true);
CREATE POLICY delete_jobs_policy ON jobs FOR DELETE USING (true);

-- Grant table privileges to standard roles
GRANT ALL ON TABLE jobs TO anon, authenticated, service_role, postgres;

