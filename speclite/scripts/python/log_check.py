#!/usr/bin/env python3
"""Append one entry to a phase's check log.

Writes to <feature_dir>/logs/<phase>/index.md for every phase EXCEPT constitution, which
is always project-wide and lives at .speclite/logs/1-constitution/index.md instead - it's
never tied to a single feature.

This script only manages index.md. The agent is free to also drop other files (test
output, screenshots, extra docs) into the same logs/<phase>/ folder, organized into
its own subfolders by type - that part is not scripted, by design.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from common import PHASE_ORDER, append_log, get_feature_paths, get_repo_root
except ImportError:  # pragma: no cover - direct execution from unusual cwd
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from common import PHASE_ORDER, append_log, get_feature_paths, get_repo_root


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Record a check-log entry for the active feature.")
    parser.add_argument("--phase", required=True, choices=PHASE_ORDER, help="Which speclite phase")
    parser.add_argument(
        "--status", required=True, choices=["PASS", "WARN", "FAIL", "INFO"], help="Outcome of the check"
    )
    parser.add_argument("--summary", required=True, help="One-line summary shown in the log table")
    parser.add_argument(
        "--details", default="", help="Optional longer Markdown, collapsed under a <details> block"
    )
    args = parser.parse_args(list(argv if argv is not None else sys.argv[1:]))

    if args.phase == "constitution":
        repo_root = get_repo_root(Path(__file__))
        base_dir = repo_root / ".speclite"
    else:
        paths = get_feature_paths(script_file=Path(__file__))
        base_dir = paths.feature_dir

    log_path = append_log(base_dir, args.phase, args.status, args.summary, args.details)
    print(f"Logged [{args.status}] {args.phase}: {args.summary}")
    print(f"-> {log_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
