#!/bin/bash

# LangFlow Connect - Deployment Script
# Automated deployment for different environments

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENVIRONMENT=${1:-development}
ACTION=${2:-deploy}

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

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is not installed"
    fi
    
    # Check pip
    if ! command -v pip &> /dev/null; then
        error "pip is not installed"
    fi
    
    # Check git
    if ! command -v git &> /dev/null; then
        error "git is not installed"
    fi
    
    log "Prerequisites check passed"
}

# Setup Python environment
setup_python_env() {
    log "Setting up Python environment..."
    
    cd "$PROJECT_ROOT"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        log "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install dependencies
    log "Installing dependencies..."
    pip install -r requirements.txt
    
    # Install optional dependencies
    if [ "$ENVIRONMENT" = "production" ]; then
        pip install asyncpg
    fi
    
    log "Python environment setup complete"
}

# Setup environment variables
setup_env() {
    log "Setting up environment variables..."
    
    cd "$PROJECT_ROOT"
    
    # Copy environment template if it doesn't exist
    if [ ! -f ".env" ]; then
        if [ -f "env.example" ]; then
            cp env.example .env
            warn "Created .env from template. Please edit with your configuration."
        else
            error "No environment template found"
        fi
    fi
    
    log "Environment setup complete"
}

# Run tests
run_tests() {
    log "Running tests..."
    
    cd "$PROJECT_ROOT"
    source venv/bin/activate
    
    # Run basic functionality test
    if python clean_demo.py; then
        log "Basic functionality test passed"
    else
        error "Basic functionality test failed"
    fi
    
    # Run simple test
    if python simple_test.py; then
        log "Simple test passed"
    else
        error "Simple test failed"
    fi
    
    log "All tests passed"
}

# Deploy to development
deploy_development() {
    log "Deploying to development environment..."
    
    cd "$PROJECT_ROOT"
    source venv/bin/activate
    
    # Create necessary directories
    mkdir -p logs data cache
    
    # Test the system
    run_tests
    
    log "Development deployment complete"
    log "To start the system, run: python -m src.system_coordinator"
}

# Deploy to production
deploy_production() {
    log "Deploying to production environment..."
    
    # Check if running as root for systemd setup
    if [ "$EUID" -ne 0 ]; then
        error "Production deployment requires root privileges"
    fi
    
    cd "$PROJECT_ROOT"
    
    # Create system user
    if ! id "langflow" &>/dev/null; then
        log "Creating langflow user..."
        useradd -r -s /bin/false -d /opt/langflow-connect langflow
    fi
    
    # Create installation directory
    mkdir -p /opt/langflow-connect
    
    # Copy files
    cp -r * /opt/langflow-connect/
    chown -R langflow:langflow /opt/langflow-connect
    
    # Setup Python environment
    cd /opt/langflow-connect
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install asyncpg
    
    # Setup systemd service
    cp deployment/systemd/langflow-connect.service /etc/systemd/system/
    systemctl daemon-reload
    systemctl enable langflow-connect
    
    # Start service
    systemctl start langflow-connect
    
    log "Production deployment complete"
    log "Service status: systemctl status langflow-connect"
}

# Deploy with Docker
deploy_docker() {
    log "Deploying with Docker..."
    
    cd "$PROJECT_ROOT"
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
    fi
    
    # Build and start containers
    cd deployment/docker
    docker-compose up -d --build
    
    log "Docker deployment complete"
    log "Check status: docker-compose ps"
}

# Deploy to Kubernetes
deploy_kubernetes() {
    log "Deploying to Kubernetes..."
    
    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        error "kubectl is not installed"
    fi
    
    cd "$PROJECT_ROOT/deployment/kubernetes"
    
    # Create namespace
    kubectl apply -f namespace.yaml
    
    # Create secrets
    kubectl apply -f secret.yaml
    
    # Deploy application
    kubectl apply -f deployment.yaml
    
    log "Kubernetes deployment complete"
    log "Check status: kubectl get pods -n langflow-system"
}

# Backup existing installation
backup_existing() {
    log "Creating backup of existing installation..."
    
    BACKUP_DIR="/backup/langflow-connect/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    if [ -d "/opt/langflow-connect" ]; then
        cp -r /opt/langflow-connect/* "$BACKUP_DIR/"
        log "Backup created: $BACKUP_DIR"
    else
        warn "No existing installation found to backup"
    fi
}

# Rollback deployment
rollback() {
    log "Rolling back deployment..."
    
    # Find latest backup
    LATEST_BACKUP=$(ls -t /backup/langflow-connect/ | head -1)
    
    if [ -z "$LATEST_BACKUP" ]; then
        error "No backup found for rollback"
    fi
    
    BACKUP_PATH="/backup/langflow-connect/$LATEST_BACKUP"
    
    # Stop service
    systemctl stop langflow-connect
    
    # Restore from backup
    rm -rf /opt/langflow-connect
    cp -r "$BACKUP_PATH" /opt/langflow-connect
    
    # Restart service
    systemctl start langflow-connect
    
    log "Rollback complete from: $BACKUP_PATH"
}

# Health check
health_check() {
    log "Performing health check..."
    
    # Check if service is running
    if systemctl is-active --quiet langflow-connect; then
        log "Service is running"
    else
        error "Service is not running"
    fi
    
    # Check logs for errors
    if journalctl -u langflow-connect --since "5 minutes ago" | grep -i error; then
        warn "Errors found in recent logs"
    else
        log "No errors in recent logs"
    fi
    
    log "Health check complete"
}

# Main deployment logic
main() {
    log "Starting LangFlow Connect deployment..."
    log "Environment: $ENVIRONMENT"
    log "Action: $ACTION"
    
    case "$ACTION" in
        "deploy")
            check_prerequisites
            setup_python_env
            setup_env
            
            case "$ENVIRONMENT" in
                "development")
                    deploy_development
                    ;;
                "production")
                    backup_existing
                    deploy_production
                    health_check
                    ;;
                "docker")
                    deploy_docker
                    ;;
                "kubernetes")
                    deploy_kubernetes
                    ;;
                *)
                    error "Unknown environment: $ENVIRONMENT"
                    ;;
            esac
            ;;
        "rollback")
            rollback
            health_check
            ;;
        "test")
            check_prerequisites
            setup_python_env
            run_tests
            ;;
        "health")
            health_check
            ;;
        *)
            error "Unknown action: $ACTION"
            ;;
    esac
    
    log "Deployment completed successfully!"
}

# Show usage
usage() {
    echo "Usage: $0 [environment] [action]"
    echo ""
    echo "Environments:"
    echo "  development  - Local development setup"
    echo "  production   - Production server deployment"
    echo "  docker       - Docker container deployment"
    echo "  kubernetes   - Kubernetes cluster deployment"
    echo ""
    echo "Actions:"
    echo "  deploy       - Deploy the application (default)"
    echo "  rollback     - Rollback to previous version"
    echo "  test         - Run tests only"
    echo "  health       - Perform health check"
    echo ""
    echo "Examples:"
    echo "  $0 development deploy"
    echo "  $0 production deploy"
    echo "  $0 docker deploy"
    echo "  $0 kubernetes deploy"
    echo "  $0 production rollback"
    echo "  $0 production health"
}

# Check if help is requested
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    usage
    exit 0
fi

# Run main function
main "$@" 