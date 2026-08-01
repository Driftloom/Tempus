#!/bin/bash
# PostgreSQL restore script for TEMPUS
# Usage: ./restore_database.sh <backup_file>

set -e

# Configuration
BACKUP_FILE="${1}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-tempus}"
DB_USER="${DB_USER:-tempus}"

# Validate backup file
if [ -z "${BACKUP_FILE}" ]; then
    echo "ERROR: Backup file path required"
    echo "Usage: $0 <backup_file>"
    exit 1
fi

if [ ! -f "${BACKUP_FILE}" ]; then
    echo "ERROR: Backup file not found: ${BACKUP_FILE}"
    exit 1
fi

# Confirm restore
echo "WARNING: This will restore the database from backup."
echo "Backup file: ${BACKUP_FILE}"
echo "Database: ${DB_NAME}"
echo ""
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "${CONFIRM}" != "yes" ]; then
    echo "Restore cancelled"
    exit 0
fi

# Perform restore
echo "Starting restore at $(date)"
gunzip -c "${BACKUP_FILE}" | PGPASSWORD="${DB_PASSWORD}" psql \
    -h "${DB_HOST}" \
    -p "${DB_PORT}" \
    -U "${DB_USER}" \
    -d "${DB_NAME}"

echo "Restore completed successfully at $(date)"
