#!/usr/bin/env python3
"""Detect where a speclite project/feature currently stands, and what to run next.

This is what lets the manager skill chain phases automatically without the user having
to remember the order or where they left off. Run with no arguments any time; it never
asks a question itself - it just reports NEXT_PHASE and REASON, and the calling agent
decides how to act on that (including asking the user something, if NEEDS_USER_INPUT
is true).

Constitution (Phase 1) is recommended as the first thing to run in a brand-new project,
but - matching Spec Kit's own model - it's not a hard gate: once a feature exists, its
absence never blocks specify/plan/tasks/implement. Later phases just read
.speclite/memory/principles.md "if it exists".
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from common import (
        count_unchecked_boxes,
        extract_section,
        get_repo_root,
        list_all_features,
        project_principles_path,
        read_feature_json,
        read_log_text,
    )
except ImportError:  # pragma: no cover - direct execution from unusual cwd
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from common import (
        count_unchecked_boxes,
        extract_section,
        get_repo_root,
        list_all_features,
        project_principles_path,
        read_feature_json,
        read_log_text,
    )


def _emit(payload: dict, json_mode: bool) -> int:
    if json_mode:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for key, value in payload.items():
            print(f"{key}: {value}")
    return 0


def _log_has_status(log_text: str, *statuses: str) -> bool:
    """Whether the log's table contains a row with any of the given status words."""
    return any(f" {status} " in log_text or f" {status} |" in log_text for status in statuses)


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    json_mode = "--json" in args

    repo_root = get_repo_root(Path(__file__))
    installed = (repo_root / ".speclite").is_dir()

    payload: dict = {"INSTALLED": installed, "REPO_ROOT": str(repo_root)}
    if not installed:
        payload["NEXT_PHASE"] = "install"
        payload["REASON"] = "No .speclite/ directory found - run install.py / install.ps1 first."
        payload["NEEDS_USER_INPUT"] = False
        return _emit(payload, json_mode)

    all_features = list_all_features(repo_root)
    payload["ALL_FEATURES"] = all_features
    payload["HAS_PROJECT_PRINCIPLES"] = project_principles_path(repo_root).is_file()

    active_rel = read_feature_json(repo_root)
    active_feature_dir = None
    if active_rel:
        candidate = repo_root / active_rel
        if candidate.is_dir():
            active_feature_dir = candidate

    if active_feature_dir is None and len(all_features) == 0:
        # Nothing has started yet in this project at all.
        if not payload["HAS_PROJECT_PRINCIPLES"]:
            payload["ACTIVE_FEATURE"] = None
            payload["NEXT_PHASE"] = "constitution"
            payload["REASON"] = (
                "No project constitution yet - recommended as Phase 1 before the first "
                "feature, though it's optional and can be skipped straight to specify."
            )
            payload["NEEDS_USER_INPUT"] = False
            return _emit(payload, json_mode)
        payload["ACTIVE_FEATURE"] = None
        payload["NEXT_PHASE"] = "specify"
        payload["REASON"] = "No feature exists yet - start with /speclite.specify."
        payload["NEEDS_USER_INPUT"] = False
        return _emit(payload, json_mode)

    if active_feature_dir is None:
        if len(all_features) == 1:
            active_feature_dir = repo_root / "specs" / all_features[0]
        else:
            payload["ACTIVE_FEATURE"] = None
            payload["NEXT_PHASE"] = "ambiguous"
            payload["REASON"] = (
                f"{len(all_features)} features exist and none is marked active - ask the "
                "user which one to resume (or whether to start a new one)."
            )
            payload["NEEDS_USER_INPUT"] = True
            return _emit(payload, json_mode)

    payload["ACTIVE_FEATURE"] = str(active_feature_dir)

    spec = active_feature_dir / "spec.md"
    plan = active_feature_dir / "plan.md"
    tasks = active_feature_dir / "tasks.md"

    if not spec.is_file():
        payload["NEXT_PHASE"] = "specify"
        payload["REASON"] = "spec.md not created yet."
        payload["NEEDS_USER_INPUT"] = False
        return _emit(payload, json_mode)

    spec_text = spec.read_text(encoding="utf-8", errors="ignore")
    if "[NEEDS CLARIFICATION" in spec_text:
        payload["NEXT_PHASE"] = "specify"
        payload["REASON"] = "spec.md still has open [NEEDS CLARIFICATION] markers."
        payload["NEEDS_USER_INPUT"] = True
        return _emit(payload, json_mode)

    if not plan.is_file():
        payload["NEXT_PHASE"] = "plan"
        payload["REASON"] = "plan.md not created yet."
        payload["NEEDS_USER_INPUT"] = False
        return _emit(payload, json_mode)

    plan_text = plan.read_text(encoding="utf-8", errors="ignore")
    checklist_section = extract_section(plan_text, "Pre-Implementation Checklist")
    unchecked_plan = count_unchecked_boxes(checklist_section)
    if unchecked_plan > 0:
        payload["NEXT_PHASE"] = "plan"
        payload["REASON"] = f"{unchecked_plan} Pre-Implementation Checklist item(s) still unchecked in plan.md."
        payload["NEEDS_USER_INPUT"] = False
        return _emit(payload, json_mode)

    if not tasks.is_file():
        payload["NEXT_PHASE"] = "tasks"
        payload["REASON"] = "tasks.md not created yet."
        payload["NEEDS_USER_INPUT"] = False
        return _emit(payload, json_mode)

    analyze_log = read_log_text(active_feature_dir, "tasks")
    if not _log_has_status(analyze_log, "PASS", "WARN"):
        payload["NEXT_PHASE"] = "tasks"
        payload["REASON"] = "tasks.md exists but the analyze consistency pass hasn't been logged yet."
        payload["NEEDS_USER_INPUT"] = False
        return _emit(payload, json_mode)

    tasks_text = tasks.read_text(encoding="utf-8", errors="ignore")
    unchecked_tasks = count_unchecked_boxes(tasks_text)
    if unchecked_tasks > 0:
        payload["NEXT_PHASE"] = "implement"
        payload["REASON"] = f"{unchecked_tasks} task(s) still unchecked in tasks.md."
        payload["NEEDS_USER_INPUT"] = False
        return _emit(payload, json_mode)

    implement_log = read_log_text(active_feature_dir, "implement")
    if not _log_has_status(implement_log, "PASS"):
        payload["NEXT_PHASE"] = "implement"
        payload["REASON"] = "All tasks are checked off, but the final gap-check hasn't been logged as clean yet."
        payload["NEEDS_USER_INPUT"] = False
        return _emit(payload, json_mode)

    payload["NEXT_PHASE"] = "done"
    payload["REASON"] = "Everything is checked off and the final gap-check passed."
    payload["NEEDS_USER_INPUT"] = False
    return _emit(payload, json_mode)


if __name__ == "__main__":
    raise SystemExit(main())
