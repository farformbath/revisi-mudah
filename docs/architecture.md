# MentorSpec Architecture Specification

## 1. Executive Summary
MentorSpec is an agent-native audio intelligence system designed to convert academic thesis supervision recordings into structured, evidence-grounded implementation plans.

## 2. Core Tenets
1. **The Audio is the Ground Truth:** Text transcripts are machine interpretations. Raw transcripts with millisecond timestamps are permanently preserved.
2. **Privacy Gate by Default:** Audio is never uploaded to cloud providers without explicit consent.
3. **No Autonomous Manuscript Alteration:** MentorSpec produces plans, not patches. No thesis files are touched.
4. **Mandatory Human Adjudication:** AI extracts candidates (`needs_author_review`); only the author can accept tasks.

## 3. Data Contracts
- `schemas/audio-result.schema.json`
- `schemas/feedback.schema.json`
- `schemas/adjudication.schema.json`

## 4. Academic Research Skills (ARS) Boundary
MentorSpec provides an optional export layer for ARS (`ars_adapter.py`). It formats accepted tasks into the ARS Revision Roadmap schema. It does not invoke ARS Revision Mode #390 and does not generate diff patches.

## 5. Execution Boundary Verification Protocol
To empirically verify that no thesis files are altered during execution, a recursive manifest comparison must be performed in PowerShell:

```powershell
$thesisRoot = (Resolve-Path ".\thesis").Path.TrimEnd('\')

function Get-ThesisManifest {
    param([string]$Root)
    Get-ChildItem -LiteralPath $Root -File -Recurse -Force |
        ForEach-Object {
            [PSCustomObject]@{
                RelativePath = $_.FullName.Substring($Root.Length).TrimStart('\')
                SHA256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash
            }
        } |
        Sort-Object RelativePath
}

# 1. Snapshot before pilot
$before = @(Get-ThesisManifest -Root $thesisRoot)

# 2. Run MentorSpec pipeline
uv run mentorspec inspect bimbingan.m4a
uv run mentorspec transcribe bimbingan.m4a -o transcript.json --cloud-consent deny

# 3. Snapshot after pilot
$after = @(Get-ThesisManifest -Root $thesisRoot)

# 4. Compare file paths and content hashes
$diff = @(Compare-Object -ReferenceObject $before -DifferenceObject $after -Property RelativePath, SHA256)
if ($diff.Count -eq 0) {
    Write-Host "PASS: Semua file skripsi identik pada kedua snapshot." -ForegroundColor Green
} else {
    $diff | Format-Table -AutoSize
    throw "FAIL: Ditemukan perubahan pada manifest skripsi."
}
```
*Interpretation Note: Identical hashes confirm start/end state invariance. For strict write protection, configure thesis directory permissions as read-only for the agent process.*

## 6. Local Model Format Specifications
- **`whisper.cpp`:** Requires GGML format model binaries (e.g. `ggml-base.bin`).
- **`faster-whisper`:** Requires CTranslate2 format model weights.
- **Terminology Standard:** Use *"Local-only transcription with cloud upload disabled"* for `--cloud-consent deny`. Reserve *"Air-gapped"* strictly for environments with physically/logically isolated network interfaces.

## 7. Pilot Quality Evaluation Standard
1. **Word Error Rate (WER):** $WER = \frac{S + D + I}{N}$ with normalized casing and punctuation.
2. **Feedback Precision:** Proportion of extracted items that represent genuine supervisor directives.
3. **Feedback Recall:** Proportion of actual supervisor directives identified.
4. **Evidence Traceability:** Proportion of items possessing valid quotes and timestamp bounds.
