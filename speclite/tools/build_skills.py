#!/usr/bin/env python3
"""Generate skills/speclite-<phase>/SKILL.md from commands/speclite.<phase>.md.

Mirrors Spec Kit's own dual distribution: a flat commands/ folder (for agents that read
custom slash-commands) and a skills/<name>/SKILL.md folder per command (for agents that
use the Skill format, e.g. Claude). Each generated SKILL.md is self-contained - the full
command body is embedded, not referenced - exactly matching Spec Kit's own
skills/speckit-<name>/SKILL.md files, which do the same.

Run this after editing anything under commands/ to regenerate skills/ in sync:
    python tools/build_skills.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
COMMANDS_DIR = PACKAGE_ROOT / "commands"
SKILLS_DIR = PACKAGE_ROOT / "skills"

PHASES = ["constitution", "specify", "plan", "tasks", "implement"]

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)
DESCRIPTION_RE = re.compile(r'^description:\s*"(.*)"\s*$', re.MULTILINE)


def _split_frontmatter(text: str) -> tuple[str, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError("Command file is missing YAML frontmatter")
    return match.group(1), match.group(2)


def build_phase_skill(phase: str) -> None:
    command_file = COMMANDS_DIR / f"speclite.{phase}.md"
    frontmatter, body = _split_frontmatter(command_file.read_text(encoding="utf-8"))

    desc_match = DESCRIPTION_RE.search(frontmatter)
    description = desc_match.group(1) if desc_match else phase

    skill_dir = SKILLS_DIR / f"speclite-{phase}"
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_file = skill_dir / "SKILL.md"

    new_frontmatter = (
        "---\n"
        f'name: "speclite-{phase}"\n'
        f'description: "{description}"\n'
        'compatibility: "Requires speclite project structure with .speclite/ directory"\n'
        "metadata:\n"
        '  author: "speclite"\n'
        f'  source: "commands/speclite.{phase}.md"\n'
        "---\n"
    )
    skill_file.write_text(new_frontmatter + body, encoding="utf-8")
    print(f"wrote {skill_file.relative_to(PACKAGE_ROOT)}")


NAME_DESC_RE = re.compile(r'^name:\s*(\S+)\s*$', re.MULTILINE)
DESC_UNQUOTED_RE = re.compile(r'^description:\s*(.*)$', re.MULTILINE)


def build_manager_skill() -> None:
    """Build skills/speclite/SKILL.md - the project-installed manager.

    Same content as the package-root SKILL.md (used when the whole speclite/ folder is
    dropped into a Claude skills directory directly), except commands/speclite.*.md
    references are rewritten to .agents/commands/speclite.*.md, since that's where the
    installer actually places them inside a project.
    """
    root_skill = PACKAGE_ROOT / "SKILL.md"
    frontmatter, body = _split_frontmatter(root_skill.read_text(encoding="utf-8"))

    desc_match = DESC_UNQUOTED_RE.search(frontmatter)
    description = desc_match.group(1).strip() if desc_match else "speclite manager"

    body = body.replace("commands/speclite.", ".agents/commands/speclite.")

    skill_dir = SKILLS_DIR / "speclite"
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_file = skill_dir / "SKILL.md"

    new_frontmatter = (
        "---\n"
        'name: "speclite"\n'
        f'description: "{description}"\n'
        'compatibility: "Requires speclite project structure with .speclite/ directory"\n'
        "metadata:\n"
        '  author: "speclite"\n'
        '  source: "SKILL.md"\n'
        "---\n"
    )
    skill_file.write_text(new_frontmatter + body, encoding="utf-8")
    print(f"wrote {skill_file.relative_to(PACKAGE_ROOT)}")


def main() -> int:
    for phase in PHASES:
        build_phase_skill(phase)
    build_manager_skill()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
