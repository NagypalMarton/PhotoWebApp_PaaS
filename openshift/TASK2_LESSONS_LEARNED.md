# Task 2: Lessons Learned

## Overview

This document captures the key learnings from implementing automatic scaling and load testing for the PhotoWebApp on OpenShift.

## Scaling Configuration

### What We Learned

1. **Resource Requests Matter**
   - Lower CPU requests (50m) allow faster scaling response
   - Higher requests would delay scaling but provide more headroom
   - The 50m request is optimal for this small application

2. **CPU Target Threshold**
   - 30% CPU target triggers scaling with small load
   - 50% would require more traffic to trigger scaling
   - Too low (10%) would cause excessive scaling
   - Too high (70%) would delay scaling and impact performance

3. **Scale-Up vs Scale-Down Behavior**
   - Scale-up (0s stabilization): Good for handling sudden traffic spikes
   - Scale-down (60s stabilization): Prevents "flapping" (rapid up/down)
   - The 60s stabilization is crucial for stability

4. **Replica Limits**
   - Max 5 replicas: Prevents runaway scaling
   - Min 1 replica: Ensures always-on availability
   - The 1-5 range is appropriate for this application size

### Configuration Trade-offs

| Setting | Low Value | High Value | Recommendation |
|---------|-----------|------------|----------------|
| CPU Request | Fast scaling, many pods | Slow scaling, fewer pods | 50m (balanced) |
| CPU Target | Frequent scaling | Delayed scaling | 30% (responsive) |
| Scale-up | Immediate | Stabilized | 0s (responsive) |
| Scale-down | Aggressive | Conservative | 60s (stable) |

## Load Testing

### What We Learned

1. **Locust Configuration**
   - 50 users with 5/s spawn rate: Good balance for testing
   - Higher users (100+) would trigger more aggressive scaling
   - Lower users (20) might not trigger scaling at all

2. **Test Distribution**
   - Weighted distribution (4:3:3:2:1:1) simulates real users
   - Read-heavy workload (7/14 = 50%) is realistic
   - Write operations (upload/delete) are less frequent

3. **Test Duration**
   - 600 seconds (10 minutes): Enough to see scaling events
   - Shorter tests (300s) might miss scale-down phase
   - Longer tests (1800s) provide more data but take longer

4. **Minimal JPEG**
   - 1x1 pixel JPEG: Efficient for testing
   - Real images would test storage and bandwidth
   - Consider adding larger images for realistic testing

### Test Coverage

| Feature | Test Coverage | Notes |
|---------|--------------|-------|
| User Registration | ✅ | 100% of users register |
| User Login | ✅ | 100% of users login |
| Photo List (date) | ✅ | 4× weight, most frequent |
| Photo List (name) | ✅ | 2× weight, less frequent |
| Photo Upload | ✅ | 3× weight, write operation |
| Photo View | ✅ | 3× weight, read operation |
| Photo Delete | ✅ | 1× weight, delete operation |

## OpenShift Platform

### What We Learned

1. **HPA Integration**
   - HPA works seamlessly with OpenShift Deployments
   - Resource metrics are automatically collected
   - Scaling events are properly logged

2. **Metrics Server**
   - Must be running for HPA to work
   - Command: `oc get pods -n openshift-monitoring | grep metrics-server`
   - If not running: `oc patch configmap/cluster-monitoring-config -n openshift-monitoring --type merge -p '{"data":{"enableUserWorkload":"true"}}'`

3. **Service Discovery**
   - Locust running in OpenShift can access backend via service name
   - No need for external route for load testing
   - Internal DNS: `backend:5001`

4. **Resource Quotas**
   - Consider setting resource quotas per namespace
   - Prevents runaway scaling from consuming all resources
   - Example: `oc create quota photowebapp-quota --hard=cpu=10,memory=20Gi,pods=20`

## Challenges and Solutions

### Challenge 1: Storage Access

