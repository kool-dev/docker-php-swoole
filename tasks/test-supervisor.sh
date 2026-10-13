#!/usr/bin/env bash
set -euo pipefail

image=${1:?Usage: test-supervisor.sh IMAGE}
fixture=$(mktemp -d)
container=
cleanup() {
    if [ -n "$container" ]; then
        docker logs "$container"
        docker rm -f "$container" > /dev/null
    fi
    rm -f "$fixture/artisan" "$fixture/router.php"
    rmdir "$fixture"
}
trap cleanup EXIT

# Exercise the real Supervisor config without requiring a Laravel install.
cat > "$fixture/artisan" <<'PHP'
<?php
fwrite(STDOUT, "Starting Octane test fixture\n");
fwrite(STDERR, "Testing stderr logging\n");
pcntl_exec(PHP_BINARY, ['-S', '127.0.0.1:8000', '/app/router.php']);
exit(1);
PHP
cat > "$fixture/router.php" <<'PHP'
<?php
echo 'supervisor-ok';
PHP
chmod 755 "$fixture"
chmod 644 "$fixture/artisan" "$fixture/router.php"

container=$(docker run -d -e ASUSER=1000 -v "$fixture:/app:ro" "$image")
ready=false
for attempt in $(seq 1 30); do
    if docker exec "$container" curl -fsS http://127.0.0.1/ | grep -q supervisor-ok; then
        ready=true
        break
    fi
    sleep 1
done
[ "$ready" = true ]
docker logs "$container" 2>&1 | grep -q 'Testing stderr logging'
docker stop --signal SIGTERM -t 10 "$container" > /dev/null
[ "$(docker inspect -f '{{.State.ExitCode}}' "$container")" = 0 ]
if docker logs "$container" 2>&1 | grep -Eq 'Illegal seek|CRIT.*uncaptured'; then
    exit 1
fi
