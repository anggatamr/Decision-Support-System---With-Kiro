"""
modules/distribution.py
=======================
Computation layer untuk estimasi distribusi probabilitas (Module 5).

Lapisan ini hanya berisi pure functions — tidak mengimpor Streamlit.
UI layer (render_distribution_module) akan ditambahkan pada task 9.6.
"""

from __future__ import annotations

import numpy as np
import scipy.stats as stats
from typing import Any


# ---------------------------------------------------------------------------
# MLE Estimators
# ---------------------------------------------------------------------------

def mle_normal(x: np.ndarray) -> tuple[float, float]:
    """
    MLE untuk distribusi Normal.

    Returns
    -------
    (mu, sigma) : tuple[float, float]
        mu    = np.mean(x)
        sigma = np.std(x, ddof=0)
    """
    x = np.asarray(x, dtype=float)
    return float(np.mean(x)), float(np.std(x, ddof=0))


def mle_poisson(x: np.ndarray) -> float:
    """
    MLE untuk distribusi Poisson.

    Returns
    -------
    lambda_ : float
        lambda = np.mean(x)
    """
    x = np.asarray(x, dtype=float)
    return float(np.mean(x))


def mle_exponential(x: np.ndarray) -> float:
    """
    MLE untuk distribusi Exponential.

    Returns
    -------
    lambda_ : float
        lambda = 1.0 / np.mean(x)
    """
    x = np.asarray(x, dtype=float)
    return float(1.0 / np.mean(x))


def mle_uniform(x: np.ndarray) -> tuple[float, float]:
    """
    MLE untuk distribusi Uniform.

    Returns
    -------
    (a, b) : tuple[float, float]
        a = np.min(x)
        b = np.max(x)
    """
    x = np.asarray(x, dtype=float)
    return float(np.min(x)), float(np.max(x))


def mle_binomial(x: np.ndarray, n_trials: int) -> float:
    """
    MLE untuk distribusi Binomial.

    Parameters
    ----------
    x        : array-like, observed counts (0 <= x_i <= n_trials)
    n_trials : int, jumlah percobaan per observasi

    Returns
    -------
    p_hat : float
        p = np.mean(x) / n_trials
    """
    x = np.asarray(x, dtype=float)
    return float(np.mean(x) / n_trials)


def mle_beta(x: np.ndarray) -> tuple[float, float]:
    """
    MLE untuk distribusi Beta menggunakan scipy.stats.beta.fit.

    Parameters
    ----------
    x : array-like, nilai dalam (0, 1)

    Returns
    -------
    (alpha, beta_) : tuple[float, float]
        Parameter shape yang diestimasi (loc=0, scale=1 ditetapkan).
    """
    x = np.asarray(x, dtype=float)
    # fit() mengembalikan (a, b, loc, scale); kita ambil a dan b saja
    a, b, _loc, _scale = stats.beta.fit(x, floc=0, fscale=1)
    return float(a), float(b)


# ---------------------------------------------------------------------------
# Distribution Statistics
# ---------------------------------------------------------------------------

# Mapping nama distribusi ke objek scipy.stats dan cara meneruskan params
_DIST_MAP: dict[str, Any] = {
    "Normal":      stats.norm,
    "Poisson":     stats.poisson,
    "Exponential": stats.expon,
    "Uniform":     stats.uniform,
    "Binomial":    stats.binom,
    "Beta":        stats.beta,
}

# Cara meneruskan params ke scipy.stats.<dist>.stats()
# Setiap entry adalah fungsi (params_dict) -> args_tuple
_PARAMS_TO_ARGS: dict[str, Any] = {
    # Normal: params = {"mu": ..., "sigma": ...}  atau tuple (mu, sigma)
    "Normal":      lambda p: (p["mu"], 0, p["sigma"]),          # loc=mu, scale=sigma
    # Poisson: params = {"lambda": ...}
    "Poisson":     lambda p: (p["lambda"],),
    # Exponential: params = {"lambda": ...}  → scale = 1/lambda
    "Exponential": lambda p: (0, 1.0 / p["lambda"]),            # loc=0, scale=1/lambda
    # Uniform: params = {"a": ..., "b": ...}  → loc=a, scale=b-a
    "Uniform":     lambda p: (p["a"], p["b"] - p["a"]),         # loc=a, scale=b-a
    # Binomial: params = {"n": ..., "p": ...}
    "Binomial":    lambda p: (p["n"], p["p"]),
    # Beta: params = {"alpha": ..., "beta": ...}
    "Beta":        lambda p: (p["alpha"], p["beta"]),
}


