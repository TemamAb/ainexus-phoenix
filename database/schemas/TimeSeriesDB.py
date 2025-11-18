#!/usr/bin/env python3
"""
AI-NEXUS Time Series Database Manager
Optimized for high-frequency financial data
"""

import asyncio
import pandas as pd
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncpg
from contextlib import asynccontextmanager

@dataclass
class TimeSeriesConfig:
    """Configuration for time series database"""
    chunk_time_interval: str = "1 day"
    compression_interval: str = "7 days"
    retention_period: str = "90 days"
    replication_factor: int = 2

class TimeSeriesDB:
    """High-performance time series database manager"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.pool = None
        
    async def initialize(self):
        """Initialize database connection pool"""
        self.pool = await asyncpg.create_pool(
            self.connection_string,
            min_size=5,
            max_size=20,
            command_timeout=60
        )
        
        # Create tables and indexes if they don't exist
        await self._ensure_tables_exist()
        
    async def _ensure_tables_exist(self):
        """Ensure all required tables and indexes exist"""
        async with self.pool.acquire() as conn:
            # Enable TimescaleDB if not already enabled
            await conn.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")
            
            # Check if market_prices table exists, create if not
            table_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'market_prices'
                );
            """)
            
            if not table_exists:
                # This would create the full schema from arbitrage.db.sql
                # For now, we'll assume the schema is already created
                pass
    
    @asynccontextmanager
    async def get_connection(self):
        """Get database connection from pool"""
        if not self.pool:
            await self.initialize()
            
        async with self.pool.acquire() as connection:
            yield connection
    
    async def store_market_data(self, market_data: Dict):
        """Store market data in time series database"""
        async with self.get_connection() as conn:
            await conn.executemany("""
                INSERT INTO market_prices 
                (time, exchange_id, pair_id, bid_price, ask_price, bid_size, ask_size, last_price, volume_24h)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (time, exchange_id, pair_id) DO UPDATE SET
                bid_price = EXCLUDED.bid_price,
                ask_price = EXCLUDED.ask_price,
                bid_size = EXCLUDED.bid_size,
                ask_size = EXCLUDED.ask_size,
                last_price = EXCLUDED.last_price,
                volume_24h = EXCLUDED.volume_24h
            """, [
                (
                    data['timestamp'],
                    data['exchange_id'],
                    data['pair_id'],
                    data['bid_price'],
                    data['ask_price'],
                    data.get('bid_size'),
                    data.get('ask_size'),
                    data.get('last_price'),
                    data.get('volume_24h')
                )
                for data in market_data
            ])
    
    async def get_price_history(self, pair_id: str, exchange_id: str, 
                              start_time: datetime, end_time: datetime) -> pd.DataFrame:
        """Get price history for specific pair and exchange"""
        async with self.get_connection() as conn:
            records = await conn.fetch("""
                SELECT time, bid_price, ask_price, last_price, volume_24h
                FROM market_prices
                WHERE pair_id = $1 
                AND exchange_id = $2
                AND time BETWEEN $3 AND $4
                ORDER BY time ASC
            """, pair_id, exchange_id, start_time, end_time)
            
            return pd.DataFrame(records, columns=['time', 'bid_price', 'ask_price', 'last_price', 'volume_24h'])
    
    async def calculate_moving_averages(self, pair_id: str, exchange_id: str, 
                                      periods: List[int]) -> Dict[int, float]:
        """Calculate moving averages for different periods"""
        async with self.get_connection() as conn:
            ma_results = {}
            
            for period in periods:
                # Convert period to time interval
                interval = f"{period} minutes"
                
                ma_value = await conn.fetchval("""
                    SELECT AVG(last_price) 
                    FROM market_prices
                    WHERE pair_id = $1 
                    AND exchange_id = $2
                    AND time > NOW() - INTERVAL $3
                """, pair_id, exchange_id, interval)
                
                ma_results[period] = ma_value
            
            return ma_results
    
    async def detect_price_anomalies(self, pair_id: str, exchange_id: str, 
                                   threshold_std: float = 2.0) -> List[Dict]:
        """Detect price anomalies using statistical methods"""
        async with self.get_connection() as conn:
            anomalies = await conn.fetch("""
                WITH price_stats AS (
                    SELECT 
                        AVG(last_price) as mean_price,
                        STDDEV(last_price) as std_price
                    FROM market_prices
                    WHERE pair_id = $1 
                    AND exchange_id = $2
                    AND time > NOW() - INTERVAL '1 hour'
                )
                SELECT 
                    mp.time,
                    mp.last_price,
                    ABS(mp.last_price - ps.mean_price) / ps.std_price as z_score
                FROM market_prices mp
                CROSS JOIN price_stats ps
                WHERE mp.pair_id = $1 
                AND mp.exchange_id = $2
                AND mp.time > NOW() - INTERVAL '1 hour'
                AND ABS(mp.last_price - ps.mean_price) / ps.std_price > $3
                ORDER BY mp.time DESC
            """, pair_id, exchange_id, threshold_std)
            
            return [dict(record) for record in anomalies]
    
    async def get_correlation_matrix(self, pairs: List[str], 
                                  start_time: datetime, end_time: datetime) -> pd.DataFrame:
        """Calculate correlation matrix between trading pairs"""
        async with self.get_connection() as conn:
            # Get price data for all pairs
            correlation_data = {}
            
            for pair in pairs:
                records = await conn.fetch("""
                    SELECT time, last_price
                    FROM market_prices
                    WHERE pair_id = $1
                    AND time BETWEEN $2 AND $3
                    ORDER BY time
                """, pair, start_time, end_time)
                
                if records:
                    df = pd.DataFrame(records, columns=['time', 'last_price'])
                    correlation_data[pair] = df.set_index('time')['last_price']
            
            # Create combined DataFrame and calculate correlations
            if correlation_data:
                combined_df = pd.DataFrame(correlation_data)
                return combined_df.corr()
            else:
                return pd.DataFrame()
    
    async def store_arbitrage_opportunity(self, opportunity: Dict):
        """Store arbitrage opportunity"""
        async with self.get_connection() as conn:
            await conn.execute("""
                INSERT INTO arbitrage_opportunities 
                (source_exchange_id, target_exchange_id, pair_id, source_price, 
                 target_price, spread, estimated_profit, required_capital, risk_score)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """, 
                opportunity['source_exchange_id'],
                opportunity['target_exchange_id'],
                opportunity['pair_id'],
                opportunity['source_price'],
                opportunity['target_price'],
                opportunity['spread'],
                opportunity['estimated_profit'],
                opportunity.get('required_capital'),
                opportunity.get('risk_score')
            )
    
    async def get_recent_opportunities(self, limit: int = 100) -> List[Dict]:
        """Get recent arbitrage opportunities"""
        async with self.get_connection() as conn:
            records = await conn.fetch("""
                SELECT * FROM recent_arbitrage_opportunities
                LIMIT $1
            """, limit)
            
            return [dict(record) for record in records]
    
    async def store_trade_execution(self, trade: Dict):
        """Store trade execution record"""
        async with self.get_connection() as conn:
            await conn.execute("""
                INSERT INTO trade_executions 
                (opportunity_id, buy_order_id, sell_order_id, asset_pair, 
                 buy_exchange_id, sell_exchange_id, quantity, buy_price, 
                 sell_price, fees, net_profit, execution_time_ms, status)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
            """,
                trade.get('opportunity_id'),
                trade.get('buy_order_id'),
                trade.get('sell_order_id'),
                trade['asset_pair'],
                trade['buy_exchange_id'],
                trade['sell_exchange_id'],
                trade['quantity'],
                trade['buy_price'],
                trade['sell_price'],
                trade['fees'],
                trade['net_profit'],
                trade.get('execution_time_ms'),
                trade['status']
            )
    
    async def get_performance_metrics(self, days: int = 30) -> Dict:
        """Get performance metrics for specified period"""
        async with self.get_connection() as conn:
            records = await conn.fetch("""
                SELECT * FROM daily_performance
                WHERE trade_date >= CURRENT_DATE - $1::integer
                ORDER BY trade_date DESC
            """, days)
            
            return [dict(record) for record in records]
    
    async def optimize_database(self):
        """Run database optimization tasks"""
        async with self.get_connection() as conn:
            # Compress old chunks
            await conn.execute("""
                SELECT compress_chunk(c) 
                FROM show_chunks('market_prices', older_than => INTERVAL '7 days') c;
            """)
            
            # Drop old data based on retention policy
            await conn.execute("""
                SELECT drop_chunks('market_prices', older_than => INTERVAL '90 days');
            """)
            
            # Update statistics
            await conn.execute("ANALYZE;")
    
    async def get_database_stats(self) -> Dict:
        """Get database statistics"""
        async with self.get_connection() as conn:
            # Table sizes
            table_sizes = await conn.fetch("""
                SELECT 
                    table_name,
                    pg_size_pretty(pg_total_relation_size(quote_ident(table_name))) as size
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY pg_total_relation_size(quote_ident(table_name)) DESC;
            """)
            
            # Chunk information for hypertables
            chunk_info = await conn.fetch("""
                SELECT 
                    hypertable_name,
                    chunk_name,
                    range_start,
                    range_end,
                    is_compressed,
                    chunk_size
                FROM timescaledb_information.chunks
                WHERE hypertable_name IN ('market_prices', 'portfolio_balances', 'system_metrics')
                ORDER BY range_start DESC
                LIMIT 10;
            """)
            
            return {
                'table_sizes': [dict(record) for record in table_sizes],
                'recent_chunks': [dict(record) for record in chunk_info]
            }

# Example usage
async def main():
    """Example usage of TimeSeriesDB"""
    db = TimeSeriesDB("postgresql://user:pass@localhost/ainexus")
    await db.initialize()
    
    # Example market data
    market_data = [{
        'timestamp': datetime.now(),
        'exchange_id': 'binance-uuid',
        'pair_id': 'eth-usdt-uuid', 
        'bid_price': 1800.50,
        'ask_price': 1800.75,
        'last_price': 1800.60,
        'volume_24h': 1000000.0
    }]
    
    await db.store_market_data(market_data)
    
    # Get performance metrics
    metrics = await db.get_performance_metrics(7)
    print("Weekly performance:", metrics)
    
    # Get database statistics
    stats = await db.get_database_stats()
    print("Database stats:", stats)

if __name__ == "__main__":
    asyncio.run(main())
