## Description

Minimal PHP Docker image with Swoole. It is intended for [kool.dev](https://github.com/kool-dev/kool), but can fit other PHP use cases.

This image is based on [kooldev/php](https://github.com/kool-dev/docker-php), please refer to that repo README for further documentation.

## Available Tags

Images support `linux/amd64` and `linux/arm64`. NGINX variants use Python Supervisor to run NGINX and Laravel Octane. Dockerize is inherited from the base image.

Debian variants use the base image's `gosu` for user switching. Development variants include Node 24 LTS and Yarn for Octane's `--watch` mode; production variants omit them. Use tags with the `kooldev/php:` prefix.

### 8.5

- [8.5](https://github.com/kool-dev/docker-php-swoole/blob/main/8.5-swoole/Dockerfile) and [8.5-prod](https://github.com/kool-dev/docker-php-swoole/blob/main/8.5-swoole-prod/Dockerfile)
- [8.5-nginx](https://github.com/kool-dev/docker-php-swoole/blob/main/8.5-swoole-nginx/Dockerfile) and [8.5-nginx-prod](https://github.com/kool-dev/docker-php-swoole/blob/main/8.5-swoole-nginx-prod/Dockerfile)
- Debian: `8.5-debian-swoole`, `8.5-debian-swoole-prod`, `8.5-debian-swoole-nginx`, `8.5-debian-swoole-nginx-prod`

### 8.4

- [8.4](https://github.com/kool-dev/docker-php-swoole/blob/master/8.4-swoole/Dockerfile) and [8.4-prod](https://github.com/kool-dev/docker-php-swoole/blob/master/8.4-swoole-prod/Dockerfile)
- [8.4-nginx](https://github.com/kool-dev/docker-php-swoole/blob/master/8.4-swoole-nginx/Dockerfile) and [8.4-nginx-prod](https://github.com/kool-dev/docker-php-swoole/blob/master/8.4-swoole-nginx-prod/Dockerfile)
- Debian: `8.4-debian-swoole`, `8.4-debian-swoole-prod`, `8.4-debian-swoole-nginx`, `8.4-debian-swoole-nginx-prod`

### 8.3

- [8.3](https://github.com/kool-dev/docker-php-swoole/blob/master/8.3-swoole/Dockerfile) and [8.3-prod](https://github.com/kool-dev/docker-php-swoole/blob/master/8.3-swoole-prod/Dockerfile)
- [8.3-nginx](https://github.com/kool-dev/docker-php-swoole/blob/master/8.3-swoole-nginx/Dockerfile) and [8.3-nginx-prod](https://github.com/kool-dev/docker-php-swoole/blob/master/8.3-swoole-nginx-prod/Dockerfile)

### 8.2

- [8.2](https://github.com/kool-dev/docker-php-swoole/blob/master/8.2-swoole/Dockerfile) and [8.2-prod](https://github.com/kool-dev/docker-php-swoole/blob/master/8.2-swoole-prod/Dockerfile)
- [8.2-nginx](https://github.com/kool-dev/docker-php-swoole/blob/master/8.2-swoole-nginx/Dockerfile) and [8.2-nginx-prod](https://github.com/kool-dev/docker-php-swoole/blob/master/8.2-swoole-nginx-prod/Dockerfile)

### Retired versions

PHP 8.1 images are no longer built or maintained. Use PHP 8.2 or newer.

## Environment Variables

Please refer to [kooldev/php](https://github.com/kool-dev/docker-php).

### NGINX

Please refer to [kooldev/php](https://github.com/kool-dev/docker-php).

## Usage

Please refer to [kooldev/php](https://github.com/kool-dev/docker-php).

## Contributing

### Update images with templates

Dockerfiles and configuration files are generated from `fwd-template.json` and the `template` folder. Make changes to these source files rather than the generated files.

After any changes, we need to run `kool run template` to parse the templates and generate folder/files for each version.

## License

The MIT License (MIT).
