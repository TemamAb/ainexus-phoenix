#!/bin/bash

# AI-NEXUS Production Monitoring Script
# Real-time system health and performance monitoring

set -e

# Configuration
PROJECT_NAME="ai-nexus-arbitrage"
NAMESPACE="production"
ALERT_THRESHOLDS=(
    "CPU_USAGE=80"
    "MEMORY_USAGE=85" 
    "DISK_USAGE=90"
    "LATENCY_MS=1000"
    "ERROR_RATE=1"
)

# Monitoring functions
check_system_health() {
    echo "Checking system health..."
    
    # Check Kubernetes cluster
    kubectl cluster-info || {
        echo "ERROR: Kubernetes cluster unavailable"
        return 1
    }
    
    # Check node health
    kubectl get nodes -o wide || {
        echo "ERROR: Cannot retrieve node status"
        return 1
    }
    
    # Check pod status
    local pending_pods=$(kubectl get pods -n $NAMESPACE --field-selector=status.phase=Pending -o name | wc -l)
    if [ "$pending_pods" -gt 0 ]; then
        echo "WARNING: $pending_pods pods in pending state"
    fi
    
    local failed_pods=$(kubectl get pods -n $NAMESPACE --field-selector=status.phase=Failed -o name | wc -l)
    if [ "$failed_pods" -gt 0 ]; then
        echo "ERROR: $failed_pods pods in failed state"
        return 1
    fi
}

check_performance_metrics() {
    echo "Checking performance metrics..."
    
    # Get CPU usage
    local cpu_usage=$(kubectl top pods -n $NAMESPACE --containers | awk '{print $3}' | grep -Eo '[0-9]+' | head -1)
    
    # Get memory usage  
    local memory_usage=$(kubectl top pods -n $NAMESPACE --containers | awk '{print $4}' | grep -Eo '[0-9]+' | head -1)
    
    # Check against thresholds
    if [ "$cpu_usage" -gt 80 ]; then
        echo "WARNING: High CPU usage: ${cpu_usage}%"
    fi
    
    if [ "$memory_usage" -gt 85 ]; then
        echo "WARNING: High memory usage: ${memory_usage}%"
    fi
}

check_application_health() {
    echo "Checking application health..."
    
    # Test API endpoints
    local api_url=$(kubectl get service ai-nexus-router -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
    
    if [ -n "$api_url" ]; then
        local response_time=$(curl -o /dev/null -s -w '%{time_total}\n' "https://$api_url/health")
        local status_code=$(curl -o /dev/null -s -w '%{http_code}\n' "https://$api_url/health")
        
        if [ "$status_code" -ne 200 ]; then
            echo "ERROR: Health check failed with status: $status_code"
            return 1
        fi
        
        if (( $(echo "$response_time > 1.0" | bc -l) )); then
            echo "WARNING: High response time: ${response_time}s"
        fi
    fi
}

check_database_connections() {
    echo "Checking database connections..."
    
    # Check Redis
    kubectl exec -n $NAMESPACE deployment/redis -- redis-cli ping | grep -q PONG || {
        echo "ERROR: Redis connection failed"
        return 1
    }
    
    # Check PostgreSQL
    kubectl exec -n $NAMESPACE deployment/postgres -- pg_isready -U postgres || {
        echo "ERROR: PostgreSQL connection failed"
        return 1
    }
}

check_arbitrage_performance() {
    echo "Checking arbitrage performance..."
    
    # Get recent arbitrage metrics from Prometheus
    local success_rate=$(curl -s "http://prometheus:9090/api/v1/query?query=arbitrage_success_rate" | jq -r '.data.result[0].value[1]')
    local avg_profit=$(curl -s "http://prometheus:9090/api/v1/query?query=arbitrage_avg_profit" | jq -r '.data.result[0].value[1]')
    
    if [ -n "$success_rate" ] && [ "$success_rate" != "null" ]; then
        if (( $(echo "$success_rate < 0.5" | bc -l) )); then
            echo "WARNING: Low arbitrage success rate: $(echo "$success_rate * 100" | bc)%"
        fi
    fi
    
    if [ -n "$avg_profit" ] && [ "$avg_profit" != "null" ]; then
        if (( $(echo "$avg_profit < 0" | bc -l) )); then
            echo "ERROR: Negative average profit: $avg_profit"
            return 1
        fi
    fi
}

generate_monitoring_report() {
    echo "Generating monitoring report..."
    
    local report_file="monitoring/reports/health-$(date +%Y%m%d-%H%M%S).json"
    
    mkdir -p monitoring/reports
    
    kubectl get pods -n $NAMESPACE -o json > monitoring/current_status.json
    
    cat > $report_file << EOL
{
    "timestamp": "$(date -Iseconds)",
    "project": "$PROJECT_NAME",
    "health_checks": {
        "system_health": "healthy",
        "application_health": "healthy", 
        "database_health": "healthy",
        "performance_metrics": "normal"
    },
    "recommendations": []
}
EOL
    
    echo "Monitoring report saved: $report_file"
}

# Continuous monitoring mode
continuous_monitoring() {
    echo "Starting continuous monitoring..."
    
    while true; do
        echo "=== Monitoring Cycle $(date) ==="
        
        check_system_health
        check_performance_metrics
        check_application_health
        check_database_connections
        check_arbitrage_performance
        
        generate_monitoring_report
        
        echo "=== Cycle Complete ==="
        sleep 60  # Check every minute
    done
}

# Main execution
case "${1:-}" in
    "continuous")
        continuous_monitoring
        ;;
    "report")
        check_system_health
        check_performance_metrics
        check_application_health
        check_database_connections
        check_arbitrage_performance
        generate_monitoring_report
        ;;
    *)
        echo "Usage: $0 {continuous|report}"
        exit 1
        ;;
esac
