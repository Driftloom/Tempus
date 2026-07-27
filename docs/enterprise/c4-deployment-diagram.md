# C4 Deployment Diagram - TEMPUS

## Deployment Overview

### Local Development Deployment

```
┌─────────────────────────────────────────────────────────────────┐
│                     Developer Machine                            │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    Docker Compose                          │  │
│  │                                                           │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  │
│  │  │ TEMPUS Core  │  │ PostgreSQL   │  │    Redis     │  │  │
│  │  │  (FastAPI)   │  │  + pgvector  │  │              │  │  │
│  │  │  Port: 8000  │  │  Port: 5432  │  │  Port: 6379  │  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │  │
│  │                                                           │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  │
│  │  │   Ollama     │  │ Celery       │  │   Chrome     │  │  │
│  │  │  (Local LLM) │  │   Worker     │  │ Extension    │  │  │
│  │  │  Port: 11434 │  │              │  │              │  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │  │
│  │                                                           │  │
│  │  ┌──────────────┐  ┌──────────────┐                      │  │
│  │  │  VS Code     │  │  Web Dashboard│                      │  │
│  │  │ Extension    │  │              │                      │  │
│  │  └──────────────┘  └──────────────┘                      │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Network: docker-compose bridge network                         │
│  Volumes: postgres_data, redis_data, ollama_data                │
└─────────────────────────────────────────────────────────────────┘
```

