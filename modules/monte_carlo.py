"""
modules/monte_carlo.py
----------------------
Computation layer untuk Modul 7: Monte Carlo Simulation dan Sensitivity Analysis.

Semua fungsi di lapisan ini adalah pure functions — tidak mengimpor Streamlit
dan dapat diuji secara independen.

UI layer (render_monte_carlo_module) akan diimplementasikan pada task 12.5.
"""

from __future__ import annotations

import ast
import math
import operator
import numpy as np
from typing import TypedDict, Any


# ---------------------------------------------------------------------------
# Safe Expression Evaluator (replaces eval() for security)
# ---------------------------------------------------------------------------

# Allowed operators in expressions
_OPERATORS: dict[type, Any] = {
    ast.Add:  operator.add,
    ast.Sub:  operator.sub,
    ast.Mult: operator.mul,
    ast.Div:  operator.truediv,
    ast.Pow:  operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
    ast.Mod:  operator.mod,
    ast.FloorDiv: operator.floordiv,
}

# Allowed math functions (numpy-compatible for array inputs)
_SAFE_FUNCTIONS: dict[str, Any] = {
    "abs":   np.abs,
    "sqrt":  np.sqrt,
    "exp":   np.exp,
    "log":   np.log,
    "log10": np.log10,
    "log2":  np.log2,
    "sin":   np.sin,
    "cos":   np.cos,
    "tan":   np.tan,
    "ceil":  np.ceil,
    "floor": np.floor,
    "round": np.round,
    "min":   np.minimum,
    "max":   np.maximum,
    "sum":   np.sum,
    "pi":    math.pi,
    "e":     math.e,
}


def _eval_node(node: ast.AST, namespace: dict[str, Any]) -> Any:
    """Recursively evaluate an AST node against a variable namespace."""
    if isinstance(node, ast.Expression):
        return _eval_node(node.body, namespace)

    elif isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Konstanta tidak didukung: {node.value!r}")

    elif isinstance(node, ast.Name):
        name = node.id
        if name in namespace:
            return namespace[name]
        if name in _SAFE_FUNCTIONS:
            return _SAFE_FUNCTIONS[name]
        raise NameError(f"Nama '{name}' tidak terdefinisi dalam ekspresi.")

    elif isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _OPERATORS:
            raise ValueError(f"Operator tidak didukung: {op_type.__name__}")
        left = _eval_node(node.left, namespace)
        right = _eval_node(node.right, namespace)
        return _OPERATORS[op_type](left, right)

    elif isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _OPERATORS:
            raise ValueError(f"Operator unary tidak didukung: {op_type.__name__}")
        operand = _eval_node(node.operand, namespace)
        return _OPERATORS[op_type](operand)

    elif isinstance(node, ast.Call):
        func = _eval_node(node.func, namespace)
        if not callable(func):
            raise ValueError(f"'{node.func}' bukan fungsi yang dapat dipanggil.")
        args = [_eval_node(arg, namespace) for arg in node.args]
        if node.keywords:
            raise ValueError("Keyword arguments tidak didukung dalam ekspresi simulasi.")
        return func(*args)

    elif isinstance(node, ast.Attribute):
        # Allow np.sqrt, np.log, etc. via attribute access
        obj = _eval_node(node.value, namespace)
        attr = node.attr
        if obj is np and hasattr(np, attr):
            return getattr(np, attr)
        raise ValueError(f"Akses atribut '{attr}' tidak diizinkan.")

    else:
        raise ValueError(
            f"Konstruksi ekspresi tidak didukung: {type(node).__name__}. "
            "Gunakan operasi aritmatika dasar dan fungsi matematika yang diizinkan."
        )


def safe_eval_expr(expr: str, namespace: dict[str, Any]) -> Any:
    """
    Evaluasi ekspresi matematis secara aman menggunakan AST parser.

    Menggantikan eval() dengan parser AST yang hanya mengizinkan:
    - Operasi aritmatika: +, -, *, /, **, %, //
    - Fungsi matematika: abs, sqrt, exp, log, sin, cos, tan, ceil, floor, round, min, max, sum
    - Konstanta: pi, e
    - Variabel dari namespace yang diberikan
    - Akses np.* untuk fungsi numpy

    Parameters
    ----------
    expr : str
        Ekspresi matematis yang akan dievaluasi.
    namespace : dict
        Variabel yang tersedia dalam ekspresi (nama → nilai/array).

    Returns
    -------
    Any
        Hasil evaluasi ekspresi (biasanya np.ndarray atau float).

    Raises
    ------
    ValueError
        Jika ekspresi mengandung konstruksi yang tidak diizinkan.
    NameError
        Jika ekspresi mereferensikan variabel yang tidak ada di namespace.
    SyntaxError
        Jika ekspresi memiliki sintaks Python yang tidak valid.
    """
    try:
        tree = ast.parse(expr.strip(), mode="eval")
    except SyntaxError as e:
        raise SyntaxError(f"Sintaks ekspresi tidak valid: {e.msg}") from e

    # Inject np into namespace for np.* calls
    full_namespace = {"np": np, **namespace}
    return _eval_node(tree, full_namespace)


