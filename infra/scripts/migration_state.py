#!/usr/bin/env python3
"""Compatibility entrypoint for the shared runtime migration-state evaluator."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
API_ROOT = ROOT / 'services' / 'api'
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app.migration_state import (  # noqa: E402,F401
    MigrationPackageError,
    applied_rows,
    evaluate_migration_state,
    main,
    migration_files,
    safe_public_status,
)


if __name__ == '__main__':
    raise SystemExit(main())
