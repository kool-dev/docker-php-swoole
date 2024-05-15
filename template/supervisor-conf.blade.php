[program:nginx]
depends_on = php-fpm
command = nginx -g "daemon off;"
stopasgroup = true
stderr_logfile = /dev/stderr
stdout_logfile = /dev/stdout

[program:octane]
command = php artisan octane:start --server=swoole --watch
stopasgroup = true
stderr_logfile = /dev/stderr
stdout_logfile = /dev/stdout