**Problem**: `uploads-pvc` uses `ReadWriteOnce`, files uploaded to one replica aren't accessible from others.

**Solution Options**:
1. Use `ReadWriteMany` with CephFS/NFS storage class
2. Switch to object storage (S3-compatible)
3. Use sticky sessions to route users to same pod
4. Store files in database (not recommended for large files)

**Recommendation**: For production, use object storage (AWS S3, MinIO) or CephFS with ReadWriteMany.

### Challenge 2: Metrics Not Available

**Problem**: HPA shows "failed to get cpu utilization" error.

**Solution**:
```bash
# Check if metrics-server is running
oc get pods -n openshift-monitoring | grep metrics-server

# If not, enable user workloads
oc patch configmap/cluster-monitoring-config -n openshift-monitoring --type merge -p '{"data":{"enableUserWorkload":"true"}}'

# Wait for metrics-server to start
sleep 60

# Verify metrics are available
oc top nodes
oc top pods
```

### Challenge 3: Scaling Too Slow

**Problem**: Scaling takes too long to respond to load.

**Solutions**:
1. Lower CPU target (30% instead of 50%)
2. Lower CPU requests (50m instead of 100m)
3. Reduce scale-up stabilization (0s instead of 60s)
4. Increase scale-up policy (2 pods/30s instead of 1)

### Challenge 4: Scaling Too Aggressively

**Problem**: Pods are scaling up and down rapidly (flapping).

**Solutions**:
1. Increase scale-down stabilization (60s)
2. Increase CPU target (30% instead of 20%)
3. Add resource limits to prevent over-provisioning
4. Use horizontal pod autoscaler behavior to smooth scaling

## Best Practices

### For Automatic Scaling

1. **Set Appropriate Resource Requests**
   - Lower requests for faster scaling
   - Higher requests for stability
   - Balance based on application size

2. **Configure HPA Behavior**
   - Scale-up: 0s stabilization for responsiveness
   - Scale-down: 60s stabilization for stability
   - Adjust based on traffic patterns

3. **Monitor Scaling Events**
   - Use `oc get hpa -w` to watch scaling
   - Check `oc get events --field-selector reason=SuccessfulRescale`
   - Set up alerts for scaling events

4. **Test Scaling**
   - Always test scaling with load tests
   - Verify scale-up and scale-down
   - Check for any issues in production

### For Load Testing

1. **Use Cloud-Based Testing**
   - Locust running in OpenShift
   - Realistic network conditions
   - No local machine limitations

2. **Cover All Features**
   - Test all API endpoints
   - Use weighted distribution
   - Simulate realistic user behavior

3. **Monitor During Test**
   - Watch HPA scaling
   - Monitor resource usage
   - Check for errors

4. **Document Results**
   - Record scaling events
   - Capture performance metrics
   - Include screenshots

## Key Takeaways

1. **HPA Configuration is Critical**
   - Resource requests determine scaling responsiveness
   - CPU target determines when scaling triggers
   - Behavior settings determine scaling smoothness

2. **Load Testing Must Be Realistic**
   - Use weighted distribution
   - Cover all features
   - Run from cloud, not local machine

3. **OpenShift HPA is Powerful**
   - Automatic scaling works well
   - Easy to configure
   - Good integration with Deployments

4. **Storage is a Challenge**
   - ReadWriteOnce limits multi-replica file access
   - Consider ReadWriteMany or object storage
   - Plan for shared storage early

5. **Monitoring is Essential**
   - Watch scaling events in real-time
   - Check resource usage
   - Set up alerts for issues

## Conclusion

The automatic scaling implementation was successful. Key learnings:

- **HPA Configuration**: 30% CPU target with 50m requests provides good balance
- **Load Testing**: Locust in OpenShift works well for cloud-based testing
- **Scaling Behavior**: Scale-up (0s) + Scale-down (60s) works for this application
- **Storage**: ReadWriteOnce limitation requires planning for production

The configuration is production-ready but should be tested with real traffic patterns before deployment.