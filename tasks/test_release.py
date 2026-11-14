"""Offline tests for the release boundary."""

import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import release


TRUSTED = dict(GITHUB_REPOSITORY="kool-dev/docker-php-swoole",
               GITHUB_REF="refs/heads/main", GITHUB_EVENT_NAME="push",
               GITHUB_RUN_ID="12345", GITHUB_RUN_ATTEMPT="2")


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        env = patch.dict(os.environ, TRUSTED, clear=True)
        env.start()
        self.addCleanup(env.stop)
        self.records = [
            dict(repository=release.REPOSITORY, run_id="12345", run_attempt="2",
                 tag=tag, arch=arch, digest=f"sha256:{index:064x}",
                 image_id=f"sha256:{index + 100:064x}",
                 staging_tag=release.staging_tag("12345", "2", tag, arch))
            for index, (tag, arch) in enumerate(
                (tag, arch) for tag in release.TAGS for arch in release.ARCHES)
        ]

    def write(self, records=None):
        (self.directory / "records.json").write_text(
            json.dumps(self.records if records is None else records))

    def test_complete_metadata(self):
        self.write()
        self.assertEqual(len(release.load_records(self.directory, "12345", "2")), 48)

    def test_invalid_metadata_never_touches_registry(self):
        cases = [self.records[:-1], self.records + [self.records[0]], [], {}]
        for field, value in (
            ("repository", "attacker/php"), ("run_attempt", "1"), ("run_id", "999"),
            ("tag", "latest"), ("arch", "s390x"), ("staging_tag", "old-attempt"),
            ("digest", "sha256:bad"), ("digest", "sha256:" + "g" * 64),
            ("digest", "sha256:" + "a" * 64 + ";echo bad"),
            ("digest", None), ("image_id", "bad"),
        ):
            records = copy.deepcopy(self.records)
            records[0][field] = value
            cases.append(records)
        records = copy.deepcopy(self.records)
        del records[0]["digest"]
        cases.append(records)
        for records in cases:
            with self.subTest(records=str(records)[:150]):
                self.write(records)
                with patch.object(release, "command") as command:
                    with self.assertRaises(ValueError):
                        release.promote(self.directory)
                    command.assert_not_called()

    def test_all_remote_platforms_preflight_before_manifest_updates(self):
        self.write()
        commands = []
        platforms = {record["digest"]: record["arch"] for record in self.records}

        def docker(*args):
            commands.append(args)
            if "inspect" in args:
                digest = args[4].split("@")[1]
                return json.dumps(dict(os="linux", architecture=platforms[digest]))
            return ""

        with patch.object(release, "command", side_effect=docker):
            release.promote(self.directory)
        self.assertEqual(len(commands), 72)
        self.assertTrue(all(cmd[3] == "inspect" for cmd in commands[:48]))
        for tag, cmd in zip(release.TAGS, commands[48:]):
            self.assertEqual(cmd[:6], ("docker", "buildx", "imagetools", "create",
                                      "--tag", f"kooldev/php:{tag}"))
            self.assertEqual(cmd[6:], tuple(
                f"kooldev/php@{record['digest']}" for record in self.records
                if record["tag"] == tag))
        self.assertFalse(any("build" in cmd or "pull" in cmd for cmd in commands))

    def test_last_bad_remote_platform_prevents_all_stable_updates(self):
        self.write()
        responses = [json.dumps(dict(os="linux", architecture=r["arch"]))
                     for r in self.records]
        responses[-1] = '{"os":"linux","architecture":"amd64"}'
        with patch.object(release, "command", side_effect=responses) as command:
            with self.assertRaises(ValueError):
                release.promote(self.directory)
            self.assertEqual(command.call_count, 48)
            self.assertTrue(all(call.args[3] == "inspect" for call in command.call_args_list))

    def test_registry_failure_prevents_all_stable_updates(self):
        self.write()
        with patch.object(release, "command", side_effect=RuntimeError("registry unavailable")):
            with self.assertRaises(RuntimeError):
                release.promote(self.directory)

    def test_stage_retags_tested_image_ids_without_pull_or_build(self):
        image_ids = ["sha256:" + "a" * 64, "sha256:" + "b" * 64]
        commands = []

        def docker(*args):
            commands.append(args)
            image_id = image_ids[0 if len(commands) <= 5 else 1]
            if args[:3] == ("docker", "image", "inspect"):
                if "--format" in args:
                    return image_id
                return json.dumps([dict(Id=image_id, Architecture="amd64", Os="linux")])
            if "imagetools" in args:
                return json.dumps(dict(digest="sha256:" + "c" * 64))
            return ""

        with patch.object(release, "command", side_effect=docker):
            release.stage("8.5-swoole", "-prod", "amd64", self.directory)
        self.assertEqual(len(commands), 10)
        for offset, image_id in ((0, image_ids[0]), (5, image_ids[1])):
            self.assertEqual(commands[offset + 1][:3], ("docker", "tag", image_id))
            self.assertEqual(commands[offset + 2][-1], commands[offset + 1][-1])
            self.assertEqual(commands[offset + 3][-1], commands[offset + 1][-1])
        records = json.loads(next(self.directory.glob("*.json")).read_text())
        self.assertEqual([record["image_id"] for record in records], image_ids)
        self.assertTrue(all(record["staging_tag"].startswith("ci-swoole-12345-2-")
                            for record in records))
        self.assertFalse(any("build" in cmd or "pull" in cmd for cmd in commands))

    def test_retag_mismatch_prevents_push(self):
        image = dict(Id="sha256:" + "a" * 64, Architecture="amd64", Os="linux")
        with patch.object(release, "command",
                          side_effect=[json.dumps([image]), "", "sha256:" + "b" * 64]) as command:
            with self.assertRaises(ValueError):
                release.stage("8.5-swoole", "", "amd64", self.directory)
        self.assertFalse(any(call.args[1] == "push" for call in command.call_args_list))
        self.assertEqual(list(self.directory.iterdir()), [])

    def test_untrusted_events_cannot_stage_or_promote(self):
        for override in (
            dict(GITHUB_EVENT_NAME="pull_request"),
            dict(GITHUB_EVENT_NAME="pull_request_target"),
            dict(GITHUB_EVENT_NAME="workflow_dispatch", GITHUB_REF="refs/heads/feature"),
            dict(GITHUB_REPOSITORY="fork/docker-php-swoole"),
            dict(GITHUB_RUN_ATTEMPT="0"),
        ):
            with self.subTest(override=override), patch.dict(os.environ, override):
                with patch.object(release, "command") as command:
                    for action in (lambda: release.promote(self.directory),
                                   lambda: release.stage("8.5-swoole", "", "amd64", self.directory)):
                        with self.assertRaises(ValueError):
                            action()
                    command.assert_not_called()

    def test_workflow_publication_boundary(self):
        workflow = (Path(__file__).resolve().parents[1] /
                    ".github/workflows/ci-cd.yml").read_text()
        build = workflow.split("  build:\n")[1].split("  publish:\n")[0]
        publish = workflow.split("  publish:\n")[1].split("  dispatch:\n")[0]
        dispatch = workflow.split("  dispatch:\n")[1]
        guard = ("contains(fromJSON('[\"push\", \"workflow_dispatch\", \"repository_dispatch\"]'), "
                 "github.event_name) && github.ref == 'refs/heads/main' && "
                 "github.repository == 'kool-dev/docker-php-swoole'")
        self.assertEqual(build.count("if: " + guard), 3)
        self.assertIn("if: " + guard, publish)
        self.assertIn("if: " + guard, dispatch)
        self.assertIn("needs: [build, workflow-tests]", publish)
        self.assertIn("needs: publish", dispatch)
        self.assertLess(build.index("Test Supervisor lifecycle"), build.index("Login to DockerHub"))
        self.assertLess(build.index("Tests (dev)"), build.index("Login to DockerHub"))
        self.assertEqual(workflow.count("uses: docker/build-push-action@"), 2)
        self.assertNotIn("setup-qemu", workflow)
        self.assertNotIn("build-push-action", publish)
        self.assertIn("kooldev/php:${{ matrix.version }}${{ matrix.type }}="
                      "docker-image://localhost:5000/", build)
        self.assertIn("runner: ubuntu-24.04\n", build)
        self.assertIn("runner: ubuntu-24.04-arm\n", build)
        self.assertIn("name: swoole-${{ github.run_id }}-${{ github.run_attempt }}-", build)
        self.assertIn("pattern: swoole-${{ github.run_id }}-${{ github.run_attempt }}-*", publish)
        self.assertIn("actions/upload-artifact@v7.0.2", build)
        self.assertIn("actions/download-artifact@v8.0.2", publish)
        self.assertNotIn("schedule:", workflow)
        self.assertIn("cancel-in-progress: ${{ github.event_name == 'pull_request' }}", workflow)
        self.assertIn("secrets.DISPATCH_TOKEN || secrets.WORKFLOW_TOKEN", dispatch)
        self.assertIn("timeout-minutes: 5", dispatch)


if __name__ == "__main__":
    unittest.main()
