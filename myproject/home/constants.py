"""
Application constants for school rolls data application.

This module centralizes configuration values used across the application
to ensure consistency and ease of maintenance.
"""

from typing import List, Dict

# Data range
DATA_START_YEAR: int = 1996
DATA_END_YEAR: int = 2018
YEARS: List[int] = list(range(DATA_START_YEAR, DATA_END_YEAR + 1))

# Pagination
DEFAULT_PAGE_SIZE: int = 200
MAX_PAGE_SIZE: int = 1000
MIN_PAGE_SIZE: int = 1

# Graph configuration
GRAPH_COLOR_PALETTE: List[str] = [
    '#6366f1',  # Indigo
    '#f59e0b',  # Amber
    '#22c55e',  # Green
    '#3b82f6',  # Blue
    '#fb7185',  # Pink
    '#34d399',  # Emerald
]

MAX_SCHOOLS_PER_GRAPH: int = 50  # Limit to prevent performance issues

# Graph styling (dark theme to match site CSS)
GRAPH_STYLE: Dict[str, str] = {
    'figure.facecolor': '#141414',
    'axes.facecolor': '#141414',
    'axes.edgecolor': '#2a2a2a',
    'axes.labelcolor': '#f5f5f5',
    'xtick.color': '#a3a3a3',
    'ytick.color': '#a3a3a3',
    'text.color': '#f5f5f5',
    'grid.color': '#2a2a2a',
    'legend.facecolor': '#1e1e1e',
    'legend.edgecolor': '#2a2a2a',
    'savefig.facecolor': '#141414',
    'savefig.edgecolor': '#141414',
}

# Field name mappings for display
FIELD_DISPLAY_NAMES: Dict[str, str] = {
    'School_Type': 'School Type',
}

# Fields to exclude from API responses
EXCLUDED_FIELDS = ['Code', 'LA_Code', 'LA_Name']
