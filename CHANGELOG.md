# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] — 2026-05-19

### Added
- Push-to-talk recording via Enter key — no silence detection, no timeouts
- Local transcription with [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (Whisper `tiny` model, ~75 MB, fully offline)
- Google Speech API fallback when Whisper fails — explicitly shown on screen
- Rule-based prompt optimizer (no external AI required):
  - Removes filler words in Spanish and English (`eh`, `um`, `o sea`, `like`, `you know`…)
  - Strips polite preambles (`puedes`, `can you`, `i want you to`…)
  - Normalizes Spanish subjunctive/infinitive → imperative (`que refactorices` → `Refactoriza`)
  - Strips enclitic pronouns from infinitives (`explicarme` → `Explica`)
  - Converts multi-part requests into numbered lists
  - Capitalizes and adds end punctuation
- Single-keypress action menu: send to Claude Code / copy / edit / record again
- Edit mode with pre-filled text via `prompt_toolkit`
- Auto-paste into Claude Code via AppleScript keystroke simulation
- `/voice` slash command for Claude Code — opens a vertical split panel in Ghostty
- Bilingual UI: auto-detects system locale (Spanish / English)
- First-run onboarding screen with privacy notice and microphone permission trigger
- Guided installer (`install.sh`) with Homebrew dependency management and venv setup
- Privacy-first design: audio files deleted immediately after each transcription

[1.0.0]: https://github.com/guillevarela/claude-voice/releases/tag/v1.0.0
