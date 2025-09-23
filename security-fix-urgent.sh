#!/bin/bash
# فوری: بلاک کردن دسترسی بیرونی به Redis
# اجرا کنید: sudo bash security-fix-urgent.sh

echo "🚨 اقدامات امنیتی فوری برای Redis..."

# 1. بلاک کردن پورت 6379 از دسترسی بیرونی
echo "📝 بلاک کردن پورت 6379..."
sudo iptables -I DOCKER-USER -p tcp --dport 6379 -j DROP

# 2. بررسی قوانین فایروال
echo "🔍 بررسی قوانین فایروال..."
sudo iptables -L DOCKER-USER -n --line-numbers | grep 6379

# 3. بررسی وضعیت پورت‌ها
echo "🔍 بررسی وضعیت پورت‌ها..."
ss -tulnp | grep 6379 || echo "پورت 6379 بسته است ✅"

# 4. نصب iptables-persistent برای حفظ قوانین
echo "📦 نصب iptables-persistent..."
sudo apt update && sudo apt install -y iptables-persistent

# 5. ذخیره قوانین فایروال
echo "💾 ذخیره قوانین فایروال..."
sudo netfilter-persistent save

echo "✅ اقدامات امنیتی فوری تکمیل شد!"
echo "⚠️  توجه: Redis همچنان بدون پسورد است - برای امنیت کامل فایل‌های docker-compose را اصلاح کنید"