def compute_dist_stats(dist_type: str, params: dict) -> dict:
    """
    Hitung statistik distribusi: mean, variance, skewness, kurtosis.

    Parameters
    ----------
    dist_type : str
        Salah satu dari "Normal", "Poisson", "Exponential", "Uniform",
        "Binomial", "Beta".
    params : dict
        Parameter distribusi. Key yang diharapkan per distribusi:
        - Normal:      {"mu": float, "sigma": float}
        - Poisson:     {"lambda": float}
        - Exponential: {"lambda": float}
        - Uniform:     {"a": float, "b": float}
        - Binomial:    {"n": int, "p": float}
        - Beta:        {"alpha": float, "beta": float}

    Returns
    -------
    dict dengan key "mean", "variance", "skewness", "kurtosis"
    """
    dist = _DIST_MAP[dist_type]
    args = _PARAMS_TO_ARGS[dist_type](params)
    mean, var, skew, kurt = dist.stats(*args, moments="mvsk")
    return {
        "mean":     float(mean),
        "variance": float(var),
        "skewness": float(skew),
        "kurtosis": float(kurt),
    }


# ---------------------------------------------------------------------------
# Bootstrap Confidence Intervals
# ---------------------------------------------------------------------------

def _reestimate_params(dist_type: str, x_boot: np.ndarray, n_trials: int = 1) -> tuple:
    """
    Re-estimasi parameter MLE dari satu bootstrap sample.
    Mengembalikan tuple parameter (urutan sesuai _PARAMS_TO_ARGS).
    """
    if dist_type == "Normal":
        return mle_normal(x_boot)
    elif dist_type == "Poisson":
        return (mle_poisson(x_boot),)
    elif dist_type == "Exponential":
        return (mle_exponential(x_boot),)
    elif dist_type == "Uniform":
        return mle_uniform(x_boot)
    elif dist_type == "Binomial":
        return (mle_binomial(x_boot, n_trials),)
    elif dist_type == "Beta":
        return mle_beta(x_boot)
    else:
        raise ValueError(f"Distribusi tidak dikenal: {dist_type}")


_PARAM_NAMES: dict[str, list[str]] = {
    "Normal":      ["mu", "sigma"],
    "Poisson":     ["lambda"],
    "Exponential": ["lambda"],
    "Uniform":     ["a", "b"],
    "Binomial":    ["p"],
    "Beta":        ["alpha", "beta"],
}


def compute_param_ci(
    dist_type: str,
    x: np.ndarray,
    params: dict,
    n_bootstrap: int = 1000,
    rng_seed: int | None = None,
) -> dict:
    """
    Hitung 95% Confidence Interval untuk parameter distribusi via bootstrap.

    Parameters
    ----------
    dist_type   : str   — nama distribusi
    x           : array-like — data observasi
    params      : dict  — parameter estimasi awal (digunakan untuk n_trials Binomial)
    n_bootstrap : int   — jumlah bootstrap samples (default 1000)
    rng_seed    : int | None — seed untuk reproducibility (opsional)

    Returns
    -------
    dict mapping param_name -> (lower_2.5, upper_97.5)
    Contoh: {"mu": (1.2, 3.4), "sigma": (0.5, 1.1)}
    """
    x = np.asarray(x, dtype=float)
    n = len(x)
    rng = np.random.default_rng(rng_seed)

    # Ambil n_trials untuk Binomial
    n_trials = int(params.get("n", 1))

    # Kumpulkan bootstrap estimates
    boot_estimates: list[tuple] = []
    for _ in range(n_bootstrap):
        x_boot = rng.choice(x, size=n, replace=True)
        try:
            est = _reestimate_params(dist_type, x_boot, n_trials=n_trials)
            # Pastikan est adalah tuple
            if not isinstance(est, tuple):
                est = (est,)
            boot_estimates.append(est)
        except Exception:
            # Lewati sample yang gagal (misal: semua nilai sama untuk Beta)
            continue

    if len(boot_estimates) == 0:
        # Fallback: kembalikan CI yang sama dengan estimasi titik
        param_names = _PARAM_NAMES[dist_type]
        return {name: (float("nan"), float("nan")) for name in param_names}

    # Konversi ke array: shape (n_valid_boots, n_params)
    boot_array = np.array(boot_estimates)  # shape (B, k)

    param_names = _PARAM_NAMES[dist_type]
    ci = {}
    for i, name in enumerate(param_names):
        col = boot_array[:, i]
        lower = float(np.percentile(col, 2.5))
        upper = float(np.percentile(col, 97.5))
        ci[name] = (lower, upper)

    return ci


