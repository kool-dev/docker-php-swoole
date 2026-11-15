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

The 24 native jobs use `ubuntu-24.04` for amd64 and `ubuntu-24.04-arm` for arm64. Each builds and tests a base/NGINX pair through a job-local registry; NGINX consumes that same job's fresh base. After all tests in a job pass, trusted main-branch runs retag those exact tested daemon images (without rebuilding) to `kooldev/php:ci-swoole-RUN_ID-RUN_ATTEMPT-VARIANT-ARCH`. PRs, forks, and manual feature-branch runs never log in, stage, publish, or notify OCI8.

A single manifest-only job requires every native job and the workflow checks to succeed. It validates all 24 stable tags × both architectures, run/attempt scope, repository, unique tag/platform entries, digest format, tested image ID and Linux OS before updating any stable tag. Staging verifies each local tested image's platform and records Docker's push digest directly. Publication trusts those artifacts rather than re-reading 48 remote manifests/configs; staging also avoids 48 post-push inspections. Stable manifests reference the recorded immutable Docker Hub digests, never staging tag lookups or rebuilt images. Metadata artifacts are retained for seven days. There is no cross-tag transaction: a registry failure during promotion can still leave a partially updated release.

If all native build/test/staging jobs succeeded and only publication or dispatch needs retrying, use **Resume publication** on `main`, supplying the CI/CD `source_run` ID and completed `source_attempt`. It downloads only that attempt's complete metadata and republishes all 24 manifests without rebuilding or staging again. The source must be the latest trusted CI/CD run and latest completed attempt at the current default-branch commit. Failed/missing native jobs, expired metadata, or stale commits require a fresh complete CI/CD run. Older metadata without the tested-platform fields is not accepted.

Recovery shares CI/CD's release lock; OCI8 is notified only after all manifests succeed. Repeating recovery can repeat that notification. For normal CI/CD reruns, still choose **Re-run all jobs**, not just failed jobs: incomplete current attempts fail closed. Never combine metadata from different attempts.

Manifest assembly still reads Docker Hub and consumes pull allowance. Resume only once quota is available; these changes reduce requests, not eliminate limits. Publication uses the existing Docker driver rather than booting another BuildKit container. Staging tags accumulate until separately cleaned up. Receiver push and PHP dispatch triggers are preserved; avoid scheduling a standalone receiver release immediately before a PHP parent release when possible.

Only after all 24 stable manifests succeed, one bounded notification sends `docker-php-swoole-updated` to `kool-dev/docker-php-oci8`, allowing its Swoole-derived variants to rebuild after their parents. OCI8 must listen for this event and serialize its own releases; this chain does not trigger PHP again.

The notification uses `DISPATCH_TOKEN`, falling back to `WORKFLOW_TOKEN`. The selected credential must permit repository dispatch to OCI8; secret presence alone does not verify access. Missing credentials or failed dispatches fail the notification job visibly, without undoing published images. The CI/CD job summary distinguishes publication from notification; an accepted dispatch does not prove OCI8 completed. Investigate and use Resume publication for an eligible source, or a fresh full run otherwise; there is no independent downstream schedule to mask a broken chain. This is not an atomic release or digest-pinned parent chain.

Release logic has offline coverage via `python3 -m unittest discover -s tasks -p 'test_release.py' -v`; CI also runs actionlint and `python3 tasks/test_release_registry.py` against a disposable local registry. The latter stages tiny scratch fixtures and verifies all 24 two-platform manifests without touching Docker Hub (set `RELEASE_TEST_REGISTRY=localhost:PORT` to use another local port). It does not execute ARM code. Native amd64/arm64 image tests remain required to validate the actual runtime images.

### Update images with templates

Dockerfiles and configuration files are generated from `fwd-template.json` and the `template` folder. Make changes to these source files rather than the generated files.

After any changes, we need to run `kool run template` to parse the templates and generate folder/files for each version.

## License

The MIT License (MIT).
