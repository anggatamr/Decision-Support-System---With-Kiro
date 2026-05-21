"""
utils/validators.py
-------------------
Semua fungsi validasi input untuk Dashboard DSS.

Setiap fungsi mengembalikan tuple (is_valid, pesan_error) atau
(is_valid, list_sel_invalid) sesuai kontrak interface-nya.
"""

from __future__ import annotations

import math
import re
from typing import Any


# ---------------------------------------------------------------------------
# Konstanta
# ---------------------------------------------------------------------------

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB
ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls"}

# Distribusi yang didukung modul Probabilistic (Req 6)
DISTRIBUTION_PARAMS_REQUIRED: dict[str, list[str]] = {
    "Normal":      ["mu", "sigma"],
    "Binomial":    ["p", "n_trials"],
    "Poisson":     ["lambda"],
    "Exponential": ["lambda"],
    "Uniform":     ["a", "b"],
    "Beta":        ["alpha", "beta"],
}

# Distribusi yang didukung modul Monte Carlo (Req 8)
SIM_DIST_PARAMS_REQUIRED: dict[str, list[str]] = {
    "Normal":     ["mean", "std"],
    "Uniform":    ["min", "max"],
    "Triangular": ["min", "mode", "max"],
}

# Namespace aman untuk eval ekspresi simulasi
_SAFE_BUILTINS: dict[str, Any] = {}
_SAFE_GLOBALS: dict[str, Any] = {
    "__builtins__": _SAFE_BUILTINS,
}


# ---------------------------------------------------------------------------
# 1. validate_file
# ---------------------------------------------------------------------------

def validate_file(uploaded_file) -> tuple[bool, str]:
    """
    Validasi file yang diunggah pengguna.

    Cek:
    - Format: hanya CSV atau XLSX/XLS
    - Ukuran: ≤ 50 MB
    - Non-empty: ukuran > 0 byte

    Returns
    -------
    (True, "")                  — file valid
    (False, pesan_kesalahan)    — file tidak valid
    """
    if uploaded_file is None:
        return False, "Tidak ada file yang diunggah."

    # --- cek ekstensi ---
    filename: str = getattr(uploaded_file, "name", "") or ""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        return (
            False,
            f"Format file tidak didukung: '.{ext}'. "
            "Harap unggah file berformat CSV atau XLSX.",
        )

    # --- cek ukuran ---
    # Streamlit UploadedFile menyediakan atribut .size (bytes)
    size: int = getattr(uploaded_file, "size", None)
    if size is None:
        # Fallback: baca seluruh konten untuk menghitung ukuran
        try:
            content = uploaded_file.read()
            size = len(content)
            uploaded_file.seek(0)
        except Exception:
            return False, "Tidak dapat membaca ukuran file."

    if size == 0:
        return False, "File tidak memiliki baris data (file kosong)."

    if size > MAX_FILE_SIZE_BYTES:
        size_mb = size / (1024 * 1024)
        return (
            False,
            f"Ukuran file ({size_mb:.1f} MB) melebihi batas maksimum 50 MB. "
            "Harap kompres atau potong dataset Anda.",
        )

    return True, ""


# ---------------------------------------------------------------------------
# 2. validate_payoff_matrix
# ---------------------------------------------------------------------------

def validate_payoff_matrix(matrix: list[list]) -> tuple[bool, list[tuple[int, int]]]:
    """
    Validasi matriks payoff (list of lists).

    Setiap sel dianggap tidak valid jika:
    - Kosong (None, "", atau string yang hanya berisi spasi)
    - Tidak dapat dikonversi ke float

    Returns
    -------
    (True, [])                          — semua sel valid
    (False, [(row, col), ...])          — daftar posisi sel yang tidak valid
    """
    invalid: list[tuple[int, int]] = []

    for i, row in enumerate(matrix):
        for j, cell in enumerate(row):
            if not _is_numeric_cell(cell):
                invalid.append((i, j))

    return len(invalid) == 0, invalid


