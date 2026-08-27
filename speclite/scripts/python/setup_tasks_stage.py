#!/usr/bin/env python3
"""Prepare Phase 4 (tasks): verify plan.md's checklist is clean, stage tasks.md."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

try:
    from common import count_unchecked_boxes, extract_section, get_feature_paths, resolve_template
except ImportError:  # pragma: no cover - direct execution from unusual cwd
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from common import count_unchecked_boxes, extract_section, get_feature_paths, resolve_template


def _help_text(argv0: str) -> str:
    return f"Usage: {argv0} [--json]\n  --json    Output machine-readable JSON\n"


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    if "--help" in args or "-h" in args:
        sys.stdout.write(_help_text(sys.argv[0]))
        return 0
    json_mode = "--json" in args

    paths = get_feature_paths(script_file=Path(__file__))

    if not paths.plan.is_file():
        print(
            f"ERROR: plan.md not found in {paths.feature_dir}. Run /speclite.plan first.",
            file=sys.stderr,
        )
        return 1

    plan_text = paths.plan.read_text(encoding="utf-8", errors="ignore")
    checklist_section = extract_section(plan_text, "Pre-Implementation Checklist")
    unchecked = count_unchecked_boxes(checklist_section)
    if unchecked > 0:
        print(
            f"ERROR: plan.md's Pre-Implementation Checklist still has {unchecked} unchecked "
            "item(s). Finish /speclite.plan before generating tasks.",
            file=sys.stderr,
        )
        return 1

    if not paths.tasks.is_file():
        template = resolve_template("tasks-template", paths.repo_root)
        if template is not None:
            shutil.copy(template, paths.tasks)
        else:
            paths.tasks.touch()

    payload = {
        "FEATURE_DIR": str(paths.feature_dir),
        "SPEC_FILE": str(paths.spec),
        "PLAN_FILE": str(paths.plan),
        "TASKS_FILE": str(paths.tasks),
    }

    if json_mode:
        print(json.dumps(payload, ensure_ascii=False))
    else:
        for key, value in payload.items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
