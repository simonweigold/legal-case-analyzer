"""Shared helpers for Private International Law tools.
Provides lightweight CSV loading and mapping utilities referenced by individual tool modules.
"""
from __future__ import annotations
import csv
import os
from typing import List, Dict

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
_JURISDICTIONS_CSV = os.path.join(_DATA_DIR, "jurisdictions.csv")
_THEMES_CSV = os.path.join(_DATA_DIR, "themes.csv")


def _safe_read_csv(path: str) -> List[Dict[str, str]]:
    if not os.path.isfile(path):
        return []
    rows: List[Dict[str, str]] = []
    try:
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append({k: (v or '').strip() for k, v in row.items()})
    except Exception:
        return []
    return rows


def load_jurisdictions() -> List[Dict[str, str]]:
    """Load jurisdictions from CSV. Returns empty list if file missing or unreadable."""
    return _safe_read_csv(_JURISDICTIONS_CSV)


def load_themes() -> List[Dict[str, str]]:
    """Load PIL themes definitions from CSV."""
    return _safe_read_csv(_THEMES_CSV)


def get_jurisdiction_legal_system_mapping() -> Dict[str, str]:
    """Return mapping of jurisdiction name (lowercase) -> legal system type.
    Falls back to empty dict if data unavailable. Expects columns 'name' and 'legal_system'.
    """
    mapping: Dict[str, str] = {}
    for row in load_jurisdictions():
        name = row.get('name', '').strip()
        system = row.get('legal_system', '').strip()
        if name and system:
            mapping[name.lower()] = system
    return mapping

__all__ = [
    'load_jurisdictions',
    'load_themes',
    'get_jurisdiction_legal_system_mapping',
]
