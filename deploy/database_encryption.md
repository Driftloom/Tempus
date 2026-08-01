# Database Encryption at Rest Configuration

## Overview

This document provides guidance for enabling encryption at rest for the PostgreSQL database used by TEMPUS.

## PostgreSQL Encryption Options

### Option 1: Transparent Data Encryption (TDE) - Recommended

PostgreSQL does not have built-in TDE, but can be achieved through:

#### Using File System Encryption
Encrypt the entire data directory at the filesystem level:

```bash
 # On Linux with LUKS
 cryptsetup luksFormat /dev/sdb1
 cryptsetup luksOpen /dev/sdb1 tempus_db
 mkfs.ext4 /dev/mapper/tempus_db
 mount /dev/mapper/tempus_db /var/lib/postgresql
```

#### Using Cloud Provider Encryption
If using managed PostgreSQL (AWS RDS, Google Cloud SQL, Azure Database):
- Enable encryption at rest in the cloud provider console
- Most providers offer this at no additional cost

### Option 2: Application-Level Encryption

Encrypt sensitive fields before storage using the existing encryption manager:

```python
from app.security.encryption import EncryptionManager

encryption_manager = EncryptionManager()

# Encrypt sensitive data
encrypted_data = encryption_manager.encrypt("sensitive_information")

# Store encrypted_data in database
# Decrypt when needed
decrypted_data = encryption_manager.decrypt(encrypted_data)
```

### Option 3: PostgreSQL Extension: pgcrypto

Use the pgcrypto extension for column-level encryption:

```sql
-- Enable extension
CREATE EXTENSION pgcrypto;

-- Encrypt data
INSERT INTO sensitive_data (encrypted_field)
VALUES (pgp_sym_encrypt('my secret', 'encryption_key'));

-- Decrypt data
SELECT pgp_sym_decrypt(encrypted_field::bytea, 'encryption_key')
FROM sensitive_data;
```

## Recommended Configuration for TEMPUS

### Step 1: Enable File System Encryption (Production)

For production deployments, encrypt the PostgreSQL data directory:

**AWS EBS:**
```bash
# Create encrypted volume
aws ec2 create-volume --size 100 --volume-type gp3 --encrypted --kms-key-id <key-id>
```

**Google Cloud Persistent Disk:**
```bash
# Create encrypted disk
gcloud compute disks create tempus-db --size 100GB --type pd-balanced --disk-encryption-key <key-id>
```

### Step 2: Enable pgcrypto Extension

Add to Alembic migration:

```python
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

def downgrade():
    op.execute("DROP EXTENSION IF EXISTS pgcrypto")
```

### Step 3: Encrypt Sensitive Fields

Identify and encrypt sensitive fields:
- User passwords (already hashed with bcrypt)
- API keys
- OAuth tokens
- PII in memory items

### Step 4: Configure Backup Encryption

Ensure backups are encrypted:

```bash
# Encrypt backup with GPG
pg_dump tempus | gzip | gpg --encrypt --recipient <key-id> > backup.sql.gz.gpg
```

## Environment Variables

Add to `.env`:

```bash
# Database Encryption
DB_ENCRYPTION_ENABLED=true
DB_ENCRYPTION_KEY_ID=<kms-key-id>  # For cloud KMS
```

## Verification

Verify encryption is working:

```bash
# Check data directory is encrypted
lsblk -f

# Check pgcrypto extension
psql -d tempus -c "SELECT * FROM pg_extension WHERE extname = 'pgcrypto';"
```

## References

- PostgreSQL Security: https://www.postgresql.org/docs/current/security.html
- pgcrypto Documentation: https://www.postgresql.org/docs/current/pgcrypto.html
- AWS RDS Encryption: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Overview.Encryption.html
