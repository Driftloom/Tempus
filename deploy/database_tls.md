# Database TLS/SSL Configuration

## Overview

This document provides guidance for configuring TLS/SSL encryption for PostgreSQL database connections in TEMPUS.

## PostgreSQL SSL Configuration

### Step 1: Enable SSL on PostgreSQL Server

Edit `postgresql.conf`:

```conf
# Enable SSL
ssl = on
ssl_cert_file = 'server.crt'
ssl_key_file = 'server.key'
ssl_ca_file = 'root.crt'

# Require SSL for all connections
ssl_protocols = 'TLSv1.2,TLSv1.3'
ssl_ciphers = 'HIGH:MEDIUM:+3DES:!aNULL'
ssl_prefer_server_ciphers = on
```

### Step 2: Generate SSL Certificates

#### Self-Signed Certificates (Development)

```bash
# Generate CA
openssl genrsa -out rootCA.key 4096
openssl req -x509 -new -nodes -key rootCA.key -sha256 -days 3650 -out rootCA.crt

# Generate server certificate
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr
openssl x509 -req -in server.csr -CA rootCA.crt -CAkey rootCA.key -CAcreateserial -out server.crt -days 365 -sha256
```

#### Production Certificates (Let's Encrypt or Commercial CA)

Use certificates from a trusted CA for production.

### Step 3: Configure Client SSL

Update `DATABASE_URL` in `.env`:

```bash
# Require SSL
DATABASE_URL=postgresql+asyncpg://tempus:password@localhost:5432/tempus?sslmode=require

# Verify server certificate (recommended for production)
DATABASE_URL=postgresql+asyncpg://tempus:password@localhost:5432/tempus?sslmode=verify-full&sslrootcert=/path/to/root.crt
```

### SSL Modes

| Mode | Description |
|------|-------------|
| `disable` | No SSL (not recommended) |
| `allow` | Try SSL, fall back to non-SSL |
| `prefer` | Try SSL, fall back to non-SSL (default) |
| `require` | Require SSL, no certificate verification |
| `verify-ca` | Require SSL and verify CA |
| `verify-full` | Require SSL and verify CA and hostname |

### Step 4: Update Docker Compose

For development with Docker, update `deploy/docker-compose.yml`:

```yaml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: tempus
      POSTGRES_USER: tempus
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./certs/server.crt:/var/lib/postgresql/server.crt:ro
      - ./certs/server.key:/var/lib/postgresql/server.key:ro
    command:
      - "postgres"
      - "-c"
      - "ssl=on"
      - "-c"
      - "ssl_cert_file=/var/lib/postgresql/server.crt"
      - "-c"
      - "ssl_key_file=/var/lib/postgresql/server.key"
```

### Step 5: Update Application Configuration

Update `apps/core/app/core/config.py`:

```python
class Settings(BaseSettings):
    # Database with SSL
    database_url: str
    database_ssl_mode: str = "require"  # verify-full for production
    database_ssl_root_cert: str | None = None
```

### Step 6: Verify SSL Connection

Test the connection:

```bash
# Using psql
psql "postgresql://tempus:password@localhost:5432/tempus?sslmode=require"

# Check if SSL is being used
psql -c "SELECT ssl_is_used(), ssl_version();"
```

## Cloud Provider SSL

### AWS RDS
SSL is enabled by default. Update connection string:

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@db-instance.region.rds.amazonaws.com/dbname?sslmode=require
```

### Google Cloud SQL
SSL is required. Download client certificate and update connection:

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@db-instance/dbname?sslmode=require&sslrootcert=/path/to/client-cert.pem
```

### Azure Database for PostgreSQL
SSL is required by default:

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@db-instance.postgres.database.azure.com/dbname?sslmode=require
```

## Environment Variables

Add to `.env.example`:

```bash
# Database SSL Configuration
DATABASE_SSL_MODE=require  # disable, allow, prefer, require, verify-ca, verify-full
DATABASE_SSL_ROOT_CERT=/path/to/root.crt  # For verify-ca and verify-full
```

## Security Best Practices

1. **Always use SSL in production** - Set `sslmode=require` at minimum
2. **Verify certificates in production** - Use `sslmode=verify-full`
3. **Use strong ciphers** - Configure `ssl_ciphers` in postgresql.conf
4. **Rotate certificates** - Before expiration (typically 1 year)
5. **Monitor SSL connections** - Log SSL usage and certificate expiry

## Troubleshooting

### Connection Refused
- Check PostgreSQL is running with SSL enabled
- Verify certificate files exist and have correct permissions

### Certificate Verification Failed
- Ensure `sslrootcert` points to correct CA certificate
- Check certificate chain is complete

### Performance Issues
- SSL adds overhead (~5-10%)
- Consider connection pooling to mitigate
- Use hardware acceleration if available

## References

- PostgreSQL SSL Documentation: https://www.postgresql.org/docs/current/ssl-tcp.html
- asyncpg SSL: https://magicstack.github.io/asyncpg/usage.html#ssl
- AWS RDS SSL: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.SSL.html