# ---------------------------------------------------------------------------
# UI Layer — render_distribution_module()
# Task 9.6 — Requirements: 6.1–6.16
# ---------------------------------------------------------------------------

# UI-layer imports are kept inside render_distribution_module() so this module
# can be imported without streamlit/plotly installed (e.g. during unit/property-based tests).

# ---------------------------------------------------------------------------
# Konstanta distribusi
# ---------------------------------------------------------------------------

_DIST_OPTIONS = ["Normal", "Binomial", "Poisson", "Exponential", "Uniform", "Beta"]

_LATEX_FORMULAS: dict[str, str] = {
    "Normal":      r"f(x|\mu,\sigma) = \frac{1}{\sigma\sqrt{2\pi}} \exp\!\left(-\frac{(x-\mu)^2}{2\sigma^2}\right)",
    "Poisson":     r"P(X=k|\lambda) = \frac{\lambda^k e^{-\lambda}}{k!}",
    "Exponential": r"f(x|\lambda) = \lambda e^{-\lambda x}, \quad x \geq 0",
    "Uniform":     r"f(x|a,b) = \frac{1}{b-a}, \quad a \leq x \leq b",
    "Binomial":    r"P(X=k|n,p) = \binom{n}{k} p^k (1-p)^{n-k}",
    "Beta":        r"f(x|\alpha,\beta) = \frac{x^{\alpha-1}(1-x)^{\beta-1}}{B(\alpha,\beta)}, \quad 0 < x < 1",
}

_DIST_DESCRIPTIONS: dict[str, str] = {
    "Normal": (
        "Distribusi **Normal** (Gaussian) adalah distribusi kontinu simetris berbentuk lonceng. "
        "Parameter μ (mu) menentukan pusat distribusi, sedangkan σ (sigma) menentukan lebar/sebaran. "
        "MLE: μ̂ = mean(x), σ̂ = std(x, ddof=0)."
    ),
    "Binomial": (
        "Distribusi **Binomial** memodelkan jumlah keberhasilan dalam n percobaan independen "
        "dengan probabilitas keberhasilan p. "
        "MLE: p̂ = mean(x) / n_trials."
    ),
    "Poisson": (
        "Distribusi **Poisson** memodelkan jumlah kejadian dalam interval waktu/ruang tertentu "
        "dengan rata-rata λ. "
        "MLE: λ̂ = mean(x)."
    ),
    "Exponential": (
        "Distribusi **Exponential** memodelkan waktu antar kejadian dalam proses Poisson. "
        "Parameter λ adalah laju kejadian (rate). "
        "MLE: λ̂ = 1 / mean(x)."
    ),
    "Uniform": (
        "Distribusi **Uniform** kontinu mengasumsikan semua nilai dalam interval [a, b] "
        "memiliki probabilitas yang sama. "
        "MLE: â = min(x), b̂ = max(x)."
    ),
    "Beta": (
        "Distribusi **Beta** adalah distribusi kontinu pada interval (0, 1), cocok untuk "
        "memodelkan proporsi atau probabilitas. "
        "Parameter α dan β dikestimasi via scipy.stats.beta.fit (MLE)."
    ),
}


# ---------------------------------------------------------------------------
# Helper: bangun scipy args dari params dict
# ---------------------------------------------------------------------------

def _build_scipy_args(dist_type: str, params: dict) -> tuple:
    """Konversi params dict ke args tuple untuk scipy.stats."""
    if dist_type == "Normal":
        return (params["mu"], params["sigma"])          # loc=mu, scale=sigma
    elif dist_type == "Poisson":
        return (params["lambda"],)                       # mu=lambda
    elif dist_type == "Exponential":
        return (0.0, 1.0 / params["lambda"])             # loc=0, scale=1/lambda
    elif dist_type == "Uniform":
        return (params["a"], params["b"] - params["a"]) # loc=a, scale=b-a
    elif dist_type == "Binomial":
        return (int(params["n"]), params["p"])           # n, p
    elif dist_type == "Beta":
        return (params["alpha"], params["beta"])         # a, b
    else:
        raise ValueError(f"Distribusi tidak dikenal: {dist_type}")


