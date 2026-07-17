#!/usr/bin/env python3
"""Regenerate all scale-up question bank files with unique stems."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gen_business_scaleup import main as gen_business
from gen_people_scaleup import main as gen_people
from gen_process_scaleup import main as gen_process


def main() -> None:
    print("=== Regenerating People domain ===")
    gen_people()
    print("\n=== Regenerating Process domain ===")
    gen_process()
    print("\n=== Regenerating Business domain ===")
    gen_business()
    print("\n=== All scale-up files regenerated ===")


if __name__ == "__main__":
    main()
