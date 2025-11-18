//! AI-NEXUS High-Frequency Price Engine
//! Memory-safe, high-performance price calculations

#![allow(unused)]
use std::collections::{HashMap, VecDeque};
use std::sync::Arc;
use tokio::sync::RwLock;
use rustc_hash::FxHashMap;

/// High-performance price engine with thread-safe operations
pub struct PriceEngine {
    price_data: Arc<RwLock<FxHashMap<String, f64>>>,
    price_history: Arc<RwLock<FxHashMap<String, VecDeque<f64>>>>,
    max_history: usize,
}

impl PriceEngine {
    pub fn new(max_history: usize) -> Self {
        Self {
            price_data: Arc::new(RwLock::new(FxHashMap::default())),
            price_history: Arc::new(RwLock::new(FxHashMap::default())),
            max_history,
        }
    }

    /// Update price for a symbol (thread-safe)
    pub async fn update_price(&self, symbol: String, price: f64) {
        // Update current price
        {
            let mut data = self.price_data.write().await;
            data.insert(symbol.clone(), price);
        }

        // Update price history
        {
            let mut history = self.price_history.write().await;
            let entry = history.entry(symbol).or_insert_with(|| VecDeque::with_capacity(self.max_history));
            
            if entry.len() >= self.max_history {
                entry.pop_front();
            }
            entry.push_back(price);
        }
    }

    /// Get current price for symbol
    pub async fn get_price(&self, symbol: &str) -> Option<f64> {
        let data = self.price_data.read().await;
        data.get(symbol).copied()
    }

    /// Calculate moving average
    pub async fn moving_average(&self, symbol: &str, period: usize) -> Option<f64> {
        let history = self.price_history.read().await;
        let prices = history.get(symbol)?;
        
        if prices.len() < period {
            return None;
        }

        let sum: f64 = prices.iter().rev().take(period).sum();
        Some(sum / period as f64)
    }

    /// Calculate volatility (standard deviation)
    pub async fn volatility(&self, symbol: &str, period: usize) -> Option<f64> {
        let history = self.price_history.read().await;
        let prices = history.get(symbol)?;
        
        if prices.len() < period {
            return None;
        }

        let recent_prices: Vec<f64> = prices.iter().rev().take(period).copied().collect();
        let mean = recent_prices.iter().sum::<f64>() / period as f64;
        
        let variance = recent_prices.iter()
            .map(|&p| (p - mean).powi(2))
            .sum::<f64>() / period as f64;
        
        Some(variance.sqrt())
    }

    /// Batch update prices for multiple symbols
    pub async fn batch_update_prices(&self, updates: Vec<(String, f64)>) {
        let mut data = self.price_data.write().await;
        let mut history = self.price_history.write().await;

        for (symbol, price) in updates {
            // Update current price
            data.insert(symbol.clone(), price);

            // Update history
            let entry = history.entry(symbol).or_insert_with(|| VecDeque::with_capacity(self.max_history));
            if entry.len() >= self.max_history {
                entry.pop_front();
            }
            entry.push_back(price);
        }
    }

    /// Get price correlation between two symbols
    pub async fn correlation(&self, symbol1: &str, symbol2: &str, period: usize) -> Option<f64> {
        let history = self.price_history.read().await;
        let prices1 = history.get(symbol1)?;
        let prices2 = history.get(symbol2)?;

        if prices1.len() < period || prices2.len() < period {
            return None;
        }

        let prices1_vec: Vec<f64> = prices1.iter().rev().take(period).copied().collect();
        let prices2_vec: Vec<f64> = prices2.iter().rev().take(period).copied().collect();

        Self::calculate_correlation(&prices1_vec, &prices2_vec)
    }

