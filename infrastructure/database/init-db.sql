-- Initialize AI-NEXUS database schema
CREATE DATABASE IF NOT EXISTS ainexus;

-- Create tables for arbitrage data, risk metrics, etc.
CREATE TABLE IF NOT EXISTS arbitrage_opportunities (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    chain VARCHAR(50),
    protocol VARCHAR(100),
    profit_estimate DECIMAL(20,8),
    executed BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS risk_metrics (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metric_name VARCHAR(100),
    metric_value DECIMAL(20,8),
    threshold DECIMAL(20,8)
);

CREATE TABLE IF NOT EXISTS performance_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    execution_time_ms INTEGER,
    success BOOLEAN,
    error_message TEXT
);
