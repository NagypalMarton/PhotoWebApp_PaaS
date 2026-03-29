# Task 2: Load Test Procedure Guide

## Overview
This guide walks through running a comprehensive load test on the PhotoWebApp to verify automatic scaling.

## Prerequisites

### Required Tools
1. **OpenShift CLI** (`oc`) - Installed and authenticated
2. **Locust** - Running in OpenShift (via `locust-openshift.yaml`)
3. **Metrics Server** - Enabled in OpenShift cluster

### Environment Setup
```bash
# Set your project namespace
export NAMESPACE=photowebapp
oc project $NAMESPACE

# Get the frontend route
export FRONTEND_URL=$(oc get route frontend -o jsonpath='{.spec.host}')
echo "Frontend URL: $FRONTEND_URL"

# Get the backend route (for Locust)
export BACKEND_URL="http://backend:5001"
echo "Backend URL: $BACKEND_URL"
```

## Test Configuration

### Locust Settings
| Parameter | Value | Description |
|-----------|-------|-------------|
| **Users** | 20-50 | Virtual users to simulate |
| **Spawn Rate** | 5 users/s | Users per second to spawn |
| **Duration** | 5-10 minutes | Test duration |
| **Host** | `http://backend:5001` | Backend service URL |

### Test Scenario Distribution
| Task | Weight | Percentage | Description |
|------|--------|------------|-------------|
| List by Date | 4 | 29% | GET /api/photos?sort=date |
| View Photo | 3 | 21% | GET /api/photos/{id}/image |
| Upload Photo | 3 | 21% | POST /api/photos |
| List by Name | 2 | 14% | GET /api/photos?sort=name |
| Delete Photo | 1 | 7% | DELETE /api/photos/{id} |
| Health Check | 1 | 7% | GET /api/health |

## Test Execution

### Step 1: Deploy Locust
```bash
# Apply Locust deployment
oc apply -f locust/locust-openshift.yaml

# Wait for Locust pod to be ready
oc wait pod -l app=locust --for=condition=Ready --timeout=60s

# Get Locust web UI URL
export LOCUST_URL=$(oc get route locust -o jsonpath='{.spec.host}')
echo "Locust UI: https://$LOCUST_URL"
```

### Step 2: Monitor Scaling
```bash
# Open a new terminal and run:
oc get hpa -w

# Or watch pod counts:
oc get pods -l app=frontend -w
oc get pods -l app=backend -w
```

### Step 3: Run Test via Web UI
1. Open `https://$LOCUST_URL` in browser
2. Configure test parameters:
   - **Number of users**: 50
   - **Spawn rate**: 5
   - **Host**: `http://backend:5001`
3. Click **Start swarming**
4. Monitor metrics in real-time

### Step 4: Run Test via CLI
```bash
# Execute test from Locust pod
oc exec -it $(oc get pod -l app=locust -o jsonpath='{.items[0].metadata.name}') -- \
  locust --host http://backend:5001 \
         --users 50 \
         --spawn-rate 5 \
         --run-time 600 \
         --headless
```

## Expected Scaling Behavior

### Phase 1: Initial State (0-30s)
```
Frontend: 1 replica
Backend: 1 replica
CPU: ~20-30% per pod
```

### Phase 2: Load Increase (30-120s)
```
Frontend: 1 → 3 replicas (after ~60s)
Backend: 1 → 3 replicas (after ~60s)
CPU: ~60-70% per pod (target: 50%)
```

### Phase 3: Peak Load (120-300s)
```
Frontend: 3 → 5 replicas (after ~90s)
Backend: 3 → 5 replicas (after ~90s)
CPU: ~45-55% per pod (stabilized)
```

### Phase 4: Load Decrease (300-600s)
```
Frontend: 5 → 3 replicas (after ~60s stabilization)
Backend: 5 → 3 replicas (after ~60s stabilization)
CPU: ~30-40% per pod
```

### Phase 5: Steady State (600s+)
```
Frontend: 1 replica (after scale-down)
Backend: 1 replica (after scale-down)
CPU: ~20-30% per pod
```

## Metrics to Collect

### HPA Metrics
```bash
# Before test
oc get hpa

# During test (in another terminal)
watch -n 5 'oc get hpa'

# After test
oc get hpa
```

### Pod Metrics
```bash
# Frontend pod counts
oc get deployment frontend -o jsonpath='{.status.readyReplicas}{"\n"}'

# Backend pod counts
oc get deployment backend -o jsonpath='{.status.readyReplicas}{"\n"}'

# All pods
oc get pods -l app=frontend -o wide
oc get pods -l app=backend -o wide
```

### Resource Usage
```bash
# CPU usage per pod
oc top pods -l app=frontend
oc top pods -l app=backend

# Memory usage per pod
oc top pods -l app=frontend --use-protocol-buffers
oc top pods -l app=backend --use-protocol-buffers
```

### Locust Test Results
```bash
# Get test results from Locust pod
oc exec -it $(oc get pod -l app=locust -o jsonpath='{.items[0].metadata.name}') -- \
  cat /locust_output.csv
```

## Success Criteria

### Scaling Up (Verified)
- [ ] Frontend scales from 1 → 5 replicas under load
- [ ] Backend scales from 1 → 5 replicas under load
- [ ] Scale-up completes within 2-3 minutes
- [ ] CPU utilization stabilizes around 50%

### Scaling Down (Verified)
- [ ] Frontend scales from 5 → 1 replicas after load stops
- [ ] Backend scales from 5 → 1 replicas after load stops
- [ ] Scale-down completes within 2-3 minutes
- [ ] No requests fail during scale events

### Performance (Verified)
- [ ] All API endpoints respond within 2 seconds
- [ ] Error rate < 1%
- [ ] No connection timeouts
- [ ] Database connections remain stable

## Troubleshooting

### Locust Cannot Connect
```bash
# Check Locust pod status
oc get pod -l app=locust

# Check Locust logs
oc logs -l app=locust

# Verify backend service is accessible
oc exec -it $(oc get pod -l app=locust -o jsonpath='{.items[0].metadata.name}') -- \
  nc -zv backend 5001
```

### HPA Not Scaling
```bash
# Check HPA events
oc describe hpa frontend-hpa | grep -A 5 "Events:"

# Check if metrics-server is running
oc get pods -n openshift-monitoring | grep metrics-server

# Check resource requests
oc get deployment frontend -o jsonpath='{.spec.template.spec.containers[0].resources}'
```

### Pods Failing to Start
```bash
# Check pod events
oc describe pod <pod-name>

# Check pod logs
oc logs <pod-name> -f

# Check PVC status
oc get pvc
```

## Test Report Template

### Test Summary
```
Test Date: _______________
Test Duration: _______________
Users Simulated: _______________
Spawn Rate: _______________
```

### Scaling Results
| Component | Initial | Peak | Final | Scale-up Time | Scale-down Time |
|-----------|---------|------|-------|---------------|-----------------|
| Frontend | 1 | 5 | 1 | _______ | _______ |
| Backend | 1 | 5 | 1 | _______ | _______ |

### Performance Metrics
| Metric | Value | Status |
|--------|-------|--------|
| Avg Response Time | _______ | < 2s ✓ |
| Error Rate | _______ | < 1% ✓ |
| Max CPU Usage | _______ | < 70% ✓ |
| Database Connections | _______ | Stable ✓ |

### Screenshots
- [ ] HPA scaling graph
- [ ] Pod count graph
- [ ] Locust test results
- [ ] Resource usage graph

### Conclusion
- [ ] Scaling up verified
- [ ] Scaling down verified
- [ ] Performance requirements met
- [ ] No critical errors