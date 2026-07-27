# Migration Guide - TEMPUS

## Overview

This document provides comprehensive guidance for migrating between versions of TEMPUS, including database migrations, API changes, configuration updates, and deployment procedures.

## Migration Types

### Minor Version Migration (X.Y.Z → X.Y.Z+1)
- Backward compatible
- No breaking changes
- Optional migration
- Recommended within 30 days

### Major Version Migration (X.Y.Z → X+1.0.0)
- Breaking changes
- Required migration
- Migration window required
- Mandatory within 90 days

### Database Migration
- Schema changes
- Data migration
- Index changes
- Performance optimization

## Pre-Migration Checklist

### Planning
- [ ] Review release notes and breaking changes
- [ ] Identify affected components
- [ ] Plan migration window
- [ ] Notify stakeholders
- [ ] Schedule maintenance window

### Backup
- [ ] Create full database backup
- [ ] Verify backup integrity
- [ ] Backup configuration files
- [ ] Backup custom code and extensions
- [ ] Document current state

### Testing
- [ ] Test migration in staging environment
- [ ] Verify application functionality
- [ ] Test rollback procedure
- [ ] Performance testing
- [ ] Security testing

### Communication
- [ ] Notify users of maintenance window
- [ ] Update status page
- [ ] Prepare communication templates
- [ ] Identify support contacts

## Migration Procedures

### Database Migration

#### Using Alembic

**Generate Migration**
```bash
# Generate migration script
alembic revision --autogenerate -m "description"

# Review generated migration
alembic upgrade head
```

**Apply Migration**
```bash
# Apply migration to staging
alembic upgrade head

# Verify migration
alembic current
alembic history
```

**Rollback Migration**
```bash
# Rollback to previous version
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision_id>
```

**Production Migration**
```bash
# Step 1: Create backup
pg_dump -Fc tempus > tempus_backup_$(date +%Y%m%d).dump

# Step 2: Apply migration
alembic upgrade head

# Step 3: Verify migration
# Run verification queries

# Step 4: Monitor for issues
# Check logs and metrics
```

#### Manual Migration

**For Complex Migrations**
```sql
-- Example: Add new column with default
ALTER TABLE tasks ADD COLUMN priority VARCHAR(20) DEFAULT 'medium';
UPDATE tasks SET priority = 'medium' WHERE priority IS NULL;
ALTER TABLE tasks ALTER COLUMN priority SET NOT NULL;

-- Example: Create index
CREATE INDEX idx_tasks_user_status ON tasks(user_id, status);

-- Example: Migrate data
UPDATE memory_items SET layer = 'semantic' WHERE layer = 'short_term' AND created_at < NOW() - INTERVAL '7 days';
```

### Application Migration

#### Docker Image Update

**Pull New Image**
```bash
# Pull new image
docker pull tempus/api:v1.1.0

# Tag as latest
docker tag tempus/api:v1.1.0 tempus/api:latest
```

**Kubernetes Deployment**
```bash
# Update deployment image
kubectl set image deployment/tempus-api tempus-api=tempus/api:v1.1.0 -n tempus-prod

# Monitor rollout
kubectl rollout status deployment/tempus-api -n tempus-prod

# Check pod status
kubectl get pods -n tempus-prod -l app=tempus-api
```

#### Blue-Green Deployment

**Deploy to Green**
```bash
# Deploy new version to green
kubectl apply -f k8s/tempus-api-green.yaml

# Run smoke tests against green
# Test critical endpoints

# Switch traffic to green
kubectl patch ingress tempus-api -n tempus-prod -p '{"spec":{"rules":[{"host":"api.tempus.ai","http":{"paths":[{"path":"/","backend":{"serviceName":"tempus-api-green","servicePort":80}}]}}]}}'
```

**Rollback if Needed**
```bash
# Switch traffic back to blue
kubectl patch ingress tempus-api -n tempus-prod -p '{"spec":{"rules":[{"host":"api.tempus.ai","http":{"paths":[{"path":"/","backend":{"serviceName":"tempus-api-blue","servicePort":80}}]}}]}}'

# Investigate green issues
# Fix and redeploy
```

### Configuration Migration

#### Environment Variables

**Review Changes**
```bash
# Compare old and new configuration
diff .env.old .env.new
```

**Update Configuration**
```bash
# Update Kubernetes ConfigMap
kubectl create configmap tempus-config --from-env-file=.env.new --dry-run=client -o yaml | kubectl apply -f -

# Restart pods to pick up new config
kubectl rollout restart deployment/tempus-api -n tempus-prod
```

#### Secrets Migration

**Rotate Secrets**
```bash
# Generate new secrets
# Update AWS Secrets Manager
aws secretsmanager put-secret-value --secret-id tempus/prod --secret-string file://secrets.json

# Restart pods to pick up new secrets
kubectl rollout restart deployment/tempus-api -n tempus-prod
```

### Extension Migration

#### Chrome Extension

**Update Manifest**
```json
{
  "version": "1.1.0",
  "manifest_version": 3
}
```

**Publish Update**
```bash
# Build extension
pnpm build:chrome

# Submit to Chrome Web Store
# Follow Chrome Web Store submission process
```

#### VS Code Extension

**Update Package.json**
```json
{
  "version": "1.1.0"
}
```

**Publish Update**
```bash
# Build extension
pnpm build:vscode

# Publish to marketplace
vsce publish
```

## Version-Specific Migrations

