#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
docker exec postgres pg_dump -U user appdb > $BACKUP_DIR/backup_$TIMESTAMP.sql