def _get_scipy_dist(dist_type: str):
    """Kembalikan objek scipy.stats untuk distribusi yang dipilih."""
    mapping = {
        "Normal":      _scipy_stats.norm,
        "Poisson":     _scipy_stats.poisson,
        "Exponential": _scipy_stats.expon,
        "Uniform":     _scipy_stats.uniform,
        "Binomial":    _scipy_stats.binom,
        "Beta":        _scipy_stats.beta,
    }
    return mapping[dist_type]


def _is_discrete(dist_type: str) -> bool:
    return dist_type in ("Poisson", "Binomial")


# ---------------------------------------------------------------------------
# Helper: bangun params dict dari validator-compatible format
# ---------------------------------------------------------------------------

def _normalize_params_for_validator(dist_type: str, raw_params: dict) -> dict:
    """
    validate_distribution_params menggunakan key 'n_trials' untuk Binomial,
    sedangkan internal kita pakai 'n'. Normalisasi di sini.
    """
    if dist_type == "Binomial":
        p = raw_params.get("p", raw_params.get("p"))
        n = raw_params.get("n", raw_params.get("n_trials"))
        return {"p": p, "n_trials": n}
    return raw_params


# ---------------------------------------------------------------------------
# Render fungsi utama
# ---------------------------------------------------------------------------

