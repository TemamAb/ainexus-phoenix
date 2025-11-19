#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simplified Adaptive Profit Calculator for Start Engine
"""

import numpy as np
from datetime import datetime

class SimpleProfitCalculator:
    def __init__(self):
        self.base_range = (40000, 200000)
        self.adjustment_factors = {}
        
    def calculate_profit_target(self, market_volatility=0.5, liquidity=0.7, 
                              success_rate=0.92, execution_speed=12):
        """Calculate adaptive profit target with simple factors"""
        
        volatility_boost = 1.0 + (market_volatility - 0.5) * 0.8
        liquidity_boost = 0.8 + (liquidity * 0.4)
        performance_boost = 0.7 + (success_rate * 0.5)
        speed_boost = 1.3 - (execution_speed / 50)
        
        total_adjustment = volatility_boost * liquidity_boost * performance_boost * speed_boost
        
        base_low, base_high = self.base_range
        new_low = int(base_low * total_adjustment)
        new_high = int(base_high * total_adjustment)
        
        new_low = max(20000, min(new_low, 300000))
        new_high = max(40000, min(new_high, 500000))
        new_high = max(new_high, new_low * 1.2)
        
        confidence = min(liquidity, success_rate)
        
        self.adjustment_factors = {
            'volatility_boost': volatility_boost,
            'liquidity_boost': liquidity_boost,
            'performance_boost': performance_boost,
            'speed_boost': speed_boost,
            'total_adjustment': total_adjustment
        }
        
        return {
            'range': (new_low, new_high),
            'confidence': confidence,
            'factors': self.adjustment_factors
        }

if __name__ == "__main__":
    calculator = SimpleProfitCalculator()
    
    conditions = [
        {"market_volatility": 0.8, "liquidity": 0.9, "success_rate": 0.95, "execution_speed": 10},
        {"market_volatility": 0.3, "liquidity": 0.6, "success_rate": 0.88, "execution_speed": 18},
        {"market_volatility": 0.5, "liquidity": 0.7, "success_rate": 0.92, "execution_speed": 12},
    ]
    
    print("ADAPTIVE PROFIT TARGET EXAMPLES:")
    print("=" * 35)
    
    for i, cond in enumerate(conditions, 1):
        target = calculator.calculate_profit_target(**cond)
        
        print(f"Example {i}:")
        print(f"  Conditions: Volatility={cond['market_volatility']:.1%}, "
              f"Liquidity={cond['liquidity']:.1%}, Success={cond['success_rate']:.1%}")
        print(f"  Daily Target: ${target['range'][0]:,.0f} - ${target['range'][1]:,.0f}")
        print(f"  Confidence: {target['confidence']:.1%}")
        print(f"  Adjustment: {target['factors']['total_adjustment']:.2f}x")
        print()