### Migration to v1.1.0

**Breaking Changes**
- API endpoint changes: `/api/v1/tasks` → `/api/v2/tasks`
- Database schema: Added `priority` column to `tasks` table

**Migration Steps**
1. Update database schema
2. Update API client code
3. Update extension API calls
4. Test all functionality
5. Deploy to production

**Rollback Procedure**
1. Revert API client code
2. Rollback database schema
3. Revert extension API calls
4. Verify functionality

### Migration to v2.0.0

**Breaking Changes**
- Authentication: JWT token format changed
- Database: Major schema restructure
- Configuration: New configuration format

**Migration Steps**
1. Backup all data
2. Migrate database schema
3. Migrate authentication tokens
4. Update configuration
5. Update all clients
6. Test thoroughly
7. Deploy to production

**Rollback Procedure**
1. Restore database from backup
2. Revert configuration
3. Revert clients
4. Verify functionality

## Post-Migration Verification

### Database Verification

**Schema Verification**
```sql
-- Check table structure
\d tasks
\d memory_items

-- Check indexes
SELECT indexname FROM pg_indexes WHERE tablename = 'tasks';

-- Check data integrity
SELECT COUNT(*) FROM tasks;
SELECT COUNT(*) FROM memory_items;
```

**Data Verification**
```sql
-- Verify data migration
SELECT COUNT(*) FROM tasks WHERE priority IS NOT NULL;

-- Verify relationships
SELECT COUNT(*) FROM tasks WHERE user_id NOT IN (SELECT id FROM users);
```

### Application Verification

**Health Checks**
```bash
# Check application health
curl https://api.tempus.ai/health/live

# Check readiness
curl https://api.tempus.ai/health/ready
```

**Functional Testing**
```bash
# Test API endpoints
curl https://api.tempus.ai/api/v1/tasks

# Test authentication
curl -H "Authorization: Bearer $TOKEN" https://api.tempus.ai/api/v1/tasks

# Test WebSocket connection
wscat -c wss://api.tempus.ai/ws
```

### Performance Verification

**Load Testing**
```bash
# Run load test with k6
k6 run load-test.js

# Verify performance metrics
# Check response times
# Check error rates
```

**Monitoring**
```bash
# Check metrics in Prometheus
# Check logs in Loki
# Check traces in Jaeger
```

## Rollback Procedures

### Database Rollback

**Using Alembic**
```bash
# Rollback to previous version
alembic downgrade -1

# Verify rollback
alembic current
```

**Manual Rollback**
```sql
-- Example: Drop new column
ALTER TABLE tasks DROP COLUMN priority;

-- Example: Drop new index
DROP INDEX idx_tasks_user_status;
```

**Restore from Backup**
```bash
# Restore from backup
pg_restore -h postgres-tempus.xxx.rds.amazonaws.com -U tempus -d tempus tempus_backup_20260722.dump
```

### Application Rollback

**Kubernetes Rollback**
```bash
# Rollback deployment
kubectl rollout undo deployment/tempus-api -n tempus-prod

# Verify rollback
kubectl rollout status deployment/tempus-api -n tempus-prod
```

**Docker Rollback**
```bash
# Pull previous image
docker pull tempus/api:v1.0.0

# Tag as latest
docker tag tempus/api:v1.0.0 tempus/api:latest

# Restart containers
docker-compose restart
```

### Configuration Rollback

**Restore Configuration**
```bash
# Restore from backup
cp .env.backup .env

# Restart pods
kubectl rollout restart deployment/tempus-api -n tempus-prod
```

## Migration Best Practices

### Planning
- Always plan migration windows during low-traffic periods
- Allow buffer time for unexpected issues
- Have rollback plan ready before starting
- Communicate clearly with all stakeholders

### Testing
- Always test in staging first
- Test rollback procedure
- Perform load testing for major changes
- Test with realistic data volumes

### Execution
- Use blue-green deployment for zero downtime
- Monitor closely during migration
- Have team on standby during migration
- Document any issues encountered

### Verification
- Verify all functionality post-migration
- Monitor metrics for 24 hours
- Check logs for errors
- Gather user feedback

## Troubleshooting

### Common Issues

**Migration Fails**
- Check database connection
- Verify migration script syntax
- Check for data conflicts
- Review error logs

**Application Errors**
- Check configuration changes
- Verify API compatibility
- Check for missing dependencies
- Review application logs

**Performance Degradation**
- Check database query performance
- Verify index usage
- Check resource utilization
- Review slow queries

### Debugging Commands

**Database Debugging**
```sql
-- Check running queries
SELECT * FROM pg_stat_activity WHERE state = 'active';

-- Check query performance
SELECT * FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;

-- Check locks
SELECT * FROM pg_locks;
```

**Application Debugging**
```bash
# Check pod logs
kubectl logs -n tempus-prod -l app=tempus-api --tail=100

# Check pod status
kubectl describe pod <pod-name> -n tempus-prod

# Check events
kubectl get events -n tempus-prod --sort-by='.lastTimestamp'
```

## Conclusion

This migration guide provides comprehensive procedures for migrating between versions of TEMPUS. Following these procedures ensures smooth migrations with minimal downtime and risk.

Key migration strengths:
1. Clear migration types and procedures
2. Comprehensive pre-migration checklist
3. Detailed database migration steps
4. Blue-green deployment for zero downtime
5. Thorough post-migration verification
6. Robust rollback procedures
7. Troubleshooting guidance
