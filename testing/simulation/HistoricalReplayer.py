#!/usr/bin/env python3
"""
AI-NEXUS Historical Market Replayer
Production-like simulation with historical data
"""

import pandas as pd
import numpy as np
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

class HistoricalReplayer:
    """Replay historical market data for strategy testing"""
    
    def __init__(self, data_source: str, speed_multiplier: float = 1.0):
        self.data_source = data_source
        self.speed_multiplier = speed_multiplier
        self.current_time = None
        self.is_playing = False
        self.observers = []
        self.historical_data = self.load_historical_data()
        
    def load_historical_data(self) -> Dict[str, pd.DataFrame]:
        """Load historical market data"""
        # This would load from database or files in production
        return {
            'ETH/USD': self.generate_sample_data('ETH', 1800, 0.02),
            'BTC/USD': self.generate_sample_data('BTC', 30000, 0.015),
            'UNI/USD': self.generate_sample_data('UNI', 6.0, 0.03)
        }
    
    def generate_sample_data(self, symbol: str, base_price: float, volatility: float) -> pd.DataFrame:
        """Generate sample historical data for testing"""
        dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='1min')
        returns = np.random.normal(0, volatility, len(dates))
        
        prices = [base_price]
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))
        
        df = pd.DataFrame({
            'timestamp': dates,
            'open': prices,
            'high': [p * 1.001 for p in prices],  # Slightly higher
            'low': [p * 0.999 for p in prices],   # Slightly lower
            'close': prices,
            'volume': np.random.uniform(1000, 10000, len(dates))
        })
        
        return df
    
    async def replay_period(self, start_date: datetime, end_date: datetime):
        """Replay specific historical period"""
        self.current_time = start_date
        self.is_playing = True
        
        logging.info(f"Starting replay from {start_date} to {end_date}")
        
        while self.current_time <= end_date and self.is_playing:
            # Get market data for current timestamp
            market_data = self.get_market_snapshot(self.current_time)
            
            # Notify observers
            await self.notify_observers(market_data)
            
            # Advance time
            await asyncio.sleep(1.0 / self.speed_multiplier)
            self.current_time += timedelta(minutes=1)
        
        self.is_playing = False
        logging.info("Historical replay completed")
    
    def get_market_snapshot(self, timestamp: datetime) -> Dict:
        """Get market data for specific timestamp"""
        snapshot = {
            'timestamp': timestamp,
            'prices': {},
            'volumes': {},
            'spreads': {}
        }
        
        for symbol, data in self.historical_data.items():
            # Find closest timestamp in data
            time_diff = abs(data['timestamp'] - timestamp)
            closest_idx = time_diff.idxmin()
            
            if time_diff[closest_idx] < timedelta(minutes=1):
                snapshot['prices'][symbol] = data.loc[closest_idx, 'close']
                snapshot['volumes'][symbol] = data.loc[closest_idx, 'volume']
                snapshot['spreads'][symbol] = (
                    data.loc[closest_idx, 'high'] - data.loc[closest_idx, 'low']
                ) / data.loc[closest_idx, 'close']
        
        return snapshot
    
    def add_observer(self, observer):
        """Add strategy observer"""
        self.observers.append(observer)
    
    async def notify_observers(self, market_data: Dict):
        """Notify all observers of new market data"""
        for observer in self.observers:
            try:
                await observer.on_market_data(market_data)
            except Exception as e:
                logging.error(f"Observer error: {e}")
    
    def pause(self):
        """Pause replay"""
        self.is_playing = False
    
    def resume(self):
        """Resume replay"""
        if not self.is_playing and self.current_time:
            self.is_playing = True
            asyncio.create_task(self.continue_replay())
    
    async def continue_replay(self):
        """Continue replay from current time"""
        # Implementation for continuing replay
        pass

