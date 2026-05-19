# 🎙 Voice Prompt for Claude Code

**Stop typing your prompts. Just talk.**

Record your voice, transcribe it locally with Whisper (audio never leaves your Mac), clean it up automatically, and paste it straight into Claude Code — all with a single keypress.

Made with ♥ by [Guille Varela](https://github.com/guillevarela) · [Nodox Studio](https://nodox.studio)

![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform: macOS](https://img.shields.io/badge/platform-macOS-lightgrey.svg)
![Python: 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)

---

## Demo

Type `/voice` inside Claude Code — a split panel opens right alongside your chat:

```
┌──────────────────────────────────────────────────────┐
│  🎙  Voice Prompt  ·  Claude Code                    │
│  ────────────────────────────────────────────────    │
│  by Nodox Studio  ·  Ctrl+C to exit  ·  Cmd+W close │
│                                                      │
│  ►  Press Enter to record…                          │
│                                                      │
│  🔴 Recording…  press Enter to stop                 │
│                                                      │
│  ⟳  Transcribing…  [Whisper — local]               │
│                                                      │
│  🎤 Dictated:    uh can you fix the bug in the      │
│                  login form, like, you know          │
│  ✨ Optimized:   Fix the bug in the login form.     │
│                                                      │
│  1 🚀 Send to Claude Code                           │
│  2 ✨ Copy optimized prompt                         │
│  3 ✏️  Edit text                                     │
│  4 🔴 Record again                                  │
│                                                      │
│  Press a number…  1                                 │
│                                                      │
│  ✓  Sent to Claude Code.                            │
└──────────────────────────────────────────────────────┘
```

---

## What the optimizer does

No AI — just fast, deterministic local rules:

| You say | Claude receives |
|---|---|
| `"uh can you fix the bug in the login form"` | `Fix the bug in the login form.` |
| `"could you please refactor the nav component"` | `Refactor the nav component.` |
| `"can you explain me how the auth system works"` | `Explain how the auth system works.` |
| `"i need you to create an endpoint, and also add tests, and also document it"` | `1. Create an endpoint.` / `2. Add tests.` / `3. Document it.` |

Rules applied on-device, no API call, no latency:

1. **Removes filler words** — `uh`, `um`, `like`, `you know`, `eh`, `o sea`, `bueno`, `pues`…
2. **Strips polite preambles** — `can you`, `could you`, `quiero que`, `necesito que`…
3. **Normalizes Spanish verbs** — `que refactorices` → `Refactoriza`, `explicarme` → `Explica`
4. **Multi-part → numbered list** — detects `and also`, `y también`, `y además`…
5. **Capitalizes and adds end punctuation**

---

## Requirements

- macOS 13+
- Python 3.10+
- [Homebrew](https://brew.sh)
- [Claude Code](https://claude.ai/code) CLI
- [Ghostty](https://ghostty.org) terminal *(for the `/voice` split panel — other terminals work fine, just without the auto-open)*

---

## Installation

```bash
git clone https://github.com/nodox-studio/claude-voice
cd claude-voice
chmod +x install.sh
./install.sh
```

The installer walks you through everything: what gets installed, what permissions it needs, and what stays on your machine. It asks before doing anything.

### macOS permissions

You'll need to grant two permissions:
- **Microphone** — macOS will show a dialog on first recording
- **Accessibility** — needed for auto-paste into Claude Code
  → System Settings → Privacy & Security → Accessibility → enable your terminal app

---

## Usage

**From inside Claude Code (recommended):**

Type `/voice` — opens a vertical split panel in Ghostty with the tool running right alongside your chat.

**From any terminal:**
```bash
voice
```

**Workflow:**
1. Press `Enter` → starts recording
2. Speak your prompt naturally (filler words, incomplete sentences — doesn't matter)
3. Press `Enter` → stops, transcribes, and optimizes
4. Pick an action with a single keypress — no Enter needed

Press `Ctrl+C` to exit · `Cmd+W` to close the split panel

---

## Privacy

This was a design priority, not an afterthought.

| | |
|---|---|
| ✅ | **Audio never leaves your Mac** — Whisper runs entirely on-device |
| ✅ | **Temp files deleted immediately** after every transcription, even on failure |
| ✅ | **No telemetry, no analytics, no accounts** — it's just a script |
| ⚠️ | **Google fallback** — if Whisper fails with a technical error, the app falls back to Google Speech API and tells you explicitly on screen. You can remove this fallback in `voice_prompt.py` if you want hard-fail instead. |

---

## Configuration

Edit these constants near the top of `voice_prompt.py`:

```python
WHISPER_MODEL = "tiny"     # tiny (~75 MB) · base (~150 MB) · small (~500 MB)
TERMINAL_APP  = "Ghostty"  # Ghostty · iTerm2 · WezTerm · Terminal
```

`tiny` is fast and works well for short prompts. Upgrade to `base` or `small` if you need better accuracy with heavy accents or complex vocabulary.

`TERMINAL_APP` controls which terminal receives the auto-paste. The `/voice` split panel is Ghostty-only, but recording and paste work with any terminal listed above.

---

## Security

- All `subprocess` calls use argument lists — no `shell=True`, no injection risk
- Transcribed text is never passed as a shell argument — it goes through `pbcopy` (stdin) and is pasted with a simulated `Cmd+V`
- Temp audio files are deleted in a `finally` block, even if transcription fails
- No credentials, API keys, or tokens required or stored
- Auto-paste uses AppleScript keystroke simulation, which requires Accessibility permission granted explicitly by you in System Settings

---

## Contributing

Found a bug? Have an idea? PRs are very welcome.

- 🌍 **More languages** — Whisper supports 99 languages. Add your language's filler words to the optimizer in `voice_prompt.py`
- 🖥 **Other terminals** — iTerm2, WezTerm, kitty… the main thing to swap is the AppleScript split navigation
- 🐛 **Issues** → open a GitHub issue or email **somos@nodox.studio**

---

## Support

If this saves you time and you feel like it — no pressure at all:

☕ [Buy Guille a coffee](https://ko-fi.com/guillevarela)

---

## License

MIT © [Guille Varela](https://github.com/guillevarela) / [Nodox Studio](https://nodox.studio)
