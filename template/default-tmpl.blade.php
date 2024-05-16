map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
}

server {
    listen @{{ .Env.NGINX_LISTEN }} default_server;
    server_name _;
@{{ if isTrue .Env.NGINX_HTTPS }}
    listen @{{ .Env.NGINX_LISTEN_HTTPS }} ssl http2;
    ssl_certificate     @{{ .Env.NGINX_HTTPS_CERT }};
    ssl_certificate_key @{{ .Env.NGINX_HTTPS_CERT_KEY }};
    ssl_protocols       TLSv1 TLSv1.1 TLSv1.2;
    ssl_ciphers         HIGH:!aNULL:!MD5;
@{{ end }}
    root @{{ .Env.NGINX_ROOT }};
    index @{{ .Env.NGINX_INDEX }};
    charset utf-8;

    location = /favicon.ico { log_not_found off; access_log off; }
    location = /robots.txt  { log_not_found off; access_log off; }

    client_max_body_size @{{ .Env.NGINX_CLIENT_MAX_BODY_SIZE }};

    error_page 404 /index.php;

    location /index.php {
        try_files /not_exists @octane;
    }

    location / {
        try_files $uri $uri/ @octane;

        add_header X-Served-By kool.dev;
    }

    location @octane {
        set $suffix "";

        if ($uri = /index.php) {
            set $suffix ?$query_string;
        }

        proxy_http_version 1.1;
        proxy_set_header Host $http_host;
        proxy_set_header Scheme $scheme;
        proxy_set_header SERVER_PORT $server_port;
        proxy_set_header REMOTE_ADDR $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;

        proxy_pass http://127.0.0.1:8000$suffix;
    }

    location ~ /\.ht {
        deny all;
    }

    # good practices
    add_header X-Frame-Options "SAMEORIGIN";

    # basic H5BP suggestions
    include h5bp/internet_explorer/x-ua-compatible.conf;
    include h5bp/security/referrer-policy.conf;
    include h5bp/security/x-content-type-options.conf;
    include h5bp/security/x-xss-protection.conf;

    # performance enhancements (mostly for caching static data)
    include h5bp/web_performance/cache-file-descriptors.conf;
    include h5bp/web_performance/pre-compressed_content_gzip.conf;
}
