FROM kooldev/php:8.1-node

RUN apk add --no-cache --virtual .build-deps $PHPIZE_DEPS && \
    pecl install swoole && \
    docker-php-ext-enable swoole && \
    # cleanup
    apk del .build-deps && \
    rm -rf /var/cache/apk/* /tmp/*
