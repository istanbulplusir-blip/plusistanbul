#!/bin/bash
# اسکریپت نصب امن برای Peykan Tourism Platform
# اجرا کنید: sudo bash deploy-secure.sh

set -e

echo "🚀 شروع نصب امن Peykan Tourism Platform..."

# بررسی دسترسی root
if [ "$EUID" -ne 0 ]; then
    echo "❌ این اسکریپت باید با دسترسی root اجرا شود"
    exit 1
fi

# 1. نصب وابستگی‌ها
echo "📦 نصب وابستگی‌ها..."
apt update
apt install -y docker.io docker-compose-plugin iptables-persistent ufw fail2ban

# 2. تنظیم فایروال
echo "🔥 تنظیم فایروال..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# 3. تنظیم iptables برای Docker
echo "🐳 تنظیم امنیت Docker..."
iptables -I DOCKER-USER -p tcp --dport 5432 -j DROP
iptables -I DOCKER-USER -p tcp --dport 6379 -j DROP
iptables -I DOCKER-USER -p tcp --dport 8000 -j DROP
iptables -I DOCKER-USER -p tcp --dport 3000 -j DROP

# 4. تنظیم fail2ban
echo "🛡️ تنظیم fail2ban..."
cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log

[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
EOF

systemctl enable fail2ban
systemctl restart fail2ban

# 5. ایجاد کاربر غیر root برای Docker
echo "👤 ایجاد کاربر امن..."
useradd -m -s /bin/bash peykan
usermod -aG docker peykan

# 6. تنظیم مجوزات فایل‌ها
echo "📁 تنظیم مجوزات..."
chown -R peykan:peykan /opt/peykan-tourism
chmod 600 /opt/peykan-tourism/backend/.env.production
chmod 600 /opt/peykan-tourism/redis/redis.conf

# 7. ایجاد systemd service
echo "⚙️ ایجاد systemd service..."
cat > /etc/systemd/system/peykan-tourism.service << EOF
[Unit]
Description=Peykan Tourism Platform
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/peykan-tourism
ExecStart=/usr/bin/docker compose -f docker-compose.production-secure.yml up -d
ExecStop=/usr/bin/docker compose -f docker-compose.production-secure.yml down
TimeoutStartSec=0
User=peykan
Group=peykan

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable peykan-tourism

# 8. ذخیره تنظیمات فایروال
echo "💾 ذخیره تنظیمات..."
netfilter-persistent save

# 9. تولید کلیدهای امن
echo "🔑 تولید کلیدهای امن..."
SECRET_KEY=$(openssl rand -base64 50)
JWT_SECRET=$(openssl rand -base64 50)
REDIS_PASSWORD=$(openssl rand -base64 32)
POSTGRES_PASSWORD=$(openssl rand -base64 32)

echo "📝 کلیدهای تولید شده:"
echo "SECRET_KEY=$SECRET_KEY"
echo "JWT_SECRET_KEY=$JWT_SECRET"
echo "REDIS_PASSWORD=$REDIS_PASSWORD"
echo "POSTGRES_PASSWORD=$POSTGRES_PASSWORD"
echo ""
echo "⚠️ این کلیدها را در فایل .env.production قرار دهید!"

echo "✅ نصب امن تکمیل شد!"
echo "🔧 برای شروع سرویس: sudo systemctl start peykan-tourism"
echo "📊 برای بررسی وضعیت: sudo systemctl status peykan-tourism"
