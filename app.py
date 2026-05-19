"""
app.py — Entry point untuk Dashboard DSS (Decision Support System).

Tanggung jawab:
- Konfigurasi halaman Streamlit (set_page_config)
- Inisialisasi semua key st.session_state
- Inject CSS custom dan render sidebar navigasi
- Routing: active_module == None → halaman sambutan; selain itu → renderer modul

Requirements: 1.3, 1.4, 1.7, 1.8
"""

from __future__ import annotations

import streamlit as st

# ---------------------------------------------------------------------------
# Konfigurasi halaman — HARUS dipanggil sebelum perintah Streamlit lainnya
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard DSS — Decision Support System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Import komponen UI
# ---------------------------------------------------------------------------
from ui.styles import inject_custom_css
from ui.sidebar import render_sidebar

# ---------------------------------------------------------------------------
# Import renderer modul — gunakan try/except karena modul belum semua ada
# ---------------------------------------------------------------------------

def _placeholder_renderer(module_name: str):
    """Renderer sementara untuk modul yang belum diimplementasikan."""
    def _render():
        st.info(
            f"⚙️ **Modul sedang dalam pengembangan**\n\n"
            f"Modul `{module_name}` belum tersedia. "
            f"Silakan tunggu pembaruan berikutnya.",
            icon="🔧",
        )
    return _render


try:
    from modules.data_driven import render_data_driven_module
except (ImportError, Exception):
    render_data_driven_module = _placeholder_renderer("data_driven")

try:
    from modules.payoff_table import render_payoff_table_module
except (ImportError, Exception):
    render_payoff_table_module = _placeholder_renderer("payoff_table")

try:
    from modules.ev_eol import render_ev_eol_module
except (ImportError, Exception):
    render_ev_eol_module = _placeholder_renderer("ev_eol")

try:
    from modules.uncertainty import render_uncertainty_module
except (ImportError, Exception):
    render_uncertainty_module = _placeholder_renderer("uncertainty")

try:
    from modules.distribution import render_distribution_module
except (ImportError, Exception):
    render_distribution_module = _placeholder_renderer("distribution")

try:
    from modules.utility import render_utility_module
except (ImportError, Exception):
    render_utility_module = _placeholder_renderer("utility")

try:
    from modules.monte_carlo import render_monte_carlo_module
except (ImportError, Exception):
    render_monte_carlo_module = _placeholder_renderer("monte_carlo")

try:
    from modules.recommendation_engine import render_recommendation_module
except (ImportError, Exception):
    render_recommendation_module = _placeholder_renderer("recommendation")

# ---------------------------------------------------------------------------
# Peta routing: key modul → fungsi renderer
# ---------------------------------------------------------------------------
MODULE_RENDERERS: dict[str, callable] = {
    "data_driven":    render_data_driven_module,
    "payoff_table":   render_payoff_table_module,
    "ev_eol":         render_ev_eol_module,
    "uncertainty":    render_uncertainty_module,
    "distribution":   render_distribution_module,
    "utility":        render_utility_module,
    "monte_carlo":    render_monte_carlo_module,
    "recommendation": render_recommendation_module,
}


# ---------------------------------------------------------------------------
# Inisialisasi session state
# ---------------------------------------------------------------------------

def _init_session_state() -> None:
    """
    Inisialisasi semua key st.session_state dengan nilai default.
    Hanya mengisi key yang belum ada agar state yang sudah tersimpan
    tidak tertimpa saat halaman di-rerun (Requirement 1.8).
    """
    defaults: dict = {
        # Dataset — Data-Driven DSS
        "df":                   None,   # pd.DataFrame | None
        "df_filename":          None,   # str | None

        # Payoff Table — digunakan bersama oleh modul 2–5
        "payoff_matrix":        None,   # np.ndarray shape (m, n) | None
        "alt_names":            [],     # list[str]
        "state_names":          [],     # list[str]

        # EV / EOL
        "probabilities":        None,   # np.ndarray shape (n,) | None
        "ev_results":           None,   # dict | None
        "eol_results":          None,   # dict | None

        # Uncertainty criteria
        "uncertainty_results":  None,   # dict | None

        # Distribution
        "dist_type":            None,   # str | None
        "dist_params":          None,   # dict | None

        # Utility
        "utility_params":       None,   # dict | None
        "utility_func_type":    None,   # str | None

        # Monte Carlo
        "mc_results":           None,   # np.ndarray | None
        "mc_input_matrix":      None,   # np.ndarray | None

        # Navigasi
        "active_module":        None,   # str | None

        # Indikator penyelesaian modul (untuk sidebar ✅)
        "completed_modules":    set(),  # set[str]
    }

    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


