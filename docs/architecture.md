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

# 2. Run complete MentorSpec pipeline:
#    a. Inspect audio
#    b. Transcribe audio
#    c. Extract feedback candidates
#    d. Perform author adjudication
#    e. Build implementation plan (and optional ARS export)
uv run mentorspec inspect bimbingan.m4a
uv run mentorspec transcribe bimbingan.m4a -o transcript.json --cloud-consent deny
# (Proceed through adjudication and roadmap generation; do not edit thesis files concurrently)

# 3. Snapshot after complete pipeline execution
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

## 7. Pilot Quality Evaluation Standard (Operational Definitions)
1. **Word Error Rate (WER):** $\text{WER} = \frac{S + D + I}{N}$ against human-corrected reference. Normalization covers case and basic punctuation only; **do not** normalize numbers, acronyms, or methodology terms.
2. **Feedback Precision:** $\frac{\text{True Substantive Directives}}{\text{Total Extracted Feedback Items}}$.
3. **Feedback Recall:** $\frac{\text{Caught Directives}}{\text{Total Substantive Directives in Human Reference}}$.
4. **Evidence Traceability (Dual Verification):**
   - **Structural Verification:** Quote strictly matches transcript segment text and timestamp interval.
   - **Audio Verification:** Human auditor confirms supervisor utterance is audible at the designated timestamp.
