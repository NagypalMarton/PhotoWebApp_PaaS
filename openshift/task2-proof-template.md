# Task 2: Proof of Scaling Template

## Proof of Scaling - PhotoWebApp

**Test Date:** _______________
**Namespace:** photowebapp
**Test Duration:** _______________

---

## 1. Scaling Up Verification

### Before Test (Initial State)
```
$ oc get hpa
NAME             REFERENCE                   TARGETS   MINPODS   MAXPODS   REPLICAS   AGE
frontend-hpa     Deployment/frontend         20%/50%   1         5         1          5m
backend-hpa      Deployment/backend          15%/50%   1         5         1          5m

$ oc get pods -l app=frontend -o wide
NAME                          READY   STATUS    RESTARTS   AGE   IP           NODE
frontend-7d9f8b6c5-x2k4p      1/1     Running   0          5m    10.128.0.5   worker-0

$ oc get pods -l app=backend -o wide
NAME                          READY   STATUS    RESTARTS   AGE   IP           NODE
backend-6f8c7d9b4-m3n5o       1/1     Running   0          5m    10.128.0.6   worker-0
```

### During Test (Peak Load)
```
$ oc get hpa
NAME             REFERENCE                   TARGETS   MINPODS   MAXPODS   REPLICAS   AGE
frontend-hpa     Deployment/frontend         52%/50%   1         5         5          10m
backend-hpa      Deployment/backend          48%/50%   1         5         5          10m

$ oc get pods -l app=frontend -o wide
NAME                          READY   STATUS    RESTARTS   AGE   IP           NODE
frontend-7d9f8b6c5-x2k4p      1/1     Running   0          10m   10.128.0.5   worker-0
frontend-7d9f8b6c5-a8b2c      1/1     Running   0          2m    10.128.0.7   worker-1
frontend-7d9f8b6c5-d4e5f      1/1     Running   0          2m    10.128.0.8   worker-1
frontend-7d9f8b6c5-g6h7i      1/1     Running   0          1m    10.128.0.9   worker-2
frontend-7d9f8b6c5-j8k9l      1/1     Running   0          1m    10.128.0.10  worker-2

$ oc get pods -l app=backend -o wide
NAME                          READY   STATUS    RESTARTS   AGE   IP           NODE
backend-6f8c7d9b4-m3n5o       1/1     Running   0          10m   10.128.0.6   worker-0
backend-6f8c7d9b4-p1q2r       1/1     Running   0          2m    10.128.0.11  worker-1
backend-6f8c7d9b4-s3t4u       1/1     Running   0          2m    10.128.0.12  worker-1
backend-6f8c7d9b4-v5w6x       1/1     Running   0          1m    10.128.0.13  worker-2
backend-6f8c7d9b4-y7z8a       1/1     Running   0          1m    10.128.0.14  worker-2
```

### Scaling Events
```
$ oc get events --field-selector reason=SuccessfulRescale
LAST SEEN   TYPE     REASON              OBJECT              MESSAGE
2m          Normal   SuccessfulRescale   hpa/frontend-hpa    New size: 3; reason: current CPU utilization 65% > target 50%
1m          Normal   SuccessfulRescale   hpa/frontend-hpa    New size: 5; reason: current CPU utilization 60% > target 50%
2m          Normal   SuccessfulRescale   hpa/backend-hpa     New size: 3; reason: current CPU utilization 55% > target 50%
1m          Normal   SuccessfulRescale   hpa/backend-hpa     New size: 5; reason: current CPU utilization 52% > target 50%
```

---

## 2. Scaling Down Verification

### After Test (Load Decreased)
```
$ oc get hpa
NAME             REFERENCE                   TARGETS   MINPODS   MAXPODS   REPLICAS   AGE
frontend-hpa     Deployment/frontend         25%/50%   1         5         3          15m
backend-hpa      Deployment/backend          20%/50%   1         5         3          15m

$ oc get pods -l app=frontend -o wide
NAME                          READY   STATUS    RESTARTS   AGE   IP           NODE
frontend-7d9f8b6c5-x2k4p      1/1     Running   0          15m   10.128.0.5   worker-0
frontend-7d9f8b6c5-a8b2c      1/1     Running   0          7m    10.128.0.7   worker-1
frontend-7d9f8b6c5-d4e5f      1/1     Running   0          7m    10.128.0.8   worker-1

$ oc get pods -l app=backend -o wide
NAME                          READY   STATUS    RESTARTS   AGE   IP           NODE
backend-6f8c7d9b4-m3n5o       1/1     Running   0          15m   10.128.0.6   worker-0
backend-6f8c7d9b4-p1q2r       1/1     Running   0          7m    10.128.0.11  worker-1
backend-6f8c7d9b4-s3t4u       1/1     Running   0          7m    10.128.0.12  worker-1
```

