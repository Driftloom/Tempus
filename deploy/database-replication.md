# PostgreSQL Replication Configuration

## Overview

This document describes the PostgreSQL replication setup for TEMPUS production deployment using Kubernetes StatefulSets with streaming replication.

## Architecture

**Primary-Replica Configuration:**
- 1 Primary (read-write)
- 2 Replicas (read-only)
- Automatic failover via Patroni (recommended for production)

## Current Setup

The Kubernetes StatefulSet in `deploy/k8s/postgres-statefulset.yaml` provides:
- 3 PostgreSQL replicas
- Persistent storage for each replica
- Service discovery via headless service

## Replication Configuration

### Enable Streaming Replication

Add to `postgres-statefulset.yaml`:

```yaml
env:
- name: POSTGRES_REPLICATION_USER
  value: "replicator"
- name: POSTGRES_REPLICATION_PASSWORD
  valueFrom:
    secretKeyRef:
      name: postgres-secrets
      key: replication-password
- name: POSTGRES_REPLICATION_MODE
  value: "master"
```

### Configure pg_hba.conf for Replication

```conf
# Replication connections
host replication replicator 0.0.0.0/0 md5
host replication replicator ::/0 md5
```

### Configure recovery.conf for Replicas

```conf
standby_mode = 'on'
primary_conninfo = 'host=postgres-0.postgres port=5432 user=replicator password=<password>'
```

## Application Configuration

Update `DATABASE_URL` to use read replicas:

```python
# Primary (write)
DATABASE_URL = "postgresql+asyncpg://tempus:password@postgres-0.postgres:5432/tempus"

# Replica (read)
DATABASE_READ_URL = "postgresql+asyncpg://tempus:password@postgres-1.postgres:5432/tempus"
```

## Connection Pooling

Configure PgBouncer for connection pooling:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pgbouncer
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: pgbouncer
        image: pgbouncer/pgbouncer:latest
        env:
        - name: DATABASES_HOST
          value: "postgres"
        - name: DATABASES_PORT
          value: "5432"
        - name: DATABASES_DBNAME
          value: "tempus"
        - name: DATABASES_USER
          value: "tempus"
        - name: DATABASES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secrets
              key: POSTGRES_PASSWORD
        - name: POOL_MODE
          value: "transaction"
        - name: MAX_CLIENT_CONN
          value: "1000"
```

## Failover Strategy

### Manual Failover

Promote a replica to primary:

```bash
kubectl exec postgres-1 -- pg_ctl promote -D /var/lib/postgresql/data/pgdata
```

### Automatic Failover (Patroni)

For production, use Patroni for automatic failover:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: patroni
spec:
  template:
    spec:
      containers:
      - name: patroni
        image: patroni:latest
        env:
        - name: PATRONI_SCOPE
          value: "tempus-postgres"
        - name: PATRONI_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: PATRONI_RESTAPI_CONNECT_ADDRESS
          value: "0.0.0.0:8008"
        - name: PATRONI_POSTGRESQL_CONNECT_ADDRESS
          value: "$(POD_IP):5432"
        - name: PATRONI_POSTGRESQL_DATA_DIR
          value: "/var/lib/postgresql/data/pgdata"
        - name: PATRONI_POSTGRESQL_LISTEN
          value: "0.0.0.0:5432"
        - name: PATRONI_POSTGRESQL_MAX_CONNECTIONS
          value: "100"
```

## Monitoring

### Replication Lag Monitoring

```sql
-- Check replication lag on primary
SELECT client_addr, state, sync_state, 
       pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS lag_bytes
FROM pg_stat_replication;
```

### Prometheus Exporter

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres-exporter
spec:
  template:
    spec:
      containers:
      - name: exporter
        image: prometheuscommunity/postgres-exporter:latest
        env:
        - name: DATA_SOURCE_URI
          value: "postgresql://tempus:password@postgres:5432/tempus?sslmode=disable"
        ports:
        - containerPort: 9187
```

## Backup Strategy

### WAL Archiving

Configure WAL archiving for point-in-time recovery:

```yaml
env:
- name: ARCHIVE_MODE
  value: "on"
- name: ARCHIVE_COMMAND
  value: "wal-g wal-push %p"
- name: RESTORE_COMMAND
  value: "wal-g wal-fetch %f %p"
```

### Backup Schedule

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: wal-g/wal-g:latest
            command:
            - wal-g
            - backup
            - push
            - postgres://tempus:password@postgres:5432/tempus
```

## Scaling

### Add More Replicas

Update `replicas` in `postgres-statefulset.yaml`:

```yaml
spec:
  replicas: 5  # Add 2 more replicas
```

### Read-Only Traffic Routing

Configure application to route read queries to replicas:

```python
import random

READ_REPLICAS = [
    "postgres-1.postgres",
    "postgres-2.postgres",
]

def get_read_db_url():
    replica = random.choice(READ_REPLICAS)
    return f"postgresql+asyncpg://tempus:password@{replica}:5432/tempus"

# Use for SELECT queries
async def get_tasks(db: AsyncSession):
    if is_read_query:
        db_url = get_read_db_url()
        # Use read replica connection
```

## Security

### TLS/SSL for Replication

Enable TLS for replication connections:

```yaml
env:
- name: POSTGRES_HOST_AUTH_METHOD
  value: "scram-sha-256"
- name: POSTGRES_SSL
  value: "on"
- name: POSTGRES_SSL_CERT_FILE
  value: "/var/lib/postgresql/data/server.crt"
- name: POSTGRES_SSL_KEY_FILE
  value: "/var/lib/postgresql/data/server.key"
```

## Troubleshooting

### Check Replication Status

```bash
kubectl exec postgres-0 -- psql -U tempus -d tempus -c "SELECT * FROM pg_stat_replication;"
```

### Check Replica Lag

```bash
kubectl exec postgres-1 -- psql -U tempus -d tempus -c "SELECT pg_is_in_recovery(), pg_last_xact_replay_timestamp();"
```

### Promote Replica to Primary

```bash
kubectl exec postgres-1 -- pg_ctl promote -D /var/lib/postgresql/data/pgdata
```

## References

- [PostgreSQL Streaming Replication](https://www.postgresql.org/docs/current/streaming-replication.html)
- [Patroni High Availability](https://patroni.readthedocs.io/)
- [PgBouncer Connection Pooling](https://www.pgbouncer.org/)
