-- AI-NEXUS Arbitrage Database Schema
-- Optimized for high-frequency trading data

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "timescaledb";

-- Core tables for arbitrage operations
CREATE TABLE exchanges (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    api_base_url VARCHAR(255),
    fee_structure JSONB,
    rate_limits JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE trading_pairs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    base_asset VARCHAR(20) NOT NULL,
    quote_asset VARCHAR(20) NOT NULL,
    symbol VARCHAR(50) NOT NULL UNIQUE,
    min_trade_size DECIMAL(20,8),
    max_trade_size DECIMAL(20,8),
    price_precision INTEGER,
    quantity_precision INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT unique_base_quote UNIQUE (base_asset, quote_asset)
);

CREATE TABLE market_prices (
    time TIMESTAMPTZ NOT NULL,
    exchange_id UUID NOT NULL REFERENCES exchanges(id),
    pair_id UUID NOT NULL REFERENCES trading_pairs(id),
    bid_price DECIMAL(20,8) NOT NULL,
    ask_price DECIMAL(20,8) NOT NULL,
    bid_size DECIMAL(20,8),
    ask_size DECIMAL(20,8),
    last_price DECIMAL(20,8),
    volume_24h DECIMAL(20,8),
    spread DECIMAL(10,8) GENERATED ALWAYS AS (ask_price - bid_price) STORED,
    
    PRIMARY KEY (time, exchange_id, pair_id)
);

-- Convert to hypertable for time-series data
SELECT create_hypertable('market_prices', 'time');

-- Arbitrage opportunities table
CREATE TABLE arbitrage_opportunities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_exchange_id UUID NOT NULL REFERENCES exchanges(id),
    target_exchange_id UUID NOT NULL REFERENCES exchanges(id),
    pair_id UUID NOT NULL REFERENCES trading_pairs(id),
    source_price DECIMAL(20,8) NOT NULL,
    target_price DECIMAL(20,8) NOT NULL,
    spread DECIMAL(10,8) NOT NULL,
    estimated_profit DECIMAL(20,8) NOT NULL,
    required_capital DECIMAL(20,8),
    risk_score DECIMAL(5,4),
    detected_at TIMESTAMPTZ DEFAULT NOW(),
    expired_at TIMESTAMPTZ,
    
    CONSTRAINT different_exchanges CHECK (source_exchange_id != target_exchange_id)
);

-- Trade execution records
CREATE TABLE trade_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    opportunity_id UUID REFERENCES arbitrage_opportunities(id),
    buy_order_id VARCHAR(100),
    sell_order_id VARCHAR(100),
    asset_pair VARCHAR(50) NOT NULL,
    buy_exchange_id UUID NOT NULL REFERENCES exchanges(id),
    sell_exchange_id UUID NOT NULL REFERENCES exchanges(id),
    quantity DECIMAL(20,8) NOT NULL,
    buy_price DECIMAL(20,8) NOT NULL,
    sell_price DECIMAL(20,8) NOT NULL,
    fees DECIMAL(20,8) NOT NULL,
    net_profit DECIMAL(20,8) NOT NULL,
    execution_time_ms INTEGER,
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'executing', 'completed', 'failed', 'cancelled')),
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Portfolio and balance tracking
CREATE TABLE portfolio_balances (
    time TIMESTAMPTZ NOT NULL,
    exchange_id UUID NOT NULL REFERENCES exchanges(id),
    asset VARCHAR(20) NOT NULL,
    total_balance DECIMAL(20,8) NOT NULL,
    available_balance DECIMAL(20,8) NOT NULL,
    locked_balance DECIMAL(20,8) NOT NULL,
    
    PRIMARY KEY (time, exchange_id, asset)
);

SELECT create_hypertable('portfolio_balances', 'time');

-- Risk management and limits
CREATE TABLE risk_limits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    limit_type VARCHAR(50) NOT NULL UNIQUE,
    limit_value DECIMAL(20,8) NOT NULL,
    timeframe VARCHAR(20),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE risk_violations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    limit_type VARCHAR(50) NOT NULL,
    current_value DECIMAL(20,8) NOT NULL,
    limit_value DECIMAL(20,8) NOT NULL,
    violation_time TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    action_taken VARCHAR(100)
);

-- AI model performance tracking
CREATE TABLE ai_model_performance (
    time TIMESTAMPTZ NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    accuracy DECIMAL(5,4),
    precision DECIMAL(5,4),
    recall DECIMAL(5,4),
    f1_score DECIMAL(5,4),
    inference_time_ms DECIMAL(10,2),
    training_loss DECIMAL(10,6),
    validation_loss DECIMAL(10,6),
    
    PRIMARY KEY (time, model_name, model_version)
);

SELECT create_hypertable('ai_model_performance', 'time');

-- System performance metrics
CREATE TABLE system_metrics (
    time TIMESTAMPTZ NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(20,8) NOT NULL,
    tags JSONB,
    
    PRIMARY KEY (time, metric_name)
);

SELECT create_hypertable('system_metrics', 'time');

-- Indexes for performance
CREATE INDEX idx_market_prices_pair_time ON market_prices (pair_id, time DESC);
CREATE INDEX idx_market_prices_exchange_pair ON market_prices (exchange_id, pair_id, time DESC);
CREATE INDEX idx_arbitrage_opportunities_detected ON arbitrage_opportunities (detected_at DESC);
CREATE INDEX idx_trade_executions_created ON trade_executions (created_at DESC);
CREATE INDEX idx_trade_executions_status ON trade_executions (status, created_at);
CREATE INDEX idx_portfolio_balances_asset ON portfolio_balances (asset, time DESC);
CREATE INDEX idx_risk_violations_time ON risk_violations (violation_time DESC);

-- Views for common queries
CREATE VIEW recent_arbitrage_opportunities AS
SELECT 
    ao.id,
    e1.name as source_exchange,
    e2.name as target_exchange,
    tp.symbol,
    ao.spread,
    ao.estimated_profit,
    ao.detected_at
FROM arbitrage_opportunities ao
JOIN exchanges e1 ON ao.source_exchange_id = e1.id
JOIN exchanges e2 ON ao.target_exchange_id = e2.id
JOIN trading_pairs tp ON ao.pair_id = tp.id
WHERE ao.detected_at >= NOW() - INTERVAL '1 hour'
ORDER BY ao.estimated_profit DESC;

CREATE VIEW daily_performance AS
SELECT
    DATE(te.created_at) as trade_date,
    COUNT(*) as total_trades,
    SUM(CASE WHEN te.status = 'completed' THEN 1 ELSE 0 END) as successful_trades,
    SUM(te.net_profit) as total_profit,
    AVG(te.execution_time_ms) as avg_execution_time,
    MIN(te.net_profit) as min_profit,
    MAX(te.net_profit) as max_profit
FROM trade_executions te
WHERE te.created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(te.created_at)
ORDER BY trade_date DESC;

-- Insert initial data
INSERT INTO risk_limits (limit_type, limit_value, timeframe) VALUES
('daily_loss_limit', 1000.00, 'daily'),
('max_position_size', 10000.00, 'per_trade'),
('max_drawdown', 0.10, 'daily'),
('min_profit_threshold', 0.002, 'per_trade'),
('var_95_confience', 500.00, 'daily');

-- Create update timestamp function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add triggers for updated_at
CREATE TRIGGER update_exchanges_updated_at BEFORE UPDATE ON exchanges
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_risk_limits_updated_at BEFORE UPDATE ON risk_limits
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
