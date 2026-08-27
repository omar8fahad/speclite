#!/usr/bin/env python3
"""Install speclite into a project, non-destructively.

Usage (typical): copy this whole `speclite/` folder into your project root, then run:
    python speclite/install.py

By default the target project is the PARENT of the folder this script lives in - i.e.
wherever you dropped the `speclite/` folder is treated as "next to the project root".
Pass --target-dir explicitly if you'd rather install somewhere else.

Guarantees:
  - Only ever writes inside <target>/.speclite/ - nothing else in the project is touched.
  - Never overwrites or deletes an existing file. If a file already exists at the
    destination, it is left completely alone and reported as "skipped" at the end.
  - Safe to re-run any time (e.g. after updating this package) - it will only add files
    that are missing, never clobber files you or an agent have already customized.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent

# (source relative to PACKAGE_ROOT, destination relative to <target>/.speclite/)
COPY_SETS: list[tuple[str, str]] = [
    ("templates", "templates"),
    ("scripts/python", "scripts/python"),
    ("scripts/powershell", "scripts/powershell"),
    ("commands", "commands"),
]

# Empty directories to guarantee exist even before anything is written there.
ENSURE_DIRS: list[str] = ["memory", "logs"]


def _help_text(argv0: str) -> str:
    return (
        f"Usage: {argv0} [--target-dir <path>] [--dry-run]\n"
        "  --target-dir <path>  Install into <path>/.speclite/ instead of the parent of\n"
        "                       this script's folder\n"
        "  --dry-run            Show what would happen without writing anything\n"
    )


def _copy_tree_non_destructive(src: Path, dst: Path, *, dry_run: bool) -> tuple[list[str], list[str]]:
    """Copy every file under src into dst, skipping any file that already exists at dst.

    Returns (installed_relative_paths, skipped_relative_paths).
    """
    installed: list[str] = []
    skipped: list[str] = []
    if not src.is_dir():
        return installed, skipped

    skip_names = {"__pycache__", ".DS_Store"}
    skip_suffixes = {".pyc", ".pyo"}

    for source_file in sorted(src.rglob("*")):
        if source_file.is_dir():
            continue
        if skip_names & set(source_file.parts):
            continue
        if source_file.suffix in skip_suffixes:
            continue
        rel = source_file.relative_to(src)
        dest_file = dst / rel
        if dest_file.exists():
            skipped.append(str(dest_file))
            continue
        installed.append(str(dest_file))
        if not dry_run:
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, dest_file)
    return installed, skipped


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    if "--help" in args or "-h" in args:
        sys.stdout.write(_help_text(sys.argv[0]))
        return 0

    dry_run = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]

    target_dir = PACKAGE_ROOT.parent
    if "--target-dir" in args:
        i = args.index("--target-dir")
        if i + 1 >= len(args):
            print("Error: --target-dir requires a value", file=sys.stderr)
            return 1
        target_dir = Path(args[i + 1]).resolve()

    speclite_dir = target_dir / ".speclite"

    print(f"Installing speclite into: {speclite_dir}")
    if dry_run:
        print("(dry run - nothing will be written)")

    all_installed: list[str] = []
    all_skipped: list[str] = []

    for src_rel, dst_rel in COPY_SETS:
        src = PACKAGE_ROOT / src_rel
        dst = speclite_dir / dst_rel
        installed, skipped = _copy_tree_non_destructive(src, dst, dry_run=dry_run)
        all_installed.extend(installed)
        all_skipped.extend(skipped)

    for rel in ENSURE_DIRS:
        d = speclite_dir / rel
        if not dry_run:
            d.mkdir(parents=True, exist_ok=True)

    print(f"\nInstalled {len(all_installed)} file(s).")
    if all_skipped:
        print(
            f"Skipped {len(all_skipped)} file(s) that already existed (left untouched, "
            "nothing was overwritten):"
        )
        for path in all_skipped:
            try:
                rel_display = Path(path).relative_to(target_dir)
            except ValueError:
                rel_display = path
            print(f"  - {rel_display}")
        print(
            "\nIf any of these are stale versions from an older speclite install, compare "
            "them by hand and update manually - this installer will never overwrite an "
            "existing file automatically."
        )
    else:
        print("No conflicts.")

    if not dry_run:
        print(f"\nDone. Next step: run /speclite.constitution (Phase 1) to get started.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