# ---------------------------------------------------------------------------
# Halaman sambutan
# ---------------------------------------------------------------------------

def render_welcome_page() -> None:
    """
    Render halaman sambutan yang ditampilkan saat belum ada modul yang dipilih.

    Menampilkan:
    - Judul aplikasi
    - Deskripsi singkat tentang DSS
    - Panduan langkah-langkah penggunaan aplikasi (Requirement 1.7)
    """
    # Judul utama
    st.title("📊 Dashboard DSS — Decision Support System")
    st.markdown(
        "**Selamat datang di Dashboard DSS** — platform analisis keputusan interaktif "
        "untuk keperluan presentasi akademik mahasiswa Statistika."
    )
    st.divider()

    # Deskripsi DSS
    col_desc, col_info = st.columns([2, 1])

    with col_desc:
        st.subheader("🎯 Apa itu Decision Support System?")
        st.markdown(
            """
            **Decision Support System (DSS)** atau Sistem Pendukung Keputusan adalah
            sistem berbasis komputer yang membantu pengambil keputusan dalam menganalisis
            data, membangun model, dan mengevaluasi alternatif keputusan secara kuantitatif.

            Dashboard ini mengintegrasikan **dua paradigma DSS** dalam satu antarmuka:

            - 📊 **Data-Driven DSS** — eksplorasi dan analisis dataset nyata menggunakan
              statistik deskriptif, visualisasi tren, dan analisis korelasi.
            - 🧮 **Model-Driven DSS** — penerapan enam kelompok metode Teori Keputusan
              kuantitatif: dari analisis di bawah kepastian, risiko, ketidakpastian,
              pemodelan probabilistik, fungsi utilitas, hingga simulasi Monte Carlo.
            """
        )

    with col_info:
        st.info(
            "**8 Modul Tersedia**\n\n"
            "1. 📊 Data-Driven DSS\n"
            "2. 📋 Payoff Table\n"
            "3. 🎲 EV & EOL\n"
            "4. ❓ Kriteria Ketidakpastian\n"
            "5. 📈 Distribusi Probabilitas\n"
            "6. ⚖️ Fungsi Utilitas\n"
            "7. 🎰 Monte Carlo\n"
            "8. 🏆 Recommendation Engine",
            icon="📌",
        )

    st.divider()

    # Panduan penggunaan
    st.subheader("🗺️ Panduan Penggunaan Aplikasi")
    st.markdown("Ikuti langkah-langkah berikut untuk memaksimalkan penggunaan dashboard:")

    steps = [
        (
            "1️⃣ Unggah Dataset (Opsional)",
            "Mulai dengan modul **📊 Data-Driven DSS** di sidebar untuk mengunggah "
            "file CSV atau XLSX. Eksplorasi statistik deskriptif, tren data, dan "
            "matriks korelasi antar variabel numerik.",
        ),
        (
            "2️⃣ Buat Payoff Table",
            "Buka modul **📋 Certainty — Payoff Table** untuk mendefinisikan "
            "alternatif keputusan, kondisi alam (state of nature), dan nilai payoff "
            "setiap kombinasinya. Payoff table ini akan digunakan oleh modul-modul berikutnya.",
        ),
        (
            "3️⃣ Analisis di Bawah Risiko (EV & EOL)",
            "Gunakan modul **🎲 Risk — EV & EOL** untuk memasukkan probabilitas "
            "kondisi alam dan menghitung Expected Value (EV), Expected Opportunity "
            "Loss (EOL), serta EVPI (Expected Value of Perfect Information).",
        ),
        (
            "4️⃣ Analisis di Bawah Ketidakpastian",
            "Modul **❓ Uncertainty** menghitung empat kriteria keputusan tanpa "
            "informasi probabilitas: Maximax (optimistis), Maximin (pesimistis), "
            "Minimax Regret (Savage), dan Laplace (netral).",
        ),
        (
            "5️⃣ Pemodelan Distribusi Probabilitas",
            "Modul **📈 Probabilistic — Distribusi** memungkinkan estimasi parameter "
            "distribusi (Normal, Binomial, Poisson, Exponential, Uniform, Beta) "
            "dari data yang diunggah atau input manual.",
        ),
        (
            "6️⃣ Fungsi Utilitas & Preferensi Risiko",
            "Modul **⚖️ Utility** melakukan curve fitting fungsi utilitas dan "
            "mengklasifikasikan preferensi risiko pengambil keputusan: "
            "Risk Averse, Risk Neutral, atau Risk Seeking.",
        ),
        (
            "7️⃣ Simulasi Monte Carlo",
            "Modul **🎰 Simulation — Monte Carlo** menjalankan simulasi dengan "
            "≥10.000 iterasi dan analisis sensitivitas (Spearman correlation) "
            "untuk mengidentifikasi variabel input yang paling berpengaruh.",
        ),
        (
            "✅ Rekomendasi Otomatis",
            "Setelah menjalankan minimal dua modul Model-Driven DSS, "
            "**Recommendation Engine** akan merangkum alternatif terbaik dari "
            "semua metode dan menampilkan tingkat konsensus antar metode.",
        ),
    ]

    for title, description in steps:
        with st.expander(title, expanded=False):
            st.markdown(description)

    st.divider()

    # Tips penggunaan
    st.subheader("💡 Tips Penggunaan")
    col_tip1, col_tip2, col_tip3 = st.columns(3)

    with col_tip1:
        st.success(
            "**State Tersimpan Otomatis**\n\n"
            "Data yang sudah diinput di satu modul akan tetap tersimpan "
            "saat Anda berpindah ke modul lain dalam sesi yang sama.",
            icon="💾",
        )

    with col_tip2:
        st.info(
            "**Indikator ✅ di Sidebar**\n\n"
            "Modul yang sudah memiliki data atau hasil akan ditandai "
            "dengan ikon ✅ di sidebar navigasi.",
            icon="🧭",
        )

    with col_tip3:
        st.warning(
            "**Mulai dari Payoff Table**\n\n"
            "Modul EV & EOL, Uncertainty, dan Utility membutuhkan "
            "Payoff Table yang sudah didefinisikan terlebih dahulu.",
            icon="⚠️",
        )

    st.divider()
    st.caption(
        "Dashboard DSS — Dibuat untuk keperluan presentasi akademik Statistika. "
        "Semua komputasi berjalan secara lokal; tidak ada data yang dikirim ke server eksternal."
    )