### Enterprise Production Deployment (Kubernetes)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           Kubernetes Cluster                                      │
│                                                                                   │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                         Namespace: tempus-prod                               │  │
│  │                                                                             │  │
│  │  ┌─────────────────────────────────────────────────────────────────────┐  │  │
│  │  │                     Application Layer                                 │  │  │
│  │  │                                                                       │  │  │
│  │  │  ┌─────────────────────────────────────────────────────────────┐  │  │  │
│  │  │  │            TEMPUS Core Deployment (3 replicas)                 │  │  │  │
│  │  │  │                                                               │  │  │  │
│  │  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │  │  │  │
│  │  │  │  │   Pod 1  │ │   Pod 2  │ │   Pod 3  │ │   Pod N  │         │  │  │  │
│  │  │  │  │          │ │          │ │          │ │          │         │  │  │  │
│  │  │  │  │ FastAPI  │ │ FastAPI  │ │ FastAPI  │ │ FastAPI  │         │  │  │  │
│  │  │  │  │ :8000    │ │ :8000    │ │ :8000    │ │ :8000    │         │  │  │  │
│  │  │  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘         │  │  │  │
│  │  │  │                                                               │  │  │  │
│  │  │  │  HPA: 3-10 replicas based on CPU/memory                       │  │  │  │
│  │  │  └─────────────────────────────────────────────────────────────┘  │  │  │
│  │  │                                                                       │  │  │
│  │  │  ┌─────────────────────────────────────────────────────────────┐  │  │  │
│  │  │  │            Celery Worker Deployment (5 replicas)               │  │  │  │
│  │  │  │                                                               │  │  │  │
│  │  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │  │  │  │
│  │  │  │  │ Worker 1 │ │ Worker 2 │ │ Worker 3 │ │ Worker N │         │  │  │  │
│  │  │  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘         │  │  │  │
│  │  │  │                                                               │  │  │  │
│  │  │  │  HPA: 5-20 replicas based on queue depth                     │  │  │  │
│  │  │  └─────────────────────────────────────────────────────────────┘  │  │  │
│  │  └─────────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                             │  │
│  │  ┌─────────────────────────────────────────────────────────────────────┐  │  │
│  │  │                        Services                                    │  │  │
│  │  │                                                                       │  │  │
│  │  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │  │  │
│  │  │  │ tempus-api-svc   │  │ tempus-ws-svc    │  │ tempus-worker-svc │  │  │  │
│  │  │  │ ClusterIP        │  │ ClusterIP        │  │ ClusterIP        │  │  │  │
│  │  │  │ Port: 80 → 8000  │  │ Port: 80 → 8000  │  │ Port: 80 → 8000  │  │  │  │
│  │  │  └──────────────────┘  └──────────────────┘  └──────────────────┘  │  │  │
│  │  └─────────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                             │  │
│  │  ┌─────────────────────────────────────────────────────────────────────┐  │  │
│  │  │                      Ingress                                        │  │  │
│  │  │                                                                       │  │  │
│  │  │  ┌─────────────────────────────────────────────────────────────┐  │  │  │
│  │  │  │            NGINX Ingress Controller                             │  │  │  │
│  │  │  │                                                               │  │  │  │
│  │  │  │  /api → tempus-api-svc                                        │  │  │  │
│  │  │  │  /ws → tempus-ws-svc                                          │  │  │  │
│  │  │  │  TLS termination                                              │  │  │  │
│  │  │  └─────────────────────────────────────────────────────────────┘  │  │  │
│  │  └─────────────────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                                                                   │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                         Data Layer                                        │  │
│  │                                                                             │  │
│  │  ┌─────────────────────────────────────────────────────────────┐  │  │
│  │  │            PostgreSQL StatefulSet (HA)                        │  │  │
│  │  │                                                               │  │  │
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐                     │  │  │
│  │  │  │ Primary  │ │ Replica 1│ │ Replica 2│                     │  │  │
│  │  │  │          │ │          │ │          │                     │  │  │
│  │  │  │ pgvector │ │ pgvector │ │ pgvector │                     │  │  │
│  │  │  └──────────┘ └──────────┘ └──────────┘                     │  │  │
│  │  │                                                               │  │  │
│  │  │  Patroni for automatic failover                               │  │  │
│  │  │  PgBouncer for connection pooling                             │  │  │
│  │  └─────────────────────────────────────────────────────────────┘  │  │
│  │                                                                       │  │
│  │  ┌─────────────────────────────────────────────────────────────┐  │  │
│  │  │            Redis Cluster (6 nodes)                           │  │  │
│  │  │                                                               │  │  │
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐                     │  │  │
│  │  │  │ Master 1 │ │ Master 2 │ │ Master 3 │                     │  │  │
│  │  │  └──────────┘ └──────────┘ └──────────┘                     │  │  │
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐                     │  │  │
│  │  │  │ Slave 1  │ │ Slave 2  │ │ Slave 3  │                     │  │  │
│  │  │  └──────────┘ └──────────┘ └──────────┘                     │  │  │
│  │  │                                                               │  │  │
│  │  │  Redis Sentinel for automatic failover                        │  │  │
│  │  └─────────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                                                                   │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                     Monitoring & Observability                            │  │
│  │                                                                             │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │  │
│  │  │Prometheus│ │ Grafana  │ │  Jaeger  │ │   Loki   │ │AlertMgr  │        │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘        │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Cloud Deployment (AWS)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           AWS Cloud Environment                                   │
│                                                                                   │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                         VPC (10.0.0.0/16)                                   │  │
│  │                                                                             │  │
│  │  ┌─────────────────────────────────────────────────────────────────────┐  │  │
│  │  │                    Public Subnets                                     │  │  │
│  │  │                                                                       │  │  │
│  │  │  ┌─────────────────────────────────────────────────────────────┐  │  │  │
│  │  │  │            Application Load Balancer (ALB)                      │  │  │  │
│  │  │  │                                                               │  │  │  │
│  │  │  │  HTTPS listener (Port 443)                                   │  │  │  │
│  │  │  │  ACM certificate                                             │  │  │  │
│  │  │  │  Target groups: api, websocket                                │  │  │  │
│  │  │  └─────────────────────────────────────────────────────────────┘  │  │  │
│  │  │                                                                       │  │  │
│  │  │  ┌─────────────────────────────────────────────────────────────┐  │  │  │
│  │  │  │            NAT Gateway                                        │  │  │  │
│  │  │  └─────────────────────────────────────────────────────────────┘  │  │  │
│  │  └─────────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                             │  │
│  │  ┌─────────────────────────────────────────────────────────────────────┐  │  │
│  │  │                    Private Subnets                                    │  │  │
│  │  │                                                                       │  │  │
│  │  │  ┌─────────────────────────────────────────────────────────────┐  │  │  │
│  │  │  │            EKS Cluster                                         │  │  │  │
│  │  │  │                                                               │  │  │  │
│  │  │  │  ┌─────────────────────────────────────────────────────┐  │  │  │  │
│  │  │  │  │            TEMPUS Core Pods (3+)                       │  │  │  │  │
│  │  │  │  └─────────────────────────────────────────────────────┘  │  │  │  │
│  │  │  │                                                               │  │  │  │
│  │  │  │  ┌─────────────────────────────────────────────────────┐  │  │  │  │
│  │  │  │  │            Celery Worker Pods (5+)                     │  │  │  │  │
│  │  │  │  └─────────────────────────────────────────────────────┘  │  │  │  │
│  │  │  └─────────────────────────────────────────────────────────────┘  │  │  │
│  │  │                                                                       │  │  │
│  │  │  ┌─────────────────────────────────────────────────────────────┐  │  │  │
│  │  │  │            Amazon RDS PostgreSQL (Multi-AZ)                │  │  │  │
│  │  │  │                                                               │  │  │  │
│  │  │  │  - Primary instance (db.r6g.xlarge)                         │  │  │  │
│  │  │  │  - 2 Read replicas                                          │  │  │  │
│  │  │  │  - pgvector extension                                        │  │  │  │
│  │  │  │  - Automated backups                                         │  │  │  │
│  │  │  │  - Multi-AZ deployment                                      │  │  │  │
│  │  │  └─────────────────────────────────────────────────────────────┘  │  │  │
│  │  │                                                                       │  │  │
│  │  │  ┌─────────────────────────────────────────────────────────────┐  │  │  │
│  │  │  │            Amazon ElastiCache Redis (Cluster Mode)          │  │  │  │
│  │  │  │                                                               │  │  │  │
│  │  │  │  - 3 node cluster (cache.r6g.large)                         │  │  │  │
│  │  │  │  - Multi-AZ deployment                                      │  │  │  │
│  │  │  │  - Automatic failover                                       │  │  │  │
│  │  │  │  - Redis Cluster mode                                       │  │  │  │
│  │  │  └─────────────────────────────────────────────────────────────┘  │  │  │
│  │  │                                                                       │  │  │
│  │  │  ┌─────────────────────────────────────────────────────────────┐  │  │  │
│  │  │  │            Amazon EKS (Kubernetes)                           │  │  │  │
│  │  │  │                                                               │  │  │  │
│  │  │  │  - Managed control plane                                     │  │  │  │
│  │  │  │  - Managed node groups                                      │  │  │  │
│  │  │  │  - Fargate support (optional)                                │  │  │  │
│  │  │  │  - IRSA for IAM roles                                       │  │  │  │
│  │  │  └─────────────────────────────────────────────────────────────┘  │  │  │
│  │  └─────────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                             │  │
│  │  ┌─────────────────────────────────────────────────────────────────────┐  │  │
│  │  │                    Security Groups                                   │  │  │
│  │  │                                                                       │  │  │
│  │  │  - ALB Security Group: 443 from 0.0.0.0/0                         │  │  │
│  │  │  - EKS Security Group: 8080 from ALB SG                            │  │  │
│  │  │  - RDS Security Group: 5432 from EKS SG                            │  │  │
│  │  │  - ElastiCache Security Group: 6379 from EKS SG                     │  │  │
│  │  └─────────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                                                                   │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                     AWS Services                                           │  │
│  │                                                                             │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │  │
│  │  │  S3      │ │ CloudWatch│ │  KMS     │ │ Secrets  │ │  ACM     │        │  │
│  │  │ (Backups)│ │ (Logs)   │ │ (Keys)   │ │ Manager  │ │ (Certs)  │        │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘        │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Deployment Descriptions

