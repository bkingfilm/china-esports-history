#!/usr/bin/env python3
"""Validate content mapping, navigation, local links, and built page counts."""

from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
MAP_PATH = ROOT / "project" / "content-map.csv"
CONFIG_PATH = ROOT / "mkdocs.yml"
EXPECTED_CONTENT = 67
EXPECTED_PAGES = 75
VALID_TRANSLATION_STATES = {"not_started", "translating", "review", "published"}
CONTENT_DIRS = (
    DOCS / "zh" / "chapters",
    DOCS / "zh" / "gamehistory",
    DOCS / "zh" / "appendix",
)
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
HTML_LINK_RE = re.compile(r"""(?:src|href)\s*=\s*["']([^"']+)["']""", re.IGNORECASE)


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def normalized_repo_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def content_files() -> list[Path]:
    return sorted(
        path
        for directory in CONTENT_DIRS
        for path in directory.glob("*.md")
        if path.name != "index.md"
    )


def read_mapping(errors: list[str]) -> list[dict[str, str]]:
    with MAP_PATH.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != EXPECTED_CONTENT:
        fail(errors, f"content map has {len(rows)} rows; expected {EXPECTED_CONTENT}")
    return rows


def validate_mapping(rows: list[dict[str, str]], errors: list[str]) -> None:
    actual_files = {normalized_repo_path(path) for path in content_files()}
    mapped_files = {row["new_path"] for row in rows}
    if len(actual_files) != EXPECTED_CONTENT:
        fail(errors, f"found {len(actual_files)} Chinese content files; expected {EXPECTED_CONTENT}")
    if actual_files != mapped_files:
        missing = sorted(actual_files - mapped_files)
        extra = sorted(mapped_files - actual_files)
        fail(errors, f"content map/file mismatch; unmapped={missing}, missing={extra}")

    for field in ("content_id", "original_path", "new_path"):
        values = [row[field] for row in rows]
        duplicates = sorted({value for value in values if values.count(value) > 1})
        if duplicates:
            fail(errors, f"duplicate {field}: {duplicates}")

    for row in rows:
        content_id = row["content_id"]
        new_path = ROOT / row["new_path"]
        if not new_path.is_file():
            fail(errors, f"{content_id}: new path does not exist: {row['new_path']}")
        if row["migrated"] != "yes":
            fail(errors, f"{content_id}: migrated must be yes")
        if row["zh_status"] != "published":
            fail(errors, f"{content_id}: Chinese source must be published")
        if row["en_status"] not in VALID_TRANSLATION_STATES:
            fail(errors, f"{content_id}: invalid English status {row['en_status']!r}")
        if row["en_status"] == "published":
            if not row["en_path"]:
                fail(errors, f"{content_id}: published English translation has no path")
            elif not (ROOT / row["en_path"]).is_file():
                fail(errors, f"{content_id}: English path does not exist: {row['en_path']}")

        check = subprocess.run(
            ["git", "cat-file", "-e", f"HEAD:{row['original_path']}"],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if check.returncode != 0:
            fail(errors, f"{content_id}: original path is absent from HEAD: {row['original_path']}")


def flatten_nav(value: object) -> list[str]:
    paths: list[str] = []
    if isinstance(value, str) and value.endswith(".md"):
        paths.append(value)
    elif isinstance(value, list):
        for item in value:
            paths.extend(flatten_nav(item))
    elif isinstance(value, dict):
        for item in value.values():
            paths.extend(flatten_nav(item))
    return paths


def output_route(markdown_path: Path) -> str:
    relative = markdown_path.relative_to(DOCS)
    if relative.name == "index.md":
        return (relative.parent / "index.html").as_posix()
    return (relative.with_suffix("") / "index.html").as_posix()


def validate_pages_and_nav(errors: list[str]) -> None:
    pages = sorted(DOCS.rglob("*.md"))
    if len(pages) != EXPECTED_PAGES:
        fail(errors, f"found {len(pages)} Markdown pages; expected {EXPECTED_PAGES}")

    routes = [output_route(path) for path in pages]
    if len(routes) != len(set(routes)):
        duplicates = sorted({route for route in routes if routes.count(route) > 1})
        fail(errors, f"duplicate output routes: {duplicates}")

    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    nav_paths = flatten_nav(config.get("nav", []))
    expected = {path.relative_to(DOCS).as_posix() for path in pages}
    actual = set(nav_paths)
    if len(nav_paths) != len(actual):
        duplicates = sorted({path for path in nav_paths if nav_paths.count(path) > 1})
        fail(errors, f"duplicate navigation entries: {duplicates}")
    if expected != actual:
        fail(
            errors,
            "navigation/page mismatch; "
            f"not_in_nav={sorted(expected - actual)}, missing_pages={sorted(actual - expected)}",
        )


def clean_target(raw_target: str) -> str:
    target = raw_target.strip()
    if " " in target and target.rsplit(" ", 1)[-1].startswith(("'", '"')):
        target = target.rsplit(" ", 1)[0]
    return unquote(urlsplit(target).path)


def validate_links(errors: list[str]) -> None:
    sources = list(DOCS.rglob("*.md")) + [
        ROOT / "README.md",
        ROOT / "CONTRIBUTING.md",
        ROOT / "project" / "information-architecture.md",
        ROOT / "project" / "localization.md",
        ROOT / "project" / "maintenance.md",
    ]
    for source in sources:
        text = source.read_text(encoding="utf-8")
        raw_targets = MARKDOWN_LINK_RE.findall(text) + HTML_LINK_RE.findall(text)
        for raw_target in raw_targets:
            if not raw_target or raw_target.startswith(("#", "//", "{")):
                continue
            parsed = urlsplit(raw_target.strip())
            if parsed.scheme or parsed.netloc:
                continue
            target_path = clean_target(raw_target)
            if not target_path:
                continue
            resolved = (source.parent / target_path).resolve()
            if target_path.endswith("/"):
                resolved = resolved / "index.md"
            if not resolved.exists():
                fail(
                    errors,
                    f"{normalized_repo_path(source)}: broken local link {raw_target!r}",
                )


def validate_site(site: Path, errors: list[str]) -> None:
    if not site.is_dir():
        fail(errors, f"built site directory does not exist: {site}")
        return
    html_pages = sorted(site.rglob("index.html"))
    if len(html_pages) != EXPECTED_PAGES:
        fail(errors, f"built site has {len(html_pages)} index pages; expected {EXPECTED_PAGES}")
    if not (site / "sitemap.xml").is_file():
        fail(errors, "built site is missing sitemap.xml")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path, help="also validate a built MkDocs site")
    args = parser.parse_args()

    errors: list[str] = []
    rows = read_mapping(errors)
    validate_mapping(rows, errors)
    validate_pages_and_nav(errors)
    validate_links(errors)
    if args.site:
        validate_site(args.site.resolve(), errors)

    if errors:
        print("Validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        f"Validation passed: {EXPECTED_CONTENT} mapped content files, "
        f"{EXPECTED_PAGES} Markdown pages, complete navigation, and valid local links."
    )
    if args.site:
        print(f"Built site passed: {EXPECTED_PAGES} generated HTML pages and sitemap.xml.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
