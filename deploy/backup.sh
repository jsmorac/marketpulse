#!/bin/bash
set -euo pipefail

# Variables
DB_NAME="marketpulse"
DB_USER="marketpulse"
CONTAINER="marketpulse-postgres"
BACKUP_DIR="/tmp/mp_backups"
DATE=$(date +%Y-%m-%d)
FILENAME="marketpulse_${DATE}.sql.gz"

# Crear carpeta temporal
mkdir -p "$BACKUP_DIR"

# Hacer el dump y comprimir
docker exec "$CONTAINER" pg_dump -U "$DB_USER" -d "$DB_NAME" --no-password | gzip > "$BACKUP_DIR/$FILENAME"

# Subir a Backblaze
rclone copy "$BACKUP_DIR/$FILENAME" backblaze:market-pulse/postgres/

# Borrar el archivo local (ya está en Backblaze)
rm "$BACKUP_DIR/$FILENAME"

echo "Backup completado: $FILENAME"
