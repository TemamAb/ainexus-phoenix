#!/usr/bin/env python3
"""
Production Database Setup & Migration Manager
Handles database initialization, schema migrations, and production data seeding
"""

import sqlite3
import psycopg2
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional

class DatabaseManager:
    def __init__(self, db_path: str = "arbitrage.db"):
        self.db_path = db_path
        self.logger = self._setup_logging()
        
    def _setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(__name__)
    
    def initialize_production_database(self):
        """Initialize production database with all required tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Trades table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    dex_a TEXT NOT NULL,
                    dex_b TEXT NOT NULL,
                    token_pair TEXT NOT NULL,
                    amount_in REAL NOT NULL,
                    amount_out REAL NOT NULL,
                    profit REAL NOT NULL,
                    gas_cost REAL NOT NULL,
                    net_profit REAL NOT NULL,
                    tx_hash TEXT UNIQUE,
                    status TEXT DEFAULT 'completed'
                )
            ''')
            
            # Risk limits table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS risk_limits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    strategy_id TEXT NOT NULL,
                    max_position_size REAL DEFAULT 10000,
                    daily_loss_limit REAL DEFAULT 5000,
                    max_drawdown REAL DEFAULT 0.1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Market data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    dex TEXT NOT NULL,
                    token_pair TEXT NOT NULL,
                    price REAL NOT NULL,
                    liquidity REAL NOT NULL,
                    volume_24h REAL DEFAULT 0
                )
            ''')
            
            conn.commit()
            self.logger.info("✅ Production database initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Database initialization failed: {e}")
            raise
    
    def run_migrations(self):
        """Run database migrations for production"""
        migrations = [
            "ALTER TABLE trades ADD COLUMN slippage REAL DEFAULT 0;",
            "CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades(timestamp);",
            "CREATE INDEX IF NOT EXISTS idx_market_data_dex ON market_data(dex);"
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for migration in migrations:
            try:
                cursor.execute(migration)
                self.logger.info(f"✅ Applied migration: {migration[:50]}...")
            except Exception as e:
                self.logger.warning(f"⚠️ Migration skipped: {e}")
        
        conn.commit()
        conn.close()

if __name__ == "__main__":
    db_manager = DatabaseManager()
    db_manager.initialize_production_database()
    db_manager.run_migrations()
