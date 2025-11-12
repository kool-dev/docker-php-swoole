## Description

Minimal PHP Docker image with Swoole drive. It's use is intended for [kool.dev](https://github.com/kool-dev/kool), but can fit in any other PHP use-case.

This image is based on [kooldev/php](https://github.com/kool-dev/docker-php), please refer to that repo README for further documentation.

## Available Tags

### 8.4

- [8.4](https://github.com/kool-dev/docker-php-swoole/blob/master/8.4-swoole/Dockerfile) and [8.4-prod](https://github.com/kool-dev/docker-php-swoole/blob/master/8.4-swoole-prod/Dockerfile)
- [8.4-nginx](https://github.com/kool-dev/docker-php-swoole/blob/master/8.4-swoole-nginx/Dockerfile) and [8.4-nginx-prod](https://github.com/kool-dev/docker-php-swoole/blob/master/8.4-swoole-nginx-prod/Dockerfile)

### 8.3

- [8.3](https://github.com/kool-dev/docker-php-swoole/blob/master/8.3-swoole/Dockerfile) and [8.3-prod](https://github.com/kool-dev/docker-php-swoole/blob/master/8.3-swoole-prod/Dockerfile)
- [8.3-nginx](https://github.com/kool-dev/docker-php-swoole/blob/master/8.3-swoole-nginx/Dockerfile) and [8.3-nginx-prod](https://github.com/kool-dev/docker-php-swoole/blob/master/8.3-swoole-nginx-prod/Dockerfile)

### 8.2

- [8.2](https://github.com/kool-dev/docker-php-swoole/blob/master/8.2-swoole/Dockerfile) and [8.2-prod](https://github.com/kool-dev/docker-php-swoole/blob/master/8.2-swoole-prod/Dockerfile)
- [8.2-nginx](https://github.com/kool-dev/docker-php-swoole/blob/master/8.2-swoole-nginx/Dockerfile) and [8.2-nginx-prod](https://github.com/kool-dev/docker-php-swoole/blob/master/8.2-swoole-nginx-prod/Dockerfile)

### 8.1

- [8.1](https://github.com/kool-dev/docker-php-swoole/blob/master/8.1-swoole/Dockerfile) and [8.1-prod](https://github.com/kool-dev/docker-php-swoole/blob/master/8.1-swoole-prod/Dockerfile)
- [8.1-nginx](https://github.com/kool-dev/docker-php-swoole/blob/master/8.1-swoole-nginx/Dockerfile) and [8.1-nginx-prod](https://github.com/kool-dev/docker-php-swoole/blob/master/8.1-swoole-nginx-prod/Dockerfile)

### Legacy Versions

- [8.0](https://github.com/kool-dev/docker-php-swoole/blob/master/8.0-swoole/Dockerfile), [8.0-prod](https://github.com/kool-dev/docker-php-swoole/blob/master/8.0-swoole-prod/Dockerfile), [8.0-nginx](https://github.com/kool-dev/docker-php-swoole/blob/master/8.0-swoole-nginx/Dockerfile), [8.0-nginx-prod](https://github.com/kool-dev/docker-php-swoole/blob/master/8.0-swoole-nginx-prod/Dockerfile)

## Environment Variables

Please refer to [kooldev/php](https://github.com/kool-dev/docker-php).

### NGINX

Please refer to [kooldev/php](https://github.com/kool-dev/docker-php).

## Usage

Please refer to [kooldev/php](https://github.com/kool-dev/docker-php).

## Contributing

### Update images with templates

The Dockerfile's are automatically managed by `fwd-template.json` configuration file and files in the `template` folder. We should always make changes directly to these files.

After any changes, we need to run `kool run template` to parse the templates and generate folder/files for each version.

## License

The MIT License (MIT). Please see [License File](LICENSE.md) for more information.
