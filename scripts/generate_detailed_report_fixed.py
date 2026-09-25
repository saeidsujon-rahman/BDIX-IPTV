#!/usr/bin/env python3
"""Run the detailed report with corrected attribute parsing."""
from pathlib import Path

path = Path("scripts/generate_detailed_report.py")
source = path.read_text(encoding="utf-8")
source = source.replace(r"r'([\\w-]+)=\"", r"r'([\w-]+)=\"")
exec(compile(source, str(path), "exec"), {"__name__": "__main__", "__file__": str(path)})
