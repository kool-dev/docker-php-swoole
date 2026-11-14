"""Opt-in real registry boundary test; only writes to the specified loopback registry."""

import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from unittest.mock import patch

import release


def main():
    registry = os.environ.get("RELEASE_TEST_REGISTRY", "localhost:5000")
    if not re.fullmatch(r"localhost:[0-9]+", registry):
        raise ValueError("Integration test requires a loopback registry")
    repository = f"{registry}/swoole-release-test/php"
    original = release.command
    commands = []

    def local_command(*args):
        # Production code stays hard-coded to Docker Hub. Only this test rewrites
        # references; no credentials, production writes, or production reads.
        mapped = []
        for arg in args:
            for prefix in ("localhost:5000/kooldev/php", "kooldev/php"):
                if arg.startswith(prefix + ":") or arg.startswith(prefix + "@"):
                    arg = repository + arg[len(prefix):]
                    break
            mapped.append(arg)
        commands.append(mapped)
        return original(*mapped)

    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        (root / "Dockerfile").write_text("FROM scratch\nLABEL purpose=swoole-release-test\n")
        digests, ids = {}, {}
        for arch in release.ARCHES:
            target = f"{repository}:fixture-{arch}"
            subprocess.run(["docker", "buildx", "build", "--platform", f"linux/{arch}",
                            "--provenance=false", "--load", "--tag", target,
                            str(root)], check=True)
            ids[arch] = original("docker", "image", "inspect", "--format", "{{.Id}}", target)
            original("docker", "push", "--quiet", target)
            digests[arch] = json.loads(original(
                "docker", "buildx", "imagetools", "inspect", target,
                "--format", "{{json .Manifest}}"))["digest"]

        # The inspected daemon IDs are our tested fixture images. Stage them by
        # ID through the unmodified production code, with registry-only routing.
        for tag in ("8.5-swoole-prod", "8.5-swoole-nginx-prod"):
            original("docker", "tag", ids["amd64"], f"{repository}:{tag}")
        env = dict(GITHUB_REPOSITORY="kool-dev/docker-php-swoole",
                   GITHUB_REF="refs/heads/main", GITHUB_EVENT_NAME="push",
                   GITHUB_RUN_ID="12345", GITHUB_RUN_ATTEMPT="2")
        with patch.dict(os.environ, env), patch.object(release, "command", local_command):
            release.stage("8.5-swoole", "-prod", "amd64", root / "staged")
            staged = json.loads(next((root / "staged").glob("*.json")).read_text())
            assert all(record["image_id"] == ids["amd64"] for record in staged)
            assert all(record["digest"] == digests["amd64"] for record in staged)
            # Expand the two tiny native-config fixtures over the complete release
            # shape. This tests real remote preflight and all stable manifest writes.
            records = [
                dict(repository=release.REPOSITORY, run_id="12345", run_attempt="2",
                     tag=tag, arch=arch, digest=digests[arch], image_id=ids[arch],
                     staging_tag=release.staging_tag("12345", "2", tag, arch))
                for tag in release.TAGS for arch in release.ARCHES
            ]
            metadata = root / "metadata"
            metadata.mkdir()
            (metadata / "records.json").write_text(json.dumps(records))
            commands.clear()
            release.promote(metadata)
            assert len(commands) == 72
            assert all(cmd[3] == "inspect" for cmd in commands[:48])
            for tag in release.TAGS:
                manifest = json.loads(original(
                    "docker", "buildx", "imagetools", "inspect",
                    f"{repository}:{tag}", "--raw"))
                assert {entry["platform"]["architecture"] for entry in manifest["manifests"]} == {
                    "amd64", "arm64"}
                assert {entry["digest"] for entry in manifest["manifests"]} == set(digests.values())
    print("PASS: exact daemon-ID staging and 24 two-platform manifest-only promotions, loopback only")


if __name__ == "__main__":
    main()
