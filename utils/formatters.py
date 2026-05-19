"""
utils/formatters.py

Fungsi pemformatan angka numerik untuk Dashboard DSS.
Semua fungsi mengembalikan string dan menangani edge case:
NaN, infinity, dan None secara graceful.

Requirements: 10.7
"""

import math


def _is_invalid(value) -> bool:
    """Kembalikan True jika value adalah None, NaN, atau infinity."""
    if value is None:
        return True
    try:
        f = float(value)
    except (TypeError, ValueError):
        return True
    return math.isnan(f) or math.isinf(f)


def _invalid_repr(value) -> str:
    """Kembalikan representasi string untuk nilai yang tidak valid."""
    if value is None:
        return "N/A"
    try:
        f = float(value)
        if math.isnan(f):
            return "NaN"
        if math.isinf(f):
            return "∞" if f > 0 else "-∞"
    except (TypeError, ValueError):
        pass
    return "N/A"


def fmt_monetary(value: float) -> str:
    """
    Format nilai moneter ke 2 desimal.

    Contoh:
        fmt_monetary(1234.5)   → "1234.50"
        fmt_monetary(0.1)      → "0.10"
        fmt_monetary(None)     → "N/A"
        fmt_monetary(float('nan'))  → "NaN"
        fmt_monetary(float('inf'))  → "∞"

    Requirements: 10.7
    """
    if _is_invalid(value):
        return _invalid_repr(value)
    return f"{float(value):.2f}"


def fmt_probability(value: float) -> str:
    """
    Format nilai probabilitas ke 2 desimal.

    Contoh:
        fmt_probability(0.75)  → "0.75"
        fmt_probability(1.0)   → "1.00"
        fmt_probability(None)  → "N/A"
        fmt_probability(float('nan'))  → "NaN"

    Requirements: 10.7
    """
    if _is_invalid(value):
        return _invalid_repr(value)
    return f"{float(value):.2f}"


def fmt_stat(value: float) -> str:
    """
    Format nilai statistik (korelasi, p-value, koefisien) ke 4 desimal.

    Contoh:
        fmt_stat(0.9876543)    → "0.9877"
        fmt_stat(-0.12345)     → "-0.1235"
        fmt_stat(None)         → "N/A"
        fmt_stat(float('nan')) → "NaN"
        fmt_stat(float('inf')) → "∞"

    Requirements: 10.7
    """
    if _is_invalid(value):
        return _invalid_repr(value)
    return f"{float(value):.4f}"


# Tipe format yang didukung oleh fmt_number
_FMT_TYPES = {
    "monetary": fmt_monetary,
    "probability": fmt_probability,
    "stat": fmt_stat,
}


def fmt_number(value: float, fmt_type: str) -> str:
    """
    Dispatcher ke formatter yang tepat berdasarkan fmt_type.

    Parameter:
        value    : Nilai numerik yang akan diformat.
        fmt_type : Salah satu dari "monetary", "probability", atau "stat".

    Kembalikan:
        String hasil format, atau "N/A" / "NaN" / "∞" untuk nilai tidak valid.

    Raise:
        ValueError jika fmt_type tidak dikenali.

    Contoh:
        fmt_number(1234.5, "monetary")     → "1234.50"
        fmt_number(0.75, "probability")    → "0.75"
        fmt_number(0.9876, "stat")         → "0.9876"
        fmt_number(None, "monetary")       → "N/A"

    Requirements: 10.7
    """
    formatter = _FMT_TYPES.get(fmt_type)
    if formatter is None:
        raise ValueError(
            f"fmt_type tidak dikenali: '{fmt_type}'. "
            f"Pilihan yang valid: {list(_FMT_TYPES.keys())}"
        )
    return formatter(value)
