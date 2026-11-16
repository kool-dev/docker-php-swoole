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

### Release freshness

PHP's scheduled rebuild sends `docker-php-updated` after publication to start a Swoole rebuild. Swoole has no separate cron schedule; manual workflow runs remain available for recovery. Builds explicitly pull parents. Main-branch releases share a concurrency group and are not canceled in progress; only superseded PR runs are canceled. GitHub may replace pending runs and does not promise FIFO ordering.

The 24 native jobs use `ubuntu-24.04` for amd64 and `ubuntu-24.04-arm` for arm64. Each builds and tests a base/NGINX pair using Docker's same-job local image store; NGINX never force-pulls a stale public base. A shared check verifies the tested base ID and full layer ancestry. After all runtime/Supervisor/dev tests pass, trusted main-branch runs stage those exact immutable IDs without rebuilding. PRs, forks, and manual feature-branch runs never log in, stage, publish, or notify OCI8.

CI uses [shared Bash/`jq` actions](https://github.com/kool-dev/action/blob/master/image-ci.md), pinned in the workflow. One publisher validates the complete 24-tag × two-architecture release before stable updates. Swoole builds, generation checks and runtime tests stay here.

Recovery requires **Re-run all jobs**, not just failed jobs: artifacts and staging tags are scoped to the current run ID **and attempt**, and incomplete attempts fail closed. A new manual main-branch workflow run also rebuilds/tests the complete release. Do not combine artifacts from previous attempts.

Only after all 24 stable manifests succeed, one bounded notification sends `docker-php-swoole-updated` to `kool-dev/docker-php-oci8`, allowing its Swoole-derived variants to rebuild after their parents. OCI8 must listen for this event and serialize its own releases; this chain does not trigger PHP again.

The notification uses `DISPATCH_TOKEN`, falling back to `WORKFLOW_TOKEN`. The selected credential must permit repository dispatch to OCI8; secret presence alone does not verify access. Missing credentials or failed dispatches fail the notification job visibly, without undoing published images. The job summary distinguishes publication from notification; an accepted dispatch does not prove OCI8 completed. Investigate and retry a failed notification with a manual workflow run; there is no independent downstream schedule to mask a broken chain. This is not an atomic release or digest-pinned parent chain.

Shared Bash contract and real loopback-registry tests live in the tooling repository. Here CI runs the real template generator and native image/Supervisor tests. Synthetic registry fixtures do not execute ARM application code.

### Update images with templates

Dockerfiles and configuration files are generated from `fwd-template.json` and the `template` folder. Make changes to these source files rather than the generated files.

After any changes, we need to run `kool run template` to parse the templates and generate folder/files for each version.

## License

The MIT License (MIT).
