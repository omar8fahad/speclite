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

Layout inside a target project (created by install.py / install.ps1):
  .speclite/
    feature.json              # points at the active feature directory
    memory/principles.md      # the ONE project-wide constitution
    logs/1-constitution/      # project-wide constitution check log
    templates/                # spec/plan/tasks/principles templates + reference guides
    scripts/{python,powershell}/  # this bundle, copied in verbatim
    commands/                 # the 5 phase command files
  specs/NNN-short-name/
    spec.md
    plan.md
    tasks.md
    references/               # user-supplied source material, see REFERENCE_SUBDIRS below
      PRD/  images/  fonts/  sounds/  videos/  data/  docs/
    logs/                     # one subfolder per phase (2-5); the agent organizes each by
      2-specify/index.md      # content type. Phase 1 has no per-feature folder here - its
      3-plan/index.md         # log always lives at .speclite/logs/1-constitution/ instead.
      4-tasks/index.md
      5-implement/index.md
"""

from __future__ import annotations

import datetime
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# Canonical phase keys -> their log/reference folder names, in execution order.
PHASE_DIRS: dict[str, str] = {
    "constitution": "1-constitution",
    "specify": "2-specify",
    "plan": "3-plan",
    "tasks": "4-tasks",
    "implement": "5-implement",
}
PHASE_ORDER: list[str] = list(PHASE_DIRS.keys())

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
    """Pre-create the per-feature phase log folders under base_dir/logs/ (idempotent).

    Constitution (Phase 1) is intentionally excluded here - it's always project-wide, so
    its log lives at .speclite/logs/1-constitution/ instead of inside any feature.
    """
    logs_dir = base_dir / "logs"
    for phase_key, phase_dir_name in PHASE_DIRS.items():
        if phase_key == "constitution":
            continue
        (logs_dir / phase_dir_name).mkdir(parents=True, exist_ok=True)
    return logs_dir


# --------------------------------------------------------------------------
# Check log: one row per check, appended to <base>/logs/<phase>/index.md.
# The agent is free to add its own subfolders next to index.md within the
# same phase folder for typed artifacts (test output, screenshots, extra
# docs) - this helper only ever manages index.md itself.
# --------------------------------------------------------------------------

_LOG_BADGES = {"PASS": "\u2705", "WARN": "\u26a0\ufe0f", "FAIL": "\u274c", "INFO": "\u2139\ufe0f"}


def append_log(base_dir: Path, phase: str, status: str, summary: str, details: str = "") -> Path:
    """Append one row to base_dir/logs/<phase>/index.md. Returns the index.md path.

    base_dir is normally a feature directory (specs/NNN-name/). For the constitution
    phase, always pass repo_root / ".speclite" instead - that single, project-wide check
    lives at .speclite/logs/1-constitution/index.md, never inside a feature.
    """
    if phase not in PHASE_DIRS:
        raise ValueError(f"Unknown phase '{phase}'. Expected one of: {', '.join(PHASE_ORDER)}")

    phase_dir = base_dir / "logs" / PHASE_DIRS[phase]
    phase_dir.mkdir(parents=True, exist_ok=True)
    log_path = phase_dir / "index.md"

    is_new = not log_path.is_file()
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    badge = _LOG_BADGES.get(status.upper(), "\u2022")
    lines: list[str] = []
    if is_new:
        lines.append(f"# {phase.capitalize()} - Check Log\n")
        lines.append("\n")
        lines.append(
            "Other files in this folder (test output, screenshots, extra docs) are organized "
            "by the agent as needed - this table only tracks pass/fail checks.\n"
        )
        lines.append("\n")
        lines.append("| Time | Status | Summary |\n")
        lines.append("|------|--------|---------|\n")
    row_summary = summary.replace("|", "/").replace("\n", " ").strip()
    lines.append(f"| {ts} | {badge} {status.upper()} | {row_summary} |\n")
    with log_path.open("a", encoding="utf-8") as fh:
        fh.writelines(lines)
    if details:
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(f"\n<details><summary>{ts} details</summary>\n\n{details}\n\n</details>\n\n")
    return log_path


def read_log_text(base_dir: Path, phase: str) -> str:
    log_path = base_dir / "logs" / PHASE_DIRS[phase] / "index.md"
    if not log_path.is_file():
        return ""
    try:
        return log_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


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
