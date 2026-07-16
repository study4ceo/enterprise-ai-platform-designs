#!/bin/bash
# Kubernetes Deployment Script for AI SRE Stack
# This script automates the deployment process

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="ai-sre-stack"
DEPLOYMENT_NAME="ai-sre-orchestrator"
IMAGE_REGISTRY="${IMAGE_REGISTRY:-your-registry}"
IMAGE_NAME="${IMAGE_NAME:-ai-sre-stack}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
FULL_IMAGE="${IMAGE_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"

# Functions
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl not found. Please install kubectl."
        exit 1
    fi
    print_success "kubectl found: $(kubectl version --client --short 2>/dev/null || echo 'installed')"
    
    # Check cluster connection
    if ! kubectl cluster-info &> /dev/null; then
        print_error "Cannot connect to Kubernetes cluster. Check your kubeconfig."
        exit 1
    fi
    print_success "Connected to cluster: $(kubectl config current-context)"
    
    # Check if running from k8s directory
    if [ ! -f "namespace.yaml" ]; then
        print_error "Please run this script from the k8s/ directory"
        exit 1
    fi
    print_success "Running from k8s directory"
}

create_namespace() {
    print_header "Step 1: Creating Namespace"
    
    if kubectl get namespace $NAMESPACE &> /dev/null; then
        print_warning "Namespace $NAMESPACE already exists"
    else
        kubectl apply -f namespace.yaml
        print_success "Namespace $NAMESPACE created"
    fi
}

setup_secrets() {
    print_header "Step 2: Setting Up Secrets"
    
    print_warning "IMPORTANT: You must configure secrets before deployment!"
    print_info "Options:"
    print_info "  1. Edit secrets.yaml and apply it (NOT recommended for production)"
    print_info "  2. Use Sealed Secrets (recommended)"
    print_info "  3. Use External Secrets Operator"
    print_info "  4. Use cloud provider secrets (AWS/Azure/GCP)"
    
    read -p "Have you configured secrets? (yes/no): " secrets_ready
    
    if [ "$secrets_ready" != "yes" ]; then
        print_error "Please configure secrets before continuing"
        print_info "See k8s/README.md for instructions"
        exit 1
    fi
    
    if kubectl get secret ai-sre-secrets -n $NAMESPACE &> /dev/null; then
        print_success "Secret ai-sre-secrets found"
    else
        print_warning "Secret ai-sre-secrets not found"
        read -p "Apply secrets.yaml? (yes/no): " apply_secrets
        if [ "$apply_secrets" == "yes" ]; then
            kubectl apply -f secrets.yaml
            print_success "Secrets applied"
        else
            print_error "Secrets required. Exiting."
            exit 1
        fi
    fi
}

apply_configmap() {
    print_header "Step 3: Applying ConfigMap"
    
    kubectl apply -f configmap.yaml
    print_success "ConfigMap applied"
}

setup_rbac() {
    print_header "Step 4: Setting Up RBAC"
    
    kubectl apply -f rbac.yaml
    print_success "ServiceAccount, ClusterRole, and ClusterRoleBinding created"
}

create_storage() {
    print_header "Step 5: Creating Storage"
    
    kubectl apply -f pvc.yaml
    print_success "PersistentVolumeClaims created"
    
    # Wait for PVCs to be bound
    print_info "Waiting for PVCs to be bound..."
    kubectl wait --for=condition=Bound pvc/audit-logs-pvc -n $NAMESPACE --timeout=60s || true
}

update_deployment_image() {
    print_header "Step 6: Updating Deployment Image"
    
    print_info "Current image in deployment.yaml:"
    grep "image:" deployment.yaml | head -1
    
    print_info "Updating to: $FULL_IMAGE"
    
    # Create backup
    cp deployment.yaml deployment.yaml.bak
    
    # Update image
    sed -i.tmp "s|image:.*|image: $FULL_IMAGE|g" deployment.yaml
    rm -f deployment.yaml.tmp
    
    print_success "Deployment image updated"
}