### Local Development Deployment

#### Docker Compose Configuration

**Purpose**: Local development and testing

**Components**:
- **TEMPUS Core**: FastAPI application on port 8000
- **PostgreSQL**: PostgreSQL 15 with pgvector extension on port 5432
- **Redis**: Redis 7 on port 6379
- **Ollama**: Local LLM service on port 11434
- **Celery Worker**: Background task processor
- **Chrome Extension**: Browser extension for testing
- **VS Code Extension**: VS Code extension for testing

**Networking**:
- Docker bridge network for inter-container communication
- All services on same network
- Ports exposed to host for external access

**Volumes**:
- `postgres_data`: PostgreSQL data persistence
- `redis_data`: Redis data persistence
- `ollama_data`: Ollama model storage

**Configuration**:
- Environment variables in `.env` file
- Hot reload enabled for development
- Debug mode enabled
- Local file system for storage

### Enterprise Production Deployment

#### Kubernetes Configuration

**Purpose**: Enterprise production deployment with high availability

**Namespace**: `tempus-prod`

**Components**:

**TEMPUS Core Deployment**:
- **Replicas**: 3 (minimum) to 10 (maximum) via HPA
- **Resources**:
  - Requests: 256Mi memory, 250m CPU
  - Limits: 512Mi memory, 500m CPU
- **Health Checks**:
  - Liveness: `/health/live` every 10s
  - Readiness: `/health/ready` every 5s
- **Auto-scaling**: Based on CPU (70%) and memory (80%)

