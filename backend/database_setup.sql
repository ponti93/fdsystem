-- Fraud Detection System Database Schema
-- PostgreSQL Database Setup

-- Users Table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    risk_profile JSONB,
    status VARCHAR(20) DEFAULT 'active'
);

-- Transactions Table
CREATE TABLE transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'NGN',
    transaction_type VARCHAR(50),
    merchant_id VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_method VARCHAR(50),
    ip_address INET,
    device_fingerprint VARCHAR(255),
    location_data JSONB,
    transaction_status VARCHAR(20)
);

-- Fraud Assessments Table
CREATE TABLE fraud_assessments (
    assessment_id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(50) REFERENCES transactions(transaction_id),
    fraud_score DECIMAL(5,4) NOT NULL,
    risk_factors JSONB,
    model_version VARCHAR(20),
    decision VARCHAR(20) NOT NULL,
    confidence_level DECIMAL(5,4),
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fraud Rules Table
CREATE TABLE fraud_rules (
    rule_id SERIAL PRIMARY KEY,
    rule_name VARCHAR(100) NOT NULL,
    rule_description TEXT,
    rule_logic JSONB,
    weight DECIMAL(3,2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better performance
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_timestamp ON transactions(timestamp);
CREATE INDEX idx_transactions_amount ON transactions(amount);
CREATE INDEX idx_fraud_assessments_transaction_id ON fraud_assessments(transaction_id);
CREATE INDEX idx_fraud_assessments_fraud_score ON fraud_assessments(fraud_score);
CREATE INDEX idx_fraud_assessments_decision ON fraud_assessments(decision);

-- Insert default fraud rules
INSERT INTO fraud_rules (rule_name, rule_description, rule_logic, weight, is_active) VALUES
('high_amount', 'High transaction amount rule', '{"threshold": 500000, "currency": "NGN"}', 0.6, TRUE),
('round_amount', 'Suspicious round amounts', '{"amounts": [100000, 200000, 500000, 1000000, 2000000]}', 0.3, TRUE),
('very_high_amount', 'Very high transaction amounts', '{"threshold": 1000000, "currency": "NGN"}', 0.5, TRUE),
('risky_merchant', 'Risky merchant categories', '{"categories": ["casino", "gambling", "crypto", "betting"]}', 0.4, TRUE),
('unusual_time', 'Unusual transaction times', '{"start_hour": 23, "end_hour": 6}', 0.2, TRUE),
('velocity_check', 'Transaction velocity analysis', '{"max_transactions": 5, "time_window": 300}', 0.7, TRUE),
('location_anomaly', 'Location-based anomaly detection', '{"max_distance": 100}', 0.5, TRUE);

-- Create sample users for testing
INSERT INTO users (email, phone_number, risk_profile, status) VALUES
('test_user_001@example.com', '+2348012345678', '{"risk_level": "low", "transaction_count": 150, "avg_amount": 75000}', 'active'),
('test_user_002@example.com', '+2348012345679', '{"risk_level": "medium", "transaction_count": 50, "avg_amount": 200000}', 'active'),
('test_user_003@example.com', '+2348012345680', '{"risk_level": "high", "transaction_count": 10, "avg_amount": 800000}', 'active'),
('admin@fraudsystem.com', '+2348012345681', '{"risk_level": "admin", "role": "administrator"}', 'active');