deploy_application() {
    print_header "Step 7: Deploying Application"
    
    kubectl apply -f deployment.yaml
    print_success "Deployment created"
    
    # Wait for deployment
    print_info "Waiting for deployment to be ready..."
    kubectl wait --for=condition=available --timeout=300s \
        deployment/$DEPLOYMENT_NAME -n $NAMESPACE || true
    
    # Check status
    kubectl get deployment $DEPLOYMENT_NAME -n $NAMESPACE
}

deploy_service() {
    print_header "Step 8: Creating Service (Optional)"
    
    read -p "Deploy service for metrics/webhooks? (yes/no): " deploy_svc
    
    if [ "$deploy_svc" == "yes" ]; then
        kubectl apply -f service.yaml
        print_success "Service created"
    else
        print_info "Skipping service creation"
    fi
}

verify_deployment() {
    print_header "Verifying Deployment"
    
    print_info "All resources in namespace:"
    kubectl get all -n $NAMESPACE
    
    echo ""
    print_info "Pod status:"
    kubectl get pods -n $NAMESPACE
    
    echo ""
    print_info "Deployment status:"
    kubectl describe deployment $DEPLOYMENT_NAME -n $NAMESPACE | grep -A 5 "Conditions:"
}

show_logs() {
    print_header "Showing Recent Logs"
    
    print_info "Last 20 lines of logs:"
    kubectl logs deployment/$DEPLOYMENT_NAME -n $NAMESPACE --tail=20 || \
        print_warning "Could not fetch logs yet. Pod may still be starting."
}

print_next_steps() {
    print_header "Deployment Complete!"
    
    print_success "AI SRE Stack deployed successfully to $NAMESPACE namespace"
    
    echo ""
    print_info "Next Steps:"
    echo "  1. Check logs:"
    echo "     kubectl logs -f deployment/$DEPLOYMENT_NAME -n $NAMESPACE"
    echo ""
    echo "  2. Check status:"
    echo "     kubectl get pods -n $NAMESPACE"
    echo ""
    echo "  3. Describe pod:"
    echo "     kubectl describe pod -l app=$DEPLOYMENT_NAME -n $NAMESPACE"
    echo ""
    echo "  4. Access pod shell:"
    echo "     kubectl exec -it deployment/$DEPLOYMENT_NAME -n $NAMESPACE -- bash"
    echo ""
    echo "  5. View audit logs:"
    echo "     kubectl exec deployment/$DEPLOYMENT_NAME -n $NAMESPACE -- cat /app/logs/audit.jsonl"
    echo ""
    echo "  6. Update config:"
    echo "     kubectl edit configmap ai-sre-config -n $NAMESPACE"
    echo "     kubectl rollout restart deployment/$DEPLOYMENT_NAME -n $NAMESPACE"
    echo ""
    echo "  7. Scale:"
    echo "     kubectl scale deployment/$DEPLOYMENT_NAME -n $NAMESPACE --replicas=3"
    echo ""
    
    print_info "Documentation:"
    echo "  - Full guide: ../DEPLOYMENT_GUIDE.md"
    echo "  - K8s guide: ./README.md"
    echo "  - Testing: ../QUICK_TEST_INSTRUCTIONS.md"
}

cleanup() {
    print_header "Cleanup"
    
    # Restore backup if exists
    if [ -f "deployment.yaml.bak" ]; then
        mv deployment.yaml.bak deployment.yaml
        print_info "Restored deployment.yaml from backup"
    fi
}

# Main execution
main() {
    print_header "AI SRE Stack - Kubernetes Deployment"
    
    print_info "Deploying to namespace: $NAMESPACE"
    print_info "Using image: $FULL_IMAGE"
    
    echo ""
    read -p "Continue with deployment? (yes/no): " continue_deploy
    
    if [ "$continue_deploy" != "yes" ]; then
        print_info "Deployment cancelled"
        exit 0
    fi
    
    # Run deployment steps
    check_prerequisites
    create_namespace
    setup_secrets
    apply_configmap
    setup_rbac
    create_storage
    update_deployment_image
    deploy_application
    deploy_service
    verify_deployment
    show_logs
    print_next_steps
    
    cleanup
}

# Trap errors
trap cleanup EXIT

# Run main
main