# ---------------------------------------------------------------------------
# Data Model
# ---------------------------------------------------------------------------

class MCResult(TypedDict):
    """Hasil simulasi Monte Carlo."""
    output: np.ndarray          # shape (N,), nilai output simulasi
    input_matrix: np.ndarray    # shape (N, k), k = jumlah variabel input
    var_names: list[str]        # nama setiap variabel input
    spearman_corrs: np.ndarray  # shape (k,), korelasi Spearman per variabel
    n_iterations: int           # jumlah iterasi yang dijalankan


# ---------------------------------------------------------------------------
# Computation Layer
# ---------------------------------------------------------------------------

def sample_variable(dist_type: str, params: dict, n: int) -> np.ndarray:
    """
    Bangkitkan n sampel acak dari distribusi yang ditentukan.

    Parameters
    ----------
    dist_type : str
        Jenis distribusi: "Normal", "Uniform", atau "Triangular".
    params : dict
        Parameter distribusi:
        - Normal:     {"mean": float, "std": float}
        - Uniform:    {"min": float, "max": float}
        - Triangular: {"min": float, "mode": float, "max": float}
    n : int
        Jumlah sampel yang dibangkitkan.

    Returns
    -------
    np.ndarray
        Array sampel dengan shape (n,).

    Raises
    ------
    ValueError
        Jika dist_type tidak dikenali.
    """
    if dist_type == "Normal":
        return np.random.normal(params["mean"], params["std"], n)
    elif dist_type == "Uniform":
        return np.random.uniform(params["min"], params["max"], n)
    elif dist_type == "Triangular":
        # Parameter c (mode relatif) dihitung tapi tidak digunakan langsung
        # karena np.random.triangular menerima left, mode, right secara langsung.
        return np.random.triangular(params["min"], params["mode"], params["max"], n)
    else:
        raise ValueError(
            f"Jenis distribusi tidak dikenali: '{dist_type}'. "
            "Pilihan yang valid: 'Normal', 'Uniform', 'Triangular'."
        )


def run_monte_carlo(
    variables: list[dict],
    expr: str,
    n: int = 10_000,
) -> MCResult:
    """
    Jalankan simulasi Monte Carlo dengan N iterasi.

    Ekspresi output dievaluasi menggunakan namespace terbatas untuk keamanan:
    - `__builtins__` diset ke {} (mencegah akses ke built-in Python)
    - Hanya variabel input dan `np` yang tersedia di namespace

    Parameters
    ----------
    variables : list[dict]
        Daftar variabel input simulasi. Setiap dict harus memiliki key:
        - "name": str — nama variabel (digunakan dalam ekspresi)
        - "dist_type": str — jenis distribusi
        - "params": dict — parameter distribusi
    expr : str
        Ekspresi matematis output simulasi menggunakan nama variabel.
        Contoh: "revenue - cost" atau "np.sqrt(x**2 + y**2)"
    n : int
        Jumlah iterasi simulasi. Default: 10.000.

    Returns
    -------
    MCResult
        TypedDict berisi output, input_matrix, var_names, spearman_corrs,
        dan n_iterations.
    """
    # Bangkitkan sampel untuk setiap variabel dan susun sebagai matriks (N, k)
    input_matrix = np.column_stack([
        sample_variable(v["dist_type"], v["params"], n) for v in variables
    ])

    # Buat namespace dengan nama variabel → kolom input_matrix
    namespace = {v["name"]: input_matrix[:, i] for i, v in enumerate(variables)}

    # Evaluasi ekspresi dengan AST parser yang aman (menggantikan eval())
    output = safe_eval_expr(expr, namespace)
    output = np.asarray(output, dtype=np.float64)

    # Hitung korelasi Spearman untuk sensitivity analysis
    var_names = [v["name"] for v in variables]
    sensitivity = compute_sensitivity(input_matrix, output, var_names)
    spearman_corrs = np.array([sensitivity[name] for name in var_names])

    return MCResult(
        output=output,
        input_matrix=input_matrix,
        var_names=var_names,
        spearman_corrs=spearman_corrs,
        n_iterations=n,
    )


