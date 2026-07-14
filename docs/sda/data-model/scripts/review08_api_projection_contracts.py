#!/usr/bin/env python3
"""Compatibility entrypoint for F08 API contract evidence.

Review 09 requires expected API contracts to be independent reviewed source and observed
shapes to be compared separately. This wrapper intentionally delegates to the Review 09
comparator and must not regenerate expected contracts from OpenAPI/AST.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
helper = ROOT / 'docs' / 'sda' / 'data-model' / 'scripts' / 'review09_api_contract_comparison.py'
subprocess.run([sys.executable, str(helper)], cwd=ROOT, check=True)
