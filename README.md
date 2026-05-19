# 🎙 Voice Prompt for Claude Code

**Stop typing your prompts. Just talk.**

Record your voice, transcribe it locally with Whisper (audio never leaves your Mac), clean it up automatically, and send it straight to Claude Code — all with a single keypress.

Made with ♥ by [Guille Varela](https://github.com/guillevarela) · [Nodox Studio](https://nodox.studio)

![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform: macOS](https://img.shields.io/badge/platform-macOS-lightgrey.svg)
![Python: 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)

---

## What it does

You open a split panel in Ghostty, press `Enter` to record, speak your prompt, press `Enter` again to stop — and the tool transcribes, removes filler words, and sends the optimized text directly to your Claude Code input. No copy-paste. No switching windows. No losing focus.

```
  1 🚀 Send to Claude Code     ← pastes directly, hands-free
  2 ✨ Copy optimized prompt   ← to clipboard if you prefer
  3 ✏️  Edit before sending     ← tweak the text first
  4 🔴 Record again
```

## Requirements

- macOS 13+
- Python 3.10+
- [Homebrew](https://brew.sh)
- [Claude Code](https://claude.ai/code) CLI
- [Ghostty](https://ghostty.org) terminal *(for the `/voice` auto split panel — other terminals work fine, just without the auto-open)*

## Installation

```bash
git clone https://github.com/guillevarela/claude-voice
cd claude-voice
chmod +x install.sh
./install.sh
```

The installer walks you through everything: what gets installed, what permissions it needs, and what stays on your machine. It will ask before doing anything.

### macOS permissions

You'll need to grant two permissions (macOS will prompt you):
- **Microphone** — to record your voice *(macOS shows a dialog on first use)*
- **Accessibility** — needed for auto-paste into Claude Code
  → System Settings → Privacy & Security → Accessibility → enable your terminal app

## Usage

**From any terminal:**
```bash
voice
```

**From inside Claude Code (recommended):**

Type `/voice` — it opens a vertical split panel in Ghostty with the tool running right alongside your chat.

**Workflow:**
1. Press `Enter` → starts recording
2. Speak your prompt naturally (filler words, incomplete sentences — doesn't matter)
3. Press `Enter` → stops, transcribes, and optimizes
4. Pick an action with a single keypress — no Enter needed

Press `Ctrl+C` to exit · `Cmd+W` to close the split panel

## Privacy

This was a design priority, not an afterthought.

| | |
|---|---|
| ✅ | **Audio never leaves your Mac** — Whisper runs entirely on-device |
| ✅ | **Temp files deleted immediately** after every transcription, even if it fails |
| ✅ | **No telemetry, no analytics, no accounts** — it's just a script |
| ⚠️ | **Google fallback** — if Whisper fails, the app falls back to Google Speech API and tells you explicitly on screen. You can disable this in `voice_prompt.py` if you want hard-fail instead. |

## Configuration

Edit these constants at the top of `voice_prompt.py`:

```python
WHISPER_MODEL = "tiny"   # tiny (~75 MB) · base (~150 MB) · small (~500 MB)
```

`tiny` is fast and great for short prompts. Go up to `base` or `small` if you need better accuracy with heavy accents or complex vocabulary.

## How the optimizer works

No AI involved here — just deterministic text rules applied locally:

1. **Removes filler words** — *"uh"*, *"um"*, *"like"*, *"you know"*, *"eh"*, *"o sea"*, *"bueno"*…
2. **Converts polite openers to direct imperatives** — *"Can you make the button bigger?"* → *"Make the button bigger."*
3. **Capitalizes and adds end punctuation**

## Security

- All `subprocess` calls use argument lists — no `shell=True`, no injection risk
- Temp audio files are deleted in a `finally` block, even if transcription fails
- No credentials, API keys, or tokens required or stored
- Auto-paste uses AppleScript keystroke simulation, which requires explicit Accessibility permission granted by you in System Settings

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
