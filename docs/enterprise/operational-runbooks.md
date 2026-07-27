# Operational Runbooks and Incident Response Playbooks - TEMPUS

## Overview

This document provides operational runbooks for common procedures and incident response playbooks for different incident types in the TEMPUS system.

## Operational Runbooks

### Runbook 1: Database Backup and Restore

#### Backup Procedure

**Daily Automated Backups**
1. Verify automated backup schedule (daily at 3:00 AM UTC)
2. Check backup completion in CloudWatch logs
3. Verify backup integrity with pg_verifybackup
4. Confirm backup stored in S3 with lifecycle policy

**Manual Backup**
```bash
# Connect to PostgreSQL instance
psql -h postgres-tempus.xxx.us-east-1.rds.amazonaws.com -U tempus -d tempus

# Create backup
pg_dump -Fc tempus > tempus_backup_$(date +%Y%m%d).dump

# Upload to S3
aws s3 cp tempus_backup_$(date +%Y%m%d).dump s3://tempus-backups/
```

**Verification**
1. Check backup file size matches expected size
2. Verify backup can be restored to test instance
3. Document backup completion in runbook log

#### Restore Procedure

**Point-in-Time Recovery (PITR)**
1. Identify recovery timestamp
2. Stop application to prevent writes
3. Initiate PITR from AWS RDS console
4. Select recovery timestamp
5. Restore to new instance
6. Verify data integrity
7. Update application connection string
8. Restart application
9. Monitor for errors

**Full Restore from Backup**
```bash
# Download backup from S3
aws s3 cp s3://tempus-backups/tempus_backup_20260722.dump .

# Restore to test instance
pg_restore -h test-postgres.xxx.rds.amazonaws.com -U tempus -d tempus tempus_backup_20260722.dump

# Verify data
psql -h test-postgres.xxx.rds.amazonaws.com -U tempus -d tempus -c "SELECT COUNT(*) FROM users;"
```

### Runbook 2: Application Deployment

#### Blue-Green Deployment

**Prerequisites**
1. Verify all tests pass in CI/CD
2. Confirm Docker image built and pushed
3. Check database migrations ready
4. Verify configuration updated

**Deployment Steps**
1. Deploy new version to green environment
2. Run smoke tests against green
3. Switch 10% traffic to green
4. Monitor green for 5 minutes
5. Switch 50% traffic to green
6. Monitor green for 10 minutes
7. Switch 100% traffic to green
8. Keep blue for rollback (30 minutes)
9. Decommission blue after successful deployment

**Rollback Procedure**
1. Switch traffic back to blue
2. Investigate green environment issues
3. Fix issues in green
4. Resume deployment from step 1

#### Canary Deployment

**Deployment Steps**
1. Deploy new version to canary
2. Route 5% traffic to canary
3. Monitor canary metrics (error rate, latency)
4. Gradually increase traffic (10%, 25%, 50%)
5. If metrics healthy, proceed to full rollout
6. If metrics degraded, rollback immediately

**Rollback Procedure**
1. Route all traffic back to stable
2. Scale down canary to zero
3. Investigate canary issues
4. Fix and redeploy

### Runbook 3: Service Scaling

#### Horizontal Pod Autoscaler (HPA)

**Check Current HPA Status**
```bash
kubectl get hpa -n tempus-prod
kubectl describe hpa tempus-api -n tempus-prod
```

**Adjust HPA Configuration**
```bash
# Edit HPA
kubectl edit hpa tempus-api -n tempus-prod

# Example: Increase max replicas
spec:
  maxReplicas: 20
  minReplicas: 5
```

**Manual Scaling**
```bash
# Scale up
kubectl scale deployment tempus-api --replicas=10 -n tempus-prod

# Scale down
kubectl scale deployment tempus-api --replicas=3 -n tempus-prod
```

#### Cluster Autoscaler

**Check Cluster Autoscaler Status**
```bash
kubectl get configmap cluster-autoscaler-status -n kube-system
```

**Adjust Cluster Autoscaler**
```bash
# Edit node group auto-scaling
aws eks update-nodegroup-config \
  --cluster-name tempus-cluster \
  --nodegroup-name tempus-nodegroup \
  --scaling-config minSize=3,maxSize=20
```

### Runbook 4: Certificate Rotation

