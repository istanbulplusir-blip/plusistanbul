#!/bin/bash
# اسکریپت پشتیبان‌گیری امن برای Peykan Tourism Platform
# اجرا کنید: sudo bash backup-secure.sh

set -e

BACKUP_DIR="/opt/backups/peykan"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="peykan_backup_$DATE"

echo "💾 شروع پشتیبان‌گیری امن Peykan Tourism Platform..."

# ایجاد دایرکتوری پشتیبان‌گیری
mkdir -p "$BACKUP_DIR"

# 1. پشتیبان‌گیری از Database
echo "🗄️ پشتیبان‌گیری از Database..."
docker exec peykan_postgres pg_dump -U peykan_user peykan > "$BACKUP_DIR/database_$BACKUP_NAME.sql"

# 2. پشتیبان‌گیری از Redis
echo "🔴 پشتیبان‌گیری از Redis..."
docker exec peykan_redis redis-cli -a "$REDIS_PASSWORD" BGSAVE
sleep 5
docker cp peykan_redis:/data/dump.rdb "$BACKUP_DIR/redis_$BACKUP_NAME.rdb"

# 3. پشتیبان‌گیری از Media files
echo "📁 پشتیبان‌گیری از Media files..."
docker run --rm -v peykan_media_volume:/data -v "$BACKUP_DIR":/backup alpine tar czf /backup/media_$BACKUP_NAME.tar.gz -C /data .

# 4. پشتیبان‌گیری از Static files
echo "📄 پشتیبان‌گیری از Static files..."
docker run --rm -v peykan_static_volume:/data -v "$BACKUP_DIR":/backup alpine tar czf /backup/static_$BACKUP_NAME.tar.gz -C /data .

# 5. پشتیبان‌گیری از Configuration files
echo "⚙️ پشتیبان‌گیری از Configuration files..."
tar czf "$BACKUP_DIR/config_$BACKUP_NAME.tar.gz" \
    docker-compose.production-secure.yml \
    backend/env.production-secure \
    redis/redis.conf \
    nginx/nginx-secure.conf

# 6. ایجاد فایل اطلاعات پشتیبان‌گیری
echo "📋 ایجاد فایل اطلاعات..."
cat > "$BACKUP_DIR/backup_info_$BACKUP_NAME.txt" << EOF
Peykan Tourism Platform Backup
Date: $(date)
Backup Name: $BACKUP_NAME
Files:
- database_$BACKUP_NAME.sql (PostgreSQL dump)
- redis_$BACKUP_NAME.rdb (Redis dump)
- media_$BACKUP_NAME.tar.gz (Media files)
- static_$BACKUP_NAME.tar.gz (Static files)
- config_$BACKUP_NAME.tar.gz (Configuration files)

Restore Commands:
1. Database: docker exec -i peykan_postgres psql -U peykan_user peykan < database_$BACKUP_NAME.sql
2. Redis: docker cp redis_$BACKUP_NAME.rdb peykan_redis:/data/dump.rdb && docker restart peykan_redis
3. Media: docker run --rm -v peykan_media_volume:/data -v $(pwd):/backup alpine tar xzf /backup/media_$BACKUP_NAME.tar.gz -C /data
4. Static: docker run --rm -v peykan_static_volume:/data -v $(pwd):/backup alpine tar xzf /backup/static_$BACKUP_NAME.tar.gz -C /data
EOF

# 7. فشرده‌سازی کل پشتیبان‌گیری
echo "📦 فشرده‌سازی پشتیبان‌گیری..."
cd "$BACKUP_DIR"
tar czf "../${BACKUP_NAME}_complete.tar.gz" *
cd ..

# 8. حذف فایل‌های موقت
echo "🧹 پاک‌سازی فایل‌های موقت..."
rm -rf "$BACKUP_DIR"

# 9. تنظیم مجوزات امن
echo "🔒 تنظیم مجوزات امن..."
chmod 600 "/opt/backups/${BACKUP_NAME}_complete.tar.gz"
chown root:root "/opt/backups/${BACKUP_NAME}_complete.tar.gz"

# 10. حذف پشتیبان‌گیری‌های قدیمی (بیش از 30 روز)
echo "🗑️ حذف پشتیبان‌گیری‌های قدیمی..."
find /opt/backups -name "peykan_backup_*.tar.gz" -mtime +30 -delete

echo "✅ پشتیبان‌گیری امن تکمیل شد!"
echo "📁 مکان پشتیبان‌گیری: /opt/backups/${BACKUP_NAME}_complete.tar.gz"
echo "📊 حجم فایل: $(du -h "/opt/backups/${BACKUP_NAME}_complete.tar.gz" | cut -f1)"
