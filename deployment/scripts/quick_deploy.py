#!/usr/bin/env python3
"""
AI-NEXUS v5.0 Quick Deployment Script
Fast-track deployment with essential checks
"""

import os
import sys
import time
from pathlib import Path

def check_environment():
    """Verify deployment environment"""
    print("í´ Checking deployment environment...")
    
    # Check essential directories
    essential_dirs = [
        "core_foundation",
        "advanced_ai", 
        "performance",
        "testing",
        "smart_contracts"
    ]
    
    for dir_name in essential_dirs:
        if not Path(dir_name).exists():
            print(f"â Missing directory: {dir_name}")
            return False
        print(f"â Directory: {dir_name}")
    
    return True

def verify_critical_files():
    """Verify essential system files"""
    print("\ní³ Verifying critical files...")
    
    critical_files = [
        "core_foundation/ai_intelligence/MarketScanner.py",
        "core_foundation/smart_contracts/FlashLoan.sol", 
        "advanced_ai/strategy_engine/StrategyOrchestrator.py",
        "testing/quality_assurance/SystemIntegrationTest.py"
    ]
    
    for file_path in critical_files:
        if not Path(file_path).exists():
            print(f"â Missing file: {file_path}")
            return False
        print(f"â File: {file_path}")
    
    return True

def quick_system_test():
    """Run quick system functionality test"""
    print("\ní·ª Running quick system test...")
    
    try:
        # Test basic AI functionality
        from core_foundation.ai_intelligence.MarketScanner import MarketScanner
        scanner = MarketScanner({'min_profit_threshold': 100})
        print("â MarketScanner: OPERATIONAL")
        
        # Test strategy orchestration
        from advanced_ai.strategy_engine.StrategyOrchestrator import StrategyOrchestrator
        orchestrator = StrategyOrchestrator({'cycle_interval': 2.0})
        print("â StrategyOrchestrator: OPERATIONAL")
        
        # Test data aggregation
        from core_foundation.data_intelligence.CrossChainDataAggregator import CrossChainDataAggregator
        aggregator = CrossChainDataAggregator({'active_chains': ['ethereum']})
        print("â CrossChainDataAggregator: OPERATIONAL")
        
        return True
        
    except Exception as e:
        print(f"â System test failed: {e}")
        return False

def main():
    """Execute quick deployment"""
    print("í¾¯ AI-NEXUS v5.0 QUICK DEPLOYMENT")
    print("================================")
    
    start_time = time.time()
    
    # Run deployment checks
    if not check_environment():
        print("â Environment check failed")
        sys.exit(1)
    
    if not verify_critical_files():
        print("â Critical files verification failed") 
        sys.exit(1)
    
    if not quick_system_test():
        print("â System functionality test failed")
        sys.exit(1)
    
    deployment_time = time.time() - start_time
    
    print(f"\ní¾ DEPLOYMENT SUCCESSFUL!")
    print(f"â±ï¸  Deployment time: {deployment_time:.2f}s")
    print("ï¿½ï¿½ System Status: READY FOR OPERATION")
    
    # Provide next steps
    print("\ní³ NEXT STEPS:")
    print("1. Start live data collection: python core_foundation/data_intelligence/CrossChainDataAggregator.py")
    print("2. Activate bot system: python advanced_ai/strategy_engine/StrategyOrchestrator.py")
    print("3. Deploy contracts: npx hardhat run scripts/deploy.js --network goerli")
    print("4. Monitor system: python testing/quality_assurance/SystemIntegrationTest.py")

if __name__ == "__main__":
    main()
