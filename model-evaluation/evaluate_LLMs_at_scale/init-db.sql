-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Evaluation jobs table
CREATE TABLE evaluation_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    name TEXT,
    status TEXT NOT NULL DEFAULT 'queued', -- queued, running, completed, failed, cancelled
    priority INT DEFAULT 1, -- 1=low, 2=normal, 3=high
    total_tasks INT DEFAULT 0,
    completed_tasks INT DEFAULT 0,
    failed_tasks INT DEFAULT 0,
    total_cost_usd NUMERIC(10,6) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_jobs_user_id ON evaluation_jobs(user_id);
CREATE INDEX idx_jobs_status ON evaluation_jobs(status);
CREATE INDEX idx_jobs_created_at ON evaluation_jobs(created_at DESC);

-- Evaluation tasks table
CREATE TABLE evaluation_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID REFERENCES evaluation_jobs(id) ON DELETE CASCADE,
    model TEXT NOT NULL,
    prompt TEXT NOT NULL,
    response TEXT,
    reference TEXT,
    status TEXT NOT NULL DEFAULT 'queued', -- queued, running, completed, failed, retrying
    retry_count INT DEFAULT 0,
    max_retries INT DEFAULT 3,
    error_message TEXT,
    tokens_used INT,
    cost_usd NUMERIC(10,6),
    latency_ms INT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_tasks_job_id ON evaluation_tasks(job_id);
CREATE INDEX idx_tasks_status ON evaluation_tasks(status);
CREATE INDEX idx_tasks_model ON evaluation_tasks(model);

-- Evaluation results table (TimescaleDB hypertable)
CREATE TABLE evaluation_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID REFERENCES evaluation_tasks(id) ON DELETE CASCADE,
    metrics JSONB NOT NULL, -- {bleu: 0.85, rouge: 0.9, bertscore: 0.92}
    metric_type TEXT, -- bleu, rouge, bertscore, llm_judge
    score NUMERIC(5,4),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Convert to hypertable for time-series data
SELECT create_hypertable('evaluation_results', 'created_at');

CREATE INDEX idx_results_task_id ON evaluation_results(task_id);
CREATE INDEX idx_results_metric_type ON evaluation_results(metric_type);

-- Prompt embeddings table for semantic search
CREATE TABLE prompt_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID REFERENCES evaluation_tasks(id) ON DELETE CASCADE,
    prompt_text TEXT NOT NULL,
    embedding vector(1536), -- OpenAI ada-002 dimension
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vector similarity index
CREATE INDEX ON prompt_embeddings USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Cost tracking table (TimescaleDB hypertable)
CREATE TABLE cost_tracking (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    job_id UUID REFERENCES evaluation_jobs(id),
    model TEXT NOT NULL,
    input_tokens INT,
    output_tokens INT,
    cost_usd NUMERIC(10,6),
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

SELECT create_hypertable('cost_tracking', 'timestamp');

CREATE INDEX idx_cost_user_id ON cost_tracking(user_id, timestamp DESC);
CREATE INDEX idx_cost_model ON cost_tracking(model, timestamp DESC);

-- Model rate limits table
CREATE TABLE model_rate_limits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model TEXT UNIQUE NOT NULL,
    requests_per_minute INT NOT NULL,
    tokens_per_minute INT,
    daily_budget_usd NUMERIC(10,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert default rate limits
INSERT INTO model_rate_limits (model, requests_per_minute, tokens_per_minute, daily_budget_usd) VALUES
('gemini-pro', 60, 60000, 50.00),
('gpt-4', 10, 10000, 100.00),
('gpt-3.5-turbo', 60, 60000, 20.00),
('claude-3-sonnet', 50, 50000, 75.00);

-- Dead letter queue table
CREATE TABLE dead_letter_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID REFERENCES evaluation_tasks(id),
    error_message TEXT,
    retry_count INT,
    payload JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_dlq_created_at ON dead_letter_queue(created_at DESC);

-- Audit log table
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    action TEXT NOT NULL,
    resource_type TEXT,
    resource_id UUID,
    details JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

SELECT create_hypertable('audit_log', 'created_at');

CREATE INDEX idx_audit_user_id ON audit_log(user_id, created_at DESC);

-- Create default admin user (password: admin123)
INSERT INTO users (email, hashed_password) VALUES
('admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5v7K9D0ZqH7Zm');
