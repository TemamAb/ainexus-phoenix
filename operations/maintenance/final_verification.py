#!/usr/bin/env python3
"""
AI-NEXUS Final Verification System
Comprehensive system validation and health checks
"""

import asyncio
import logging
from typing import Dict, List
from datetime import datetime
import pandas as pd

class SystemVerification:
    """Comprehensive system verification and validation"""
    
    def __init__(self):
        self.verification_results = {}
        self.health_checks = [
            self.check_database_connectivity,
            self.check_exchange_connections,
            self.check_ai_models,
            self.check_risk_limits,
            self.check_performance_metrics,
            self.check_security_configuration
        ]
    
    async def run_full_verification(self) -> Dict:
        """Run complete system verification"""
        logging.info("Starting comprehensive system verification...")
        
        verification_report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'PASS',
            'checks': {},
            'recommendations': []
        }
        
        # Run all health checks
        for check in self.health_checks:
            try:
                check_name = check.__name__
                logging.info(f"Running verification: {check_name}")
                
                result = await check()
                verification_report['checks'][check_name] = result
                
                if not result.get('passed', False):
                    verification_report['overall_status'] = 'FAIL'
                    verification_report['recommendations'].extend(
                        result.get('recommendations', [])
                    )
                    
            except Exception as e:
                logging.error(f"Verification {check_name} failed: {e}")
                verification_report['checks'][check_name] = {
                    'passed': False,
                    'error': str(e)
                }
                verification_report['overall_status'] = 'FAIL'
        
        logging.info(f"Verification completed: {verification_report['overall_status']}")
        return verification_report
    
    async def check_database_connectivity(self) -> Dict:
        """Verify database connectivity and performance"""
        try:
            from database.schemas.TimeSeriesDB import TimeSeriesDB
            
            db = TimeSeriesDB("postgresql://user:pass@localhost/ainexus")
            await db.initialize()
            
            # Test query performance
            start_time = datetime.now()
            stats = await db.get_database_stats()
            query_time = (datetime.now() - start_time).total_seconds()
            
            # Check if TimescaleDB is properly configured
            has_hypertables = any(
                'market_prices' in str(chunk) for chunk in stats.get('recent_chunks', [])
            )
            
            return {
                'passed': query_time < 1.0 and has_hypertables,
                'query_time_seconds': query_time,
                'has_hypertables': has_hypertables,
                'table_count': len(stats.get('table_sizes', [])),
                'recommendations': [
                    'Ensure TimescaleDB extension is enabled',
                    'Monitor database growth and performance'
                ] if not has_hypertables else []
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': str(e),
                'recommendations': ['Check database connection string', 'Verify PostgreSQL is running']
            }
    
    async def check_exchange_connections(self) -> Dict:
        """Verify exchange API connectivity"""
        try:
            from execution.exchange_connector import ExchangeConnector
            
            connector = ExchangeConnector()
            exchanges = ['binance', 'coinbase', 'kraken']
            results = {}
            
            for exchange in exchanges:
                try:
                    # Test connectivity with minimal API call
                    status = await connector.test_connection(exchange)
                    results[exchange] = {
                        'connected': status.get('connected', False),
                        'latency_ms': status.get('latency', 0)
                    }
                except Exception as e:
                    results[exchange] = {
                        'connected': False,
                        'error': str(e)
                    }
            
            all_connected = all(result['connected'] for result in results.values())
            avg_latency = sum(
                result.get('latency_ms', 1000) for result in results.values() 
                if result.get('connected', False)
            ) / max(1, sum(1 for r in results.values() if r.get('connected', False)))
            
            return {
                'passed': all_connected and avg_latency < 500,
                'exchange_status': results,
                'average_latency_ms': avg_latency,
                'recommendations': [
                    'Check API keys and permissions',
                    'Monitor exchange rate limits'
                ] if not all_connected else []
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': str(e),
                'recommendations': ['Verify exchange connector configuration']
            }
    
    async def check_ai_models(self) -> Dict:
        """Verify AI models are loaded and performing correctly"""
        try:
            from core.ai_intelligence import AIIntelligenceEngine
            
            ai_engine = AIIntelligenceEngine()
            model_status = await ai_engine.get_model_status()
            
            all_models_loaded = all(
                status.get('loaded', False) for status in model_status.values()
            )
            
            # Check model performance metrics
            performance_issues = []
            for model_name, status in model_status.items():
                accuracy = status.get('accuracy', 0)
                if accuracy < 0.7:  # 70% accuracy threshold
                    performance_issues.append(f"{model_name} accuracy: {accuracy:.2%}")
            
            return {
                'passed': all_models_loaded and not performance_issues,
                'models_loaded': all_models_loaded,
                'model_details': model_status,
                'performance_issues': performance_issues,
                'recommendations': [
                    'Retrain underperforming models',
                    'Update training data'
                ] if performance_issues else []
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': str(e),
                'recommendations': ['Check AI model paths and dependencies']
            }
    
    async def check_risk_limits(self) -> Dict:
        """Verify risk management system"""
        try:
            from risk.risk_manager import RiskManager
            
            risk_manager = RiskManager()
            limits_status = await risk_manager.get_limits_status()
            
            all_limits_ok = all(
                not limit.get('violated', False) for limit in limits_status.values()
            )
            
            current_exposure = await risk_manager.get_current_exposure()
            exposure_ok = current_exposure.get('total_exposure', 0) < 10000  # $10k limit
            
            return {
                'passed': all_limits_ok and exposure_ok,
                'limits_status': limits_status,
                'current_exposure': current_exposure,
                'recommendations': [
                    'Review risk limits configuration',
                    'Monitor exposure levels'
                ] if not all_limits_ok else []
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': str(e),
                'recommendations': ['Verify risk management configuration']
            }
    
    async def check_performance_metrics(self) -> Dict:
        """Verify system performance metrics"""
        try:
            from monitoring.performance_tracker import PerformanceTracker
            
            tracker = PerformanceTracker()
            metrics = await tracker.get_system_metrics()
            
            # Check critical performance thresholds
            execution_latency = metrics.get('avg_execution_latency_ms', 1000)
            success_rate = metrics.get('success_rate', 0)
            system_uptime = metrics.get('uptime_percentage', 0)
            
            latency_ok = execution_latency < 100  # 100ms threshold
            success_ok = success_rate > 0.8  # 80% success rate
            uptime_ok = system_uptime > 0.99  # 99% uptime
            
            return {
                'passed': latency_ok and success_ok and uptime_ok,
                'execution_latency_ms': execution_latency,
                'success_rate': success_rate,
                'uptime_percentage': system_uptime,
                'recommendations': [
                    'Optimize execution pipeline',
                    'Review failed trade analysis',
                    'Check system resource usage'
                ] if not (latency_ok and success_ok) else []
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': str(e),
                'recommendations': ['Verify performance monitoring setup']
            }
    
    async def check_security_configuration(self) -> Dict:
        """Verify security configuration"""
        try:
            from security.security_manager import SecurityManager
            
            security_mgr = SecurityManager()
            security_status = await security_mgr.get_security_status()
            
            encryption_ok = security_status.get('encryption_enabled', False)
            mfa_ok = security_status.get('mfa_required', False)
            audit_ok = security_status.get('audit_logging', False)
            
            return {
                'passed': encryption_ok and mfa_ok and audit_ok,
                'encryption_enabled': encryption_ok,
                'mfa_required': mfa_ok,
                'audit_logging': audit_ok,
                'recommendations': [
                    'Enable full disk encryption',
                    'Require MFA for all accounts',
                    'Enable comprehensive audit logging'
                ] if not (encryption_ok and mfa_ok and audit_ok) else []
            }
            
        except Exception as e:
            return {
                'passed': False,
                'error': str(e),
                'recommendations': ['Review security configuration']
            }
    
    async def generate_verification_report(self, verification_results: Dict) -> str:
        """Generate human-readable verification report"""
        report = f"""
AI-NEXUS System Verification Report
==================================
Timestamp: {verification_results['timestamp']}
Overall Status: {verification_results['overall_status']}

Detailed Results:
----------------
"""
        
        for check_name, result in verification_results['checks'].items():
            status = "PASS" if result.get('passed', False) else "FAIL"
            report += f"\n{check_name}: {status}"
            
            if not result.get('passed', False):
                report += f"\n  Error: {result.get('error', 'Unknown error')}"
        
        if verification_results['recommendations']:
            report += "\n\nRecommendations:\n----------------"
            for rec in verification_results['recommendations']:
                report += f"\n• {rec}"
        
        return report