#### TLS Certificate Rotation

**Prerequisites**
1. New certificate obtained from ACM or cert-manager
2. Certificate validated and tested
3. Maintenance window scheduled

**Rotation Steps**
1. Update Ingress resource with new certificate
2. Verify certificate loaded by NGINX
3. Test SSL connection with new certificate
4. Monitor for SSL errors
5. Keep old certificate for rollback (24 hours)

**Verification**
```bash
# Test SSL connection
openssl s_client -connect api.tempus.ai:443 -servername api.tempus.ai

# Check certificate details
echo | openssl s_client -connect api.tempus.ai:443 2>/dev/null | openssl x509 -noout -dates
```

### Runbook 5: Secret Rotation

#### Database Password Rotation

**Prerequisites**
1. Maintenance window scheduled
2. Application configured to read from Secrets Manager
3. Rollback procedure documented

**Rotation Steps**
1. Generate new password
2. Update password in Secrets Manager
3. Update password in PostgreSQL
4. Restart application pods
5. Verify database connectivity
6. Monitor for authentication errors

**PostgreSQL Password Update**
```bash
# Connect as superuser
psql -h postgres-tempus.xxx.rds.amazonaws.com -U postgres

# Change password
ALTER USER tempus WITH PASSWORD 'new_secure_password';

# Verify connection
psql -h postgres-tempus.xxx.rds.amazonaws.com -U tempus -d tempus
```

#### API Key Rotation

**Rotation Steps**
1. Generate new API keys
2. Update keys in Secrets Manager
3. Update application configuration
4. Restart application
5. Verify API connectivity
6. Revoke old keys

### Runbook 6: Log Aggregation and Analysis

#### Log Collection

**Check Log Aggregation**
```bash
# Check Loki logs
kubectl logs -n loki -l app=loki

# Check Fluent Bit logs
kubectl logs -n tempus-prod -l app=fluent-bit
```

**Log Analysis**
```bash
# Search for errors in logs
logcli query --from="24h" '{app="tempus-api"} |= "ERROR"'

# Search for specific user activity
logcli query --from="1h" '{user_id="user-123"}'

# Export logs for analysis
logcli query --from="24h" '{app="tempus-api"}' > tempus_logs.json
```

#### Log Retention

**Configure Log Retention**
```bash
# Update Loki retention
kubectl edit configmap loki-config -n loki

# Set retention period
retention:
  enabled: true
  period: 30d
```

## Incident Response Playbooks

### Incident Response Process

**1. Detection**
- Alert received from monitoring
- Incident severity assessed
- Incident declared
- On-call engineer notified

**2. Triage**
- Gather initial information
- Assess impact and scope
- Determine severity level
- Assign incident commander

**3. Mitigation**
- Implement immediate fixes
- Stabilize system
- Prevent further damage
- Communicate status

**4. Resolution**
- Implement permanent fix
- Verify fix resolves issue
- Monitor for recurrence
- Close incident

**5. Post-Incident**
- Conduct post-mortem
- Document lessons learned
- Update runbooks
- Implement improvements

### Incident Severity Levels

**Severity 1 (Critical)**
- System completely down
- Data loss or corruption
- Security breach
- Impact: All users

**Severity 2 (High)**
- Major functionality degraded
- Significant performance degradation
- Partial data loss
- Impact: Most users

**Severity 3 (Medium)**
- Minor functionality degraded
- Performance degradation
- No data loss
- Impact: Some users

**Severity 4 (Low)**
- Cosmetic issues
- Minor performance impact
- No functional impact
- Impact: Few users

### Playbook 1: Application Outage

**Detection**
- Alert: API error rate > 50%
- Alert: Application health check failing
- User reports: Application inaccessible

**Triage**
1. Check application pod status
2. Check application logs
3. Check database connectivity
4. Check external dependencies

**Mitigation**
```bash
# Check pod status
kubectl get pods -n tempus-prod

# Check pod logs
kubectl logs -n tempus-prod -l app=tempus-api --tail=100

# Restart pods if needed
kubectl rollout restart deployment tempus-api -n tempus-prod

# Scale up if resource exhaustion
kubectl scale deployment tempus-api --replicas=10 -n tempus-prod
```