def compute_sim_stats(output: np.ndarray) -> dict:
    """
    Hitung statistik ringkasan dari output simulasi Monte Carlo.

    Parameters
    ----------
    output : np.ndarray
        Array output simulasi dengan shape (N,).

    Returns
    -------
    dict
        Dictionary berisi:
        - "mean": float — rata-rata
        - "std": float — standar deviasi
        - "p5": float — persentil ke-5
        - "p95": float — persentil ke-95
        - "min": float — nilai minimum
        - "max": float — nilai maksimum
    """
    return {
        "mean": float(np.mean(output)),
        "std":  float(np.std(output)),
        "p5":   float(np.percentile(output, 5)),
        "p95":  float(np.percentile(output, 95)),
        "min":  float(np.min(output)),
        "max":  float(np.max(output)),
    }


def compute_sensitivity(
    input_matrix: np.ndarray,
    output: np.ndarray,
    var_names: list[str],
) -> dict[str, float]:
    """
    Hitung korelasi Spearman antara setiap variabel input dan output simulasi.

    Korelasi Spearman mengukur hubungan monoton (tidak harus linear) antara
    variabel input dan output, sehingga cocok untuk sensitivity analysis
    pada model non-linear.

    Parameters
    ----------
    input_matrix : np.ndarray
        Matriks variabel input dengan shape (N, k).
    output : np.ndarray
        Array output simulasi dengan shape (N,).
    var_names : list[str]
        Nama setiap variabel input (panjang harus = k).

    Returns
    -------
    dict[str, float]
        Dictionary {nama_variabel: korelasi_spearman}.
        Nilai korelasi dalam rentang [-1, 1].
    """
    from scipy.stats import spearmanr

    return {
        name: float(spearmanr(input_matrix[:, i], output).correlation)
        for i, name in enumerate(var_names)
    }


# ---------------------------------------------------------------------------
# UI layer — render_monte_carlo_module()
# Task 12.5 — Requirements: 8.1–8.14
# ---------------------------------------------------------------------------

