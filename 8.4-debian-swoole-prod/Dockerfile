FROM kooldev/php:8.4-debian-prod

COPY --from=mlocati/php-extension-installer /usr/bin/install-php-extensions /usr/local/bin/

# The Debian base removes PHP's build tools after compiling its extensions.
RUN apt-get update && apt-get install -y --no-install-recommends $PHPIZE_DEPS \
    && install-php-extensions swoole \
    && apt-get purge -y --auto-remove $PHPIZE_DEPS \
    && rm -rf /var/lib/apt/lists/*

