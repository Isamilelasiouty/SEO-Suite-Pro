"""
CSV Export Utility for SEO Suite Pro:
Generates UTF-8 with BOM CSV streams compatible with Microsoft Excel, Google Sheets, and data pipelines.
"""

import pandas as pd

def generate_csv_bytes(df: pd.DataFrame) -> bytes:
    """Converts a DataFrame into UTF-8 with BOM encoded bytes."""
    if df is None or df.empty:
        return b""
    return df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