def _is_numeric_cell(cell: Any) -> bool:
    """Kembalikan True jika cell dapat dikonversi ke float dan bukan NaN/Inf."""
    if cell is None:
        return False
    if isinstance(cell, str):
        cell = cell.strip()
        if cell == "":
            return False
    try:
        val = float(cell)
        return math.isfinite(val)
    except (ValueError, TypeError):
        return False


# ---------------------------------------------------------------------------
# 3. validate_probabilities
# ---------------------------------------------------------------------------

def validate_probabilities(probs: list[float]) -> tuple[bool, str]:
    """
    Validasi vektor probabilitas.

    Cek:
    - Setiap nilai berada dalam rentang [0, 1]
    - Jumlah total berada dalam toleransi ±0.001 dari 1.0

    Returns
    -------
    (True, "")                  — probabilitas valid
    (False, pesan_kesalahan)    — probabilitas tidak valid
    """
    if not probs:
        return False, "Daftar probabilitas tidak boleh kosong."

    # Cek setiap nilai
    out_of_range = []
    for idx, p in enumerate(probs):
        try:
            p_float = float(p)
        except (ValueError, TypeError):
            return False, f"Nilai probabilitas ke-{idx + 1} bukan angka yang valid."
        if not (0.0 <= p_float <= 1.0):
            out_of_range.append((idx + 1, p_float))

    if out_of_range:
        detail = ", ".join(
            f"P{i}={v:.4f}" for i, v in out_of_range
        )
        return (
            False,
            f"Nilai probabilitas berikut berada di luar rentang [0, 1]: {detail}.",
        )

    # Cek jumlah total
    total = sum(float(p) for p in probs)
    if abs(total - 1.0) > 0.001:
        return (
            False,
            f"Jumlah probabilitas ({total:.6f}) harus sama dengan 1.0 "
            f"(toleransi ±0.001). Selisih saat ini: {abs(total - 1.0):.6f}.",
        )

    return True, ""


# ---------------------------------------------------------------------------
# 4. validate_distribution_params
# ---------------------------------------------------------------------------

def validate_distribution_params(dist_type: str, params: dict) -> tuple[bool, str]:
    """
    Validasi parameter distribusi probabilitas (modul Probabilistic, Req 6).

    Constraint per distribusi:
    - Normal:      sigma > 0
    - Binomial:    p ∈ (0, 1), n_trials > 0 (integer)
    - Poisson:     lambda > 0
    - Exponential: lambda > 0
    - Uniform:     a < b
    - Beta:        alpha > 0, beta > 0

    Returns
    -------
    (True, "")                  — parameter valid
    (False, pesan_kesalahan)    — parameter tidak valid
    """
    if dist_type not in DISTRIBUTION_PARAMS_REQUIRED:
        supported = ", ".join(DISTRIBUTION_PARAMS_REQUIRED.keys())
        return False, f"Jenis distribusi '{dist_type}' tidak dikenal. Pilihan: {supported}."

    # Pastikan semua kunci yang diperlukan ada
    required_keys = DISTRIBUTION_PARAMS_REQUIRED[dist_type]
    missing = [k for k in required_keys if k not in params]
    if missing:
        return False, f"Parameter yang diperlukan untuk {dist_type} tidak lengkap: {missing}."

    # Validasi per distribusi
    if dist_type == "Normal":
        sigma = _to_float(params.get("sigma"))
        if sigma is None or sigma <= 0:
            return (
                False,
                f"Parameter σ (sigma) untuk distribusi Normal harus > 0. "
                f"Nilai saat ini: {params.get('sigma')}.",
            )

    elif dist_type == "Binomial":
        p = _to_float(params.get("p"))
        n_trials = _to_float(params.get("n_trials"))
        if p is None or not (0.0 < p < 1.0):
            return (
                False,
                f"Parameter p untuk distribusi Binomial harus berada dalam (0, 1). "
                f"Nilai saat ini: {params.get('p')}.",
            )
        if n_trials is None or n_trials <= 0 or not float(n_trials).is_integer():
            return (
                False,
                f"Parameter n_trials untuk distribusi Binomial harus berupa bilangan bulat positif. "
                f"Nilai saat ini: {params.get('n_trials')}.",
            )

    elif dist_type == "Poisson":
        lam = _to_float(params.get("lambda"))
        if lam is None or lam <= 0:
            return (
                False,
                f"Parameter λ (lambda) untuk distribusi Poisson harus > 0. "
                f"Nilai saat ini: {params.get('lambda')}.",
            )

    elif dist_type == "Exponential":
        lam = _to_float(params.get("lambda"))
        if lam is None or lam <= 0:
            return (
                False,
                f"Parameter λ (lambda) untuk distribusi Exponential harus > 0. "
                f"Nilai saat ini: {params.get('lambda')}.",
            )

    elif dist_type == "Uniform":
        a = _to_float(params.get("a"))
        b = _to_float(params.get("b"))
        if a is None or b is None:
            return False, "Parameter a dan b untuk distribusi Uniform harus berupa angka."
        if a >= b:
            return (
                False,
                f"Parameter a harus lebih kecil dari b untuk distribusi Uniform. "
                f"Nilai saat ini: a={a}, b={b}.",
            )

    elif dist_type == "Beta":
        alpha = _to_float(params.get("alpha"))
        beta = _to_float(params.get("beta"))
        errors = []
        if alpha is None or alpha <= 0:
            errors.append(f"α (alpha) harus > 0 (saat ini: {params.get('alpha')})")
        if beta is None or beta <= 0:
            errors.append(f"β (beta) harus > 0 (saat ini: {params.get('beta')})")
        if errors:
            return False, f"Parameter distribusi Beta tidak valid: {'; '.join(errors)}."

    return True, ""


