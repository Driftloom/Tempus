# Redis Clustering Configuration

## Overview

This document describes the Redis clustering setup for TEMPUS production deployment using Kubernetes StatefulSets with Redis Cluster mode.

## Architecture

**Redis Cluster Configuration:**
- 6 Redis nodes (3 masters, 3 replicas)
- Automatic sharding across 16384 hash slots
- High availability with automatic failover
- Data partitioning for horizontal scaling

## Current Setup

The Kubernetes StatefulSet in `deploy/k8s/redis-statefulset.yaml` provides:
- 3 Redis replicas (sentinel mode)
- Persistent storage for each replica
- Service discovery via headless service

## Redis Cluster Mode

### Enable Cluster Mode

Update `redis-statefulset.yaml` to enable cluster mode:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis-cluster
  labels:
    app: redis-cluster
spec:
  serviceName: redis-cluster
  replicas: 6
  selector:
    matchLabels:
      app: redis-cluster
  template:
    metadata:
      labels:
        app: redis-cluster
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        command:
        - redis-server
        - /conf/redis-cluster.conf
        ports:
        - containerPort: 6379
          name: client
        - containerPort: 16379
          name: cluster-bus
        env:
        - name: POD_IP
          valueFrom:
            fieldRef:
              fieldPath: status.podIP
        volumeMounts:
        - name: redis-config
          mountPath: /conf
        - name: redis-storage
          mountPath: /data
```

### Redis Cluster Configuration

Update `redis-config` ConfigMap:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: redis-cluster-config
data:
  redis-cluster.conf: |
    cluster-enabled yes
    cluster-config-file nodes.conf
    cluster-node-timeout 5000
    cluster-announce-ip $(POD_IP)
    cluster-announce-port 6379
    cluster-announce-bus-port 16379
    appendonly yes
    appendfsync everysec
    maxmemory 256mb
    maxmemory-policy allkeys-lru
    save 900 1
    save 300 10
    save 60 10000
```

## Cluster Initialization

### Create Redis Cluster

After deploying the StatefulSet, initialize the cluster:

```bash
# Wait for all pods to be ready
kubectl wait --for=condition=ready pod -l app=redis-cluster --timeout=300s

# Initialize cluster with 3 masters
kubectl exec redis-cluster-0 -- redis-cli --cluster create \
  $(kubectl get pod -l app=redis-cluster -o jsonpath='{range .items[*]}{.status.podIP}:6379 {end}') \
  --cluster-replicas 1
```

### Verify Cluster Status

```bash
kubectl exec redis-cluster-0 -- redis-cli cluster info
kubectl exec redis-cluster-0 -- redis-cli cluster nodes
```

## Application Configuration

### Update Redis Client for Cluster Mode

Update `apps/core/app/cache/redis_client.py`:

```python
import redis.asyncio as redis
from redis.cluster import RedisCluster

class RedisClusterClient:
    def __init__(self):
        self.cluster = None
    
    async def connect(self):
        """Connect to Redis cluster."""
        self.cluster = RedisCluster(
            host="redis-cluster",
            port=6379,
            decode_responses=True,
            skip_full_coverage_check=True,
            max_connections=50
        )
    
    async def get(self, key: str) -> str | None:
        """Get value from cluster."""
        return await self.cluster.get(key)
    
    async def set(self, key: str, value: str, ex: int | None = None) -> bool:
        """Set value in cluster."""
        return await self.cluster.set(key, value, ex=ex)
    
    async def delete(self, key: str) -> int:
        """Delete key from cluster."""
        return await self.cluster.delete(key)
    
    async def close(self):
        """Close cluster connection."""
        await self.cluster.close()
```

### Update Environment Variables

Update `deploy/k8s/secrets.yaml`:

```yaml
stringData:
  redis-url: "redis://:CHANGE_ME@redis-cluster:6379/0"
```

## Scaling

### Add More Nodes

Update `replicas` in `redis-statefulset.yaml`:

```yaml
spec:
  replicas: 9  # Add 3 more nodes (maintain 1:1 master:replica ratio)
```

### Rebalance Cluster

After adding nodes, rebalance the cluster:

```bash
kubectl exec redis-cluster-0 -- redis-cli --cluster rebalance \
  --cluster-threshold 1 \
  --cluster-use-empty-masters
```