# Automated verification scheduler
class VerificationScheduler:
    """Schedule regular system verification"""
    
    def __init__(self, verification_interval: int = 3600):  # 1 hour default
        self.verification_interval = verification_interval
        self.verification_system = SystemVerification()
        self.is_running = False
    
    async def start_scheduled_verification(self):
        """Start scheduled verification"""
        self.is_running = True
        
        while self.is_running:
            try:
                logging.info("Running scheduled system verification...")
                
                results = await self.verification_system.run_full_verification()
                report = await self.verification_system.generate_verification_report(results)
                
                # Log report
                logging.info(f"Verification report:\n{report}")
                
                # Send alerts if verification failed
                if results['overall_status'] == 'FAIL':
                    await self.send_verification_alert(results)
                
                # Store verification results
                await self.store_verification_results(results)
                
            except Exception as e:
                logging.error(f"Scheduled verification failed: {e}")
            
            # Wait for next verification
            await asyncio.sleep(self.verification_interval)
    
    async def send_verification_alert(self, results: Dict):
        """Send verification failure alerts"""
        # Implementation would send alerts via email, Slack, etc.
        logging.warning("System verification failed - sending alerts")
        
        # Example: Send to monitoring system
        from monitoring.alert_manager import AlertManager
        alert_mgr = AlertManager()
        
        await alert_mgr.send_alert(
            level="ERROR",
            title="System Verification Failed",
            message=f"System verification failed with {len(results['recommendations'])} recommendations",
            details=results
        )
    
    async def store_verification_results(self, results: Dict):
        """Store verification results for historical analysis"""
        # Implementation would store in database
        logging.info("Storing verification results")
        
        from database.schemas.TimeSeriesDB import TimeSeriesDB
        db = TimeSeriesDB("postgresql://user:pass@localhost/ainexus")
        
        # Store in system_metrics table
        await db.store_system_metrics([{
            'timestamp': datetime.now(),
            'metric_name': 'verification_status',
            'metric_value': 1 if results['overall_status'] == 'PASS' else 0,
            'tags': {'checks_passed': sum(1 for r in results['checks'].values() if r.get('passed', False))}
        }])

# Example usage
async def main():
    """Run system verification"""
    verification = SystemVerification()
    results = await verification.run_full_verification()
    
    report = await verification.generate_verification_report(results)
    print(report)
    
    # Start scheduled verification
    scheduler = VerificationScheduler(verification_interval=1800)  # 30 minutes
    await scheduler.start_scheduled_verification()

if __name__ == "__main__":
    asyncio.run(main())