# ---------------------------------------------------------------------------
# 5. validate_sim_variable
# ---------------------------------------------------------------------------

def validate_sim_variable(name: str, dist_type: str, params: dict) -> tuple[bool, str]:
    """
    Validasi variabel input simulasi Monte Carlo (Req 8).

    Constraint per distribusi:
    - Normal:     std > 0
    - Uniform:    min < max
    - Triangular: min ≤ mode ≤ max

    Returns
    -------
    (True, "")                  — variabel valid
    (False, pesan_kesalahan)    — variabel tidak valid
    """
    # Validasi nama variabel
    if not name or not name.strip():
        return False, "Nama variabel tidak boleh kosong."

    # Nama harus berupa identifier Python yang valid
    clean_name = name.strip()
    if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", clean_name):
        return (
            False,
            f"Nama variabel '{clean_name}' tidak valid. "
            "Gunakan huruf, angka, dan underscore saja (tidak boleh diawali angka).",
        )

    if dist_type not in SIM_DIST_PARAMS_REQUIRED:
        supported = ", ".join(SIM_DIST_PARAMS_REQUIRED.keys())
        return (
            False,
            f"Jenis distribusi '{dist_type}' tidak didukung untuk simulasi. "
            f"Pilihan: {supported}.",
        )

    # Pastikan semua kunci yang diperlukan ada
    required_keys = SIM_DIST_PARAMS_REQUIRED[dist_type]
    missing = [k for k in required_keys if k not in params]
    if missing:
        return (
            False,
            f"Parameter yang diperlukan untuk distribusi {dist_type} "
            f"pada variabel '{clean_name}' tidak lengkap: {missing}.",
        )

    # Validasi constraint per distribusi
    if dist_type == "Normal":
        std = _to_float(params.get("std"))
        if std is None or std <= 0:
            return (
                False,
                f"Parameter std untuk variabel '{clean_name}' (Normal) harus > 0. "
                f"Nilai saat ini: {params.get('std')}.",
            )

    elif dist_type == "Uniform":
        mn = _to_float(params.get("min"))
        mx = _to_float(params.get("max"))
        if mn is None or mx is None:
            return (
                False,
                f"Parameter min dan max untuk variabel '{clean_name}' (Uniform) "
                "harus berupa angka.",
            )
        if mn >= mx:
            return (
                False,
                f"Parameter min harus lebih kecil dari max untuk variabel '{clean_name}' (Uniform). "
                f"Nilai saat ini: min={mn}, max={mx}.",
            )

    elif dist_type == "Triangular":
        mn = _to_float(params.get("min"))
        mode = _to_float(params.get("mode"))
        mx = _to_float(params.get("max"))
        if mn is None or mode is None or mx is None:
            return (
                False,
                f"Parameter min, mode, dan max untuk variabel '{clean_name}' (Triangular) "
                "harus berupa angka.",
            )
        if not (mn <= mode <= mx):
            return (
                False,
                f"Constraint Triangular tidak terpenuhi untuk variabel '{clean_name}': "
                f"harus min ≤ mode ≤ max. "
                f"Nilai saat ini: min={mn}, mode={mode}, max={mx}.",
            )
        if mn >= mx:
            return (
                False,
                f"Parameter min harus lebih kecil dari max untuk variabel '{clean_name}' (Triangular). "
                f"Nilai saat ini: min={mn}, max={mx}.",
            )

    return True, ""


