#!/usr/bin/env python3
"""Check that required speclite artifacts exist before a phase runs."""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from common import count_unchecked_boxes, get_feature_paths, project_principles_path
except ImportError:  # pragma: no cover - direct execution from unusual cwd
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from common import count_unchecked_boxes, get_feature_paths, project_principles_path

HELP_TEXT = """Usage: check_prerequisites.py [OPTIONS]

OPTIONS:
  --json           Output machine-readable JSON
  --require-plan   Fail if plan.md is missing
  --require-tasks  Fail if tasks.md is missing
  --paths-only     Only print resolved paths, skip all validation
  --help, -h       Show this help message
"""


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    if "--help" in args or "-h" in args:
        sys.stdout.write(HELP_TEXT)
        return 0

    json_mode = "--json" in args
    require_plan = "--require-plan" in args
    require_tasks = "--require-tasks" in args
    paths_only = "--paths-only" in args

    paths = get_feature_paths(no_persist=paths_only, script_file=Path(__file__))

    if paths_only:
        payload = {
            "REPO_ROOT": str(paths.repo_root),
            "FEATURE_DIR": str(paths.feature_dir),
            "SPEC_FILE": str(paths.spec),
            "PLAN_FILE": str(paths.plan),
            "TASKS_FILE": str(paths.tasks),
            "LOGS_DIR": str(paths.logs_dir),
        }
        if json_mode:
            print(json.dumps(payload, ensure_ascii=False))
        else:
            for key, value in payload.items():
                print(f"{key}: {value}")
        return 0

    if not paths.spec.is_file():
        print(
            f"ERROR: spec.md not found in {paths.feature_dir}. Run /speclite.specify first.",
            file=sys.stderr,
        )
        return 1
    if require_plan and not paths.plan.is_file():
        print(
            f"ERROR: plan.md not found in {paths.feature_dir}. Run /speclite.plan first.",
            file=sys.stderr,
        )
        return 1
    if require_tasks and not paths.tasks.is_file():
        print(
            f"ERROR: tasks.md not found in {paths.feature_dir}. Run /speclite.tasks first.",
            file=sys.stderr,
        )
        return 1
    if require_tasks and paths.tasks.is_file():
        tasks_text = paths.tasks.read_text(encoding="utf-8", errors="ignore")
        if count_unchecked_boxes(tasks_text) == 0 and "T00" not in tasks_text:
            print(
                f"ERROR: tasks.md in {paths.feature_dir} has no tasks yet. Run /speclite.tasks first.",
                file=sys.stderr,
            )
            return 1

    docs: list[str] = []
    if paths.plan.is_file():
        docs.append("plan.md")
    if paths.tasks.is_file():
        docs.append("tasks.md")
    if project_principles_path(paths.repo_root).is_file():
        docs.append("principles.md (project-wide)")
    if paths.references_dir.is_dir():
        for sub in sorted(paths.references_dir.iterdir()):
            if sub.is_dir() and any(f.is_file() and f.name != ".gitkeep" for f in sub.iterdir()):
                docs.append(f"references/{sub.name}/")

    payload = {"FEATURE_DIR": str(paths.feature_dir), "AVAILABLE_DOCS": docs}
    if json_mode:
        print(json.dumps(payload, ensure_ascii=False))
    else:
        print(f"FEATURE_DIR: {paths.feature_dir}")
        print(f"AVAILABLE_DOCS: {', '.join(docs) if docs else '(none)'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
