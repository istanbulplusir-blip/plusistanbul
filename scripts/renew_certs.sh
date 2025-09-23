#!/usr/bin/env bash
set -euo pipefail
cd /home/djangouser/peykan-tourism
# Renew using webroot (plugin remembered, but we pass explicitly for safety)
/usr/bin/docker-compose run --rm --entrypoint certbot certbot renew --webroot -w /var/www/certbot --quiet || true
# Reload nginx after potential renewal
/usr/bin/docker-compose exec -T nginx nginx -t && /usr/bin/docker-compose exec -T nginx nginx -s reload || true
