#!/usr/bin/env python3
"""Stage tested daemon images, then promote only a complete run's digests."""

import json
import os
from pathlib import Path
import re
import subprocess
import sys

REPOSITORY = "kooldev/php"
VERSIONS = ("8.2-swoole", "8.3-swoole", "8.4-swoole", "8.5-swoole",
            "8.4-debian-swoole", "8.5-debian-swoole")
TAGS = tuple(f"{version}{nginx}{kind}" for version in VERSIONS
             for nginx in ("", "-nginx") for kind in ("", "-prod"))
ARCHES = ("amd64", "arm64")
DIGEST = re.compile(r"sha256:[0-9a-f]{64}")


def command(*args):
    return subprocess.check_output(args, text=True).strip()


def release_scope():
    if (os.environ.get("GITHUB_REPOSITORY") != "kool-dev/docker-php-swoole"
            or os.environ.get("GITHUB_REF") != "refs/heads/main"
            or os.environ.get("GITHUB_EVENT_NAME") not in
            ("push", "workflow_dispatch", "repository_dispatch")):
        raise ValueError("Publication requires a trusted main-branch event")
    scope = (os.environ["GITHUB_RUN_ID"], os.environ["GITHUB_RUN_ATTEMPT"])
    if not all(re.fullmatch(r"[1-9][0-9]*", value) for value in scope):
        raise ValueError("Invalid run ID/attempt")
    return scope


def staging_tag(run, attempt, tag, arch):
    return f"ci-swoole-{run}-{attempt}-{tag}-{arch}"


def stage(version, kind, arch, directory):
    run, attempt = release_scope()
    if version not in VERSIONS or kind not in ("", "-prod") or arch not in ARCHES:
        raise ValueError("Invalid build variant/platform")
    records = []
    for tag in (f"{version}{kind}", f"{version}-nginx{kind}"):
        source = f"localhost:5000/{REPOSITORY}:{tag}"
        # No pull or rebuild: these are the daemon images used by docker run tests.
        image = json.loads(command("docker", "image", "inspect", source))[0]
        image_id = image["Id"]
        if (not DIGEST.fullmatch(image_id) or image["Architecture"] != arch
                or image["Os"] != "linux"):
            raise ValueError(f"Unexpected tested image: {source}")
        staging = staging_tag(run, attempt, tag, arch)
        target = f"{REPOSITORY}:{staging}"
        command("docker", "tag", image_id, target)
        if command("docker", "image", "inspect", "--format", "{{.Id}}", target) != image_id:
            raise ValueError("Staging tag is not the tested image")
        command("docker", "push", "--quiet", target)
        descriptor = json.loads(command("docker", "buildx", "imagetools", "inspect",
                                        target, "--format", "{{json .Manifest}}"))
        digest = descriptor["digest"]
        if not isinstance(digest, str) or not DIGEST.fullmatch(digest):
            raise ValueError(f"Invalid pushed digest: {digest}")
        records.append(dict(repository=REPOSITORY, run_id=run, run_attempt=attempt,
                            tag=tag, arch=arch, staging_tag=staging,
                            digest=digest, image_id=image_id))
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    (path / f"{version}{kind}-{arch}.json").write_text(json.dumps(records) + "\n")


def load_records(directory, run, attempt):
    records = {}
    for path in sorted(Path(directory).rglob("*.json")):
        batch = json.loads(path.read_text())
        if not isinstance(batch, list):
            raise ValueError(f"Invalid artifact: {path}")
        for record in batch:
            if not isinstance(record, dict) or set(record) != {
                "repository", "run_id", "run_attempt", "tag", "arch",
                "staging_tag", "digest", "image_id"
            }:
                raise ValueError("Malformed metadata")
            tag, arch = record["tag"], record["arch"]
            if (record["repository"] != REPOSITORY
                    or record["run_id"] != run or record["run_attempt"] != attempt
                    or tag not in TAGS or arch not in ARCHES
                    or record["staging_tag"] != staging_tag(run, attempt, tag, arch)
                    or not isinstance(record["digest"], str)
                    or not DIGEST.fullmatch(record["digest"])
                    or not isinstance(record["image_id"], str)
                    or not DIGEST.fullmatch(record["image_id"])):
                raise ValueError("Invalid repository, scope, tag, architecture or digest")
            key = (tag, arch)
            if key in records:
                raise ValueError(f"Duplicate metadata: {key}")
            records[key] = record
    if set(records) != {(tag, arch) for tag in TAGS for arch in ARCHES}:
        raise ValueError("Incomplete release: require all 24 tags on both architectures")
    return records


def promote(directory):
    run, attempt = release_scope()
    records = load_records(directory, run, attempt)
    # Resolve every immutable reference and platform before changing ANY stable tag.
    for (tag, arch), record in records.items():
        reference = f"{REPOSITORY}@{record['digest']}"
        image = json.loads(command("docker", "buildx", "imagetools", "inspect",
                                   reference, "--format", "{{json .Image}}"))
        if image["architecture"] != arch or image["os"] != "linux":
            raise ValueError(f"Wrong platform for {tag}/{arch}")
    for tag in TAGS:
        command("docker", "buildx", "imagetools", "create", "--tag",
                f"{REPOSITORY}:{tag}",
                *(f"{REPOSITORY}@{records[tag, arch]['digest']}" for arch in ARCHES))


if __name__ == "__main__":
    if len(sys.argv) == 6 and sys.argv[1] == "stage":
        stage(*sys.argv[2:])
    elif len(sys.argv) == 3 and sys.argv[1] == "promote":
        promote(sys.argv[2])
    else:
        sys.exit("Usage: release.py stage VERSION TYPE ARCH DIRECTORY | promote DIRECTORY")