**Celery Worker Deployment**:
- **Replicas**: 5 (minimum) to 20 (maximum) via HPA
- **Resources**:
  - Requests: 512Mi memory, 500m CPU
  - Limits: 1Gi memory, 1000m CPU
- **Auto-scaling**: Based on queue depth

**PostgreSQL StatefulSet**:
- **Replicas**: 3 (1 primary, 2 replicas)
- **Storage**: 100Gi PVC per replica
- **High Availability**: Patroni for automatic failover
- **Connection Pooling**: PgBouncer sidecar
- **Backups**: Automated daily backups to S3

**Redis Cluster**:
- **Nodes**: 6 (3 masters, 3 slaves)
- **Storage**: 10Gi per node
- **High Availability**: Redis Sentinel for failover
- **Persistence**: RDB + AOF

**Services**:
- **tempus-api-svc**: ClusterIP for internal API access
- **tempus-ws-svc**: ClusterIP for WebSocket connections
- **tempus-worker-svc**: ClusterIP for worker communication

**Ingress**:
- **NGINX Ingress Controller** for TLS termination
- **Routes**: `/api` → tempus-api-svc, `/ws` → tempus-ws-svc
- **TLS**: ACM certificates or cert-manager

**Monitoring**:
- **Prometheus**: Metrics collection
- **Grafana**: Visualization dashboards
- **Jaeger**: Distributed tracing
- **Loki**: Log aggregation
- **AlertManager**: Alert routing

### Cloud Deployment (AWS)

#### AWS Infrastructure

**Purpose**: Cloud-native deployment with managed services

**VPC Configuration**:
- **CIDR**: 10.0.0.0/16
- **Subnets**: 3 public, 3 private (multi-AZ)
- **NAT Gateway**: For private subnet internet access
- **Security Groups**: Restrictive rules per service

**EKS Cluster**:
- **Version**: 1.28+
- **Node Groups**: Managed node groups with auto-scaling
- **IAM**: IRSA for pod IAM roles
- **Logging**: CloudWatch integration

**RDS PostgreSQL**:
- **Instance**: db.r6g.xlarge
- **Storage**: 100Gi with auto-scaling to 1Ti
- **Multi-AZ**: True for high availability
- **Backup**: 30-day retention, point-in-time recovery
- **Encryption**: At rest and in transit
- **Extension**: pgvector for vector search

**ElastiCache Redis**:
- **Node Type**: cache.r6g.large
- **Nodes**: 3 (cluster mode)
- **Multi-AZ**: True for high availability
- **Encryption**: At rest and in transit
- **Persistence**: AOF enabled

**ALB**:
- **Type**: Application Load Balancer
- **Listeners**: HTTPS (443)
- **Certificates**: ACM
- **Target Groups**: api, websocket
- **Health Checks**: Active health checks

**AWS Services**:
- **S3**: Backup storage, static assets
- **CloudWatch**: Logs, metrics, alarms
- **KMS**: Encryption key management
- **Secrets Manager**: Secret storage
- **ACM**: TLS certificates

## Deployment Strategies

### Blue-Green Deployment

**Process**:
1. Deploy new version to green environment
2. Run smoke tests against green
3. Switch traffic from blue to green via ALB
4. Monitor green environment
5. Keep blue as rollback option

**Benefits**:
- Zero downtime deployment
- Instant rollback capability
- Testing before traffic switch

**Implementation**:
- Argo Rollouts for Kubernetes
- EKS blue-green deployment
- ALB target group switching

### Canary Deployment

**Process**:
1. Deploy new version to canary subset
2. Route 10% traffic to canary
3. Monitor canary performance and errors
4. Gradually increase traffic to new version
5. Full rollout or rollback based on metrics

**Benefits**:
- Gradual rollout reduces risk
- Real-world testing before full rollout
- Quick rollback if issues detected

**Implementation**:
- Argo Rollouts canary strategy
- Istio for traffic splitting
- Prometheus metrics for canary monitoring

### Rolling Deployment

**Process**:
1. Update deployment with new image
2. Kubernetes gradually replaces pods
3. Health checks ensure new pods are healthy
4. Old pods terminated after new pods healthy

**Benefits**:
- Simple to implement
- Built into Kubernetes
- Gradual rollout

**Implementation**:
- Kubernetes rolling update
- HPA for scaling
- Health checks for validation

## Infrastructure as Code

### Terraform Configuration

**Provider**: AWS

