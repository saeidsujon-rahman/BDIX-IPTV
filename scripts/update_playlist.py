#!/usr/bin/env python3
"""Compatibility entry point that fixes the legacy updater regex before execution."""
from pathlib import Path

path = Path("scripts/strict_update.py")
source = path.read_text(encoding="utf-8")
source = source.replace(r"r'([\\w-]+)=\"", r"r'([\w-]+)=\"")
exec(compile(source, str(path), "exec"), {"__name__": "__main__", "__file__": str(path)})
