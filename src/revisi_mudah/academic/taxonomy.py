"""Academic taxonomy and thesis chapter mappings for Revisi Mudah."""

from __future__ import annotations

CHAPTER_MAPPINGS: dict[str, list[str]] = {
    "BAB I": [
        "pendahuluan",
        "latar belakang",
        "rumusan masalah",
        "batasan masalah",
        "tujuan penelitian",
    ],
    "BAB II": [
        "tinjauan pustaka",
        "landasan teori",
        "state of the art",
        "kajian literatur",
    ],
    "BAB III": [
        "metodologi",
        "metode penelitian",
        "arsitektur",
        "algoritma",
        "dataset",
        "rumus",
        "desain sistem",
    ],
    "BAB IV": [
        "hasil dan pembahasan",
        "evaluasi",
        "pengujian",
        "grafik",
        "tabel hasil",
        "analisis",
        "akurasi",
        "f1-score",
    ],
    "BAB V": ["kesimpulan", "saran", "limitasi"],
}
