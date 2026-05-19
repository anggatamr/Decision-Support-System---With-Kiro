"""
modules/recommendation_engine.py
---------------------------------
Modul Recommendation Engine — Rekomendasi Otomatis DSS.

Mengumpulkan hasil dari semua modul Model-Driven DSS yang telah dijalankan,
menampilkan tabel ringkasan, callout box konsensus, tombol ekspor laporan,
dan disclaimer akademis.

Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8, 9.9
"""

from __future__ import annotations


def render_recommendation_module() -> None:
    """
    Render modul Recommendation Engine secara lengkap.

    Alur:
    1. Kumpulkan hasil dari semua modul yang sudah dijalankan via collect_results()
    2. Jika belum ada modul → tampilkan pesan panduan (Req 9.8)
    3. Jika hanya 1 modul → tampilkan hasil tanpa konsensus + pesan (Req 9.4)
    4. Jika ≥2 modul → tampilkan tabel ringkasan + callout konsensus (Req 9.2, 9.3, 9.5, 9.6)
    5. Render tombol "Ekspor Laporan" (Req 9.7)
    6. Tampilkan disclaimer akademis (Req 9.9)

    Requirements: 9.1–9.9
    """
    import streamlit as st
    from utils.recommendation import collect_results, find_consensus, generate_report_text
    from ui.styles import COLORS

    # ------------------------------------------------------------------
    # Judul modul
    # ------------------------------------------------------------------
    st.title("🏆 Recommendation Engine — Rekomendasi Otomatis")
    st.markdown(
        "Modul ini merangkum hasil dari semua metode Model-Driven DSS yang telah "
        "dijalankan dan menghasilkan **rekomendasi konsensus** alternatif keputusan terbaik."
    )

    # ------------------------------------------------------------------
    # Kumpulkan hasil dari semua modul (Req 9.1)
    # ------------------------------------------------------------------
    results = collect_results(dict(st.session_state))

    # ------------------------------------------------------------------
    # Kasus 1: Belum ada modul yang dijalankan (Req 9.8)
    # ------------------------------------------------------------------
    if len(results) == 0:
        st.info(
            "ℹ️ **Belum ada modul analisis yang dijalankan.**\n\n"
            "Untuk mendapatkan rekomendasi otomatis, silakan jalankan minimal satu "
            "modul Model-Driven DSS terlebih dahulu:\n\n"
            "- 📋 **Certainty — Payoff Table** → definisikan alternatif dan payoff\n"
            "- 🎲 **Risk — EV & EOL** → analisis di bawah kondisi risiko\n"
            "- ❓ **Uncertainty — Kriteria Keputusan** → analisis tanpa probabilitas\n"
            "- ⚖️ **Utility — Fungsi Utilitas** → analisis berbasis preferensi risiko\n\n"
            "Gunakan menu navigasi di sidebar untuk memulai analisis.",
            icon="🚀",
        )
        _render_disclaimer()
        return

    # ------------------------------------------------------------------
    # Kasus 2: Hanya 1 modul yang dijalankan (Req 9.4)
    # ------------------------------------------------------------------
    if len(results) == 1:
        st.warning(
            "⚠️ **Hanya 1 modul yang telah dijalankan.**\n\n"
            "Jalankan minimal 2 modul untuk mendapatkan analisis konsensus.",
            icon="📊",
        )

        st.markdown("---")
        st.subheader("📋 Hasil Modul yang Telah Dijalankan")

        method, alt = list(results.items())[0]
        st.markdown(
            f"| Metode | Alternatif Terbaik |\n"
            f"|--------|-------------------|\n"
            f"| **{method}** | **{alt}** |"
        )

        st.info(
            "💡 Jalankan minimal **2 modul** untuk mendapatkan analisis konsensus "
            "yang membandingkan rekomendasi dari berbagai metode.",
            icon="💡",
        )

        _render_export_button(results, [], 0.0)
        _render_disclaimer()
        return

    # ------------------------------------------------------------------
    # Kasus 3: ≥2 modul dijalankan — tampilkan analisis lengkap (Req 9.2, 9.3, 9.5, 9.6)
    # ------------------------------------------------------------------
    consensus_alts, consensus_pct = find_consensus(results)

    # --- Tabel ringkasan alternatif terbaik per metode (Req 9.2) ---
    st.markdown("---")
    st.subheader("📋 Ringkasan Alternatif Terbaik per Metode")

    import pandas as pd

    summary_rows = []
    for method, alt in results.items():
        is_consensus = alt in consensus_alts
        summary_rows.append({
            "Metode": method,
            "Alternatif Terbaik": alt,
            "Konsensus": "✅" if is_consensus else "",
        })

    summary_df = pd.DataFrame(summary_rows)

    # Highlight baris yang merupakan konsensus
    def _highlight_consensus(row):
        if row["Konsensus"] == "✅":
            return [
                f"background-color: {COLORS['success']}22; "
                f"font-weight: bold; color: {COLORS['success']}"
            ] * len(row)
        return [""] * len(row)

    styled_df = summary_df.style.apply(_highlight_consensus, axis=1)
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

    # --- Callout box rekomendasi utama (Req 9.5) ---
    st.markdown("---")
    st.subheader("🏆 Rekomendasi Utama")

    # Hitung metode pendukung untuk setiap alternatif konsensus
    supporting_methods = [
        method for method, alt in results.items() if alt in consensus_alts
    ]
    n_supporting = len(supporting_methods)
    n_total = len(results)

    if len(consensus_alts) == 1:
        rec_name = consensus_alts[0]
        callout_title = f"✅ Alternatif yang Direkomendasikan: **{rec_name}**"
    else:
        rec_name = ", ".join(consensus_alts)
        callout_title = f"✅ Alternatif yang Direkomendasikan (Seri): **{rec_name}**"

    # Req 9.5 — callout box menonjol dengan nama, metode pendukung, persentase konsensus
    st.success(
        f"{callout_title}\n\n"
        f"**Metode pendukung ({n_supporting} dari {n_total}):** "
        f"{', '.join(supporting_methods)}\n\n"
        f"**Tingkat konsensus:** {consensus_pct:.1f}% "
        f"({n_supporting} dari {n_total} metode)",
    )

    # --- Visualisasi konsensus (Req 9.6) ---
    _render_consensus_chart(results, consensus_alts, consensus_pct)

    # --- Tombol ekspor laporan (Req 9.7) ---
    _render_export_button(results, consensus_alts, consensus_pct)

    # --- Disclaimer akademis (Req 9.9) ---
    _render_disclaimer()


