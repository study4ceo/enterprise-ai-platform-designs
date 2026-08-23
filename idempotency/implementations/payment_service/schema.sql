-- Database schema for idempotent payment service

CREATE DATABASE IF NOT EXISTS idempotency_demo;

\c idempotency_demo;

-- Payments table with idempotency
CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    payment_id VARCHAR(100) UNIQUE NOT NULL,
    idempotency_key VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(20) NOT NULL,
    transaction_id VARCHAR(255),
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for fast lookups
CREATE INDEX idx_idempotency_key ON payments(idempotency_key);
CREATE INDEX idx_payment_id ON payments(payment_id);
CREATE INDEX idx_status ON payments(status);
CREATE INDEX idx_created_at ON payments(created_at);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to auto-update updated_at
CREATE TRIGGER update_payments_updated_at BEFORE UPDATE
    ON payments FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Sample data (optional)
INSERT INTO payments (payment_id, idempotency_key, status, transaction_id, amount, currency)
VALUES 
    ('pay_example_1', 'test_key_1', 'completed', 'txn_123', 99.99, 'USD'),
    ('pay_example_2', 'test_key_2', 'completed', 'txn_124', 149.50, 'USD')
ON CONFLICT DO NOTHING;
