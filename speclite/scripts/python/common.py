"""Shared helpers for speclite's Python scripts.

speclite is a 5-phase adaptation of GitHub's Spec Kit:
  1. constitution   (once for the whole project - same as Spec Kit's own constitution)
  2. specify         (specify + clarify)
  3. plan            (plan + checklist)
  4. tasks           (tasks + analyze)
  5. implement       (implement + converge)

Constitution philosophy matches Spec Kit's: ONE principles file for the entire project,
never per-feature. A MUST rule is non-negotiable - if any later phase finds a conflict
with one, it stops and tells the user rather than editing around it. Changing a principle
is only ever done by consciously re-running /speclite.constitution.

Phase completion is tracked entirely through the artifacts themselves (Spec Kit's own
style) - no separate check-log ledger:
  - specify:   done when spec.md has no [NEEDS CLARIFICATION] marker left
  - plan:      done when plan.md's Pre-Implementation Checklist is fully checked
  - tasks:     done when tasks.md's "Analysis Pass" checkbox is checked
  - implement: done when every task is [X] AND tasks.md's "Final Gap-Check" box is checked

Layout inside a target project (created by install.py / install.ps1):
  .speclite/
    feature.json              # points at the active feature directory
    memory/principles.md      # the ONE project-wide constitution
    templates/                # spec/plan/tasks/principles templates + reference guides
    scripts/{python,powershell}/  # this bundle, copied in verbatim
    commands/                 # the 5 phase command files
  specs/NNN-short-name/
    spec.md
    plan.md
    tasks.md
    references/               # user-supplied source material, see REFERENCE_SUBDIRS below
      PRD/  images/  fonts/  sounds/  videos/  data/  docs/
    logs/                     # ONE flat folder - not split by phase. Free-form evidence
                               # only (test output, screenshots, session notes) that the
                               # agent organizes by type as needed. Never used to decide
                               # whether a phase is done - see completion rules above.
                               # Recommended (but not enforced) to be .gitignore'd - see
                               # README.md.
"""

from __future__ import annotations

import datetime
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# Default reference subfolders created for every new feature. Users may add more later;
# these are just sensible starting buckets so the agent (and the user) know where to look.
REFERENCE_SUBDIRS: list[str] = ["PRD", "images", "fonts", "sounds", "videos", "data", "docs"]


def find_speclite_root(start_dir: Path | None = None) -> Path | None:
    """Walk upward from start_dir looking for a `.speclite/` directory."""
    current = (start_dir or Path.cwd()).resolve()
    while True:
        if (current / ".speclite").is_dir():
            return current
        parent = current.parent
        if parent == current:
            return None
        current = parent


def get_repo_root(script_file: Path | None = None) -> Path:
    root = find_speclite_root()
    if root is not None:
        return root
    if script_file is not None:
        root = find_speclite_root(script_file.resolve().parent)
        if root is not None:
            return root
        # Installed scripts live at .speclite/scripts/python/<script>.py
        try:
            return script_file.resolve().parents[3]
        except IndexError:
            pass
    return Path.cwd().resolve()


def _json_line(payload: object) -> str:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n"


# --------------------------------------------------------------------------
# The project constitution - always ONE file for the whole project, matching
# Spec Kit's own model. No scope decision, no per-feature variant.
# --------------------------------------------------------------------------

def project_principles_path(repo_root: Path) -> Path:
    return repo_root / ".speclite" / "memory" / "principles.md"


# --------------------------------------------------------------------------
# .speclite/feature.json - which specs/NNN-* directory is "active"
# --------------------------------------------------------------------------

