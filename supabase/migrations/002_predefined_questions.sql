-- Create predefined questions table
CREATE TABLE IF NOT EXISTS predefined_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_domain TEXT NOT NULL, -- 'rbi_compliance', 'api_compliance', 'codebase'
    question_text TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Seed some V1 sample compliance questions
INSERT INTO predefined_questions (agent_domain, question_text, is_active) VALUES
('rbi_compliance', 'Does the bank have a documented and approved Business Continuity Plan (BCP)?', true),
('api_compliance', 'Are API endpoints protected by OAuth2 security schemes with token validation?', true),
('codebase', 'Does the payment gateway client implementation restrict TLS version support to TLS 1.2 or higher?', true);