def render_distribution_module() -> None:
    """
    Render modul Distribusi Probabilitas secara lengkap.

    Alur:
    1. Sidebar — selector distribusi dan mode input
    2. Sidebar — input parameter (manual atau estimasi dari data)
    3. Validasi parameter via validate_distribution_params()
    4. Render PDF/PMF chart interaktif (Plotly)
    5. Jika mode data: overlay histogram
    6. Tabel parameter + CI 95%
    7. Tabel statistik distribusi
    8. Rumus LaTeX PDF/PMF
    9. Simpan ke session_state dan tandai modul selesai

    Requirements: 6.1–6.16
    """
    # UI-layer imports — kept inside function so the module can be imported
    # without streamlit/plotly installed (e.g. during unit/property-based tests).
    import streamlit as st
    import pandas as pd
    import plotly.graph_objects as go
    import scipy.stats as _scipy_stats
    from utils.validators import validate_distribution_params
    from utils.formatters import fmt_stat
    from ui.styles import COLORS

    # ------------------------------------------------------------------
    # Judul modul
    # ------------------------------------------------------------------
    st.title("📈 Probabilistic — Estimasi Distribusi Probabilitas")
    st.markdown(
        "Estimasi parameter distribusi probabilitas dari data yang diunggah "
        "atau masukkan parameter secara manual, lalu visualisasikan PDF/PMF "
        "beserta statistik distribusinya."
    )

    # ------------------------------------------------------------------
    # Sidebar — selector distribusi (Req 6.1)
    # ------------------------------------------------------------------
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📈 Distribusi Probabilitas")

    dist_type: str = st.sidebar.selectbox(
        "Pilih jenis distribusi",
        options=_DIST_OPTIONS,
        index=0,
        key="dist_type_selector",
        help="Pilih distribusi probabilitas yang ingin diestimasi.",
    )

    # ------------------------------------------------------------------
    # Sidebar — mode input (Req 6.2)
    # ------------------------------------------------------------------
    input_mode: str = st.sidebar.radio(
        "Mode input parameter",
        options=["Estimasi dari Data", "Input Manual"],
        index=0,
        key="dist_input_mode",
        help="Pilih apakah parameter diestimasi dari data atau dimasukkan manual.",
    )

    # ------------------------------------------------------------------
    # Ambil data dari session_state (untuk mode estimasi)
    # ------------------------------------------------------------------
    df: pd.DataFrame | None = st.session_state.get("df")
    numeric_cols: list[str] = []
    if df is not None:
        numeric_cols = list(df.select_dtypes(include="number").columns)

    # ------------------------------------------------------------------
    # Sidebar — input parameter berdasarkan mode
    # ------------------------------------------------------------------
    params: dict = {}
    data_col_values: np.ndarray | None = None  # data kolom terpilih (mode estimasi)
    n_trials_for_binomial: int = 10            # default n_trials Binomial

    if input_mode == "Estimasi dari Data":
        # Req 6.3 — cek ketersediaan data
        if df is None or len(numeric_cols) == 0:
            st.warning(
                "⚠️ **Tidak ada data numerik tersedia** — silakan unggah dataset "
                "terlebih dahulu di modul **📊 Data-Driven DSS**."
            )
            return

        # Selector kolom numerik
        selected_col: str = st.sidebar.selectbox(
            "Pilih kolom data",
            options=numeric_cols,
            index=0,
            key="dist_col_selector",
            help="Kolom numerik yang akan digunakan untuk estimasi MLE.",
        )
        data_col_values = df[selected_col].dropna().to_numpy(dtype=float)

        if len(data_col_values) < 2:
            st.warning(
                f"⚠️ Kolom **{selected_col}** memiliki terlalu sedikit data "
                f"({len(data_col_values)} nilai valid). Minimal diperlukan 2 nilai."
            )
            return

        # Khusus Binomial — perlu n_trials dari user
        if dist_type == "Binomial":
            n_trials_for_binomial = st.sidebar.number_input(
                "Jumlah percobaan (n_trials)",
                min_value=1,
                max_value=10000,
                value=10,
                step=1,
                key="dist_binom_n_trials_data",
                help="Jumlah percobaan per observasi untuk distribusi Binomial.",
            )

        # Estimasi MLE
        try:
            if dist_type == "Normal":
                mu, sigma = mle_normal(data_col_values)
                params = {"mu": mu, "sigma": sigma}
            elif dist_type == "Poisson":
                lam = mle_poisson(data_col_values)
                params = {"lambda": lam}
            elif dist_type == "Exponential":
                lam = mle_exponential(data_col_values)
                params = {"lambda": lam}
            elif dist_type == "Uniform":
                a, b = mle_uniform(data_col_values)
                params = {"a": a, "b": b}
            elif dist_type == "Binomial":
                p_hat = mle_binomial(data_col_values, n_trials=n_trials_for_binomial)
                params = {"p": p_hat, "n": n_trials_for_binomial}
            elif dist_type == "Beta":
                alpha, beta_ = mle_beta(data_col_values)
                params = {"alpha": alpha, "beta": beta_}
        except Exception as exc:
            st.error(f"❌ Gagal mengestimasi parameter MLE: {exc}")
            return

        # Tampilkan parameter estimasi di sidebar
        st.sidebar.markdown("**Parameter MLE yang diestimasi:**")
        for k, v in params.items():
            st.sidebar.markdown(f"- **{k}** = {v:.6f}")

    else:
        # Mode Input Manual — tampilkan input per distribusi
        st.sidebar.markdown("**Masukkan parameter distribusi:**")

        if dist_type == "Normal":
            mu = st.sidebar.number_input(
                "μ (mu) — rata-rata",
                value=0.0, step=0.1, format="%.4f",
                key="dist_manual_mu",
            )
            sigma = st.sidebar.number_input(
                "σ (sigma) — standar deviasi",
                value=1.0, min_value=0.0001, step=0.1, format="%.4f",
                key="dist_manual_sigma",
            )
            params = {"mu": mu, "sigma": sigma}

        elif dist_type == "Binomial":
            n_val = st.sidebar.number_input(
                "n — jumlah percobaan",
                value=10, min_value=1, max_value=10000, step=1,
                key="dist_manual_n",
            )
            p_val = st.sidebar.number_input(
                "p — probabilitas keberhasilan",
                value=0.5, min_value=0.0001, max_value=0.9999,
                step=0.01, format="%.4f",
                key="dist_manual_p",
            )
            params = {"p": p_val, "n": int(n_val)}
            n_trials_for_binomial = int(n_val)

        elif dist_type == "Poisson":
            lam = st.sidebar.number_input(
                "λ (lambda) — laju kejadian",
                value=1.0, min_value=0.0001, step=0.1, format="%.4f",
                key="dist_manual_lambda",
            )
            params = {"lambda": lam}

        elif dist_type == "Exponential":
            lam = st.sidebar.number_input(
                "λ (lambda) — laju (rate)",
                value=1.0, min_value=0.0001, step=0.1, format="%.4f",
                key="dist_manual_lambda_exp",
            )
            params = {"lambda": lam}

        elif dist_type == "Uniform":
            a_val = st.sidebar.number_input(
                "a — batas bawah",
                value=0.0, step=0.1, format="%.4f",
                key="dist_manual_a",
            )
            b_val = st.sidebar.number_input(
                "b — batas atas",
                value=1.0, step=0.1, format="%.4f",
                key="dist_manual_b",
            )
            params = {"a": a_val, "b": b_val}

        elif dist_type == "Beta":
            alpha_val = st.sidebar.number_input(
                "α (alpha) — parameter bentuk 1",
                value=2.0, min_value=0.0001, step=0.1, format="%.4f",
                key="dist_manual_alpha",
            )
            beta_val = st.sidebar.number_input(
                "β (beta) — parameter bentuk 2",
                value=5.0, min_value=0.0001, step=0.1, format="%.4f",
                key="dist_manual_beta",
            )
            params = {"alpha": alpha_val, "beta": beta_val}

    # ------------------------------------------------------------------
    # Validasi parameter (Req 6.10)
    # ------------------------------------------------------------------
    # Normalisasi params untuk validator (Binomial: n → n_trials)
    validator_params = _normalize_params_for_validator(dist_type, params)
    is_valid, error_msg = validate_distribution_params(dist_type, validator_params)

    if not is_valid:
        st.error(f"❌ **Parameter tidak valid:** {error_msg}")
        st.info(
            "💡 Periksa kembali nilai parameter yang Anda masukkan dan pastikan "
            "memenuhi constraint distribusi yang dipilih."
        )
        return

    # ------------------------------------------------------------------
    # Bangun scipy args
    # ------------------------------------------------------------------
    try:
        scipy_args = _build_scipy_args(dist_type, params)
        dist_obj = _get_scipy_dist(dist_type)
    except Exception as exc:
        st.error(f"❌ Gagal membangun objek distribusi: {exc}")
        return

    # ------------------------------------------------------------------
    # Hitung x range: persentil 0.1 – 99.9 (Req 6.11)
    # ------------------------------------------------------------------
    try:
        x_low = float(dist_obj.ppf(0.001, *scipy_args))
        x_high = float(dist_obj.ppf(0.999, *scipy_args))
    except Exception:
        x_low, x_high = -10.0, 10.0

    # Pastikan range valid
    if not (np.isfinite(x_low) and np.isfinite(x_high)) or x_low >= x_high:
        x_low = float(dist_obj.mean(*scipy_args)) - 5
        x_high = float(dist_obj.mean(*scipy_args)) + 5

    # ------------------------------------------------------------------
    # Render PDF/PMF chart (Req 6.11)
    # ------------------------------------------------------------------
    st.markdown("---")
    st.subheader(f"📊 {'PMF' if _is_discrete(dist_type) else 'PDF'} Distribusi {dist_type}")

    fig = go.Figure()

    if _is_discrete(dist_type):
        # PMF — nilai integer
        x_int = np.arange(int(np.floor(x_low)), int(np.ceil(x_high)) + 1)
        y_pmf = dist_obj.pmf(x_int, *scipy_args)

        fig.add_trace(go.Bar(
            x=x_int.tolist(),
            y=y_pmf.tolist(),
            name=f"PMF {dist_type}",
            marker_color=COLORS["accent"],
            opacity=0.8,
        ))
        y_label = "P(X = k)"
        x_label = "k"
    else:
        # PDF — nilai kontinu
        x_cont = np.linspace(x_low, x_high, 500)
        y_pdf = dist_obj.pdf(x_cont, *scipy_args)

        fig.add_trace(go.Scatter(
            x=x_cont.tolist(),
            y=y_pdf.tolist(),
            mode="lines",
            name=f"PDF {dist_type}",
            line=dict(color=COLORS["accent"], width=2.5),
        ))
        y_label = "f(x)"
        x_label = "x"

    # Overlay histogram data jika mode estimasi dari data (Req 6.15)
    if input_mode == "Estimasi dari Data" and data_col_values is not None:
        fig.add_trace(go.Histogram(
            x=data_col_values.tolist(),
            name="Histogram Data",
            histnorm="probability density",
            opacity=0.4,
            marker_color=COLORS["warning"],
            nbinsx=30,
        ))

    fig.update_layout(
        title=f"{'PMF' if _is_discrete(dist_type) else 'PDF'} Distribusi {dist_type}",
        xaxis_title=x_label,
        yaxis_title=y_label,
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        title_font_size=16,
    )

    st.plotly_chart(fig, use_container_width=True)

    # ------------------------------------------------------------------
    # Tabel parameter estimasi + CI 95% (Req 6.13)
    # ------------------------------------------------------------------
    st.markdown("---")
    st.subheader("📋 Parameter Estimasi dan Confidence Interval 95%")

    ci_dict: dict = {}
    if input_mode == "Estimasi dari Data" and data_col_values is not None:
        with st.spinner("⏳ Menghitung bootstrap CI 95%..."):
            try:
                ci_dict = compute_param_ci(
                    dist_type=dist_type,
                    x=data_col_values,
                    params=params,
                    n_bootstrap=500,
                    rng_seed=42,
                )
            except Exception as exc:
                st.warning(f"⚠️ Gagal menghitung CI: {exc}")

    # Bangun tabel parameter
    param_rows = []
    for param_name, param_val in params.items():
        ci_lower, ci_upper = ci_dict.get(param_name, (float("nan"), float("nan")))
        ci_str = (
            f"[{ci_lower:.4f}, {ci_upper:.4f}]"
            if (np.isfinite(ci_lower) and np.isfinite(ci_upper))
            else "—"
        )
        param_rows.append({
            "Parameter": param_name,
            "Estimasi": f"{param_val:.6f}",
            "CI 95%": ci_str,
            "Sumber": "MLE dari data" if input_mode == "Estimasi dari Data" else "Input manual",
        })

    param_df = pd.DataFrame(param_rows)
    st.dataframe(param_df, use_container_width=True, hide_index=True)

    if input_mode == "Input Manual":
        st.caption("ℹ️ CI 95% hanya tersedia pada mode estimasi dari data (bootstrap resampling).")

    # ------------------------------------------------------------------
    # Tabel statistik distribusi (Req 6.14)
    # ------------------------------------------------------------------
    st.markdown("---")
    st.subheader("📐 Statistik Distribusi")

    try:
        dist_stats = compute_dist_stats(dist_type, params)
        stats_df = pd.DataFrame([
            {"Statistik": "Mean (Rata-rata)",           "Nilai": fmt_stat(dist_stats['mean'])},
            {"Statistik": "Variance (Variansi)",        "Nilai": fmt_stat(dist_stats['variance'])},
            {"Statistik": "Skewness (Kemencengan)",     "Nilai": fmt_stat(dist_stats['skewness'])},
            {"Statistik": "Kurtosis (Keruncingan)",     "Nilai": fmt_stat(dist_stats['kurtosis'])},
        ])
        st.dataframe(stats_df, use_container_width=True, hide_index=True)
    except Exception as exc:
        st.warning(f"⚠️ Gagal menghitung statistik distribusi: {exc}")

    # ------------------------------------------------------------------
    # Rumus LaTeX PDF/PMF (Req 6.12)
    # ------------------------------------------------------------------
    st.markdown("---")
    st.subheader("📝 Rumus PDF/PMF")

    latex_formula = _LATEX_FORMULAS.get(dist_type, "")
    if latex_formula:
        st.latex(latex_formula)
    else:
        st.markdown(f"Rumus untuk distribusi {dist_type} tidak tersedia.")

    # ------------------------------------------------------------------
    # Deskripsi metodologi (Req 6.16)
    # ------------------------------------------------------------------
    with st.expander("📚 Deskripsi Metodologi", expanded=False):
        st.markdown(f"### Distribusi {dist_type}")
        st.markdown(_DIST_DESCRIPTIONS.get(dist_type, ""))
        st.markdown(
            """
            ---
            **Langkah Estimasi MLE:**
            1. Kumpulkan data observasi dari kolom yang dipilih
            2. Terapkan formula MLE sesuai distribusi yang dipilih
            3. Hitung bootstrap CI 95% dengan 500 resampling untuk mengukur ketidakpastian estimasi

            **Interpretasi Parameter:**
            - Parameter yang diestimasi merepresentasikan karakteristik populasi yang mendasari data
            - CI 95% menunjukkan rentang nilai parameter yang konsisten dengan data yang diamati
            - Semakin sempit CI, semakin presisi estimasi parameter
            """
        )

    # ------------------------------------------------------------------
    # Simpan ke session_state dan tandai modul selesai (Req 6.11, 6.13)
    # ------------------------------------------------------------------
    st.session_state["dist_type"] = dist_type
    st.session_state["dist_params"] = {
        "dist_type": dist_type,
        "params": params,
        "ci_95": ci_dict,
        "source": "data" if input_mode == "Estimasi dari Data" else "manual",
    }

    if "completed_modules" not in st.session_state:
        st.session_state["completed_modules"] = set()
    st.session_state["completed_modules"].add("distribution")
