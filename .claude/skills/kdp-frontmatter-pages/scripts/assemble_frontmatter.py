#!/usr/bin/env python3
"""Compatibility entry point for the canonical front-matter assembler."""

from pathlib import Path
import runpy


REPO_ROOT = Path(__file__).resolve().parents[4]
CANONICAL = REPO_ROOT / ".agents/skills/kdp-frontmatter-pages/scripts/assemble_frontmatter.py"

runpy.run_path(str(CANONICAL), run_name="__main__")
