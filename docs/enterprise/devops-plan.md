# DevOps Plan

## Executive Summary

This document outlines the DevOps strategy for TEMPUS including Docker containerization, Kubernetes deployment, Terraform infrastructure as code, CI/CD pipelines, and deployment automation.

## Containerization Strategy

### Docker Images

**Multi-stage Builds:**

**Python Backend:**
```dockerfile
# Build stage
FROM python:3.11-slim as builder
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

# Runtime stage
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Chrome Extension:**
```dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
```

### Docker Compose (Development)

```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: tempus
      POSTGRES_USER: tempus
      POSTGRES_PASSWORD: tempus_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  api:
    build: ./apps/core
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://tempus:tempus_password@postgres:5432/tempus
      REDIS_URL: redis://redis:6379
    depends_on:
      - postgres
      - redis

  celery:
    build: ./apps/core
    command: celery -A app.notifications.tasks worker --loglevel=info
    environment:
      DATABASE_URL: postgresql+asyncpg://tempus:tempus_password@postgres:5432/tempus
      REDIS_URL: redis://redis:6379
    depends_on:
      - postgres
      - redis

volumes:
  postgres_data:
  redis_data:
```

## Kubernetes Deployment

### Namespace Structure

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: tempus-prod
```

### ConfigMaps

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: tempus-config
  namespace: tempus-prod
data:
  DATABASE_URL: "postgresql+asyncpg://tempus:$(POSTGRES_PASSWORD)@postgres:5432/tempus"
  REDIS_URL: "redis://redis:6379"
  LOG_LEVEL: "INFO"
```

### Secrets

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: tempus-secrets
  namespace: tempus-prod
type: Opaque
stringData:
  POSTGRES_PASSWORD: "your-secure-password"
  JWT_SECRET: "your-jwt-secret"
  ANTHROPIC_API_KEY: "your-api-key"
  OPENAI_API_KEY: "your-api-key"
```

### Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tempus-api
  namespace: tempus-prod
spec:
  replicas: 3
  selector:
    matchLabels:
      app: tempus-api
  template:
    metadata:
      labels:
        app: tempus-api
    spec:
      containers:
      - name: api
        image: tempus/api:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: tempus-config
        - secretRef:
            name: tempus-secrets
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: tempus-api
  namespace: tempus-prod
spec:
  selector:
    app: tempus-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: tempus-api-hpa
  namespace: tempus-prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: tempus-api
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

## Terraform Infrastructure

### Provider Configuration

```hcl
provider "aws" {
  region = var.aws_region
}

provider "kubernetes" {
  config_path = "~/.kube/config"
}
```

### VPC

```hcl
resource "aws_vpc" "tempus" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "tempus-vpc"
  }
}
```

### EKS Cluster

```hcl
resource "aws_eks_cluster" "tempus" {
  name     = "tempus-cluster"
  role_arn = aws_iam_role.eks_cluster.arn
  version  = "1.28"

  vpc_config {
    subnet_ids = aws_subnet.public[*].id
  }
}
```

### RDS PostgreSQL

```hcl
resource "aws_db_instance" "tempus" {
  identifier     = "postgres-tempus"
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = "db.t3.medium"
  
  allocated_storage     = 100
  storage_encrypted     = true
  multi_az              = true
  
  db_name  = "tempus"
  username = "tempus"
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.tempus.id]
  db_subnet_group_name   = aws_db_subnet_group.tempus.name
  
  backup_retention_period = 30
  backup_window          = "03:00-04:00"
  
  tags = {
    Name = "tempus-postgres"
  }
}
```

### ElastiCache Redis

```hcl
resource "aws_elasticache_cluster" "tempus" {
  cluster_id           = "tempus-redis"
  engine               = "redis"
  engine_version       = "7.0"
  node_type            = "cache.t3.medium"
  num_cache_nodes      = 2
  parameter_group_name = "default.redis7"
  
  port = 6379
  
  security_group_ids = [aws_security_group.tempus.id]
  subnet_group_name  = aws_elasticache_subnet_group.tempus.name
  
  tags = {
    Name = "tempus-redis"
  }
}
```

## CI/CD Pipeline

### GitHub Actions

**Build and Test:**
```yaml
name: Build and Test

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd apps/core
        pip install -e ".[dev]"
    
    - name: Run linter
      run: |
        cd apps/core
        ruff check .
    
    - name: Run type checker
      run: |
        cd apps/core
        mypy .
    
    - name: Run tests
      run: |
        cd apps/core
        pytest --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

**Build and Push:**
```yaml
name: Build and Push

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
    
    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: ./apps/core
        push: true
        tags: tempus/api:${{ github.ref_name }}
```

**Deploy to Kubernetes:**
```yaml
name: Deploy

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure kubectl
      uses: azure/k8s-set-context@v3
      with:
        method: kubeconfig
        kubeconfig: ${{ secrets.KUBE_CONFIG }}
    
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/tempus-api \
          api=tempus/api:${{ github.ref_name }} \
          -n tempus-prod
```

## Deployment Strategy

### Blue-Green Deployment

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: tempus-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: tempus-api
  template:
    metadata:
      labels:
        app: tempus-api
    spec:
      containers:
      - name: api
        image: tempus/api:latest
  strategy:
    blueGreen:
      activeService: tempus-api-active
      previewService: tempus-api-preview
      autoPromotionEnabled: false
      scaleDownDelaySeconds: 30
```

### Canary Deployment

```yaml
strategy:
  canary:
    canaryService: tempus-api-canary
    stableService: tempus-api-stable
    trafficRouting:
      istio:
        virtualService:
          name: tempus-api-vs
    analysis:
      templates:
      - templateName: success-rate
      args:
      - name: service-name
        value: tempus-api-canary
    steps:
    - setWeight: 10
    - pause: {duration: 10m}
    - setWeight: 25
    - pause: {duration: 10m}
    - setWeight: 50
    - pause: {duration: 10m}
    - setWeight: 100
```

## Monitoring and Alerting

### Prometheus Operator

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: tempus-api
  namespace: tempus-prod
spec:
  selector:
    matchLabels:
      app: tempus-api
  endpoints:
  - port: web
    path: /metrics
```

### Alertmanager

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: alertmanager-config
data:
  alertmanager.yml: |
    global:
      resolve_timeout: 5m
    route:
      receiver: 'default'
      group_wait: 10s
      group_interval: 10s
      repeat_interval: 12h
    receivers:
    - name: 'default'
      slack_configs:
      - api_url: 'https://hooks.slack.com/services/...'
        channel: '#tempus-alerts'
```

## Conclusion

This DevOps plan provides comprehensive containerization, Kubernetes deployment, Terraform infrastructure, and CI/CD automation for TEMPUS. Implementation will enable automated, scalable, and reliable deployments.

**Total Estimated Effort:** 120-160 hours
**Timeline:** 4-6 weeks for full implementation
