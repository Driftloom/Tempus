# TEMPUS DevOps & Deployment Strategy

## Overview

TEMPUS implements comprehensive DevOps and deployment strategies supporting local-first development, enterprise production deployment, and continuous delivery. This strategy covers infrastructure as code, CI/CD pipelines, containerization, orchestration, and operational procedures.

## Deployment Architecture

### Local Development Deployment

**Components**:
- TEMPUS Core (FastAPI with uvicorn)
- PostgreSQL with pgvector
- Redis
- Ollama (local LLM)
- Celery worker

**Deployment Method**: Docker Compose

**Configuration**:
```yaml
# docker-compose.yml
version: '3.8'
services:
  core:
    build: ./apps/core
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://tempus:password@postgres:5432/tempus
      - REDIS_URL=redis://redis:6379
      - OLLAMA_HOST=http://ollama:11434
    depends_on:
      - postgres
      - redis
      - ollama
  
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      - POSTGRES_USER=tempus
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=tempus
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
  
  ollama:
    image: ollama/ollama
    volumes:
      - ollama_data:/root/.ollama
  
  celery_worker:
    build: ./apps/core
    command: celery -A app.notifications.scheduler.celery_app worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://tempus:password@postgres:5432/tempus
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

volumes:
  postgres_data:
  redis_data:
  ollama_data:
```

### Enterprise Production Deployment

**Components**:
- Kubernetes cluster
- PostgreSQL with pgvector (HA)
- Redis Cluster
- Ollama deployment (or local model deployment)
- Celery workers (horizontal scaling)
- Load balancer (NGINX or cloud LB)
- Monitoring stack (Prometheus, Grafana, Loki)
- Jaeger for tracing

**Deployment Method**: Kubernetes with Helm charts

**Infrastructure**: Terraform for infrastructure provisioning

## Infrastructure as Code

### Terraform Configuration

**Provider**: AWS, GCP, or Azure (configurable)

**Example AWS Configuration**:
```hcl
# VPC
resource "aws_vpc" "tempus" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name = "tempus-vpc"
  }
}

# EKS Cluster
resource "aws_eks_cluster" "tempus" {
  name     = "tempus-cluster"
  role_arn = aws_iam_role.eks_cluster.arn
  
  vpc_config {
    subnet_ids = aws_subnet.private[*].id
  }
  
  tags = {
    Name = "tempus-cluster"
  }
}

# RDS PostgreSQL
resource "aws_db_instance" "tempus" {
  engine         = "postgres"
  engine_version = "16.1"
  instance_class = "db.r6g.xlarge"
  
  allocated_storage     = 100
  max_allocated_storage = 1000
  
  db_name  = "tempus"
  username = var.db_username
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.database.id]
  db_subnet_group_name   = aws_db_subnet_group.tempus.name
  
  backup_retention_period = 30
  backup_window          = "03:00-04:00"
  
  tags = {
    Name = "tempus-database"
  }
}

# ElastiCache Redis
resource "aws_elasticache_cluster" "tempus" {
  cluster_id           = "tempus-redis"
  engine               = "redis"
  node_type            = "cache.r6g.large"
  num_cache_nodes      = 3
  parameter_group_name = "default.redis7"
  engine_version       = "7.0"
  
  port = 6379
  
  security_group_ids = [aws_security_group.redis.id]
  subnet_group_name  = aws_elasticache_subnet_group.tempus.name
  
  tags = {
    Name = "tempus-redis"
  }
}
```

### Kubernetes Configuration

**Helm Chart Structure**:
```
helm/tempus/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   └── hpa.yaml
└── templates/
    ├── postgres/
    └── redis/
```

**Deployment Template**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tempus-core
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: tempus-core
  template:
    metadata:
      labels:
        app: tempus-core
    spec:
      containers:
      - name: tempus-core
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: tempus-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: tempus-secrets
              key: redis-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

## CI/CD Pipeline

### GitHub Actions Configuration

**PR Pipeline**:
```yaml
name: PR

on:
  pull_request:
    branches: [main, develop]

jobs:
  python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install uv
        run: pip install uv
      
      - name: Install dependencies
        working-directory: ./apps/core
        run: uv sync
      
      - name: Run linter
        working-directory: ./apps/core
        run: uv run ruff check .
      
      - name: Run type checker
        working-directory: ./apps/core
        run: uv run mypy .
      
      - name: Run tests
        working-directory: ./apps/core
        run: uv run pytest --cov
      
      - name: Run security tests
        working-directory: ./apps/core
        run: |
          uv run bandit -r .
          uv run safety check

  typescript:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install pnpm
        run: npm install -g pnpm
      
      - name: Install dependencies
        run: pnpm install
      
      - name: Run linter
        run: pnpm lint
      
      - name: Run type checker
        run: pnpm typecheck
      
      - name: Run tests
        run: pnpm test --coverage

  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install pnpm
        run: npm install -g pnpm
      
      - name: Install dependencies
        run: pnpm install
      
      - name: Build extensions
        run: pnpm build
      
      - name: Start test environment
        run: docker-compose up -d
      
      - name: Run Chrome E2E tests
        run: pnpm test:e2e:chrome
      
      - name: Run VS Code E2E tests
        run: pnpm test:e2e:vscode
      
      - name: Stop test environment
        run: docker-compose down
```

