"""Academic taxonomy and thesis chapter mappings for MentorSpec."""

from __future__ import annotations

from revisi_mudah.core.contracts import FeedbackCategory

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


CATEGORY_DESCRIPTIONS: dict[FeedbackCategory, str] = {
    FeedbackCategory.METHODOLOGY: "Perbaikan metode penelitian, alur eksperimen, atau validasi ilmiah.",
    FeedbackCategory.THEORY: "Klarifikasi landasan teori, konsep dasar, atau literatur pendukung.",
    FeedbackCategory.DATA: "Masalah pada variabel, pengumpulan data, sampling, atau kebersihan dataset.",
    FeedbackCategory.ANALYSIS: "Kritik terhadap interpretasi hasil, anomali angka, atau perbandingan komparatif.",
    FeedbackCategory.FORMULA: "Koreksi rumus matematika, notasi algoritma, atau perhitungan statistik.",
    FeedbackCategory.CITATION: "Perbaikan sitasi, referensi usang, atau ketidaksesuaian pustaka.",
    FeedbackCategory.STRUCTURE: "Sistematika penulisan, urutan subbab, atau penempatan konten.",
    FeedbackCategory.EDITORIAL: "Bahasa baku, istilah teknis, typo, atau format template skripsi.",
    FeedbackCategory.ADMINISTRATIVE: "Tenggat waktu, syarat sidang, logbook, atau prosedur jurusan.",
}


def infer_chapter_from_text(text: str) -> str | None:
    """Heuristic lookup to infer relevant thesis chapter from Indonesian supervisor remarks."""
    lower_text = text.lower()
    for chapter, keywords in CHAPTER_MAPPINGS.items():
        if any(kw in lower_text for kw in keywords):
            return chapter
    return None
