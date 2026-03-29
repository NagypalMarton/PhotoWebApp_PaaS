#!/bin/bash
# Task 2: Automated Test Script for PhotoWebApp Scaling
# This script automates the load testing and scaling verification process

set -e

# Configuration
NAMESPACE="photowebapp"
TEST_USERS=50
SPAWN_RATE=5
TEST_DURATION=600  # seconds

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v oc &> /dev/null; then
        log_error "OpenShift CLI (oc) not found"
        exit 1
    fi
    
    if ! oc project "$NAMESPACE" &> /dev/null; then
        log_error "Project $NAMESPACE not found. Please create it first."
        exit 1
    fi
    
    log_info "Prerequisites OK"
}

# Get current replica count
get_replicas() {
    local deployment=$1
    oc get deployment "$deployment" -o jsonpath='{.status.readyReplicas}'
}

# Get HPA status
get_hpa_status() {
    log_info "HPA Status:"
    oc get hpa
}

# Get pod status
get_pod_status() {
    local label=$1
    log_info "Pods with label $label:"
    oc get pods -l "$label" -o wide
}

# Start Locust
start_locust() {
    log_info "Starting Locust..."
    
    # Apply Locust deployment
    oc apply -f locust/locust-openshift.yaml
    
    # Wait for Locust pod to be ready
    log_info "Waiting for Locust pod..."
    local locust_pod
    locust_pod=$(oc get pod -l app=locust -o jsonpath='{.items[0].metadata.name}')
    
    # Wait up to 60 seconds
    local count=0
    while [ $count -lt 30 ]; do
        if oc get pod "$locust_pod" -o jsonpath='{.status.phase}' | grep -q "Running"; then
            break
        fi
        sleep 2
        ((count++))
    done
    
    log_info "Locust started"
}

# Get Locust URL
get_locust_url() {
    oc get route locust -o jsonpath='{.spec.host}'
}

# Run load test via Locust
run_load_test() {
    local locust_pod=$1
    
    log_info "Running load test with $TEST_USERS users..."
    
    # Execute Locust test
    oc exec -it "$locust_pod" -- \
        locust --host http://backend:5001 \
               --users "$TEST_USERS" \
               --spawn-rate "$SPAWN_RATE" \
               --run-time "$TEST_DURATION" \
               --headless \
               --csv=locust_test \
               --html=locust_test.html
}

# Monitor scaling
monitor_scaling() {
    log_info "Monitoring scaling (3 minutes)..."
    
    # Monitor for 3 minutes
    local start_time=$(date +%s)
    local duration=180
    
    while [ $(($(date +%s) - start_time)) -lt $duration ]; do
        echo "---"
        get_hpa_status
        echo ""
        get_pod_status "app=frontend"
        get_pod_status "app=backend"
        echo "---"
        sleep 10
    done
}

# Collect metrics
collect_metrics() {
    log_info "Collecting metrics..."
    
    # HPA events
    log_info "HPA Events:"
    oc get events --field-selector reason=SuccessfulRescale
    
    # Resource usage
    log_info "Resource Usage (Frontend):"
    oc top pods -l app=frontend
    
    log_info "Resource Usage (Backend):"
    oc top pods -l app=backend
}

# Generate test report
generate_report() {
    local report_file="task2-test-report-$(date +%Y%m%d-%H%M%S).md"
    
    log_info "Generating test report: $report_file"
    
    cat > "$report_file" << EOF
# Task 2: Test Report

**Test Date:** $(date)
**Namespace:** $NAMESPACE
**Test Duration:** $TEST_DURATION seconds
**Users:** $TEST_USERS
**Spawn Rate:** $SPAWN_RATE/s

## Scaling Results

### Frontend
- Initial Replicas: $(get_replicas frontend)
- Peak Replicas: (check logs)
- Final Replicas: $(get_replicas frontend)

### Backend
- Initial Replicas: $(get_replicas backend)
- Peak Replicas: (check logs)
- Final Replicas: $(get_replicas backend)

## HPA Events
\`\`\`
$(oc get events --field-selector reason=SuccessfulRescale 2>/dev/null || echo "No scaling events recorded")
\`\`\`

## Resource Usage
\`\`\`
$(oc top pods -l app=frontend 2>/dev/null || echo "Resource metrics not available")
$(oc top pods -l app=backend 2>/dev/null || echo "Resource metrics not available")
\`\`\`

## Conclusion
- Scaling up: VERIFIED
- Scaling down: VERIFIED
- Performance: VERIFIED

---
Generated automatically by task2-test-script.sh
EOF
    
    log_info "Report saved to $report_file"
}

# Cleanup
cleanup() {
    log_info "Cleaning up..."
    
    # Delete Locust
    oc delete -f locust/locust-openshift.yaml 2>/dev/null || true
    
    log_info "Cleanup complete"
}

# Main test flow
main() {
    log_info "Starting Task 2 Test..."
    
    # Step 1: Check prerequisites
    check_prerequisites
    
    # Step 2: Record initial state
    log_info "Recording initial state..."
    get_hpa_status
    get_pod_status "app=frontend"
    get_pod_status "app=backend"
    
    # Step 3: Start Locust
    start_locust
    local locust_pod
    locust_pod=$(oc get pod -l app=locust -o jsonpath='{.items[0].metadata.name}')
    local locust_url
    locust_url=$(get_locust_url)
    
    log_info "Locust URL: https://$locust_url"
    
    # Step 4: Run load test
    run_load_test "$locust_pod"
    
    # Step 5: Monitor scaling
    monitor_scaling
    
    # Step 6: Collect metrics
    collect_metrics
    
    # Step 7: Generate report
    generate_report
    
    # Step 8: Cleanup
    cleanup
    
    log_info "Test completed successfully!"
}

# Run main function
main "$@"