# ---------------------------------------------------------------------------
# Helper: Visualisasi konsensus
# ---------------------------------------------------------------------------

def _render_consensus_chart(
    results: dict[str, str],
    consensus_alts: list[str],
    consensus_pct: float,
) -> None:
    """Render bar chart frekuensi rekomendasi per alternatif."""
    import streamlit as st
    import plotly.graph_objects as go
    from collections import Counter
    from ui.styles import COLORS

    counts = Counter(results.values())
    alts_sorted = sorted(counts.keys(), key=lambda a: counts[a], reverse=True)
    freq_values = [counts[a] for a in alts_sorted]
    bar_colors = [
        COLORS["success"] if a in consensus_alts else COLORS["accent"]
        for a in alts_sorted
    ]

    fig = go.Figure(go.Bar(
        x=alts_sorted,
        y=freq_values,
        marker_color=bar_colors,
        text=[f"{v} metode" for v in freq_values],
        textposition="outside",
    ))

    fig.update_layout(
        title="Frekuensi Rekomendasi per Alternatif (dari semua metode yang dijalankan)",
        xaxis_title="Alternatif Keputusan",
        yaxis_title="Jumlah Metode yang Merekomendasikan",
        template="plotly_white",
        yaxis=dict(dtick=1, range=[0, max(freq_values) + 1]),
        title_font_size=15,
    )

    st.plotly_chart(fig, use_container_width=True)

    # Tampilkan metrik konsensus (Req 9.6)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Metode Dijalankan", len(results))
    with col2:
        st.metric("Metode Mendukung Konsensus", max(Counter(results.values()).values()))
    with col3:
        st.metric("Tingkat Konsensus", f"{consensus_pct:.1f}%")


# ---------------------------------------------------------------------------
# Helper: Tombol ekspor laporan
# ---------------------------------------------------------------------------

def _render_export_button(
    results: dict[str, str],
    consensus_alts: list[str],
    consensus_pct: float,
) -> None:
    """
    Render tombol 'Ekspor Laporan' yang menghasilkan teks yang dapat disalin.
    Req 9.7
    """
    import streamlit as st
    from utils.recommendation import generate_report_text

    st.markdown("---")
    st.subheader("📄 Ekspor Laporan")

    if st.button("📋 Ekspor Laporan", type="primary", key="btn_export_report"):
        report_text = generate_report_text(results, consensus_alts, consensus_pct)
        st.code(report_text, language=None)
        st.caption(
            "💡 Klik ikon salin (🗐) di pojok kanan atas kotak teks di atas "
            "untuk menyalin laporan ke clipboard."
        )


# ---------------------------------------------------------------------------
# Helper: Disclaimer akademis
# ---------------------------------------------------------------------------

def _render_disclaimer() -> None:
    """
    Tampilkan disclaimer akademis.
    Req 9.9
    """
    import streamlit as st

    st.markdown("---")
    st.caption(
        "⚠️ **Disclaimer Akademis:** Rekomendasi yang dihasilkan oleh sistem ini "
        "bersifat analitis dan dihasilkan secara otomatis berdasarkan metode kuantitatif "
        "Teori Keputusan. Hasil analisis harus dipertimbangkan bersama dengan konteks "
        "kualitatif, pertimbangan strategis, dan faktor-faktor non-kuantitatif yang "
        "relevan. Sistem ini dirancang untuk keperluan presentasi akademik dan tidak "
        "menggantikan penilaian profesional dalam pengambilan keputusan nyata."
    )
