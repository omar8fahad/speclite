#!/usr/bin/env python3
"""Phase 1 (constitution): ensure the ONE project-wide principles.md exists.

Matches Spec Kit's own constitution philosophy: a single file for the whole project,
never per-feature. This script never overwrites an existing principles.md - if one is
already there, it's reported back untouched so the agent offers to *amend* it through
conversation instead of recreating it. Amending is always a conscious, explicit act -
never a side effect of some other phase editing around a conflict.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from common import append_log, get_repo_root, project_principles_path, resolve_template
except ImportError:  # pragma: no cover - direct execution from unusual cwd
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from common import append_log, get_repo_root, project_principles_path, resolve_template


def _help_text(argv0: str) -> str:
    return f"Usage: {argv0} [--json]\n  --json    Output machine-readable JSON\n"


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    if "--help" in args or "-h" in args:
        sys.stdout.write(_help_text(sys.argv[0]))
        return 0
    json_mode = "--json" in args

    repo_root = get_repo_root(Path(__file__))
    principles_file = project_principles_path(repo_root)
    already_existed = principles_file.is_file()

    if not already_existed:
        principles_file.parent.mkdir(parents=True, exist_ok=True)
        template = resolve_template("principles-template", repo_root)
        if template is not None:
            principles_file.write_text(template.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            principles_file.write_text("# Project Principles\n\n[Fill in]\n", encoding="utf-8")

    log_base = repo_root / ".speclite"
    summary = (
        "principles.md staged from template"
        if not already_existed
        else "principles.md already exists - amending, not recreating"
    )
    append_log(log_base, "constitution", "INFO", summary)

    payload = {
        "PRINCIPLES_FILE": str(principles_file),
        "ALREADY_EXISTED": already_existed,
    }
    if json_mode:
        print(json.dumps(payload, ensure_ascii=False))
    else:
        for key, value in payload.items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
