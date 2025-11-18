-- Risk Management Database Schema
-- Production-grade risk limits and monitoring

CREATE TABLE IF NOT EXISTS risk_limits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    strategy_id TEXT NOT NULL UNIQUE,
    max_position_size DECIMAL(15,2) DEFAULT 10000.00,
    daily_loss_limit DECIMAL(15,2) DEFAULT 5000.00,
    max_drawdown DECIMAL(5,4) DEFAULT 0.1000,
    max_leverage INTEGER DEFAULT 3,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS trade_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_id TEXT NOT NULL,
    strategy_id TEXT NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    profit_loss DECIMAL(15,2),
    risk_check_passed BOOLEAN DEFAULT TRUE,
    risk_violations JSON,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (strategy_id) REFERENCES risk_limits (strategy_id)
);

CREATE TABLE IF NOT EXISTS system_limits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    limit_type TEXT NOT NULL UNIQUE,
    limit_value DECIMAL(15,2) NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default risk limits
INSERT OR REPLACE INTO risk_limits (strategy_id, max_position_size, daily_loss_limit, max_drawdown, max_leverage) VALUES
('uniswap_pancake_arb', 5000.00, 1000.00, 0.0500, 3),
('sushiswap_quick_arb', 3000.00, 600.00, 0.0300, 2),
('multi_dex_triangular', 10000.00, 2000.00, 0.0800, 4),
('flash_loan_arb', 25000.00, 5000.00, 0.1000, 5);

-- Insert system-wide limits
INSERT OR REPLACE INTO system_limits (limit_type, limit_value, description) VALUES
('total_daily_loss', 10000.00, 'Maximum total daily loss across all strategies'),
('max_concurrent_trades', 10, 'Maximum number of concurrent trades'),
('min_profit_threshold', 5.00, 'Minimum profit threshold for executing trades'),
('system_circuit_breaker', 20000.00, 'System-wide circuit breaker threshold');

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_trade_audit_strategy ON trade_audit(strategy_id);
CREATE INDEX IF NOT EXISTS idx_trade_audit_timestamp ON trade_audit(executed_at);
CREATE INDEX IF NOT EXISTS idx_risk_limits_strategy ON risk_limits(strategy_id);

-- Create views for monitoring
CREATE VIEW IF NOT EXISTS daily_risk_summary AS
SELECT 
    strategy_id,
    COUNT(*) as trade_count,
    SUM(profit_loss) as total_pnl,
    SUM(CASE WHEN profit_loss < 0 THEN profit_loss ELSE 0 END) as total_loss
FROM trade_audit 
WHERE date(executed_at) = date('now')
GROUP BY strategy_id;

CREATE VIEW IF NOT EXISTS risk_limit_utilization AS
SELECT 
    rl.strategy_id,
    rl.daily_loss_limit,
    COALESCE(ars.total_loss, 0) as current_loss,
    (COALESCE(ars.total_loss, 0) / rl.daily_loss_limit) as utilization_ratio
FROM risk_limits rl
LEFT JOIN daily_risk_summary ars ON rl.strategy_id = ars.strategy_id;
