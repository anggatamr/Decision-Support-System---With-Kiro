"""
Recommendation Engine — utils/recommendation.py

Mengumpulkan hasil dari semua modul Model-Driven DSS yang telah dijalankan,
mengidentifikasi konsensus alternatif terbaik, dan menghasilkan laporan teks.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Any


def collect_results(session_state: dict[str, Any]) -> dict[str, str | None]:
    """
    Kumpulkan alternatif terbaik dari semua modul yang sudah dijalankan.

    Membaca session_state dan mengekstrak alternatif optimal dari setiap
    metode yang telah menghasilkan output (non-None).

    Parameters
    ----------
    session_state : dict
        Objek session_state Streamlit (atau dict biasa untuk testing).

    Returns
    -------
    dict[str, str | None]
        Mapping nama metode → nama alternatif terbaik.
        Hanya metode yang sudah dijalankan yang dimasukkan.
    """
    results: dict[str, str | None] = {}

    alt_names: list[str] = session_state.get("alt_names", [])

    # EV — alternatif dengan Expected Value tertinggi
    if session_state.get("ev_results"):
        ev_res = session_state["ev_results"]
        best_idx = ev_res["best_ev_idx"][0]
        results["EV"] = alt_names[best_idx]

    # EOL — alternatif dengan Expected Opportunity Loss terendah
    if session_state.get("ev_results"):
        ev_res = session_state["ev_results"]
        best_idx = ev_res["best_eol_idx"][0]
        results["EOL"] = alt_names[best_idx]

    # Kriteria ketidakpastian
    if session_state.get("uncertainty_results"):
        ur = session_state["uncertainty_results"]
        results["Maximax"] = alt_names[ur["maximax_idx"][0]]
        results["Maximin"] = alt_names[ur["maximin_idx"][0]]
        results["Minimax Regret"] = alt_names[ur["minimax_regret_idx"][0]]
        results["Laplace"] = alt_names[ur["laplace_idx"][0]]

    return results


def find_consensus(results: dict[str, str]) -> tuple[list[str], float]:
    """
    Identifikasi semua alternatif yang tied untuk frekuensi tertinggi.

    Parameters
    ----------
    results : dict[str, str]
        Mapping nama metode → nama alternatif terbaik.
        Tidak boleh kosong.

    Returns
    -------
    tuple[list[str], float]
        - list berisi semua alternatif yang tied untuk frekuensi tertinggi
          (diurutkan sesuai urutan kemunculan pertama di Counter)
        - persentase konsensus: max_count / len(results) * 100
    """
    counts = Counter(results.values())
    max_count = max(counts.values())
    best = [alt for alt, cnt in counts.items() if cnt == max_count]
    pct = max_count / len(results) * 100
    return best, pct


def generate_report_text(
    results: dict[str, str | None],
    consensus: list[str],
    pct: float,
) -> str:
    """
    Buat teks laporan plain-text yang dapat diekspor.

    Laporan mencakup:
    - Timestamp ekspor
    - Tabel hasil per metode
    - Alternatif konsensus dan persentase konsensus

    Parameters
    ----------
    results : dict[str, str | None]
        Mapping nama metode → nama alternatif terbaik.
    consensus : list[str]
        Daftar alternatif yang direkomendasikan (tied best).
    pct : float
        Persentase konsensus (0–100).

    Returns
    -------
    str
        Teks laporan yang siap disalin atau diunduh.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines: list[str] = [
        "=" * 60,
        "LAPORAN REKOMENDASI DSS — DECISION SUPPORT SYSTEM",
        "=" * 60,
        f"Tanggal/Waktu Ekspor : {timestamp}",
        "",
        "-" * 60,
        "HASIL PER METODE",
        "-" * 60,
    ]

    # Lebar kolom untuk alignment
    max_method_len = max((len(m) for m in results), default=10)
    col_w = max(max_method_len, 15)

    header = f"{'Metode':<{col_w}}  {'Alternatif Terbaik'}"
    lines.append(header)
    lines.append("-" * len(header))

    for method, alt in results.items():
        alt_display = alt if alt is not None else "(belum dijalankan)"
        lines.append(f"{method:<{col_w}}  {alt_display}")

    lines.append("")
    lines.append("-" * 60)
    lines.append("REKOMENDASI KONSENSUS")
    lines.append("-" * 60)

    if len(consensus) == 1:
        lines.append(f"Alternatif yang Direkomendasikan : {consensus[0]}")
    else:
        lines.append(
            f"Alternatif yang Direkomendasikan : {', '.join(consensus)} (seri)"
        )

    lines.append(f"Tingkat Konsensus               : {pct:.1f}%")
    lines.append(
        f"  ({int(round(pct * len(results) / 100))} dari {len(results)} metode)"
    )

    lines.append("")
    lines.append("-" * 60)
    lines.append("DISCLAIMER AKADEMIS")
    lines.append("-" * 60)
    lines.append(
        "Rekomendasi ini bersifat analitis dan dihasilkan secara otomatis"
    )
    lines.append(
        "berdasarkan metode kuantitatif Teori Keputusan. Hasil harus"
    )
    lines.append(
        "dipertimbangkan bersama konteks kualitatif dan pertimbangan"
    )
    lines.append("strategis yang relevan.")
    lines.append("=" * 60)

    return "\n".join(lines)
