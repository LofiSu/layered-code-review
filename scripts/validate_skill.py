#!/usr/bin/env python3
"""Check this package against the layered code review release contract."""

from __future__ import annotations

import re
import sys
from pathlib import Path

SKILL_DIRECTORY = Path("skills") / "layered-code-review"
SOURCE_URLS = (
    "https://x.com/dotey/status/2123555597387813050",
    "https://claude.dev/blog/solving-code-review-at-anthropic/",
    "https://github.com/sgl-project/sglang-omni/blob/main/.claude/skills/code-review/coding-style.md",
)
INSTALL_COMMAND = (
    "npx skills add LofiSu/layered-code-review --skill layered-code-review "
    "-a claude-code -y"
)
LIST_COMMAND = "npx skills add LofiSu/layered-code-review --list"
MANUAL_SKILL_PATH = ".claude/skills/layered-code-review/SKILL.md"
REQUIRED_SNIPPETS = (
    "Important",
    "Nit",
    "Pre-existing",
    "fresh context",
    "author and review context were not fully isolated",
    "head SHA",
    "Do not invent vote counts",
    "does not grant permission",
    "opt-in",
    "concrete impact",
    "file and line",
)
FRONTMATTER_KEYS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
}
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_PATTERN = re.compile(r"\[[^]]*\]\(([^)]+)\)")
SECRET_PATTERNS = (
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private key"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "cloud access key"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"), "GitHub token"),
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"), "GitHub token"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"), "Slack token"),
)
LOCAL_PATH_PATTERN = re.compile(
    r"(?<![A-Za-z0-9_])/(?:home|Users|tmp|opt|workspace|cursor)/[A-Za-z0-9._/-]+"
)
FOLD_MARKERS = {">-", ">", "|-", "|"}
FORBIDDEN_FILE_NAMES = {"faq.md", "llms.txt", "llms-full.txt"}


def default_root() -> Path:
    return Path(__file__).resolve().parents[1]


def validate_repository(root: Path) -> list[str]:
    """Return release-contract violations for root. An empty list means it holds."""
    errors: list[str] = []
    errors.extend(forbidden_files(root))
    errors.extend(text_file_hazards(root))
    errors.extend(skill_layout(root))
    skill_path = root / SKILL_DIRECTORY / "SKILL.md"
    if skill_path.is_file():
        errors.extend(skill_document(root, skill_path))
    errors.extend(readmes(root))
    errors.extend(license_file(root))
    errors.extend(relative_links(root))
    return errors


def main(root: Path) -> int:
    errors = validate_repository(root)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("ok")
    return 0


def forbidden_files(root: Path) -> list[str]:
    errors: list[str] = []
    for path in iter_files(root):
        if path.name.casefold() in FORBIDDEN_FILE_NAMES:
            errors.append(f"{display(root, path)}: this package does not ship {path.name}")
    return errors


def text_file_hazards(root: Path) -> list[str]:
    errors: list[str] = []
    for path in iter_files(root):
        relative = display(root, path)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"{relative}: file is not UTF-8 text")
            continue
        if "\r" in text:
            errors.append(f"{relative}: use LF line endings")
        for line_number, line in enumerate(text.splitlines(), start=1):
            if line.rstrip(" \t") != line:
                errors.append(f"{relative}:{line_number}: trailing whitespace")
        for pattern, label in SECRET_PATTERNS:
            match = pattern.search(text)
            if match is not None:
                line_number = text.count("\n", 0, match.start()) + 1
                errors.append(f"{relative}:{line_number}: remove {label}")
        path_match = LOCAL_PATH_PATTERN.search(text)
        if path_match is not None:
            line_number = text.count("\n", 0, path_match.start()) + 1
            errors.append(f"{relative}:{line_number}: remove machine-local path")
    return errors


def skill_layout(root: Path) -> list[str]:
    expected = root / SKILL_DIRECTORY / "SKILL.md"
    found = [path for path in iter_files(root) if path.name == "SKILL.md"]
    if found == [expected]:
        return []
    found_display = ", ".join(display(root, path) for path in found) or "none"
    return [
        "expected exactly skills/layered-code-review/SKILL.md so discovery "
        f"stays unambiguous, found {found_display}"
    ]


def skill_document(root: Path, skill_path: Path) -> list[str]:
    relative = display(root, skill_path)
    text = skill_path.read_text(encoding="utf-8")
    try:
        raw_frontmatter, body = split_frontmatter(text)
        frontmatter = parse_frontmatter(raw_frontmatter)
    except ValueError as error:
        return [f"{relative}: {error}"]
    errors = frontmatter_errors(frontmatter, skill_path.parent.name)
    for snippet in REQUIRED_SNIPPETS:
        if snippet not in body:
            errors.append(f"{relative}: missing required text {snippet!r}")
    for url in SOURCE_URLS:
        if url not in text:
            errors.append(f"{relative}: missing source {url}")
    return [f"{relative}: {error}" if not error.startswith(relative) else error for error in errors]