class StrategyTester:
    """Test arbitrage strategies in historical simulation"""
    
    def __init__(self, strategy, initial_capital: float = 10000):
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions = {}
        self.trade_history = []
        performance_metrics = {}
        
    async def on_market_data(self, market_data: Dict):
        """Process new market data"""
        try:
            # Get strategy signals
            signals = await self.strategy.analyze(market_data)
            
            # Execute trades based on signals
            for signal in signals:
                if signal['action'] == 'BUY' and self._can_afford(signal):
                    await self.execute_trade(signal, market_data)
                elif signal['action'] == 'SELL' and self._has_position(signal):
                    await self.execute_trade(signal, market_data)
            
            # Update performance metrics
            self.update_performance_metrics(market_data)
            
        except Exception as e:
            logging.error(f"Strategy testing error: {e}")
    
    async def execute_trade(self, signal: Dict, market_data: Dict):
        """Execute trade in simulation"""
        symbol = signal['symbol']
        price = market_data['prices'][symbol]
        quantity = signal['quantity']
        
        if signal['action'] == 'BUY':
            cost = price * quantity
            if cost <= self.current_capital:
                self.current_capital -= cost
                self.positions[symbol] = self.positions.get(symbol, 0) + quantity
                
                self.trade_history.append({
                    'timestamp': market_data['timestamp'],
                    'action': 'BUY',
                    'symbol': symbol,
                    'quantity': quantity,
                    'price': price,
                    'cost': cost
                })
        
        elif signal['action'] == 'SELL':
            if self.positions.get(symbol, 0) >= quantity:
                revenue = price * quantity
                self.current_capital += revenue
                self.positions[symbol] -= quantity
                
                self.trade_history.append({
                    'timestamp': market_data['timestamp'],
                    'action': 'SELL', 
                    'symbol': symbol,
                    'quantity': quantity,
                    'price': price,
                    'revenue': revenue
                })
    
    def _can_afford(self, signal: Dict) -> bool:
        """Check if we can afford the trade"""
        # Simplified check - in reality would use current market prices
        return self.current_capital > signal.get('estimated_cost', 0)
    
    def _has_position(self, signal: Dict) -> bool:
        """Check if we have the position to sell"""
        return self.positions.get(signal['symbol'], 0) >= signal['quantity']
    
    def update_performance_metrics(self, market_data: Dict):
        """Update performance metrics"""
        # Calculate current portfolio value
        portfolio_value = self.current_capital
        for symbol, quantity in self.positions.items():
            if symbol in market_data['prices']:
                portfolio_value += quantity * market_data['prices'][symbol]
        
        # Update metrics
        self.performance_metrics = {
            'timestamp': market_data['timestamp'],
            'portfolio_value': portfolio_value,
            'cash_balance': self.current_capital,
            'positions': self.positions.copy(),
            'total_return': (portfolio_value - self.initial_capital) / self.initial_capital,
            'sharpe_ratio': self.calculate_sharpe_ratio(),
            'max_drawdown': self.calculate_max_drawdown(),
            'win_rate': self.calculate_win_rate()
        }
    
    def calculate_sharpe_ratio(self) -> float:
        """Calculate Sharpe ratio from trade history"""
        if len(self.trade_history) < 2:
            return 0.0
        
        returns = []
        for i in range(1, len(self.trade_history)):
            # Simplified return calculation
            prev_value = self.initial_capital  # This should be improved
            current_value = self.performance_metrics['portfolio_value']
            returns.append((current_value - prev_value) / prev_value)
        
        if not returns:
            return 0.0
        
        avg_return = np.mean(returns)
        std_return = np.std(returns)
        
        return avg_return / std_return if std_return > 0 else 0.0
    
    def calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown"""
        # This would track historical portfolio values in production
        return 0.0  # Placeholder
    
    def calculate_win_rate(self) -> float:
        """Calculate trade win rate"""
        if not self.trade_history:
            return 0.0
        
        profitable_trades = 0
        for trade in self.trade_history:
            # Determine if trade was profitable
            # This would require tracking entry/exit prices
            pass
        
        return profitable_trades / len(self.trade_history) if self.trade_history else 0.0
    
    def generate_report(self) -> Dict:
        """Generate strategy performance report"""
        return {
            'initial_capital': self.initial_capital,
            'final_portfolio_value': self.performance_metrics['portfolio_value'],
            'total_return': self.performance_metrics['total_return'],
            'sharpe_ratio': self.performance_metrics['sharpe_ratio'],
            'max_drawdown': self.performance_metrics['max_drawdown'],
            'win_rate': self.performance_metrics['win_rate'],
            'total_trades': len(self.trade_history),
            'trade_history': self.trade_history,
            'final_positions': self.positions
        }

# Example usage
async def main():
    """Example of historical strategy testing"""
    
    # Create historical replayer
    replayer = HistoricalReplayer('sample_data')
    
    # Create strategy tester
    from strategies.mean_reversion import MeanReversionStrategy
    strategy = MeanReversionStrategy()
    tester = StrategyTester(strategy)
    
    # Add tester as observer
    replayer.add_observer(tester)
    
    # Replay one week of historical data
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 7)
    
    await replayer.replay_period(start_date, end_date)
    
    # Generate performance report
    report = tester.generate_report()
    print("Strategy Performance Report:")
    print(f"Total Return: {report['total_return']:.2%}")
    print(f"Sharpe Ratio: {report['sharpe_ratio']:.2f}")
    print(f"Win Rate: {report['win_rate']:.2%}")

if __name__ == '__main__':
    asyncio.run(main())