def read_feature_json(repo_root: Path) -> str:
    feature_json = repo_root / ".speclite" / "feature.json"
    if not feature_json.is_file():
        return ""
    try:
        data = json.loads(feature_json.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return ""
    value = data.get("feature_directory") if isinstance(data, dict) else None
    return value if isinstance(value, str) else ""


def persist_feature_json(repo_root: Path, feature_dir_value: str) -> None:
    value = feature_dir_value
    relative = Path(value)
    if relative.is_absolute():
        try:
            value = relative.relative_to(repo_root).as_posix()
        except ValueError:
            value = str(relative)
    if read_feature_json(repo_root) == value:
        return
    d = repo_root / ".speclite"
    d.mkdir(parents=True, exist_ok=True)
    (d / "feature.json").write_text(_json_line({"feature_directory": value}), encoding="utf-8")


def list_all_features(repo_root: Path) -> list[str]:
    specs_dir = repo_root / "specs"
    if not specs_dir.is_dir():
        return []
    return sorted(p.name for p in specs_dir.iterdir() if p.is_dir())


@dataclass(frozen=True)
class FeaturePaths:
    repo_root: Path
    feature_dir: Path
    spec: Path
    plan: Path
    tasks: Path
    references_dir: Path
    logs_dir: Path


def get_feature_paths(*, no_persist: bool = False, script_file: Path | None = None) -> FeaturePaths:
    repo_root = get_repo_root(script_file)
    env_dir = os.environ.get("SPECLITE_FEATURE_DIRECTORY", "")
    if env_dir:
        feature_dir = Path(env_dir)
        if not feature_dir.is_absolute():
            feature_dir = repo_root / feature_dir
        if not no_persist:
            persist_feature_json(repo_root, env_dir)
    else:
        stored = read_feature_json(repo_root)
        if not stored:
            print(
                "ERROR: No active feature. Run new_feature.py first, or set "
                "SPECLITE_FEATURE_DIRECTORY.",
                file=sys.stderr,
            )
            raise SystemExit(1)
        feature_dir = Path(stored)
        if not feature_dir.is_absolute():
            feature_dir = repo_root / feature_dir

    return FeaturePaths(
        repo_root=repo_root,
        feature_dir=feature_dir,
        spec=feature_dir / "spec.md",
        plan=feature_dir / "plan.md",
        tasks=feature_dir / "tasks.md",
        references_dir=feature_dir / "references",
        logs_dir=feature_dir / "logs",
    )


def resolve_template(name: str, repo_root: Path) -> Path | None:
    """Override stack: .speclite/templates/overrides/<name>.md, then .speclite/templates/<name>.md."""
    override = repo_root / ".speclite" / "templates" / "overrides" / f"{name}.md"
    if override.is_file():
        return override
    core = repo_root / ".speclite" / "templates" / f"{name}.md"
    if core.is_file():
        return core
    return None


def create_reference_dirs(feature_dir: Path) -> Path:
    """Create the standard references/ subfolders (idempotent, never touches existing files)."""
    references_dir = feature_dir / "references"
    for name in REFERENCE_SUBDIRS:
        sub = references_dir / name
        sub.mkdir(parents=True, exist_ok=True)
        keep = sub / ".gitkeep"
        if not keep.exists():
            keep.touch()
    return references_dir


def create_log_dirs(base_dir: Path) -> Path:
    """Create the single, flat logs/ folder for a feature (idempotent).

    Free-form only - test output, screenshots, session notes - organized by the agent
    into its own subfolders as needed. Never split by phase, never used to decide
    completion (see the module docstring for how each phase's completion is actually
    tracked, entirely via the artifacts themselves).
    """
    logs_dir = base_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


# --------------------------------------------------------------------------
# Small text-scanning helpers used by status.py to infer progress.
# --------------------------------------------------------------------------

def extract_section(markdown_text: str, heading: str) -> str:
    """Return the body of a `## <heading>` section, up to the next `##` heading."""
    pattern = re.compile(
        rf"^##\s+{re.escape(heading)}\s*$(.*?)(?=^##\s|\Z)", re.MULTILINE | re.DOTALL
    )
    match = pattern.search(markdown_text)
    return match.group(1) if match else ""


def count_unchecked_boxes(text: str) -> int:
    return len(re.findall(r"^\s*-\s\[\s\]", text, re.MULTILINE))


def count_checked_boxes(text: str) -> int:
    return len(re.findall(r"^\s*-\s\[[xX]\]", text, re.MULTILINE))


def is_marker_checked(text: str, marker_substring: str) -> bool:
    """Whether a checkbox line containing marker_substring (case-insensitive) is ticked
    [x] anywhere in text. Used to read artifact-based completion signals directly out of
    tasks.md (e.g. the Analysis Pass / Final Gap-Check checkboxes) instead of a log."""
    pattern = re.compile(
        r"^\s*-\s\[[xX]\].*" + re.escape(marker_substring), re.MULTILINE | re.IGNORECASE
    )
    return pattern.search(text) is not None


_TASK_LINE_RE = re.compile(r"^\s*-\s\[([ xX])\]\s+T\d+", re.MULTILINE)


def count_unchecked_tasks(text: str) -> int:
    """Count only real T-prefixed task lines (e.g. '- [ ] T001 ...') - deliberately
    distinct from count_unchecked_boxes(), which would also match tasks.md's own
    Analysis Pass / Final Gap-Check checkboxes and miscount them as tasks."""
    return sum(1 for m in _TASK_LINE_RE.finditer(text) if m.group(1) == " ")


def count_checked_tasks(text: str) -> int:
    return sum(1 for m in _TASK_LINE_RE.finditer(text) if m.group(1) in "xX")


# --------------------------------------------------------------------------
# Project Map - lives in specs/ directly (PROJECT_MAP.md, PRD_TRACEABILITY.md,
# ARCHITECTURE_MAP.md, FILE_INDEX.md, optionally PROJECT_MAP.json), alongside
# the specs/NNN-feature/ directories, never inside them. Optional, project-
# wide, not part of the logs/ system - its own sync state lives in an HTML
# comment at the top of PROJECT_MAP.md instead of a separate log file.
# --------------------------------------------------------------------------

MAP_FILE_NAMES: dict[str, str] = {
    "project_map": "PROJECT_MAP.md",
    "prd_traceability": "PRD_TRACEABILITY.md",
    "architecture_map": "ARCHITECTURE_MAP.md",
    "file_index": "FILE_INDEX.md",
    "changelog": "MAP_CHANGELOG.md",
    "json": "PROJECT_MAP.json",
}


def map_file_paths(repo_root: Path) -> dict[str, Path]:
    specs_dir = repo_root / "specs"
    return {key: specs_dir / name for key, name in MAP_FILE_NAMES.items()}


def list_source_prds(repo_root: Path) -> list[str]:
    """Every spec.md plus every references/PRD/* file, across all features - the map's
    source requirement documents, auto-derived instead of asked for."""
    specs_dir = repo_root / "specs"
    if not specs_dir.is_dir():
        return []
    found: list[Path] = []
    for feature_dir in sorted(specs_dir.iterdir()):
        if not feature_dir.is_dir():
            continue
        spec = feature_dir / "spec.md"
        if spec.is_file():
            found.append(spec)
        prd_dir = feature_dir / "references" / "PRD"
        if prd_dir.is_dir():
            found.extend(sorted(p for p in prd_dir.iterdir() if p.is_file() and p.name != ".gitkeep"))
    return [str(p.relative_to(repo_root)) for p in found]


_MAP_STATE_RE = re.compile(r"<!--\s*speclite-map-state\n(.*?)-->", re.DOTALL)
_MAP_STATE_FIELD_RE = re.compile(r"^(\w+):\s*(.*)$", re.MULTILINE)


def read_map_state(project_map_path: Path) -> dict[str, str]:
    """Parse the invisible <!-- speclite-map-state ... --> block at the top of
    PROJECT_MAP.md. Returns {} if the file or block doesn't exist yet (build mode)."""
    if not project_map_path.is_file():
        return {}
    text = project_map_path.read_text(encoding="utf-8", errors="ignore")
    match = _MAP_STATE_RE.search(text)
    if not match:
        return {}
    return {k: v.strip() for k, v in _MAP_STATE_FIELD_RE.findall(match.group(1))}


def render_map_state_block(fields: dict[str, str]) -> str:
    """The counterpart to read_map_state - build the HTML comment block to embed at the
    top of PROJECT_MAP.md when writing/updating it."""
    lines = "\n".join(f"{k}: {v}" for k, v in fields.items())
    return f"<!-- speclite-map-state\n{lines}\n-->"


def is_git_repo(repo_root: Path) -> bool:
    return (repo_root / ".git").exists()


def _run_git(repo_root: Path, args: list[str]) -> str | None:
    import subprocess

    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    return result.stdout


def git_current_commit(repo_root: Path) -> str | None:
    out = _run_git(repo_root, ["rev-parse", "HEAD"])
    return out.strip() if out else None


def git_commit_exists(repo_root: Path, commit: str) -> bool:
    return _run_git(repo_root, ["cat-file", "-e", commit]) is not None or _run_git(
        repo_root, ["cat-file", "-t", commit]
    ) is not None


def git_changed_files_since(repo_root: Path, since_commit: str) -> list[tuple[str, str]] | None:
    """Files changed between since_commit and the current working tree (committed AND
    uncommitted), as (status, path) pairs - status is one of A/M/D. Returns None if git
    isn't usable or since_commit is invalid - caller should fall back to mtime scanning."""
    if not is_git_repo(repo_root) or not git_commit_exists(repo_root, since_commit):
        return None

    changes: dict[str, str] = {}  # path -> status, while accumulating

    committed = _run_git(repo_root, ["diff", "--name-status", f"{since_commit}..HEAD"])
    if committed is not None:
        for line in committed.splitlines():
            parts = line.split("\t")
            if len(parts) >= 2:
                status, path = parts[0][:1], parts[-1]
                changes[path] = status

    working_tree = _run_git(repo_root, ["status", "--porcelain"])
    if working_tree is not None:
        for line in working_tree.splitlines():
            if len(line) < 4:
                continue
            code, path = line[:2].strip(), line[3:]
            status = "D" if "D" in code else ("A" if "A" in code or "?" in code else "M")
            changes[path] = status

    return sorted(((status, path) for path, status in changes.items()), key=lambda sp: sp[1])


DEFAULT_MAP_EXCLUDES = {
    ".git", ".speclite", ".agents", "skills", "node_modules", "__pycache__",
    "dist", "build", ".venv", "venv", ".next", "target", "vendor",
}


def mtime_changed_files_since(repo_root: Path, since_timestamp: str, known_files: set[str]) -> list[tuple[str, str]]:
    """Fallback for repos without git: files modified after since_timestamp (ISO 8601),
    plus any file in known_files (from the last FILE_INDEX.md) that no longer exists on
    disk (treated as deleted). Less precise than git, but keeps scans bounded."""
    try:
        cutoff = datetime.datetime.fromisoformat(since_timestamp).timestamp()
    except (ValueError, TypeError):
        cutoff = 0

    changed: list[tuple[str, str]] = []
    seen_on_disk: set[str] = set()
    for path in repo_root.rglob("*"):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(repo_root).parts
        if rel_parts and rel_parts[0] in DEFAULT_MAP_EXCLUDES:
            continue
        rel = str(path.relative_to(repo_root))
        seen_on_disk.add(rel)
        try:
            if path.stat().st_mtime > cutoff:
                changed.append(("M", rel))
        except OSError:
            continue

    for rel in sorted(known_files - seen_on_disk):
        changed.append(("D", rel))

    return changed
