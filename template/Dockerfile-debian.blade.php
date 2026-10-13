@unless ($prod)
FROM node:24-bookworm-slim AS node

@endunless
FROM {{ $from }}

COPY --from=mlocati/php-extension-installer /usr/bin/install-php-extensions /usr/local/bin/

# The Debian base removes PHP's build tools after compiling its extensions.
RUN apt-get update && apt-get install -y --no-install-recommends $PHPIZE_DEPS \
    && install-php-extensions swoole \
    && apt-get purge -y --auto-remove $PHPIZE_DEPS \
    && rm -rf /var/lib/apt/lists/*

@unless ($prod)
# Octane's --watch mode requires Node; keep frontend tools in dev images only.
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
COPY --from=node /opt/yarn-v*/ /opt/yarn/
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && ln -s /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx \
    && ln -s /opt/yarn/bin/yarn /usr/local/bin/yarn \
    && ln -s /opt/yarn/bin/yarnpkg /usr/local/bin/yarnpkg
@endunless