**Resolution**
1. Identify root cause
2. Implement permanent fix
3. Update runbook if needed
4. Monitor for recurrence

### Playbook 2: Database Outage

**Detection**
- Alert: Database connection errors
- Alert: Database latency > 5s
- User reports: Database errors

**Triage**
1. Check RDS instance status
2. Check database connection pool
3. Check database queries
4. Check database locks

**Mitigation**
```bash
# Check RDS status
aws rds describe-db-instances --db-instance-identifier postgres-tempus

# Check connection pool
kubectl exec -it tempus-api-xxx -n tempus-prod -- python -c "from app.database import engine; print(engine.pool.status())"

# Kill long-running queries if needed
psql -h postgres-tempus.xxx.rds.amazonaws.com -U tempus -d tempus -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'active' AND query_start < now() - interval '5 minutes';"
```

**Resolution**
1. Identify root cause (locks, long queries, connection exhaustion)
2. Implement permanent fix (query optimization, connection pool tuning)
3. Update runbook if needed
4. Monitor for recurrence

### Playbook 3: High Error Rate

**Detection**
- Alert: API error rate > 5%
- Alert: 5xx errors increasing
- User reports: Errors in application

**Triage**
1. Check error logs
2. Check error rate by endpoint
3. Check error rate by user
4. Check recent deployments

**Mitigation**
```bash
# Check error logs
logcli query --from="1h" '{app="tempus-api"} |= "ERROR"'

# Check error rate by endpoint
kubectl logs -n tempus-prod -l app=tempus-api | grep "ERROR" | awk '{print $NF}' | sort | uniq -c

# Rollback if recent deployment
kubectl rollout undo deployment tempus-api -n tempus-prod
```

**Resolution**
1. Identify root cause (deployment, bug, dependency)
2. Implement permanent fix
3. Update runbook if needed
4. Monitor for recurrence

### Playbook 4: High Latency

**Detection**
- Alert: API latency p95 > 500ms
- Alert: Database latency > 200ms
- User reports: Slow application

**Triage**
1. Check application latency metrics
2. Check database query latency
3. Check external service latency
4. Check resource utilization

**Mitigation**
```bash
# Check application latency
kubectl top pods -n tempus-prod

# Check database query latency
psql -h postgres-tempus.xxx.rds.amazonaws.com -U tempus -d tempus -c "SELECT * FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"

# Scale up if resource exhaustion
kubectl scale deployment tempus-api --replicas=10 -n tempus-prod

# Restart if memory leak
kubectl rollout restart deployment tempus-api -n tempus-prod
```

**Resolution**
1. Identify root cause (slow query, resource exhaustion, memory leak)
2. Implement permanent fix (query optimization, resource tuning, memory leak fix)
3. Update runbook if needed
4. Monitor for recurrence

### Playbook 5: Memory Exhaustion

**Detection**
- Alert: Memory usage > 90%
- Alert: OOMKilled events
- Application crashes

**Triage**
1. Check pod memory usage
2. Check memory leaks
3. Check memory limits
4. Check application memory profile

**Mitigation**
```bash
# Check memory usage
kubectl top pods -n tempus-prod --use-protocol-buffers

# Check OOMKilled events
kubectl get events -n tempus-prod --sort-by='.lastTimestamp' | grep OOMKilled

# Increase memory limits
kubectl set resources deployment tempus-api --limits=memory=1Gi -n tempus-prod

# Restart pods
kubectl rollout restart deployment tempus-api -n tempus-prod
```

**Resolution**
1. Identify root cause (memory leak, insufficient limits)
2. Implement permanent fix (memory leak fix, limit adjustment)
3. Update runbook if needed
4. Monitor for recurrence

### Playbook 6: Security Incident

**Detection**
- Alert: Unusual login activity
- Alert: SQL injection attempts
- Alert: Unauthorized access attempts
- User reports: Security concerns

**Triage**
1. Check authentication logs
2. Check authorization logs
3. Check security events
4. Assess scope of breach

**Mitigation**
```bash
# Check authentication logs
logcli query --from="24h" '{app="tempus-api"} |= "auth"'

# Block suspicious IPs
kubectl annotate ingress tempus-api nginx.ingress.kubernetes.io/block-cidrs="10.0.0.0/8" -n tempus-prod

# Rotate compromised credentials
# (Follow secret rotation runbook)

# Enable enhanced monitoring
kubectl set env deployment tempus-api LOG_LEVEL=DEBUG -n tempus-prod
```

