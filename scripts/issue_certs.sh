#!/usr/bin/env bash
set -euo pipefail
cd /home/djangouser/peykan-tourism
EMAIL="admin@peykantravelistanbul.com"
DOMAINS=("-d" "peykantravelistanbul.com" "-d" "www.peykantravelistanbul.com")
# Ensure webroot exists via nginx volume
mkdir -p ./_certbot_webroot_dummy || true
# Issue (will be no-op if already valid)
/usr/bin/docker-compose run --rm --entrypoint certbot certbot certonly \
  --webroot -w /var/www/certbot --agree-tos --no-eff-email -m "$EMAIL" -n \
  "${DOMAINS[@]}"
# Reload nginx
/usr/bin/docker-compose exec -T nginx nginx -t
/usr/bin/docker-compose exec -T nginx nginx -s reload
