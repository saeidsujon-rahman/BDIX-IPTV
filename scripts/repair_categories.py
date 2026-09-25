#!/usr/bin/env python3
"""Locked-category guard for the update workflow.

No category values are rewritten here. The strict updater controls only the
New Channels group and leaves all other groups untouched.
"""
print("Category repair skipped: locked-category policy is active.")
