from __future__ import annotations

import math
from typing import Any


def clamp_pagination(page: int, per_page: int, *, max_per_page: int = 100) -> tuple[int, int]:
    safe_page = max(1, int(page or 1))
    safe_per_page = max(1, min(int(per_page or 25), max_per_page))
    return safe_page, safe_per_page


def paginated_response(items: list[dict[str, Any]], *, page: int, per_page: int, max_per_page: int = 100) -> dict[str, Any]:
    safe_page, safe_per_page = clamp_pagination(page, per_page, max_per_page=max_per_page)
    total_items = len(items)
    total_pages = max(1, math.ceil(total_items / safe_per_page)) if total_items else 0
    start = (safe_page - 1) * safe_per_page
    end = start + safe_per_page
    return {
        'items': items[start:end],
        'pagination': {
            'page': safe_page,
            'per_page': safe_per_page,
            'total_items': total_items,
            'total_pages': total_pages,
            'has_next': safe_page < total_pages,
            'has_previous': safe_page > 1 and total_items > 0,
        },
    }
