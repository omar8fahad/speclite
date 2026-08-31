#!/usr/bin/env python3
"""Detect where a speclite project/feature currently stands, and what to run next.

This is what lets the manager skill chain phases automatically without the user having
to remember the order or where they left off. Run with no arguments any time; it never
asks a question itself - it just reports NEXT_PHASE and REASON, and the calling agent
decides how to act on that (including asking the user something, if NEEDS_USER_INPUT
is true).

Every phase's completion is read directly from its artifact, Spec Kit's own style -
there is no separate check-log this script relies on:
  - specify:   spec.md has no [NEEDS CLARIFICATION] marker left
  - plan:      plan.md's Pre-Implementation Checklist is fully checked
  - tasks:     tasks.md's "Analysis complete" checkbox is ticked
  - implement: every task is [X] AND tasks.md's Final Gap-Check checkbox is ticked

Constitution (Phase 1) is recommended as the first thing to run in a brand-new project,
but - matching Spec Kit's own model - it's not a hard gate: once a feature exists, its
absence never blocks specify/plan/tasks/implement. Later phases just read
.speclite/memory/principles.md "if it exists".

Also computes MAP_SUGGESTION/MAP_REASON - a purely informational, non-blocking nudge
about the optional Project Map (see setup_map_stage.py). This never affects NEXT_PHASE;
it's up to the calling agent to decide *when* to actually mention it (natural breakpoints
like right after implement finishes, or at the start of a project - not mid-phase).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from common import (
        count_unchecked_tasks,
        extract_section,
        count_unchecked_boxes,
        get_repo_root,
        is_marker_checked,
        list_all_features,
        map_file_paths,
        project_principles_path,
        read_feature_json,
    )
except ImportError:  # pragma: no cover - direct execution from unusual cwd
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from common import (
        count_unchecked_tasks,
        extract_section,
        count_unchecked_boxes,
        get_repo_root,
        is_marker_checked,
        list_all_features,
        map_file_paths,
        project_principles_path,
        read_feature_json,
    )

# speclite's own scaffolding - not "existing project code" for the purposes of deciding
# whether an initial Project Map build is worth suggesting.
_OWN_SCAFFOLDING = {".speclite", ".agents", "skills", "specs", "speclite", ".git"}


def _compute_map_suggestion(repo_root: Path) -> dict:
    project_map = map_file_paths(repo_root)["project_map"]

    if not project_map.is_file():
        try:
            has_other_files = any(p.name not in _OWN_SCAFFOLDING for p in repo_root.iterdir())
        except OSError:
            has_other_files = False
        if has_other_files:
            return {
                "MAP_SUGGESTION": "build",
                "MAP_REASON": (
                    "There's real code in this repo and no project map yet - consider "
                    "suggesting /speclite.map at a natural breakpoint (project start, or "
                    "right after a feature completes)."
                ),
            }
        return {"MAP_SUGGESTION": None, "MAP_REASON": None}

    try:
        map_mtime = project_map.stat().st_mtime
    except OSError:
        return {"MAP_SUGGESTION": None, "MAP_REASON": None}

    newest_tasks_mtime = 0.0
    for feature in list_all_features(repo_root):
        tasks_path = repo_root / "specs" / feature / "tasks.md"
        if tasks_path.is_file():
            try:
                newest_tasks_mtime = max(newest_tasks_mtime, tasks_path.stat().st_mtime)
            except OSError:
                continue

    if newest_tasks_mtime > map_mtime:
        return {
            "MAP_SUGGESTION": "update",
            "MAP_REASON": (
                "A feature's tasks.md changed more recently than the last map sync - "
                "consider suggesting /speclite.map (feature-integration) at a natural "
                "breakpoint, such as right after implement finishes."
            ),
        }
    return {"MAP_SUGGESTION": None, "MAP_REASON": None}


def _compute_status(repo_root: Path) -> dict:
    installed = (repo_root / ".speclite").is_dir()
    payload: dict = {"INSTALLED": installed, "REPO_ROOT": str(repo_root)}
    if not installed:
        payload["NEXT_PHASE"] = "install"
        payload["REASON"] = "No .speclite/ directory found - run install.py / install.ps1 first."
        payload["NEEDS_USER_INPUT"] = False
        return payload

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
            return payload
        payload["ACTIVE_FEATURE"] = None
        payload["NEXT_PHASE"] = "specify"
        payload["REASON"] = "No feature exists yet - start with /speclite.specify."
        payload["NEEDS_USER_INPUT"] = False
        return payload

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
            return payload

    payload["ACTIVE_FEATURE"] = str(active_feature_dir)

    spec = active_feature_dir / "spec.md"
    plan = active_feature_dir / "plan.md"
    tasks = active_feature_dir / "tasks.md"

    if not spec.is_file():
        payload["NEXT_PHASE"] = "specify"
        payload["REASON"] = "spec.md not created yet."
        payload["NEEDS_USER_INPUT"] = False
        return payload

    spec_text = spec.read_text(encoding="utf-8", errors="ignore")
    if "[NEEDS CLARIFICATION" in spec_text:
        payload["NEXT_PHASE"] = "specify"
        payload["REASON"] = "spec.md still has open [NEEDS CLARIFICATION] markers."
        payload["NEEDS_USER_INPUT"] = True
        return payload

    if not plan.is_file():
        payload["NEXT_PHASE"] = "plan"
        payload["REASON"] = "plan.md not created yet."
        payload["NEEDS_USER_INPUT"] = False
        return payload

    plan_text = plan.read_text(encoding="utf-8", errors="ignore")
    checklist_section = extract_section(plan_text, "Pre-Implementation Checklist")
    unchecked_plan = count_unchecked_boxes(checklist_section)
    if unchecked_plan > 0:
        payload["NEXT_PHASE"] = "plan"
        payload["REASON"] = f"{unchecked_plan} Pre-Implementation Checklist item(s) still unchecked in plan.md."
        payload["NEEDS_USER_INPUT"] = False
        return payload

    if not tasks.is_file():
        payload["NEXT_PHASE"] = "tasks"
        payload["REASON"] = "tasks.md not created yet."
        payload["NEEDS_USER_INPUT"] = False
        return payload

    tasks_text = tasks.read_text(encoding="utf-8", errors="ignore")
    if not is_marker_checked(tasks_text, "Analysis complete"):
        payload["NEXT_PHASE"] = "tasks"
        payload["REASON"] = "tasks.md exists but the Analysis Pass checkbox isn't checked yet."
        payload["NEEDS_USER_INPUT"] = False
        return payload

    unchecked_tasks = count_unchecked_tasks(tasks_text)
    if unchecked_tasks > 0:
        payload["NEXT_PHASE"] = "implement"
        payload["REASON"] = f"{unchecked_tasks} task(s) still unchecked in tasks.md."
        payload["NEEDS_USER_INPUT"] = False
        return payload

    if not is_marker_checked(tasks_text, "Verified against spec.md"):
        payload["NEXT_PHASE"] = "implement"
        payload["REASON"] = "All tasks are checked off, but the Final Gap-Check checkbox isn't checked yet."
        payload["NEEDS_USER_INPUT"] = False
        return payload

    payload["NEXT_PHASE"] = "done"
    payload["REASON"] = "Everything is checked off and the final gap-check passed."
    payload["NEEDS_USER_INPUT"] = False
    return payload


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    json_mode = "--json" in args

    repo_root = get_repo_root(Path(__file__))
    payload = _compute_status(repo_root)

    if payload.get("INSTALLED"):
        payload.update(_compute_map_suggestion(repo_root))

    if json_mode:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for key, value in payload.items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
