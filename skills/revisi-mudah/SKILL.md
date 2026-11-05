---
name: revisi-mudah
description: "Audio-to-Academic Implementation Planning System. Dari rekaman bimbingan menjadi rencana revisi yang terstruktur tanpa modifikasi naskah otomatis."
category: academic
risk: safe
tags: "[audio, academic, thesis, bimbingan, revisi-mudah, revision-roadmap, transcription, research-integrity]"
triggers:
  - "bimbingan"
  - "rekaman dosen"
  - "revisi-mudah"
  - "mentorspec"
  - "audio skripsi"
  - "revisi bimbingan"
  - "supervision audio"
---

# Revisi Mudah — Audio-to-Academic Implementation Planning System

**Dari rekaman bimbingan menjadi rencana revisi yang terstruktur.**

Revisi Mudah mengubah rekaman bimbingan akademik menjadi transkrip bertimestamp, ekstraksi arahan dosen berbasis bukti, dan implementation plan yang sepenuhnya berada di bawah kendali penulis.

## ⚠️ Hard Execution Boundary (Non-Negotiable)

1. **Planning Only:** Revisi Mudah menghasilkan **implementation plan saja**. Sistem **DILARANG** mengedit file naskah skripsi secara otomatis.
2. **Zero Manuscript Mutation:** Tidak ada patch LaTeX (`.tex`), Typst (`.typ`), atau dokumen Word (`.docx`) yang dibuat atau diterapkan secara otomatis.
3. **Mandatory Author Adjudication:** Semua feedback yang diekstrak berstatus awal `needs_author_review`. Hanya arahan yang disetujui (`accepted`) oleh penulis (mahasiswa) yang boleh masuk ke implementation plan. AI tidak berwenang menyetujui feedback atas inisiatif sendiri.
4. **Evidence Integrity:** Setiap kutipan (*quote*) wajib cocok secara verbatim dengan segmen transkrip bertimestamp.
5. **Strict Privacy Gate:** Tidak ada upload audio ke cloud tanpa persetujuan eksplisit pengguna (`ask`, `allow`, `deny`). Mode `deny` memblokir seluruh transmisi cloud dan mewajibkan pemrosesan lokal.

---

## Output Artifacts

Revisi Mudah menghasilkan tiga artefak resmi:

| Artefak | Format | Deskripsi |
|---|---|---|
| `transcript.json` | JSON (`audio-result.schema.json`) | Transkrip verbatim dengan timestamp milidetik dan segment ID |
| `feedback.json` | JSON (`feedback.schema.json` & `adjudication.schema.json`) | Arahan dosen dengan evidence anchor dan status keputusan penulis |
| `implementation-plan.md` | Markdown | Rencana kerja revisi terstruktur hanya dari tugas yang disetujui penulis |

---

## Workflow

```text
Audio Recording
      │
      ▼
1. Audio Inspection & Provenance (SHA-256 digest, metadata, duration)
      │
      ▼
2. Capability Routing & Privacy Gate (Local Whisper / Gemini / OMP native)
      │
      ▼
3. Verbatim Timestamped Transcription (`transcript.json`)
      │
      ▼
4. Academic Feedback Extraction (9 kategori akademik, status: needs_author_review)
      │
      ▼
5. Author Adjudication (Human-in-the-Loop: Accept / Reject / Clarify)
      │
      ▼
6. Implementation Plan Generation (`implementation-plan.md`)
      │
      ▼
7. Optional ARS Handoff Export (`ars-revision-roadmap.json`)
```

---

## MCP Tools Reference

Ketika menjalankan server MCP Revisi Mudah (`revisi-mudah-mcp`):

- **`audio_inspect(audio_path)`**: Memeriksa metadata audio (SHA-256, durasi, ukuran, tipe media).
- **`audio_transcribe(audio_path, cloud_consent)`**: Transkripsi rekaman dengan gate persetujuan privasi (`ask`, `allow`, `deny`).
- **`academic_extract_feedback(audio_result_json, raw_llm_json)`**: Ekstraksi arahan dosen dengan validasi kutipan verbatim.
- **`academic_adjudicate(feedback_json, adjudication_json)`**: Menerapkan persetujuan atau penolakan dari mahasiswa.
- **`academic_build_roadmap(audio_result_json, feedback_json)`**: Menghasilkan `implementation-plan.md` resmi untuk tugas yang disetujui saja.
- **`academic_export_ars(audio_result_json, feedback_json)`**: Ekspor data serah-terima untuk protokol Academic Research Skills (ARS).

---

## Autonomous Agent Instructions

Ketika dipanggil oleh pengguna dengan file rekaman:
1. Jalankan `audio_inspect` untuk memverifikasi integritas file dan hash.
2. Periksa kebijakan privasi sebelum melakukan transkripsi.
3. Transkripsi audio menjadi segmen verbatim bertimestamp.
4. Ekstraksi arahan ke dalam 9 kategori akademik (`methodology`, `theory`, `data`, `analysis`, `formula`, `citation`, `structure`, `editorial`, `administrative`).
5. Sajikan hasil ekstraksi kepada penulis untuk adjudikasi (*author adjudication*).
6. Setelah keputusan penulis diperoleh, buat `implementation-plan.md`.
7. Akhiri dengan deklarasi batas eksekusi: tidak ada file naskah skripsi yang diubah.
