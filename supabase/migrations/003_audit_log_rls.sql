-- Create audit logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id TEXT NOT NULL,
    node_name TEXT NOT NULL,
    input_payload JSONB DEFAULT '{}'::jsonb,
    output_payload JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Enable Row-Level Security
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Allow only INSERT operations for authenticated users (append-only)
CREATE POLICY insert_audit_logs_policy ON audit_logs
    FOR INSERT 
    WITH CHECK (true);

-- Deny UPDATE and DELETE operations for everyone on the client API
CREATE POLICY deny_update_audit_logs_policy ON audit_logs
    FOR UPDATE
    USING (false);

CREATE POLICY deny_delete_audit_logs_policy ON audit_logs
    FOR DELETE
    USING (false);