**Resolution**
1. Identify root cause (compromised credentials, vulnerability)
2. Implement permanent fix (credential rotation, vulnerability patch)
3. Conduct security audit
4. Update runbook if needed
5. Monitor for recurrence

### Playbook 7: Data Loss

**Detection**
- Alert: Data deletion events
- Alert: Database corruption
- User reports: Missing data

**Triage**
1. Check database integrity
2. Check deletion logs
3. Check backup availability
4. Assess scope of data loss

**Mitigation**
```bash
# Check database integrity
psql -h postgres-tempus.xxx.rds.amazonaws.com -U tempus -d tempus -c "SELECT * FROM pg_stat_database WHERE datname = 'tempus';"

# Check deletion logs
logcli query --from="24h" '{app="tempus-api"} |= "DELETE"'

# Restore from backup if needed
# (Follow backup restore runbook)
```

**Resolution**
1. Identify root cause (accidental deletion, corruption)
2. Implement permanent fix (data recovery, corruption fix)
3. Update runbook if needed
4. Monitor for recurrence

### Playbook 8: External Service Outage

**Detection**
- Alert: External service errors
- Alert: External service latency
- User reports: External integration failures

**Triage**
1. Check external service status
2. Check external service logs
3. Check fallback mechanisms
4. Assess impact on functionality

**Mitigation**
```bash
# Check external service status
curl -I https://api.anthropic.com

# Check external service logs
logcli query --from="1h" '{app="tempus-api"} |= "anthropic"'

# Enable fallback to local provider
kubectl set env deployment tempus-api LLM_ROUTING_STRATEGY=local-only -n tempus-prod

# Restart pods
kubectl rollout restart deployment tempus-api -n tempus-prod
```

**Resolution**
1. Identify root cause (external service outage, API changes)
2. Implement permanent fix (retry logic, fallback mechanisms)
3. Update runbook if needed
4. Monitor for recurrence

## Communication Procedures

### Incident Communication

**Internal Communication**
1. Slack: #tempus-incidents channel
2. Email: on-call@tempus.ai
3. PagerDuty: On-call engineer

**External Communication**
1. Status page: status.tempus.ai
2. Email: customers@tempus.ai
3. Twitter: @tempus_status

**Communication Templates**

**Initial Incident Notification**
```
INCIDENT DECLARED

Severity: [SEVERITY]
Service: [SERVICE]
Impact: [IMPACT]
Started: [TIMESTAMP]
Incident Commander: [NAME]

Investigation in progress. Updates to follow.
```

**Status Update**
```
INCIDENT UPDATE

Incident ID: [ID]
Status: [STATUS]
Update: [UPDATE]
Next Update: [TIME]
```

**Resolution Notification**
```
INCIDENT RESOLVED

Incident ID: [ID]
Resolved At: [TIMESTAMP]
Resolution: [RESOLUTION]
Root Cause: [ROOT CAUSE]
Preventive Measures: [MEASURES]
```

## Post-Incident Procedures

### Post-Mortem

**Post-Mortem Template**
1. Incident Summary
2. Timeline of Events
3. Root Cause Analysis
4. Impact Assessment
5. Resolution Steps
6. Lessons Learned
7. Action Items
8. Follow-up Tasks

**Post-Mortem Meeting**
- Schedule within 48 hours of resolution
- Include all stakeholders
- Focus on process improvement, not blame
- Document action items with owners and deadlines

### Runbook Updates

**Update Triggers**
- Incident reveals gap in runbook
- New procedure needed
- Procedure needs improvement
- Technology stack changes

**Update Process**
1. Identify needed update
2. Draft update
3. Review with team
4. Approve update
5. Publish update
6. Train team on update

## Conclusion

These operational runbooks and incident response playbooks provide comprehensive guidance for common operational procedures and incident scenarios. Regular review and updates ensure they remain effective as the system evolves.

Key operational strengths:
1. Comprehensive runbooks for common procedures
2. Detailed incident response playbooks
3. Clear severity levels and escalation procedures
4. Communication templates and procedures
5. Post-incident analysis and improvement process