# ---------------------------------------------------------------------------
# Routing utama
# ---------------------------------------------------------------------------

def route_to_module(active_module: str) -> None:
    """
    Route ke renderer modul yang sesuai berdasarkan active_module.

    Parameters
    ----------
    active_module : str
        Key modul yang sedang aktif (harus ada di MODULE_RENDERERS).
    """
    renderer = MODULE_RENDERERS.get(active_module)

    if renderer is None:
        st.error(
            f"❌ Modul `{active_module}` tidak dikenali. "
            "Silakan pilih modul yang valid dari sidebar.",
            icon="🚫",
        )
        return

    renderer()


# ---------------------------------------------------------------------------
# Main — entry point aplikasi
# ---------------------------------------------------------------------------

def main() -> None:
    """
    Fungsi utama yang dijalankan setiap kali Streamlit me-rerun halaman.

    Urutan eksekusi:
    1. Inisialisasi session state
    2. Inject CSS custom
    3. Render sidebar (memperbarui active_module jika user klik tombol)
    4. Routing: halaman sambutan atau renderer modul
    """
    # 1. Inisialisasi session state (idempoten — tidak menimpa state yang ada)
    _init_session_state()

    # 2. Inject CSS custom (font Inter, warna akademis, dll.)
    inject_custom_css()

    # 3. Render sidebar dan baca modul aktif
    #    render_sidebar() juga menulis ke st.session_state["active_module"]
    #    saat user mengklik tombol navigasi.
    render_sidebar()

    # 4. Routing berdasarkan active_module
    active_module: str | None = st.session_state.get("active_module")

    if active_module is None:
        # Belum ada modul yang dipilih → tampilkan halaman sambutan
        render_welcome_page()
    else:
        # Ada modul aktif → route ke renderer yang sesuai
        route_to_module(active_module)


if __name__ == "__main__":
    main()