    /// Calculate Pearson correlation coefficient
    fn calculate_correlation(x: &[f64], y: &[f64]) -> Option<f64> {
        if x.len() != y.len() || x.is_empty() {
            return None;
        }

        let n = x.len() as f64;
        let mean_x = x.iter().sum::<f64>() / n;
        let mean_y = y.iter().sum::<f64>() / n;

        let numerator: f64 = x.iter().zip(y)
            .map(|(&xi, &yi)| (xi - mean_x) * (yi - mean_y))
            .sum();

        let denom_x: f64 = x.iter()
            .map(|&xi| (xi - mean_x).powi(2))
            .sum::<f64>()
            .sqrt();

        let denom_y: f64 = y.iter()
            .map(|&yi| (yi - mean_y).powi(2))
            .sum::<f64>()
            .sqrt();

        if denom_x == 0.0 || denom_y == 0.0 {
            Some(0.0)
        } else {
            Some(numerator / (denom_x * denom_y))
        }
    }

    /// Detect price anomalies using statistical methods
    pub async fn detect_anomalies(&self, symbol: &str, threshold: f64) -> Option<bool> {
        let volatility = self.volatility(symbol, 20).await?;
        let current_price = self.get_price(symbol).await?;
        let moving_avg = self.moving_average(symbol, 20).await?;

        let deviation = (current_price - moving_avg).abs() / volatility;
        Some(deviation > threshold)
    }
}

/// Market data processor for high-frequency trading
pub struct MarketDataProcessor {
    price_engine: Arc<PriceEngine>,
    symbol_filters: FxHashMap<String, f64>,
}

impl MarketDataProcessor {
    pub fn new(price_engine: Arc<PriceEngine>) -> Self {
        Self {
            price_engine,
            symbol_filters: FxHashMap::default(),
        }
    }

    /// Process incoming market data
    pub async fn process_market_data(&mut self, symbol: String, price: f64) {
        // Apply price filter if exists
        if let Some(&filter) = self.symbol_filters.get(&symbol) {
            if price.abs() > filter {
                return; // Filter out extreme prices
            }
        }

        // Update price engine
        self.price_engine.update_price(symbol, price).await;
    }

    /// Set price filter for symbol
    pub fn set_price_filter(&mut self, symbol: String, max_price: f64) {
        self.symbol_filters.insert(symbol, max_price);
    }

    /// Get arbitrage opportunities across symbols
    pub async fn find_arbitrage_opportunities(&self, symbol_pairs: &[(&str, &str)]) -> Vec<(String, String, f64)> {
        let mut opportunities = Vec::new();

        for &(symbol1, symbol2) in symbol_pairs {
            if let (Some(price1), Some(price2)) = (
                self.price_engine.get_price(symbol1).await,
                self.price_engine.get_price(symbol2).await
            ) {
                let spread = (price1 - price2).abs() / price1.min(price2);
                
                if spread > 0.001 { // 0.1% threshold
                    opportunities.push((
                        symbol1.to_string(),
                        symbol2.to_string(),
                        spread
                    ));
                }
            }
        }

        opportunities
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tokio::test;

    #[test]
    async fn test_price_engine_basic() {
        let engine = PriceEngine::new(100);
        engine.update_price("ETH/USD".to_string(), 1800.0).await;

        let price = engine.get_price("ETH/USD").await;
        assert_eq!(price, Some(1800.0));
    }

    #[test]
    async fn test_moving_average() {
        let engine = PriceEngine::new(100);
        
        // Add some price history
        for i in 1..=5 {
            engine.update_price("TEST".to_string(), i as f64).await;
        }

        let ma = engine.moving_average("TEST", 3).await;
        assert!((ma.unwrap() - 4.0).abs() < 1e-10); // (3+4+5)/3 = 4
    }

    #[test]
    async fn test_correlation() {
        let engine = PriceEngine::new(100);
        
        // Perfectly correlated data
        for i in 1..=10 {
            engine.update_price("X".to_string(), i as f64).await;
            engine.update_price("Y".to_string(), i as f64 * 2.0).await;
        }

        let correlation = engine.correlation("X", "Y", 10).await;
        assert!((correlation.unwrap() - 1.0).abs() < 1e-10);
    }
}
