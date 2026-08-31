#!/usr/bin/env python3
"""Start a new speclite feature (Phase 2: specify).

Creates specs/NNN-short-name/ with spec.md, the standard references/ subfolders, and a
single flat logs/ folder for free-form evidence (test output, screenshots, session notes)
the agent adds later - never used to track phase completion, see status.py.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    from common import (
        create_log_dirs,
        create_reference_dirs,
        get_repo_root,
        persist_feature_json,
        project_principles_path,
        resolve_template,
    )
except ImportError:  # pragma: no cover - direct execution from unusual cwd
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from common import (
        create_log_dirs,
        create_reference_dirs,
        get_repo_root,
        persist_feature_json,
        project_principles_path,
        resolve_template,
    )

_STOP_WORDS = frozenset(
    "a an the to for of in on at by with from is are was were i want need "
    "add build create make new".split()
)


def _short_name(description: str) -> str:
    words = re.sub(r"[^a-z0-9]", " ", description.lower()).split()
    meaningful = [w for w in words if w not in _STOP_WORDS and len(w) >= 3]
    chosen = meaningful[:4] if meaningful else words[:3]
    return "-".join(chosen) or "feature"


def _next_number(specs_dir: Path) -> int:
    highest = 0
    if specs_dir.is_dir():
        for entry in specs_dir.iterdir():
            if entry.is_dir() and re.match(r"^\d{3,}-", entry.name):
                match = re.match(r"^\d+", entry.name)
                if match:
                    highest = max(highest, int(match.group()))
    return highest + 1


def _help_text(argv0: str) -> str:
    return (
        f"Usage: {argv0} [--json] [--short-name <name>] <feature description>\n"
        "  --json              Output machine-readable JSON\n"
        "  --short-name <name> Override the auto-generated 2-4 word slug\n"
    )


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    if "--help" in args or "-h" in args:
        sys.stdout.write(_help_text(sys.argv[0]))
        return 0

    json_mode = "--json" in args
    args = [a for a in args if a != "--json"]

    short_name_override = None
    if "--short-name" in args:
        i = args.index("--short-name")
        if i + 1 >= len(args):
            print("Error: --short-name requires a value", file=sys.stderr)
            return 1
        short_name_override = args[i + 1]
        del args[i : i + 2]

    description = " ".join(args).strip()
    if not description:
        print("Error: feature description is required", file=sys.stderr)
        return 1

    repo_root = get_repo_root(Path(__file__))
    specs_dir = repo_root / "specs"
    specs_dir.mkdir(parents=True, exist_ok=True)

    suffix = short_name_override or _short_name(description)
    number = _next_number(specs_dir)
    dir_name = f"{number:03d}-{suffix}"
    feature_dir = specs_dir / dir_name

    if feature_dir.is_dir():
        print(f"Error: {feature_dir} already exists", file=sys.stderr)
        return 1

    feature_dir.mkdir(parents=True)
    references_dir = create_reference_dirs(feature_dir)
    create_log_dirs(feature_dir)

    spec_file = feature_dir / "spec.md"
    template = resolve_template("spec-template", repo_root)
    if template is not None:
        spec_file.write_text(template.read_text(encoding="utf-8"), encoding="utf-8")
    else:
        spec_file.write_text(
            f"# Feature Specification: {description}\n\n"
            "[NEEDS CLARIFICATION: spec-template.md not found - see .speclite/templates/]\n",
            encoding="utf-8",
        )

    persist_feature_json(repo_root, f"specs/{dir_name}")

    project_principles = project_principles_path(repo_root)
    payload = {
        "FEATURE_DIR": str(feature_dir),
        "SPEC_FILE": str(spec_file),
        "REFERENCES_DIR": str(references_dir),
        "FEATURE_NUM": f"{number:03d}",
        "PROJECT_PRINCIPLES_FILE": str(project_principles) if project_principles.is_file() else None,
    }

    if json_mode:
        print(json.dumps(payload, ensure_ascii=False))
    else:
        for key, value in payload.items():
            print(f"{key}: {value}")
        print(f"\nDrop any PRDs, guidelines, fonts, sounds, videos, data, or docs into: {references_dir}")
        if not project_principles.is_file():
            print(
                "Note: no project constitution yet - consider running /speclite.constitution "
                "first (it's optional, but recommended as Phase 1)."
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