## High Availability

### Automatic Failover

Redis Cluster provides automatic failover:
- When a master fails, its replica is promoted
- Cluster continues serving requests
- Minimum of 3 masters required for quorum

### Sentinel Mode (Alternative)

For simpler HA without sharding, use Redis Sentinel:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis-sentinel
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        command:
        - redis-server
        - /conf/redis-sentinel.conf
        ports:
        - containerPort: 26379
          name: sentinel
```

## Monitoring

### Cluster Health Monitoring

```bash
# Check cluster health
kubectl exec redis-cluster-0 -- redis-cli cluster info

# Check node status
kubectl exec redis-cluster-0 -- redis-cli cluster nodes

# Check key distribution
kubectl exec redis-cluster-0 -- redis-cli --cluster info
```

### Prometheus Exporter

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis-exporter
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: exporter
        image: oliver006/redis_exporter:latest
        env:
        - name: REDIS_ADDR
          value: "redis://redis-cluster:6379"
        ports:
        - containerPort: 9121
```

## Backup Strategy

### Cluster Backup

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: redis-backup
spec:
  schedule: "0 3 * * *"  # Daily at 3 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: redis:7-alpine
            command:
            - redis-cli
            - --cluster
            - backup
            - /backup/redis-cluster.rdb
            volumeMounts:
            - name: backup-storage
              mountPath: /backup
```

## Security

### TLS/SSL for Cluster

Enable TLS for cluster communication:

```yaml
env:
- name: TLS_MODE
  value: "on"
- name: TLS_CERT_FILE
  value: "/etc/redis/tls/redis.crt"
- name: TLS_KEY_FILE
  value: "/etc/redis/tls/redis.key"
- name: TLS_CA_CERT_FILE
  value: "/etc/redis/tls/ca.crt"
```

### Authentication

Enable password authentication:

```yaml
env:
- name: REDIS_PASSWORD
  valueFrom:
    secretKeyRef:
      name: redis-secrets
      key: redis-password
```

Update redis config:

```conf
requirepass ${REDIS_PASSWORD}
masterauth ${REDIS_PASSWORD}
```

## Troubleshooting

### Check Cluster Status

```bash
kubectl exec redis-cluster-0 -- redis-cli cluster info
kubectl exec redis-cluster-0 -- redis-cli cluster nodes
```

### Check Slot Distribution

```bash
kubectl exec redis-cluster-0 -- redis-cli cluster slots
```

### Fix Cluster Issues

```bash
# Reset cluster (CAUTION: data loss)
kubectl exec redis-cluster-0 -- redis-cli --cluster reset

# Rebuild cluster
kubectl exec redis-cluster-0 -- redis-cli --cluster create \
  $(kubectl get pod -l app=redis-cluster -o jsonpath='{range .items[*]}{.status.podIP}:6379 {end}') \
  --cluster-replicas 1
```

### Check Failover Status

```bash
kubectl exec redis-cluster-0 -- redis-cli cluster failover
```

## Performance Optimization

### Memory Optimization

```conf
maxmemory 512mb
maxmemory-policy allkeys-lru
```

### Persistence Optimization

```conf
appendonly yes
appendfsync everysec
save 900 1
save 300 10
save 60 10000
```

### Connection Pooling

Update application connection pool:

```python
self.cluster = RedisCluster(
    host="redis-cluster",
    port=6379,
    decode_responses=True,
    max_connections=100,
    retry_on_timeout=True,
    socket_timeout=5,
    socket_connect_timeout=5
)
```

## Migration from Standalone to Cluster

### Data Migration

```bash
# Export data from standalone
kubectl exec redis-standalone-0 -- redis-cli --rdb /tmp/dump.rdb

# Import to cluster
kubectl cp redis-standalone-0:/tmp/dump.rdb /tmp/dump.rdb
kubectl cp /tmp/dump.rdb redis-cluster-0:/tmp/dump.rdb
kubectl exec redis-cluster-0 -- redis-cli --pipe < /tmp/dump.rdb
```

## References

- [Redis Cluster Tutorial](https://redis.io/topics/cluster-tutorial)
- [Redis Cluster Specification](https://redis.io/topics/cluster-spec)
- [Redis Sentinel](https://redis.io/topics/sentinel)
