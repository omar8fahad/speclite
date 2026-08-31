#!/usr/bin/env python3
"""Prepare Phase 3 (plan): verify spec.md exists and has no open clarifications, stage plan.md."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

try:
    from common import get_feature_paths, project_principles_path, resolve_template
except ImportError:  # pragma: no cover - direct execution from unusual cwd
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from common import get_feature_paths, project_principles_path, resolve_template


def _help_text(argv0: str) -> str:
    return f"Usage: {argv0} [--json]\n  --json    Output machine-readable JSON\n"


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    if "--help" in args or "-h" in args:
        sys.stdout.write(_help_text(sys.argv[0]))
        return 0
    json_mode = "--json" in args

    paths = get_feature_paths(script_file=Path(__file__))

    if not paths.spec.is_file():
        print(
            f"ERROR: spec.md not found in {paths.feature_dir}. Run /speclite.specify first.",
            file=sys.stderr,
        )
        return 1

    spec_text = paths.spec.read_text(encoding="utf-8", errors="ignore")
    if "[NEEDS CLARIFICATION" in spec_text:
        print(
            "ERROR: spec.md still has open [NEEDS CLARIFICATION] markers. "
            "Finish /speclite.specify before planning.",
            file=sys.stderr,
        )
        return 1

    if not paths.plan.is_file():
        template = resolve_template("plan-template", paths.repo_root)
        if template is not None:
            shutil.copy(template, paths.plan)
        else:
            paths.plan.touch()

    references: list[str] = []
    if paths.references_dir.is_dir():
        for sub in sorted(paths.references_dir.iterdir()):
            if not sub.is_dir():
                continue
            files = [f.name for f in sub.iterdir() if f.is_file() and f.name != ".gitkeep"]
            if files:
                references.append(f"{sub.name}/ ({len(files)} file(s))")

    project_principles = project_principles_path(paths.repo_root)
    payload = {
        "FEATURE_DIR": str(paths.feature_dir),
        "SPEC_FILE": str(paths.spec),
        "PLAN_FILE": str(paths.plan),
        "PRINCIPLES_FILE": str(project_principles) if project_principles.is_file() else None,
        "REFERENCES": references,
    }

    if json_mode:
        print(json.dumps(payload, ensure_ascii=False))
    else:
        for key, value in payload.items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
