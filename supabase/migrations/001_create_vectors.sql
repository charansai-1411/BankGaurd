-- Enable the pgvector extension to work with embedding vectors
CREATE EXTENSION IF NOT EXISTS vector;

-- Create vector store table
CREATE TABLE IF NOT EXISTS vector_store (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    namespace TEXT NOT NULL, -- e.g., 'rbi_compliance_regulation', 'api_specs_bank_doc'
    content TEXT NOT NULL,
    embedding VECTOR(768) NOT NULL, -- size 768 for Gemini text-embedding-004
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_active BOOLEAN NOT NULL DEFAULT true,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Index for cosine distance searches
CREATE INDEX IF NOT EXISTS vector_store_cosine_idx 
ON vector_store USING hnsw (embedding vector_cosine_ops);
