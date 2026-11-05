# MentorSpec Privacy & Data Protection Specification

## 1. Principles
Thesis supervision recordings frequently contain sensitive academic IP, unreleased research findings, institutional discussions, and personal evaluations. MentorSpec enforces a zero-silent-upload architecture.

## 2. Policy Modes
- `deny`: Strictly forbids any network transmission of audio bytes. Only local providers (e.g., local Whisper.cpp) can execute.
- `ask` (Default): Requests explicit confirmation from the user prior to initiating any cloud API call.
- `allow`: Permits cloud upload to configured providers (e.g. Gemini, Groq, OpenAI).

## 3. Metadata Sanitization
Audio file provenance records only the base filename (e.g., `bimbingan.m4a`) and strictly strips local absolute paths (e.g., `C:/Users/...`) to prevent workstation information disclosure in exported artifacts.