# ---------------------------------------------------------------------------
# 6. validate_sim_expression
# ---------------------------------------------------------------------------

def validate_sim_expression(expr: str, var_names: list[str]) -> tuple[bool, str]:
    """
    Validasi ekspresi output simulasi Monte Carlo.

    Strategi:
    1. Cek ekspresi tidak kosong
    2. Parse dengan AST untuk memastikan sintaks valid
    3. Evaluasi dengan nilai dummy (1.0) menggunakan safe_eval_expr
    4. Tangkap NameError, SyntaxError, ValueError, dan exception lainnya

    Returns
    -------
    (True, "")                  — ekspresi valid
    (False, pesan_kesalahan)    — ekspresi tidak valid
    """
    if not expr or not expr.strip():
        return False, "Ekspresi output tidak boleh kosong."

    # Import safe evaluator dari monte_carlo module
    try:
        from modules.monte_carlo import safe_eval_expr
    except ImportError:
        # Fallback ke eval terbatas jika import gagal
        safe_eval_expr = None  # type: ignore[assignment]

    # Buat namespace dengan nilai dummy untuk setiap variabel
    dummy_values: dict[str, float] = {name: 1.0 for name in var_names}

    try:
        if safe_eval_expr is not None:
            result = safe_eval_expr(expr.strip(), dummy_values)
        else:
            # Fallback: eval dengan namespace terbatas
            safe_namespace: dict[str, Any] = {
                "__builtins__": {},
                "abs": abs, "min": min, "max": max,
                "sum": sum, "round": round, "pow": pow,
                **dummy_values,
            }
            result = eval(expr.strip(), safe_namespace)  # noqa: S307
        float(result)
    except SyntaxError as e:
        return (
            False,
            f"Sintaks ekspresi tidak valid: {e.msg}. "
            "Periksa tanda kurung, operator, dan penulisan ekspresi.",
        )
    except NameError as e:
        return (
            False,
            f"Ekspresi mereferensikan variabel yang tidak terdefinisi: {e}. "
            f"Variabel yang tersedia: {var_names}.",
        )
    except ZeroDivisionError:
        return (
            False,
            "Ekspresi menghasilkan pembagian dengan nol pada nilai dummy. "
            "Pastikan ekspresi tidak membagi dengan variabel yang bisa bernilai 0.",
        )
    except ValueError as e:
        return (
            False,
            f"Ekspresi mengandung konstruksi yang tidak diizinkan: {e}.",
        )
    except TypeError as e:
        return (
            False,
            f"Tipe data tidak kompatibel dalam ekspresi: {e}.",
        )
    except Exception as e:  # noqa: BLE001
        return (
            False,
            f"Ekspresi tidak dapat dievaluasi: {type(e).__name__}: {e}.",
        )

    return True, ""


# ---------------------------------------------------------------------------
# Helper internal
# ---------------------------------------------------------------------------

def _to_float(value: Any) -> float | None:
    """Konversi value ke float; kembalikan None jika gagal atau NaN/Inf."""
    if value is None:
        return None
    try:
        f = float(value)
        return f if math.isfinite(f) else None
    except (ValueError, TypeError):
        return None