def frontmatter_errors(frontmatter: dict[str, str | dict[str, str]], directory_name: str) -> list[str]:
    errors: list[str] = []
    unknown = sorted(set(frontmatter) - FRONTMATTER_KEYS)
    if unknown:
        errors.append("unknown frontmatter keys: " + ", ".join(unknown))
    if "allowed-tools" in frontmatter:
        errors.append("allowed-tools would pre-approve commands; omit it")
    name = frontmatter.get("name")
    if not isinstance(name, str) or not NAME_PATTERN.fullmatch(name) or not 1 <= len(name) <= 64:
        errors.append("name must be 1-64 characters of lowercase letters, digits, and single hyphens")
    elif name != directory_name:
        errors.append(f"name {name} must match the parent directory {directory_name}")
    description = frontmatter.get("description")
    if not isinstance(description, str):
        errors.append("description is required")
    else:
        folded = description.strip()
        if not folded:
            errors.append("description is empty")
        elif len(folded) > 1024:
            errors.append(f"description is {len(folded)} characters; the maximum is 1024")
        elif "review" not in folded.casefold() or ("when" not in folded.casefold() and "使用" not in folded):
            errors.append("description must say what the skill reviews and when to use it")
    license_name = frontmatter.get("license")
    if license_name != "MIT":
        errors.append("license must be MIT")
    compatibility = frontmatter.get("compatibility")
    if compatibility is not None:
        if not isinstance(compatibility, str) or not compatibility.strip():
            errors.append("compatibility must be a non-empty string when present")
        elif len(compatibility.strip()) > 500:
            errors.append("compatibility is longer than 500 characters")
    metadata = frontmatter.get("metadata")
    if not isinstance(metadata, dict):
        errors.append("metadata.author and metadata.version are required")
    else:
        for key, value in metadata.items():
            if not isinstance(value, str):
                errors.append(f"metadata.{key} must be a string")
        if metadata.get("author") != "LofiSu":
            errors.append("metadata.author must be LofiSu")
        if metadata.get("version") != "0.1.0":
            errors.append('metadata.version must be "0.1.0"')
        if "internal" in metadata:
            errors.append("metadata.internal would hide the skill from discovery")
    return errors


def readmes(root: Path) -> list[str]:
    errors: list[str] = []
    required = (INSTALL_COMMAND, LIST_COMMAND, MANUAL_SKILL_PATH, "0.1.0", *SOURCE_URLS)
    for name in ("README.md", "README.zh-CN.md"):
        path = root / name
        if not path.is_file():
            errors.append(f"{name}: file is missing")
            continue
        text = path.read_text(encoding="utf-8")
        for snippet in required:
            if snippet not in text:
                errors.append(f"{name}: missing {snippet}")
    return errors


def license_file(root: Path) -> list[str]:
    path = root / "LICENSE"
    if not path.is_file():
        return ["LICENSE: file is missing"]
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    if "MIT License" not in text or "Permission is hereby granted" not in text:
        errors.append("LICENSE: keep the MIT license text")
    if "LofiSu" not in text:
        errors.append("LICENSE: keep the LofiSu copyright line")
    return errors


def relative_links(root: Path) -> list[str]:
    errors: list[str] = []
    root_resolved = root.resolve()
    for path in iter_files(root):
        if path.suffix.casefold() != ".md":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for match in LINK_PATTERN.finditer(text):
            target = link_target(match.group(1).strip())
            if target is None:
                continue
            relative = display(root, path)
            if target.startswith("/"):
                errors.append(f"{relative}: absolute link {target}")
                continue
            destination = (path.parent / target).resolve()
            try:
                destination.relative_to(root_resolved)
            except ValueError:
                errors.append(f"{relative}: link escapes the repository: {target}")
                continue
            if not destination.is_file():
                errors.append(f"{relative}: missing link target {target}")
    return errors


def split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must start with YAML frontmatter")
    closing = text.find("\n---\n", 3)
    if closing == -1:
        raise ValueError("SKILL.md frontmatter is missing the closing marker")
    body = text[closing + 5 :]
    if not body.strip():
        raise ValueError("SKILL.md body is empty")
    return text[4:closing], body


def parse_frontmatter(block: str) -> dict[str, str | dict[str, str]]:
    parsed: dict[str, str | dict[str, str]] = {}
    lines = block.split("\n")
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        if line.startswith((" ", "\t")):
            raise ValueError(f"frontmatter line {index + 1} is indented unexpectedly")
        key, separator, raw_value = line.partition(":")
        if separator != ":" or not key.strip():
            raise ValueError(f"frontmatter line {index + 1} is not a key")
        key = key.strip()
        raw_value = raw_value.strip()
        index += 1
        if raw_value in FOLD_MARKERS:
            collected: list[str] = []
            while index < len(lines) and (not lines[index] or lines[index].startswith((" ", "\t"))):
                collected.append(lines[index].strip())
                index += 1
            if raw_value.startswith(">"):
                parsed[key] = " ".join(part for part in collected if part)
            else:
                parsed[key] = "\n".join(collected).strip()
            continue
        if raw_value == "":
            nested: dict[str, str] = {}
            while index < len(lines) and lines[index].startswith("  ") and not lines[index].startswith("   "):
                inner_key, inner_separator, inner_value = lines[index].strip().partition(":")
                if inner_separator != ":" or not inner_key:
                    raise ValueError(f"metadata line {index + 1} is not a string value")
                nested[inner_key.strip()] = unquote(inner_value.strip())
                index += 1
            parsed[key] = nested
            continue
        parsed[key] = unquote(raw_value)
    return parsed


def unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        inner = value[1:-1]
        if value[0] == "'":
            return inner.replace("''", "'")
        return inner.replace('\\"', '"').replace("\\\\", "\\")
    return value


def link_target(raw: str) -> str | None:
    target = raw[1:-1] if raw.startswith("<") and raw.endswith(">") else raw
    if " " in target:
        target = target.split(" ", 1)[0]
    if target.startswith(("http://", "https://", "mailto:", "#")):
        return None
    target = target.split("#", 1)[0].split("?", 1)[0]
    if not target:
        return None
    return target


def iter_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue
        if path.is_file():
            files.append(path)
    return files


def display(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


if __name__ == "__main__":
    if len(sys.argv) > 2:
        print("usage: validate_skill.py [ROOT]", file=sys.stderr)
        sys.exit(2)
    chosen = Path(sys.argv[1]).resolve() if len(sys.argv) == 2 else default_root()
    sys.exit(main(chosen))
