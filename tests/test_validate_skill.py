"""Regressions for the layered code review release check."""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from scripts.validate_skill import (
    INSTALL_COMMAND,
    SOURCE_URLS,
    default_root,
    main,
    validate_repository,
)


class ValidateSkillTests(unittest.TestCase):
    def test_repository_matches_release_contract(self) -> None:
        errors = validate_repository(default_root())
        self.assertEqual(errors, [])
        self.assertEqual(main(default_root()), 0)

    def test_empty_description_is_rejected(self) -> None:
        with cloned_repository() as root:
            replace_description(root, '""')
            errors = validate_repository(root)
            self.assertTrue(any("description is empty" in error for error in errors), errors)
            self.assertEqual(main(root), 1)

    def test_description_longer_than_1024_characters_is_rejected(self) -> None:
        with cloned_repository() as root:
            replace_description(root, "a" * 1025)
            errors = validate_repository(root)
            self.assertTrue(any("maximum is 1024" in error for error in errors), errors)

    def test_name_must_match_skill_directory(self) -> None:
        with cloned_repository() as root:
            replace_once(skill_path(root), "name: layered-code-review", "name: other-review")
            errors = validate_repository(root)
            self.assertTrue(any("must match the parent directory" in error for error in errors), errors)

    def test_root_skill_file_makes_discovery_ambiguous(self) -> None:
        with cloned_repository() as root:
            (root / "SKILL.md").write_text(
                "---\nname: layered-code-review\ndescription: Review when asked.\n---\n\n# Extra\n",
                encoding="utf-8",
            )
            errors = validate_repository(root)
            self.assertTrue(any("discovery stays unambiguous" in error for error in errors), errors)

    def test_broken_relative_link_is_rejected(self) -> None:
        with cloned_repository() as root:
            append(skill_path(root), "\n[Missing](references/missing-report.md)\n")
            errors = validate_repository(root)
            self.assertTrue(any("missing-report.md" in error for error in errors), errors)

    def test_private_key_block_is_rejected(self) -> None:
        with cloned_repository() as root:
            append(root / "README.md", "\n" + "-----BEGIN " + "PRIVATE KEY-----\n")
            errors = validate_repository(root)
            self.assertTrue(any("private key" in error for error in errors), errors)

    def test_machine_local_path_is_rejected(self) -> None:
        with cloned_repository() as root:
            append(root / "README.md", "\nSee " + "/" + "home/" + "example/notes.md\n")
            errors = validate_repository(root)
            self.assertTrue(any("machine-local path" in error for error in errors), errors)

    def test_dropping_preexisting_class_is_rejected(self) -> None:
        with cloned_repository() as root:
            path = skill_path(root)
            path.write_text(path.read_text(encoding="utf-8").replace("Pre-existing", "Earlier"), encoding="utf-8")
            errors = validate_repository(root)
            self.assertTrue(any("Pre-existing" in error for error in errors), errors)

    def test_allowed_tools_is_rejected(self) -> None:
        with cloned_repository() as root:
            path = skill_path(root)
            path.write_text(
                path.read_text(encoding="utf-8").replace("\n---\n", "\nallowed-tools: Bash\n---\n", 1),
                encoding="utf-8",
            )
            errors = validate_repository(root)
            self.assertTrue(any("allowed-tools" in error for error in errors), errors)

    def test_trailing_whitespace_is_rejected(self) -> None:
        with cloned_repository() as root:
            append(root / "README.md", " \n")
            errors = validate_repository(root)
            self.assertTrue(any("trailing whitespace" in error for error in errors), errors)

    def test_removed_source_url_is_rejected(self) -> None:
        with cloned_repository() as root:
            replace_once(skill_path(root), SOURCE_URLS[0], "https://example.com/removed-source")
            errors = validate_repository(root)
            self.assertTrue(any(SOURCE_URLS[0] in error for error in errors), errors)

    def test_non_utf8_file_is_reported(self) -> None:
        with cloned_repository() as root:
            (root / "notes.bin").write_bytes(b"\xff\xfe not text")
            errors = validate_repository(root)
            self.assertTrue(any("not UTF-8" in error for error in errors), errors)
            self.assertEqual(main(root), 1)

    def test_install_command_drift_is_rejected(self) -> None:
        with cloned_repository() as root:
            replace_once(root / "README.md", INSTALL_COMMAND, "npx skills add example/other")
            errors = validate_repository(root)
            self.assertTrue(any("README.md: missing " + INSTALL_COMMAND in error for error in errors), errors)


@contextmanager
def cloned_repository():
    with tempfile.TemporaryDirectory() as directory:
        destination = Path(directory) / "repo"
        shutil.copytree(
            default_root(),
            destination,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
        )
        yield destination


def skill_path(root: Path) -> Path:
    return root / "skills" / "layered-code-review" / "SKILL.md"


def replace_description(root: Path, value: str) -> None:
    path = skill_path(root)
    text = path.read_text(encoding="utf-8")
    start = text.index("description:")
    end = text.index("\nlicense:", start)
    path.write_text(text[:start] + f"description: {value}" + text[end:], encoding="utf-8")


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise AssertionError(f"{path.name} does not contain the expected snippet")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def append(path: Path, suffix: str) -> None:
    path.write_text(path.read_text(encoding="utf-8") + suffix, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
