#!/usr/bin/env python3
"""Stage the Project Map (optional, cross-cutting capability - not one of the 5 phases).

Auto-detects build vs update mode, and for updates, computes a cheap changed-files delta
(git diff since last sync, or file-mtime fallback if there's no git) so the agent only has
to read what actually changed instead of re-scanning the whole repository every time.

The map lives directly in specs/ (PROJECT_MAP.md, PRD_TRACEABILITY.md, ARCHITECTURE_MAP.md,
FILE_INDEX.md, PROJECT_MAP.json), alongside the specs/NNN-feature/ directories - never
inside any one of them, since it's a project-wide artifact like the constitution.

No logs/ integration by design - PROJECT_MAP.md carries its own sync state (an invisible
<!-- speclite-map-state --> block at the top) instead of a separate log file.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    from common import (
        DEFAULT_MAP_EXCLUDES,
        get_repo_root,
        git_changed_files_since,
        git_current_commit,
        is_git_repo,
        list_source_prds,
        map_file_paths,
        mtime_changed_files_since,
        read_map_state,
        resolve_template,
    )
except ImportError:  # pragma: no cover - direct execution from unusual cwd
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from common import (
        DEFAULT_MAP_EXCLUDES,
        get_repo_root,
        git_changed_files_since,
        git_current_commit,
        is_git_repo,
        list_source_prds,
        map_file_paths,
        mtime_changed_files_since,
        read_map_state,
        resolve_template,
    )

# Above this many changed files, stop listing individually and recommend a broader
# full-sync pass instead - keeps a single update from ballooning into a full re-read.
CHANGED_FILES_CAP = 200


def _extract_known_files_from_file_index(file_index_path: Path) -> set[str]:
    """Best-effort: pull path-looking tokens from FILE_INDEX.md's existing entries, so the
    mtime fallback can detect deletions too (a file listed there that's now gone)."""
    if not file_index_path.is_file():
        return set()
    import re

    text = file_index_path.read_text(encoding="utf-8", errors="ignore")
    return set(re.findall(r"`([\w./\-]+\.\w+)`", text))


def _help_text(argv0: str) -> str:
    return (
        f"Usage: {argv0} [--json] [--known-changes TEXT] [--feature-dir PATH]\n"
        "  --json                Output machine-readable JSON\n"
        "  --known-changes TEXT  Optional hint about what's known to have changed\n"
        "  --feature-dir PATH    Feature directory that triggered this (feature-integration)\n"
    )


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    if "--help" in args or "-h" in args:
        sys.stdout.write(_help_text(sys.argv[0]))
        return 0
    json_mode = "--json" in args

    known_changes = None
    if "--known-changes" in args:
        i = args.index("--known-changes")
        if i + 1 < len(args):
            known_changes = args[i + 1]

    feature_dir_arg = None
    if "--feature-dir" in args:
        i = args.index("--feature-dir")
        if i + 1 < len(args):
            feature_dir_arg = args[i + 1]

    repo_root = get_repo_root(Path(__file__))
    paths = map_file_paths(repo_root)
    paths["project_map"].parent.mkdir(parents=True, exist_ok=True)

    build_mode = not paths["project_map"].is_file()
    state = read_map_state(paths["project_map"])
    current_commit = git_current_commit(repo_root) if is_git_repo(repo_root) else None

    changed_files: list[tuple[str, str]] = []
    changed_files_truncated = False
    scan_basis = "full (build mode - no prior sync)"

    if not build_mode:
        last_commit = state.get("last_sync_commit")
        last_timestamp = state.get("last_sync_timestamp")

        result = None
        if last_commit and last_commit != "none" and is_git_repo(repo_root):
            result = git_changed_files_since(repo_root, last_commit)
            if result is not None:
                scan_basis = f"git diff since {last_commit[:12]}"

        if result is None and last_timestamp:
            known_files = _extract_known_files_from_file_index(paths["file_index"])
            result = mtime_changed_files_since(repo_root, last_timestamp, known_files)
            scan_basis = f"file mtimes since {last_timestamp} (no usable git history)"

        if result is None:
            scan_basis = "full (no prior sync state found - treat as full-sync)"
            changed_files = []
        else:
            changed_files = result

        if len(changed_files) > CHANGED_FILES_CAP:
            changed_files_truncated = True
            changed_files = changed_files[:CHANGED_FILES_CAP]

    if build_mode:
        for key in ("project_map", "prd_traceability", "architecture_map", "file_index"):
            template_name = {
                "project_map": "project-map-template",
                "prd_traceability": "prd-traceability-template",
                "architecture_map": "architecture-map-template",
                "file_index": "file-index-template",
            }[key]
            template = resolve_template(template_name, repo_root)
            if template is not None:
                paths[key].write_text(template.read_text(encoding="utf-8"), encoding="utf-8")

    triggering_feature = None
    if feature_dir_arg:
        fd = Path(feature_dir_arg)
        if not fd.is_absolute():
            fd = repo_root / fd
        triggering_feature = str(fd.relative_to(repo_root)) if fd.is_dir() else feature_dir_arg

    payload = {
        "MODE": "build" if build_mode else "update",
        "MAP_FILES": {k: str(v) for k, v in paths.items()},
        "SOURCE_PRDS": list_source_prds(repo_root),
        "GIT_AVAILABLE": is_git_repo(repo_root),
        "LAST_SYNC_COMMIT": state.get("last_sync_commit"),
        "CURRENT_COMMIT": current_commit,
        "SCAN_BASIS": scan_basis,
        "CHANGED_FILES": [{"status": s, "path": p} for s, p in changed_files],
        "CHANGED_FILES_TRUNCATED": changed_files_truncated,
        "TRIGGERING_FEATURE_DIR": triggering_feature,
        "KNOWN_CHANGES_HINT": known_changes,
        "JSON_EXPORT_ENABLED": True,
        "DEFAULT_EXCLUDES": sorted(DEFAULT_MAP_EXCLUDES),
    }

    if json_mode:
        print(json.dumps(payload, ensure_ascii=False))
    else:
        for key, value in payload.items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