**Release Pipeline**:
```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: |
          docker build -t tempus/core:${{ github.ref_name }} ./apps/core
          docker tag tempus/core:${{ github.ref_name }} tempus/core:latest
      
      - name: Push Docker image
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push tempus/core:${{ github.ref_name }}
          docker push tempus/core:latest
      
      - name: Build Chrome extension
        run: pnpm --filter chrome-extension build
      
      - name: Package Chrome extension
        run: cd apps/chrome-extension && zip -r tempus-chrome-extension.zip dist/
      
      - name: Build VS Code extension
        run: pnpm --filter vscode-extension build
      
      - name: Package VS Code extension
        run: |
          cd apps/vscode-extension
          npx vsce package --out tempus-vscode-extension.vsix
      
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            apps/chrome-extension/tempus-chrome-extension.zip
            apps/vscode-extension/tempus-vscode-extension.vsix
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Container Strategy

### Docker Images

**Multi-Stage Build**:
```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app
COPY apps/core/pyproject.toml apps/core/uv.lock ./
RUN pip install uv && uv sync --frozen

# Runtime stage
FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY apps/core/app ./app

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Image Optimization**:
- Use slim base images
- Multi-stage builds
- Layer caching
- Minimal attack surface

**Image Security**:
- Regular base image updates
- Vulnerability scanning
- Image signing (cosign)
- SBOM generation

## Configuration Management

### Environment Variables

**Required Variables**:
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/tempus

# Redis
REDIS_URL=redis://host:6379

# LLM Providers
OLLAMA_HOST=http://localhost:11434
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Security
JWT_SECRET=your-secret-key
ENCRYPTION_KEY=your-encryption-key

# OAuth
GOOGLE_OAUTH_CLIENT_ID=...
GOOGLE_OAUTH_CLIENT_SECRET=...
```

**Configuration Management**:
- Kubernetes ConfigMaps for non-sensitive config
- Kubernetes Secrets for sensitive data
- Environment-specific configurations
- Configuration validation at startup

### Secrets Management

**Development**: `.env` file (gitignored)

**Production**:
- Kubernetes Secrets
- AWS Secrets Manager / GCP Secret Manager
- HashiCorp Vault (enterprise)
- Rotation policies

**Secret Rotation**:
- Automated rotation where possible
- Manual rotation procedures
- Zero-downtime rotation
- Audit logging of rotation events

## Deployment Strategies

### Blue-Green Deployment

**Process**:
1. Deploy new version to green environment
2. Run smoke tests against green
3. Switch traffic from blue to green
4. Monitor green environment
5. Keep blue as rollback option

**Benefits**:
- Zero downtime deployment
- Instant rollback capability
- Testing before traffic switch

### Canary Deployment

**Process**:
1. Deploy new version to canary subset
2. Route small percentage of traffic to canary
3. Monitor canary performance and errors
4. Gradually increase traffic to new version
5. Full rollout or rollback based on metrics

**Benefits**:
- Gradual rollout reduces risk
- Real-world testing before full rollout
- Quick rollback if issues detected

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

## Monitoring and Observability

### Health Checks

**Liveness Probe**:
```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
```

**Readiness Probe**:
```yaml
readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

### Metrics Collection

**Prometheus Integration**:
```yaml
- name: prometheus
  image: prom/prometheus
  ports:
  - "9090:9090"
  volumes:
  - ./prometheus.yml:/etc/prometheus/prometheus.yml
  - prometheus_data:/prometheus
```

### Log Aggregation

**Loki Integration**:
```yaml
- name: loki
  image: grafana/loki
  ports:
  - "3100:3100"
  volumes:
  - ./loki-config.yml:/etc/loki/local-config.yaml
```

## Operational Procedures

### Deployment Procedure

**Pre-Deployment**:
1. Run all tests
2. Review changes
3. Create release branch
4. Update documentation
5. Notify stakeholders

**Deployment**:
1. Deploy to staging environment
2. Run smoke tests
3. Deploy to production (canary or blue-green)
4. Monitor metrics and logs
5. Verify functionality

**Post-Deployment**:
1. Monitor for issues
2. Collect feedback
3. Update runbooks
4. Document lessons learned

### Rollback Procedure

**Automatic Rollback**:
- Health check failures trigger automatic rollback
- Error rate thresholds trigger rollback
- Performance degradation triggers rollback

**Manual Rollback**:
1. Identify issue
2. Assess impact
3. Execute rollback
4. Verify recovery
5. Investigate root cause

### Scaling Procedures

**Horizontal Pod Autoscaling**:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: tempus-core-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: tempus-core
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

**Vertical Scaling**:
- Monitor resource utilization
- Adjust resource requests/limits
- Consider instance type upgrades

## Disaster Recovery

### Backup Procedures

**Database Backups**:
- Automated daily backups
- Point-in-time recovery capability
- Offsite backup storage

**Configuration Backups**:
- Version-controlled configuration
- Secret backup procedures
- Regular backup verification

### Recovery Procedures

**Database Recovery**:
1. Identify recovery point
2. Restore from backup
3. Verify data integrity
4. Update application configuration
5. Resume operations

**Application Recovery**:
1. Deploy last known good version
2. Verify health checks
3. Monitor metrics
4. Investigate root cause

## Security

### Container Security

**Image Scanning**:
```yaml
- name: Scan Docker image
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: tempus/core:${{ github.ref_name }}
    format: 'sarif'
    output: 'trivy-results.sarif'
```

**Runtime Security**:
- Non-root containers
- Read-only file systems where possible
- Resource limits
- Network policies

### Infrastructure Security

**Network Security**:
- VPC with private subnets
- Security groups with minimal access
- Network policies in Kubernetes
- TLS for all communications

**Access Control**:
- IAM roles with least privilege
- RBAC in Kubernetes
- MFA for all access
- Audit logging

## Conclusion

TEMPUS implements comprehensive DevOps and deployment strategies supporting both local development and enterprise production. The combination of infrastructure as code, CI/CD pipelines, containerization, orchestration, and operational procedures provides reliable, scalable, and secure deployment capabilities.

Regular review and updates to DevOps practices ensure the deployment strategy remains effective as the system evolves and best practices improve.
