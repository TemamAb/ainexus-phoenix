#!/usr/bin/env python3
"""
AI-NEXUS Multi-Source Oracle Aggregator
Robust price aggregation with outlier detection
"""

import numpy as np
from typing import List, Dict
from statistics import median, mean

class MultiSourceAggregator:
    def __init__(self, min_sources: int = 3, outlier_threshold: float = 2.0):
        self.min_sources = min_sources
        self.outlier_threshold = outlier_threshold
        
    def aggregate_prices(self, prices: List[Dict]) -> Dict:
        """Aggregate prices from multiple sources with outlier removal"""
        if len(prices) < self.min_sources:
            return self._handle_insufficient_sources(prices)
        
        # Extract price values and weights
        price_values = [p['price'] for p in prices]
        weights = [p.get('weight', 1.0) for p in prices]
        sources = [p['source'] for p in prices]
        
        # Remove outliers using IQR method
        filtered_data = self._remove_outliers(price_values, weights, sources)
        
        if len(filtered_data['prices']) < self.min_sources:
            return self._fallback_aggregation(prices)
        
        # Calculate weighted median and mean
        weighted_median = self._weighted_median(
            filtered_data['prices'], filtered_data['weights']
        )
        weighted_mean = self._weighted_mean(
            filtered_data['prices'], filtered_data['weights']
        )
        
        # Calculate confidence based on consensus
        confidence = self._calculate_confidence(
            filtered_data['prices'], weighted_median
        )
        
        return {
            'price': weighted_median,  # Use median as it's more robust
            'mean_price': weighted_mean,
            'confidence': confidence,
            'sources_used': filtered_data['sources'],
            'total_sources': len(prices),
            'outliers_removed': len(prices) - len(filtered_data['prices'])
        }
    
    def _remove_outliers(self, prices: List[float], weights: List[float], sources: List[str]) -> Dict:
        """Remove outliers using IQR method"""
        if len(prices) < 3:
            return {'prices': prices, 'weights': weights, 'sources': sources}
        
        q1 = np.percentile(prices, 25)
        q3 = np.percentile(prices, 75)
        iqr = q3 - q1
        
        lower_bound = q1 - self.outlier_threshold * iqr
        upper_bound = q3 + self.outlier_threshold * iqr
        
        filtered_prices = []
        filtered_weights = []
        filtered_sources = []
        
        for i, price in enumerate(prices):
            if lower_bound <= price <= upper_bound:
                filtered_prices.append(price)
                filtered_weights.append(weights[i])
                filtered_sources.append(sources[i])
        
        return {
            'prices': filtered_prices,
            'weights': filtered_weights, 
            'sources': filtered_sources
        }
    
    def _weighted_median(self, values: List[float], weights: List[float]) -> float:
        """Calculate weighted median"""
        combined = sorted(zip(values, weights))
        values_sorted, weights_sorted = zip(*combined)
        
        cumulative_weights = np.cumsum(weights_sorted)
        total_weight = cumulative_weights[-1]
        midpoint = total_weight / 2
        
        for i, cum_weight in enumerate(cumulative_weights):
            if cum_weight >= midpoint:
                return values_sorted[i]
        
        return values_sorted[-1]
    
    def _weighted_mean(self, values: List[float], weights: List[float]) -> float:
        """Calculate weighted mean"""
        return sum(v * w for v, w in zip(values, weights)) / sum(weights)
    
    def _calculate_confidence(self, prices: List[float], median_price: float) -> float:
        """Calculate confidence based on price consensus"""
        if len(prices) < 2:
            return 0.5
        
        deviations = [abs(p - median_price) / median_price for p in prices]
        avg_deviation = mean(deviations)
        
        # Convert to confidence score (0-1)
        confidence = 1 - min(avg_deviation * 10, 1.0)
        return max(0, confidence)
    
    def _handle_insufficient_sources(self, prices: List[Dict]) -> Dict:
        """Handle case with insufficient price sources"""
        if not prices:
            return {'error': 'No price sources available'}
        
        # Use simple average with low confidence
        price_values = [p['price'] for p in prices]
        avg_price = mean(price_values)
        
        return {
            'price': avg_price,
            'mean_price': avg_price,
            'confidence': 0.3,  # Low confidence
            'sources_used': [p['source'] for p in prices],
            'total_sources': len(prices),
            'warning': 'Insufficient sources for robust aggregation'
        }
    
    def _fallback_aggregation(self, prices: List[Dict]) -> Dict:
        """Fallback aggregation when too many outliers removed"""
        price_values = [p['price'] for p in prices]
        weights = [p.get('weight', 1.0) for p in prices]
        
        # Use all prices but with reduced weights for outliers
        median_price = median(price_values)
        
        # Reduce weights for outliers
        adjusted_weights = []
        for i, price in enumerate(price_values):
            deviation = abs(price - median_price) / median_price
            if deviation > 0.1:  # More than 10% deviation
                adjusted_weights.append(weights[i] * 0.1)  # Reduce weight
            else:
                adjusted_weights.append(weights[i])
        
        weighted_median = self._weighted_median(price_values, adjusted_weights)
        
        return {
            'price': weighted_median,
            'mean_price': self._weighted_mean(price_values, adjusted_weights),
            'confidence': 0.6,  # Medium confidence
            'sources_used': [p['source'] for p in prices],
            'total_sources': len(prices),
            'warning': 'Fallback aggregation used due to outliers'
        }