**Resources**:
- VPC, subnets, route tables
- Security groups, NACLs
- EKS cluster, node groups
- RDS instances, snapshots
- ElastiCache clusters
- ALB, target groups
- IAM roles, policies
- S3 buckets
- CloudWatch log groups, alarms

**State Management**:
- Terraform state in S3
- State locking with DynamoDB
- Remote state for team collaboration

### Kubernetes Manifests

**Helm Charts**:
- TEMPUS Core chart
- PostgreSQL chart
- Redis chart
- Monitoring stack chart

**Custom Resources**:
- Deployments, StatefulSets
- Services, Ingress
- ConfigMaps, Secrets
- HPA, PodDisruptionBudgets
- NetworkPolicies

**GitOps**:
- ArgoCD for GitOps deployment
- Git repository as source of truth
- Automated sync and drift detection

## Security Configuration

### Network Security

**VPC Security**:
- Private subnets for application and data
- Public subnets only for ALB
- Security groups with least privilege
- Network policies for pod-to-pod communication

**TLS Configuration**:
- TLS 1.3 for all external communications
- TLS for internal service communication
- Certificate rotation every 90 days
- ACM or cert-manager for certificates

### Secrets Management

**Kubernetes Secrets**:
- Encrypted at rest (etcd encryption)
- RBAC for secret access
- Secret rotation policies
- External Secrets Operator for AWS Secrets Manager

**AWS Secrets Manager**:
- Encrypted secrets storage
- Automatic rotation every 30 days
- IAM-based access control
- Audit logging

## Monitoring and Observability

### Prometheus Metrics

**Scrape Targets**:
- TEMPUS Core pods (port 8000, /metrics)
- PostgreSQL exporter
- Redis exporter
- Node exporter
- Kubelet metrics

**Alerting Rules**:
- High error rate (> 5%)
- High latency (p95 > 500ms)
- High CPU (> 90%)
- High memory (> 90%)
- Database connection pool exhaustion

### Logging

**Log Aggregation**:
- Loki for log aggregation
- Fluent Bit for log collection
- Structured JSON logging
- Log retention: 30 days

**Log Levels**:
- Production: INFO, WARNING, ERROR, CRITICAL
- Development: DEBUG, INFO, WARNING, ERROR, CRITICAL

### Tracing

**Distributed Tracing**:
- OpenTelemetry instrumentation
- Jaeger for trace storage
- 10% sampling in production
- 100% sampling in development

## Disaster Recovery

### Backup Strategy

**Database Backups**:
- Automated daily backups to S3
- Point-in-time recovery (PITR)
- 30-day retention
- Cross-region replication for critical data

**Configuration Backups**:
- Git repository for manifests
- Terraform state in S3
- Secrets in Secrets Manager
- Regular backup verification

### High Availability

**Multi-AZ Deployment**:
- EKS nodes across multiple AZs
- RDS Multi-AZ deployment
- ElastiCache Multi-AZ deployment
- ALB cross-zone load balancing

**Failover**:
- Patroni for PostgreSQL failover
- Redis Sentinel for Redis failover
- Kubernetes pod auto-restart
- HPA for auto-scaling

## Capacity Planning

### Resource Requirements

**TEMPUS Core**:
- CPU: 250m - 500m per pod
- Memory: 256Mi - 512Mi per pod
- Pods: 3 - 10 (auto-scaling)

**Celery Workers**:
- CPU: 500m - 1000m per pod
- Memory: 512Mi - 1Gi per pod
- Pods: 5 - 20 (auto-scaling)

**PostgreSQL**:
- CPU: 2 - 4 vCPU
- Memory: 8 - 16 Gi
- Storage: 100Gi - 1Ti

**Redis**:
- CPU: 1 - 2 vCPU per node
- Memory: 4 - 8 Gi per node
- Storage: 10Gi per node

### Scaling Strategy

**Horizontal Scaling**:
- HPA based on CPU/memory metrics
- KEDA for event-based scaling (queue depth)
- Cluster autoscaler for node scaling

**Vertical Scaling**:
- Periodic resource review
- Adjust resource requests/limits
- Instance type upgrades

## Conclusion

The TEMPUS deployment architecture supports multiple deployment scenarios from local development to enterprise production. The use of Docker Compose for development, Kubernetes for enterprise, and AWS managed services for cloud provides flexibility and scalability while maintaining consistency across environments.

Key deployment strengths:
1. Multiple deployment options for different use cases
2. High availability with multi-AZ and failover
3. Infrastructure as Code for reproducibility
4. Comprehensive monitoring and observability
5. Security best practices throughout
6. Disaster recovery and backup strategies
