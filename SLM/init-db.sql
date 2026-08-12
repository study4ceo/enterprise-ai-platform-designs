-- SLM Platform Database Schema

-- Models table
CREATE TABLE IF NOT EXISTS models (
    id SERIAL PRIMARY KEY,
    model_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    size VARCHAR(50),  -- e.g., "3B", "7B"
    parameters BIGINT,  -- Number of parameters
    architecture VARCHAR(100),  -- e.g., "llama", "mistral"
    source VARCHAR(50) DEFAULT 'huggingface',
    huggingface_id VARCHAR(255),
    local_path TEXT,
    quantization VARCHAR(50),  -- e.g., "fp16", "int8", "int4"
    disk_size_mb INTEGER,
    download_status VARCHAR(50) DEFAULT 'not_downloaded',
    is_finetuned BOOLEAN DEFAULT FALSE,
    base_model_id VARCHAR(255),
    description TEXT,
    capabilities JSON,  -- {coding: true, chat: true, etc}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Datasets table
CREATE TABLE IF NOT EXISTS datasets (
    id SERIAL PRIMARY KEY,
    dataset_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    format VARCHAR(50),  -- "json", "jsonl", "csv", "parquet"
    num_samples INTEGER,
    size_mb FLOAT,
    source VARCHAR(50),  -- "upload", "huggingface", "generated"
    local_path TEXT,
    split_config JSON,  -- {train: 0.8, val: 0.1, test: 0.1}
    schema_info JSON,  -- Column definitions
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Training jobs table
CREATE TABLE IF NOT EXISTS training_jobs (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    model_id VARCHAR(255) REFERENCES models(model_id),
    dataset_id VARCHAR(255) REFERENCES datasets(dataset_id),
    
    -- Training configuration
    training_method VARCHAR(50),  -- "lora", "qlora", "full"
    config JSON,  -- All training hyperparameters
    
    -- LoRA specific
    lora_rank INTEGER,
    lora_alpha INTEGER,
    lora_dropout FLOAT,
    target_modules JSON,  -- ["q_proj", "v_proj", etc]
    
    -- Training parameters
    learning_rate FLOAT,
    num_epochs INTEGER,
    batch_size INTEGER,
    gradient_accumulation_steps INTEGER,
    warmup_steps INTEGER,
    max_seq_length INTEGER,
    
    -- Status
    status VARCHAR(50) DEFAULT 'queued',  -- queued, running, completed, failed, cancelled
    progress_percent FLOAT DEFAULT 0.0,
    current_epoch INTEGER DEFAULT 0,
    current_step INTEGER DEFAULT 0,
    total_steps INTEGER,
    
    -- Metrics
    train_loss FLOAT,
    eval_loss FLOAT,
    best_eval_loss FLOAT,
    learning_rate_current FLOAT,
    tokens_per_second FLOAT,
    
    -- Resources
    gpu_type VARCHAR(100),
    gpu_memory_used_mb INTEGER,
    estimated_time_remaining_minutes INTEGER,
    
    -- Outputs
    output_model_id VARCHAR(255),
    checkpoint_paths JSON,  -- Array of checkpoint paths
    logs_path TEXT,
    tensorboard_path TEXT,
    
    -- Timestamps
    queued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_minutes INTEGER,
    
    -- Error handling
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Training metrics (time series)
CREATE TABLE IF NOT EXISTS training_metrics (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(255) REFERENCES training_jobs(job_id),
    step INTEGER NOT NULL,
    epoch INTEGER,
    
    -- Loss metrics
    train_loss FLOAT,
    eval_loss FLOAT,
    
    -- Learning rate
    learning_rate FLOAT,
    
    -- Performance
    tokens_per_second FLOAT,
    samples_per_second FLOAT,
    gpu_memory_allocated_mb INTEGER,
    gpu_utilization_percent FLOAT,
    
    -- Time
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Additional metrics
    custom_metrics JSON
);

CREATE INDEX idx_training_metrics_job ON training_metrics(job_id, step);

-- Model evaluations
CREATE TABLE IF NOT EXISTS model_evaluations (
    id SERIAL PRIMARY KEY,
    eval_id VARCHAR(255) UNIQUE NOT NULL,
    model_id VARCHAR(255) REFERENCES models(model_id),
    
    -- Benchmark info
    benchmark_name VARCHAR(100),  -- "mmlu", "gsm8k", "hellaswag"
    dataset_name VARCHAR(255),
    num_samples INTEGER,
    
    -- Results
    accuracy FLOAT,
    perplexity FLOAT,
    score FLOAT,
    detailed_results JSON,
    
    -- Performance
    avg_latency_ms FLOAT,
    tokens_per_second FLOAT,
    memory_used_mb INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inference logs
CREATE TABLE IF NOT EXISTS inference_logs (
    id SERIAL PRIMARY KEY,
    request_id VARCHAR(255) UNIQUE NOT NULL,
    model_id VARCHAR(255) REFERENCES models(model_id),
    
    -- Request
    prompt TEXT,
    prompt_tokens INTEGER,
    
    -- Response
    response TEXT,
    response_tokens INTEGER,
    
    -- Performance
    latency_ms INTEGER,
    tokens_per_second FLOAT,
    
    -- Config
    temperature FLOAT,
    max_tokens INTEGER,
    top_p FLOAT,
    
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_inference_logs_model ON inference_logs(model_id, timestamp);
CREATE INDEX idx_inference_logs_timestamp ON inference_logs(timestamp);

-- Experiments (for A/B testing and comparison)
CREATE TABLE IF NOT EXISTS experiments (
    id SERIAL PRIMARY KEY,
    experiment_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Models to compare
    model_ids JSON,  -- Array of model IDs
    
    -- Test dataset
    test_dataset_id VARCHAR(255),
    num_samples INTEGER,
    
    -- Results
    results JSON,  -- Detailed comparison results
    winner_model_id VARCHAR(255),
    
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- User preferences (for future multi-user support)
CREATE TABLE IF NOT EXISTS user_preferences (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE,
    preferences JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- System metrics
CREATE TABLE IF NOT EXISTS system_metrics (
    id SERIAL PRIMARY KEY,
    
    -- Resource usage
    cpu_usage_percent FLOAT,
    memory_used_mb INTEGER,
    memory_total_mb INTEGER,
    disk_used_gb FLOAT,
    disk_total_gb FLOAT,
    
    -- GPU metrics
    gpu_name VARCHAR(255),
    gpu_memory_used_mb INTEGER,
    gpu_memory_total_mb INTEGER,
    gpu_utilization_percent FLOAT,
    gpu_temperature_c FLOAT,
    
    -- Network
    network_in_mb FLOAT,
    network_out_mb FLOAT,
    
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_system_metrics_timestamp ON system_metrics(timestamp);

-- Create update trigger for updated_at columns
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_models_updated_at BEFORE UPDATE ON models
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_datasets_updated_at BEFORE UPDATE ON datasets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_training_jobs_updated_at BEFORE UPDATE ON training_jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data (popular models)
INSERT INTO models (model_id, name, size, parameters, architecture, huggingface_id, description) VALUES
('llama-3.2-1b', 'Llama 3.2 1B', '1B', 1235000000, 'llama', 'meta-llama/Llama-3.2-1B-Instruct', 'Meta''s smallest Llama 3.2 model, perfect for quick experiments'),
('llama-3.2-3b', 'Llama 3.2 3B', '3B', 3213000000, 'llama', 'meta-llama/Llama-3.2-3B-Instruct', 'Balanced model with good quality and speed'),
('phi-3-mini', 'Phi-3 Mini', '3.8B', 3821000000, 'phi', 'microsoft/Phi-3-mini-4k-instruct', 'Microsoft''s efficient 3.8B model'),
('mistral-7b', 'Mistral 7B', '7B', 7241000000, 'mistral', 'mistralai/Mistral-7B-Instruct-v0.3', 'High-quality 7B model with great performance'),
('gemma-7b', 'Gemma 7B', '7B', 8537000000, 'gemma', 'google/gemma-7b-it', 'Google''s instruction-tuned 7B model')
ON CONFLICT (model_id) DO NOTHING;

-- Create initial indexes for performance
CREATE INDEX idx_models_size ON models(size);
CREATE INDEX idx_models_architecture ON models(architecture);
CREATE INDEX idx_models_is_finetuned ON models(is_finetuned);
CREATE INDEX idx_training_jobs_status ON training_jobs(status);
CREATE INDEX idx_training_jobs_model ON training_jobs(model_id);
CREATE INDEX idx_datasets_name ON datasets(name);

COMMENT ON TABLE models IS 'Stores information about available language models';
COMMENT ON TABLE datasets IS 'Stores training and evaluation datasets';
COMMENT ON TABLE training_jobs IS 'Tracks fine-tuning training jobs';
COMMENT ON TABLE training_metrics IS 'Time-series metrics during training';
COMMENT ON TABLE model_evaluations IS 'Benchmark results for models';
COMMENT ON TABLE inference_logs IS 'Logs of model inference requests';
COMMENT ON TABLE experiments IS 'A/B testing and model comparison experiments';