### Final State (Stable)
```
$ oc get hpa
NAME             REFERENCE                   TARGETS   MINPODS   MAXPODS   REPLICAS   AGE
frontend-hpa     Deployment/frontend         22%/50%   1         5         1          20m
backend-hpa      Deployment/backend          18%/50%   1         5         1          20m

$ oc get pods -l app=frontend -o wide
NAME                          READY   STATUS    RESTARTS   AGE   IP           NODE
frontend-7d9f8b6c5-x2k4p      1/1     Running   0          20m   10.128.0.5   worker-0

$ oc get pods -l app=backend -o wide
NAME                          READY   STATUS    RESTARTS   AGE   IP           NODE
backend-6f8c7d9b4-m3n5o       1/1     Running   0          20m   10.128.0.6   worker-0
```

### Scale-Down Events
```
$ oc get events --field-selector reason=SuccessfulRescale
LAST SEEN   TYPE     REASON              OBJECT              MESSAGE
5m          Normal   SuccessfulRescale   hpa/frontend-hpa    New size: 3; reason: current CPU utilization 45% < target 50%
3m          Normal   SuccessfulRescale   hpa/frontend-hpa    New size: 1; reason: current CPU utilization 25% < target 50%
5m          Normal   SuccessfulRescale   hpa/backend-hpa     New size: 3; reason: current CPU utilization 40% < target 50%
3m          Normal   SuccessfulRescale   hpa/backend-hpa     New size: 1; reason: current CPU utilization 20% < target 50%
```

---

## 3. Performance Metrics

### Locust Test Results
```
Test Configuration:
  Users: 50
  Spawn Rate: 5 users/s
  Duration: 600 seconds

Results Summary:
  Start Time: _______________
  End Time: _______________
  
  Requests:
    Total: 12,450
    OK: 12,420 (99.76%)
    KO: 30 (0.24%)
    
  Average Response Time: 450ms
  Max Response Time: 2,100ms
  Min Response Time: 50ms
  
  Current RPS: 25
  Current Users: 0
```

### API Endpoint Performance
| Endpoint | Total Requests | Avg Response Time | Success Rate |
|----------|----------------|-------------------|--------------|
| GET /api/health | 1,200 | 25ms | 100% |
| GET /api/photos?sort=date | 4,500 | 180ms | 99.8% |
| GET /api/photos?sort=name | 2,200 | 165ms | 99.9% |
| POST /api/photos | 3,000 | 850ms | 99.5% |
| GET /api/photos/{id} | 2,800 | 95ms | 100% |
| DELETE /api/photos/{id} | 750 | 120ms | 100% |

---

## 4. Screenshots

### Screenshot 1: HPA Scaling Up
![HPA Scaling Up](screenshot-hpa-scaleup.png)
*Caption: HPA showing scaling from 1 to 5 replicas during load test*

### Screenshot 2: Pod Count During Test
![Pod Count During Test](screenshot-pod-count.png)
*Caption: Frontend and Backend pod counts showing scaling events*

### Screenshot 3: Locust Test Results
![Locust Test Results](screenshot-locust-results.png)
*Caption: Locust web UI showing test results*

### Screenshot 4: Resource Usage
![Resource Usage](screenshot-resource-usage.png)
*Caption: CPU and memory usage per pod during test*

---

## 5. Verification Checklist

### Scaling Up
- [ ] Frontend scaled from 1 → 5 replicas
- [ ] Backend scaled from 1 → 5 replicas
- [ ] Scale-up completed within 2-3 minutes
- [ ] CPU utilization stabilized around 50%
- [ ] No request failures during scale-up

### Scaling Down
- [ ] Frontend scaled from 5 → 1 replicas
- [ ] Backend scaled from 5 → 1 replicas
- [ ] Scale-down completed within 2-3 minutes
- [ ] No request failures during scale-down
- [ ] Stabilization period respected (60s)

### Performance
- [ ] All endpoints responded within 2 seconds
- [ ] Error rate < 1%
- [ ] No connection timeouts
- [ ] Database connections remained stable
- [ ] No data corruption or loss

---

## 6. Conclusion

### Scaling Configuration Verified
- [x] HPA correctly monitors CPU utilization
- [x] Scale-up triggers at 50% CPU threshold
- [x] Scale-down triggers after 60s stabilization
- [x] Maximum replicas (5) reached under load
- [x] Minimum replicas (1) restored after load

### Performance Requirements Met
- [x] Response times within acceptable limits
- [x] Error rate below threshold
- [x] System stable under sustained load
- [x] Automatic scaling functional

### Recommendations
1. Consider using ReadWriteMany storage for shared uploads
2. Monitor database connection pool under higher loads
3. Consider adding memory-based scaling for memory-intensive operations
4. Implement caching for frequently accessed photos

---

**Tested By:** _______________
**Date:** _______________
**Signature:** _______________