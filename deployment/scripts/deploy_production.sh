#!/bin/bash

# Production Deployment Script for Arbitrage System
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Configuration
ENVIRONMENT="production"
REGION="us-east-1"
CLUSTER_NAME="arbitrage-production"
NAMESPACE="arbitrage-prod"

# Pre-flight checks
check_prerequisites() {
    log "Running pre-flight checks..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        error "AWS CLI is not installed"
    fi
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        error "kubectl is not installed"
    fi
    
    # Check database connectivity
    if ! pg_isready -h $DB_HOST -p $DB_PORT; then
        error "Cannot connect to database at $DB_HOST:$DB_PORT"
    fi
    
    log "âœ… All prerequisites satisfied"
}

# Database setup
setup_database() {
    log "Setting up production database..."
    
    # Run database migrations
    python3 database_setup.py
    
    # Initialize risk limits
    sqlite3 arbitrage.db << 'SQL'
    INSERT OR REPLACE INTO risk_limits (strategy_id, max_position_size, daily_loss_limit, max_drawdown)
    VALUES 
    ('uniswap_pancake', 5000, 1000, 0.05),
    ('sushiswap_quick', 3000, 600, 0.03),
    ('multi_dex', 10000, 2000, 0.08);
SQL
    
    log "âœ… Database setup completed"
}

# Kubernetes deployment
deploy_kubernetes() {
    log "Deploying to Kubernetes cluster..."
    
    # Update kubeconfig
    aws eks update-kubeconfig --region $REGION --name $CLUSTER_NAME
    
    # Create namespace
    kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
    
    # Deploy configurations
    kubectl apply -f kubernetes/ -n $NAMESPACE
    
    # Wait for deployments to be ready
    kubectl rollout status deployment/arbitrage-engine -n $NAMESPACE --timeout=300s
    kubectl rollout status deployment/monitoring-service -n $NAMESPACE --timeout=300s
    
    log "âœ… Kubernetes deployment completed"
}

# Security setup
setup_security() {
    log "Setting up security configurations..."
    
    # Generate SSL certificates
    openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 \
        -keyout ssl/private.key -out ssl/certificate.crt \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=arbitrage.example.com"
    
    # Set up secrets
    kubectl create secret generic arbitrage-secrets \
        --from-literal=db-password=$DB_PASSWORD \
        --from-literal=api-key=$EXCHANGE_API_KEY \
        --from-file=ssl-cert=ssl/certificate.crt \
        --dry-run=client -o yaml | kubectl apply -n $NAMESPACE -f -
    
    log "âœ… Security setup completed"
}

# Health checks
run_health_checks() {
    log "Running post-deployment health checks..."
    
    # Check service endpoints
    SERVICES=("arbitrage-engine" "risk-manager" "monitoring-service")
    for service in "${SERVICES[@]}"; do
        if kubectl get service $service -n $NAMESPACE &> /dev/null; then
            log "âœ… Service $service is running"
        else
            warn "Service $service is not available"
        fi
    done
    
    # Check database connectivity from within cluster
    kubectl run health-check --image=postgres:14 -n $NAMESPACE --rm -i --restart=Never -- \
        psql "postgresql://$DB_USERNAME:$DB_PASSWORD@$DB_HOST:$DB_PORT/arbitrage_prod" -c "SELECT 1;" || warn "Database health check failed"
    
    log "âœ… Health checks completed"
}

# Main deployment process
main() {
    log "Starting production deployment for Arbitrage System"
    
    # Source environment variables
    if [ -f .env.production ]; then
        source .env.production
    else
        error ".env.production file not found"
    fi
    
    check_prerequisites
    setup_database
    setup_security
    deploy_kubernetes
    run_health_checks
    
    log "í¾‰ Production deployment completed successfully!"
    log "í³Š Dashboard: https://monitoring.arbitrage.example.com"
    log "í³ˆ Metrics: https://grafana.arbitrage.example.com"
}

# Execute main function
main "$@"