def render_monte_carlo_module() -> None:
    """
    Render modul Monte Carlo Simulation & Sensitivity Analysis secara lengkap.

    Alur:
    1. Sidebar — jumlah variabel (1–10), lalu per variabel: nama, distribusi, parameter
    2. Sidebar — ekspresi output simulasi
    3. Sidebar — jumlah iterasi (default 10.000)
    4. Sidebar — tombol "Jalankan Simulasi"
    5. Validasi semua variabel dan ekspresi; tampilkan error jika tidak valid
    6. Peringatan konfirmasi jika iterasi > 1.000.000
    7. Jalankan simulasi dengan st.spinner() dan st.progress()
    8. Tampilkan histogram output + overlay kurva normal
    9. Tampilkan CDF chart
    10. Tampilkan tabel statistik ringkasan
    11. Tampilkan tornado chart sensitivity analysis
    12. st.latex() untuk rumus Monte Carlo
    13. Deskripsi metodologi
    14. Set session_state["mc_results"] dan tambahkan ke completed_modules

    Requirements: 8.1–8.14
    """
    # -----------------------------------------------------------------------
    # Lazy imports — kept inside function so the module can be imported
    # without streamlit/plotly installed (e.g. during unit/property-based tests)
    # -----------------------------------------------------------------------
    import streamlit as st
    import numpy as np
    import pandas as pd
    import plotly.graph_objects as go
    from scipy.stats import norm as scipy_norm
    from utils.validators import validate_sim_variable, validate_sim_expression
    from utils.formatters import fmt_stat
    from ui.styles import COLORS

    # -----------------------------------------------------------------------
    # Judul modul
    # -----------------------------------------------------------------------
    st.title("🎰 Simulation — Monte Carlo & Sensitivity Analysis")
    st.markdown(
        "Definisikan **variabel input** dengan distribusi probabilitas, tentukan "
        "**ekspresi output**, lalu jalankan **simulasi Monte Carlo** untuk memperoleh "
        "distribusi output dan analisis sensitivitas."
    )

    # -----------------------------------------------------------------------
    # Sidebar — jumlah variabel (Req 8.1)
    # -----------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 🎰 Monte Carlo Simulation")
    st.markdown("**Langkah 1: Variabel Input**")

    n_variables: int = st.number_input(
        label="Jumlah variabel input (1–10)",
        min_value=1,
        max_value=10,
        value=int(st.session_state.get("mc_n_variables", 2)),
        step=1,
        key="mc_n_variables_input",
    )
    st.session_state["mc_n_variables"] = n_variables

    # -----------------------------------------------------------------------
    # Sidebar — input per variabel (Req 8.1)
    # -----------------------------------------------------------------------
    dist_options = ["Normal", "Uniform", "Triangular"]

    # Ambil nilai sebelumnya jika ada
    prev_vars: list[dict] = st.session_state.get("mc_variables_input", [])

    variables_input: list[dict] = []

    for i in range(n_variables):
        st.markdown(f"**Variabel {i + 1}**")

        prev = prev_vars[i] if i < len(prev_vars) else {}

        var_name: str = st.text_input(
            label=f"Nama variabel {i + 1}",
            value=prev.get("name", f"x{i + 1}"),
            key=f"mc_var_name_{i}",
        )

        dist_type: str = st.selectbox(
            label=f"Distribusi variabel {i + 1}",
            options=dist_options,
            index=dist_options.index(prev.get("dist_type", "Normal")),
            key=f"mc_var_dist_{i}",
        )

        params: dict = {}

        if dist_type == "Normal":
            col_mean, col_std = st.columns(2)
            with col_mean:
                mean_val = st.number_input(
                    label="Mean",
                    value=float(prev.get("params", {}).get("mean", 0.0)),
                    step=1.0,
                    format="%.4f",
                    key=f"mc_var_mean_{i}",
                )
            with col_std:
                std_val = st.number_input(
                    label="Std",
                    value=float(prev.get("params", {}).get("std", 1.0)),
                    step=0.1,
                    format="%.4f",
                    key=f"mc_var_std_{i}",
                )
            params = {"mean": mean_val, "std": std_val}

        elif dist_type == "Uniform":
            col_min, col_max = st.columns(2)
            with col_min:
                min_val = st.number_input(
                    label="Min",
                    value=float(prev.get("params", {}).get("min", 0.0)),
                    step=1.0,
                    format="%.4f",
                    key=f"mc_var_min_{i}",
                )
            with col_max:
                max_val = st.number_input(
                    label="Max",
                    value=float(prev.get("params", {}).get("max", 1.0)),
                    step=1.0,
                    format="%.4f",
                    key=f"mc_var_max_{i}",
                )
            params = {"min": min_val, "max": max_val}

        elif dist_type == "Triangular":
            col_min2, col_mode, col_max2 = st.columns(3)
            with col_min2:
                tri_min = st.number_input(
                    label="Min",
                    value=float(prev.get("params", {}).get("min", 0.0)),
                    step=1.0,
                    format="%.4f",
                    key=f"mc_var_tri_min_{i}",
                )
            with col_mode:
                tri_mode = st.number_input(
                    label="Mode",
                    value=float(prev.get("params", {}).get("mode", 0.5)),
                    step=1.0,
                    format="%.4f",
                    key=f"mc_var_tri_mode_{i}",
                )
            with col_max2:
                tri_max = st.number_input(
                    label="Max",
                    value=float(prev.get("params", {}).get("max", 1.0)),
                    step=1.0,
                    format="%.4f",
                    key=f"mc_var_tri_max_{i}",
                )
            params = {"min": tri_min, "mode": tri_mode, "max": tri_max}

        variables_input.append({
            "name": var_name.strip(),
            "dist_type": dist_type,
            "params": params,
        })

    # Simpan ke session_state
    st.session_state["mc_variables_input"] = variables_input

    # -----------------------------------------------------------------------
    # Sidebar — ekspresi output (Req 8.3)
    # -----------------------------------------------------------------------
    st.markdown("**Langkah 2: Ekspresi Output**")

    var_names_preview = [v["name"] for v in variables_input if v["name"]]
    expr_placeholder = " + ".join(var_names_preview) if var_names_preview else "x1 + x2"

    expr_input: str = st.text_input(
        label="Ekspresi output simulasi",
        value=st.session_state.get("mc_expr_input", expr_placeholder),
        placeholder=expr_placeholder,
        help="Gunakan nama variabel yang telah didefinisikan. Contoh: revenue - cost",
        key="mc_expr_text_input",
    )
    st.session_state["mc_expr_input"] = expr_input

    # -----------------------------------------------------------------------
    # Sidebar — jumlah iterasi (Req 8.5)
    # -----------------------------------------------------------------------
    st.markdown("**Langkah 3: Iterasi**")

    n_iterations: int = st.number_input(
        label="Jumlah iterasi simulasi",
        min_value=100,
        max_value=10_000_000,
        value=int(st.session_state.get("mc_n_iterations", 10_000)),
        step=1_000,
        key="mc_n_iterations_input",
    )
    st.session_state["mc_n_iterations"] = n_iterations

    # -----------------------------------------------------------------------
    # Sidebar — tombol jalankan simulasi
    # -----------------------------------------------------------------------
    st.markdown("**Langkah 4: Jalankan**")
    run_clicked = st.button(
        "🚀 Jalankan Simulasi",
        key="mc_run_btn",
        use_container_width=True,
        type="primary",
    )

    # -----------------------------------------------------------------------
    # State untuk menyimpan hasil simulasi
    # -----------------------------------------------------------------------
    if "mc_run_result" not in st.session_state:
        st.session_state["mc_run_result"] = None

    # -----------------------------------------------------------------------
    # Proses saat tombol diklik
    # -----------------------------------------------------------------------
    if run_clicked:
        # --- Validasi semua variabel (Req 8.2) ---
        validation_errors: list[str] = []

        for v in variables_input:
            ok, msg = validate_sim_variable(v["name"], v["dist_type"], v["params"])
            if not ok:
                validation_errors.append(f"Variabel '{v['name']}': {msg}")

        # --- Validasi ekspresi (Req 8.4) ---
        valid_var_names = [v["name"] for v in variables_input if v["name"].strip()]
        ok_expr, msg_expr = validate_sim_expression(expr_input, valid_var_names)
        if not ok_expr:
            validation_errors.append(f"Ekspresi output: {msg_expr}")

        if validation_errors:
            for err in validation_errors:
                st.error(f"❌ {err}")
            st.session_state["mc_run_result"] = None
        else:
            # --- Peringatan iterasi > 1.000.000 (Req 8.13) ---
            proceed = True
            if n_iterations > 1_000_000:
                st.warning(
                    f"⚠️ **Peringatan:** Anda meminta **{n_iterations:,} iterasi**. "
                    "Jumlah iterasi yang sangat besar dapat membutuhkan waktu komputasi yang lama "
                    "dan menggunakan banyak memori. Pastikan Anda memiliki sumber daya yang cukup."
                )
                confirm_large = st.checkbox(
                    "✅ Saya memahami risiko dan ingin melanjutkan simulasi",
                    key="mc_confirm_large_iter",
                )
                if not confirm_large:
                    proceed = False
                    st.info("Centang kotak konfirmasi di atas untuk melanjutkan simulasi.")

            if proceed:
                # --- Jalankan simulasi dengan spinner dan progress (Req 8.12) ---
                progress_bar = st.progress(0, text="Mempersiapkan simulasi...")

                with st.spinner("⏳ Menjalankan simulasi..."):
                    try:
                        # Simulasikan progress dalam beberapa tahap
                        progress_bar.progress(10, text="Membangkitkan sampel acak...")
                        result: MCResult = run_monte_carlo(
                            variables=variables_input,
                            expr=expr_input,
                            n=n_iterations,
                        )
                        progress_bar.progress(70, text="Menghitung statistik...")
                        stats = compute_sim_stats(result["output"])
                        progress_bar.progress(90, text="Menyelesaikan analisis sensitivitas...")
                        progress_bar.progress(100, text="Simulasi selesai!")

                        st.session_state["mc_run_result"] = {
                            "result": result,
                            "stats": stats,
                        }
                        st.success(
                            f"✅ Simulasi selesai! {n_iterations:,} iterasi berhasil dijalankan."
                        )

                    except Exception as exc:
                        st.error(f"❌ Simulasi gagal: {type(exc).__name__}: {exc}")
                        st.session_state["mc_run_result"] = None

                progress_bar.empty()

    # -----------------------------------------------------------------------
    # Ambil hasil dari session_state
    # -----------------------------------------------------------------------
    run_result: dict | None = st.session_state.get("mc_run_result")

    # -----------------------------------------------------------------------
    # Jika belum ada hasil, tampilkan panduan
    # -----------------------------------------------------------------------
    if run_result is None:
        st.info(
            "💡 **Cara penggunaan:**\n"
            "1. Tentukan jumlah variabel input (1–10) di sidebar\n"
            "2. Isi nama, distribusi, dan parameter setiap variabel\n"
            "3. Masukkan ekspresi output menggunakan nama variabel\n"
            "4. Tentukan jumlah iterasi (default: 10.000)\n"
            "5. Klik tombol **▶️ Jalankan Simulasi**"
        )
    else:
        # -------------------------------------------------------------------
        # Ekstrak hasil
        # -------------------------------------------------------------------
        mc_result: MCResult = run_result["result"]
        stats: dict = run_result["stats"]

        output_arr: np.ndarray = mc_result["output"]
        input_matrix: np.ndarray = mc_result["input_matrix"]
        var_names: list[str] = mc_result["var_names"]
        spearman_corrs: np.ndarray = mc_result["spearman_corrs"]
        n_iter: int = mc_result["n_iterations"]

        # -------------------------------------------------------------------
        # Histogram output + overlay kurva normal (Req 8.6)
        # -------------------------------------------------------------------
        st.markdown("---")
        st.subheader("📊 Distribusi Output Simulasi")

        fig_hist = go.Figure()

        # Histogram
        fig_hist.add_trace(go.Histogram(
            x=output_arr.tolist(),
            nbinsx=min(50, max(20, n_iter // 200)),
            name="Frekuensi Output",
            marker_color=COLORS["accent"],
            opacity=0.7,
            histnorm="probability density",
        ))

        # Overlay kurva normal
        x_norm = np.linspace(float(output_arr.min()), float(output_arr.max()), 300)
        y_norm = scipy_norm.pdf(x_norm, loc=stats["mean"], scale=stats["std"])

        fig_hist.add_trace(go.Scatter(
            x=x_norm.tolist(),
            y=y_norm.tolist(),
            mode="lines",
            name="Kurva Normal (overlay)",
            line=dict(color=COLORS["primary"], width=2.5),
        ))

        # Garis vertikal mean
        fig_hist.add_vline(
            x=stats["mean"],
            line_dash="dash",
            line_color=COLORS["success"],
            annotation_text=f"Mean = {fmt_stat(stats['mean'])}",
            annotation_position="top right",
        )

        fig_hist.update_layout(
            title=f"Histogram Output Simulasi Monte Carlo (N = {n_iter:,})",
            xaxis_title="Nilai Output",
            yaxis_title="Densitas Probabilitas",
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            title_font_size=15,
            bargap=0.02,
        )

        st.plotly_chart(fig_hist, use_container_width=True)

        # -------------------------------------------------------------------
        # CDF chart (Req 8.8)
        # -------------------------------------------------------------------
        st.markdown("---")
        st.subheader("📈 Cumulative Distribution Function (CDF)")

        sorted_output = np.sort(output_arr)
        cdf_y = np.arange(1, len(sorted_output) + 1) / len(sorted_output)

        # Subsample untuk performa jika iterasi sangat besar
        max_points = 2000
        if len(sorted_output) > max_points:
            idx_sample = np.linspace(0, len(sorted_output) - 1, max_points, dtype=int)
            sorted_output_plot = sorted_output[idx_sample]
            cdf_y_plot = cdf_y[idx_sample]
        else:
            sorted_output_plot = sorted_output
            cdf_y_plot = cdf_y

        fig_cdf = go.Figure()

        fig_cdf.add_trace(go.Scatter(
            x=sorted_output_plot.tolist(),
            y=cdf_y_plot.tolist(),
            mode="lines",
            name="CDF Empiris",
            line=dict(color=COLORS["accent"], width=2.5),
            fill="tozeroy",
            fillcolor="rgba(193,255,114,0.13)",
        ))

        # Garis P5 dan P95
        fig_cdf.add_vline(
            x=stats["p5"],
            line_dash="dot",
            line_color=COLORS["warning"],
            annotation_text=f"P5 = {fmt_stat(stats['p5'])}",
            annotation_position="bottom right",
        )
        fig_cdf.add_vline(
            x=stats["p95"],
            line_dash="dot",
            line_color=COLORS["warning"],
            annotation_text=f"P95 = {fmt_stat(stats['p95'])}",
            annotation_position="top left",
        )

        fig_cdf.update_layout(
            title=f"CDF Output Simulasi Monte Carlo (N = {n_iter:,})",
            xaxis_title="Nilai Output",
            yaxis_title="Probabilitas Kumulatif",
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            title_font_size=15,
            yaxis=dict(range=[0, 1.05]),
        )

        st.plotly_chart(fig_cdf, use_container_width=True)

        # -------------------------------------------------------------------
        # Tabel statistik ringkasan (Req 8.7)
        # -------------------------------------------------------------------
        st.markdown("---")
        st.subheader("📋 Statistik Ringkasan Output")

        stats_df = pd.DataFrame([
            {"Statistik": "Mean (Rata-rata)",          "Nilai": fmt_stat(stats['mean'])},
            {"Statistik": "Std Dev (Standar Deviasi)", "Nilai": fmt_stat(stats['std'])},
            {"Statistik": "Persentil ke-5 (P5)",       "Nilai": fmt_stat(stats['p5'])},
            {"Statistik": "Persentil ke-95 (P95)",     "Nilai": fmt_stat(stats['p95'])},
            {"Statistik": "Minimum",                   "Nilai": fmt_stat(stats['min'])},
            {"Statistik": "Maksimum",                  "Nilai": fmt_stat(stats['max'])},
        ])

        col_stats, col_metrics = st.columns([2, 1])

        with col_stats:
            st.dataframe(stats_df, use_container_width=True, hide_index=True)

        with col_metrics:
            st.metric(
                label="Mean",
                value=fmt_stat(stats['mean']),
            )
            st.metric(
                label="Std Dev",
                value=fmt_stat(stats['std']),
            )
            st.metric(
                label="Rentang P5–P95",
                value=fmt_stat(stats['p95'] - stats['p5']),
                help="Interval kepercayaan 90% dari output simulasi",
            )

        # -------------------------------------------------------------------
        # Tornado chart sensitivity analysis (Req 8.10, 8.11)
        # -------------------------------------------------------------------
        st.markdown("---")
        st.subheader("🌪️ Tornado Chart — Sensitivity Analysis")

        # Urutkan berdasarkan |korelasi Spearman| dari terbesar ke terkecil
        abs_corrs = np.abs(spearman_corrs)
        sorted_idx = np.argsort(abs_corrs)  # ascending — plotly horizontal bar terbalik

        sorted_names = [var_names[i] for i in sorted_idx]
        sorted_corrs = [float(spearman_corrs[i]) for i in sorted_idx]
        sorted_abs   = [float(abs_corrs[i]) for i in sorted_idx]

        bar_colors = [
            COLORS["success"] if c >= 0 else COLORS["warning"]
            for c in sorted_corrs
        ]

        fig_tornado = go.Figure()

        fig_tornado.add_trace(go.Bar(
            x=sorted_corrs,
            y=sorted_names,
            orientation="h",
            marker_color=bar_colors,
            text=[f"{c:+.4f}" for c in sorted_corrs],
            textposition="outside",
            name="Korelasi Spearman",
        ))

        fig_tornado.add_vline(x=0, line_color="black", line_width=1)

        fig_tornado.update_layout(
            title="Tornado Chart — Korelasi Spearman (Sensitivity Analysis)",
            xaxis_title="Korelasi Spearman dengan Output",
            yaxis_title="Variabel Input",
            template="plotly_white",
            title_font_size=15,
            xaxis=dict(range=[-1.1, 1.1]),
            showlegend=False,
        )

        st.plotly_chart(fig_tornado, use_container_width=True)

        # Tabel korelasi
        corr_df = pd.DataFrame({
            "Variabel": [var_names[i] for i in np.argsort(abs_corrs)[::-1]],
            "Korelasi Spearman": [
                f"{float(spearman_corrs[i]):+.4f}"
                for i in np.argsort(abs_corrs)[::-1]
            ],
            "|Korelasi|": [
                f"{float(abs_corrs[i]):.4f}"
                for i in np.argsort(abs_corrs)[::-1]
            ],
            "Pengaruh": [
                "Positif" if float(spearman_corrs[i]) >= 0 else "Negatif"
                for i in np.argsort(abs_corrs)[::-1]
            ],
        })

        st.dataframe(corr_df, use_container_width=True, hide_index=True)

        most_influential = var_names[int(np.argmax(abs_corrs))]
        st.caption(
            f"**Variabel paling berpengaruh:** {most_influential} "
            f"(|ρ| = {float(abs_corrs.max()):.4f})"
        )

        # -------------------------------------------------------------------
        # Rumus LaTeX Monte Carlo (Req 8.9)
        # -------------------------------------------------------------------
        st.markdown("---")
        st.subheader("📐 Rumus Monte Carlo")

        st.latex(r"\hat{\mu} = \frac{1}{N} \sum_{i=1}^{N} f(X_i)")

        st.caption(
            r"di mana $N$ = jumlah iterasi, $X_i$ = sampel acak ke-$i$ dari distribusi input, "
            r"dan $f(\cdot)$ = fungsi output simulasi."
        )

        st.latex(r"\hat{\sigma}^2 = \frac{1}{N} \sum_{i=1}^{N} \left(f(X_i) - \hat{\mu}\right)^2")

        st.caption(
            r"Varians estimasi output simulasi. Semakin besar $N$, semakin akurat estimasi "
            r"(hukum bilangan besar)."
        )

        # -------------------------------------------------------------------
        # Simpan ke session_state (Req 8.7 — mc_results)
        # -------------------------------------------------------------------
        st.session_state["mc_results"] = mc_result
        st.session_state["mc_input_matrix"] = input_matrix

        if "completed_modules" not in st.session_state:
            st.session_state["completed_modules"] = set()
        st.session_state["completed_modules"].add("monte_carlo")

    # -----------------------------------------------------------------------
    # Download hasil simulasi
    # -----------------------------------------------------------------------
    if run_result is not None:
        st.markdown("---")
        st.subheader("📥 Unduh Hasil Simulasi")
        import pandas as _pd_dl
        dl_stats_df = _pd_dl.DataFrame([
            {"Statistik": "Mean",          "Nilai": fmt_stat(stats['mean'])},
            {"Statistik": "Std Dev",       "Nilai": fmt_stat(stats['std'])},
            {"Statistik": "P5",            "Nilai": fmt_stat(stats['p5'])},
            {"Statistik": "P95",           "Nilai": fmt_stat(stats['p95'])},
            {"Statistik": "Min",           "Nilai": fmt_stat(stats['min'])},
            {"Statistik": "Max",           "Nilai": fmt_stat(stats['max'])},
        ])
        csv_bytes = dl_stats_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Unduh Statistik Simulasi (CSV)",
            data=csv_bytes,
            file_name="monte_carlo_stats.csv",
            mime="text/csv",
        )

    # -----------------------------------------------------------------------
    # Deskripsi metodologi (Req 8.14) — selalu ditampilkan
    # -----------------------------------------------------------------------
    st.markdown("---")
    st.subheader("📚 Metodologi Monte Carlo & Sensitivity Analysis")

    with st.expander("Baca Deskripsi Metodologi", expanded=False):
        st.markdown(
            r"""
            ### Simulasi Monte Carlo

            **Simulasi Monte Carlo** adalah metode komputasi yang menggunakan bilangan acak
            untuk mengestimasi distribusi output dari model matematis yang memiliki input
            tidak pasti. Metode ini dinamai dari kasino Monte Carlo di Monaco karena
            ketergantungannya pada pengacakan.

            **Langkah-langkah simulasi:**
            1. Definisikan distribusi probabilitas untuk setiap variabel input
            2. Bangkitkan N sampel acak dari setiap distribusi input
            3. Evaluasi fungsi output $f(X_i)$ untuk setiap set sampel
            4. Analisis distribusi output yang dihasilkan

            ---

            ### Distribusi yang Didukung

            | Distribusi | Parameter | Karakteristik |
            |-----------|-----------|---------------|
            | **Normal** | mean, std | Simetris, cocok untuk variabel alami |
            | **Uniform** | min, max | Semua nilai sama mungkin dalam rentang |
            | **Triangular** | min, mode, max | Asimetris, cocok jika ada nilai paling mungkin |

            ---

            ### Konvergensi Simulasi

            Berdasarkan **Hukum Bilangan Besar**, estimasi Monte Carlo konvergen ke nilai
            sebenarnya seiring bertambahnya N:
            """
        )
        try:
            st.latex(r"\text{Kesalahan Standar} = \frac{\sigma_{output}}{\sqrt{N}}")
        except Exception:
            st.code("Kesalahan Standar = sigma_output / sqrt(N)")
        st.markdown(
            """
            - **N = 1.000**: Estimasi kasar, kesalahan ~3%
            - **N = 10.000**: Estimasi baik, kesalahan ~1%
            - **N = 100.000**: Estimasi sangat baik, kesalahan ~0.3%
            - **N = 1.000.000**: Estimasi presisi tinggi, kesalahan ~0.1%

            ---

            ### Sensitivity Analysis — Korelasi Spearman

            **Korelasi Spearman** (ρ) mengukur hubungan monoton antara variabel input dan output:
            """
        )
        try:
            st.latex(r"\rho = 1 - \frac{6 \sum d_i^2}{n(n^2 - 1)}")
        except Exception:
            st.code("rho = 1 - 6*sum(d_i^2) / (n*(n^2 - 1))")
        st.markdown(
            r"""
            di mana $d_i$ adalah selisih peringkat antara variabel input dan output.

            **Interpretasi Tornado Chart:**
            - **|ρ| mendekati 1**: Variabel sangat berpengaruh terhadap output
            - **|ρ| mendekati 0**: Variabel hampir tidak berpengaruh
            - **ρ > 0**: Hubungan positif (input naik → output naik)
            - **ρ < 0**: Hubungan negatif (input naik → output turun)

            Korelasi Spearman dipilih karena lebih robust terhadap hubungan non-linear
            dibandingkan korelasi Pearson, sehingga cocok untuk model simulasi yang kompleks.

            ---

            ### Panduan Interpretasi Hasil

            - **Mean**: Estimasi nilai harapan output simulasi
            - **Std Dev**: Ukuran ketidakpastian/variabilitas output
            - **P5–P95**: Interval kepercayaan 90% — output berada dalam rentang ini
              dengan probabilitas 90%
            - **Histogram**: Bentuk distribusi output; simetris jika mendekati normal
            - **CDF**: Probabilitas output ≤ nilai tertentu; berguna untuk analisis risiko
            """
        )
