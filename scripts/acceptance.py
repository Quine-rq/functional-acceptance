#!/usr/bin/env python3
"""Keep the original development CLI path; implementation lives in the Skill."""

from pathlib import Path
import runpy


if __name__ == "__main__":
    runpy.run_path(
        str(Path(__file__).resolve().parents[1]
            / "skills" / "functional-acceptance" / "scripts" / "acceptance.py"),
        run_name="__main__",
    )
