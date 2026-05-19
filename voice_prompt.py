#!/usr/bin/env python3
"""
voice_prompt — Voice dictation for Claude Code
Graba → Transcribe (Whisper local) → Optimiza → Envía al chat

Usage: python voice_prompt.py
"""

import sys
import os
import re
import subprocess
import tempfile
import threading
import wave
import locale
import datetime

# ── Auto-activate venv if it exists ──────────────────────────────────────────
_VENV_PYTHON = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv", "bin", "python3")
if os.path.exists(_VENV_PYTHON) and sys.executable != _VENV_PYTHON:
    os.execv(_VENV_PYTHON, [_VENV_PYTHON] + sys.argv)

# Suppress Hugging Face Hub warnings (Whisper models are public, no token needed)
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
import warnings
warnings.filterwarnings("ignore", message=".*HF Hub.*")
warnings.filterwarnings("ignore", message=".*huggingface.*")

# ── ANSI colors ───────────────────────────────────────────────────────────────
RED    = "\033[31m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
BLUE   = "\033[34m"
CYAN   = "\033[36m"
GRAY   = "\033[90m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"

# ── Language detection ────────────────────────────────────────────────────────
def _detect_lang() -> str:
    raw = os.environ.get("LANG", "") or (locale.getdefaultlocale()[0] or "")
    return "es" if raw.lower().startswith("es") else "en"

LANG = _detect_lang()

# ── i18n strings ──────────────────────────────────────────────────────────────
_S = {
    "en": {
        # Header
        "header":           "🎙  Voice Prompt  ·  Claude Code",
        "header_sub":       "by Nodox Studio  ·  Ctrl+C to exit  ·  Cmd+W to close panel",
        # Recording
        "press_enter":      "Press Enter to record…",
        "recording":        f"🔴 Recording…  press {BOLD}Enter{RESET} to stop",
        "transcribing":     "⟳  Transcribing…",
        "engine_whisper":   "[Whisper — local]",
        "engine_google":    "[Google Speech — audio sent to Google]",
        "engine_fail":      "Whisper failed ({err}), falling back to Google…",
        "no_audio":         "✗  No audio detected. Try again.",
        "no_speech":        "✗  Could not understand the audio. Try again.",
        # Menu
        "dictated":         "🎤 Dictated",
        "optimized":        "✨ Optimized",
        "menu_send":        "🚀 Send to Claude Code",
        "menu_copy":        "✨ Copy optimized prompt",
        "menu_edit":        "✏️  Edit text",
        "menu_record":      "🔴 Record again",
        "menu_prompt":      "Press a number…",
        "edit_prompt":      "  ✏️  ",
        # Feedback
        "sent":             "✓  Sent to Claude Code.",
        "copied":           "✓  Copied. Paste with Cmd+V.",
        "bye":              "👋 See you! · Cmd+W to close the panel",
        # Loading model
        "loading_model":    "⟳  Loading Whisper model ({model})…",
        "model_ready":      "ready",
        # First run
        "welcome_title":    "Welcome — first run setup",
        "welcome_what":     "This tool transcribes your voice and sends the text to Claude Code.",
        "privacy_title":    "Privacy",
        "privacy_local":    f"  {GREEN}✓{RESET}  Audio processed 100% locally by Whisper — never leaves your Mac",
        "privacy_delete":   f"  {GREEN}✓{RESET}  Temporary audio files deleted immediately after each transcription",
        "privacy_no_tele":  f"  {GREEN}✓{RESET}  No telemetry, no analytics, no accounts",
        "privacy_google":   f"  {YELLOW}⚠{RESET}  If Whisper fails, Google Speech API is used as fallback\n"
                            f"      {DIM}The app will tell you explicitly when that happens{RESET}",
        "perms_title":      "Permissions needed",
        "perms_mic":        f"  • {YELLOW}Microphone{RESET}     — macOS will show a dialog on first recording",
        "perms_access":     f"  • {YELLOW}Accessibility{RESET}  — needed to auto-paste into Claude Code\n"
                            f"    {DIM}System Settings → Privacy & Security → Accessibility → enable your terminal{RESET}",
        "support_title":    "If you find it useful",
        "support_star":     f"  ⭐  Star the repo      → {DIM}github.com/nodox-studio/claude-voice{RESET}",
        "support_coffee":   f"  ☕  Buy Guille a coffee → {DIM}ko-fi.com/guillevarela{RESET}",
        "support_email":    f"  📧  Questions & support → {DIM}somos@nodox.studio{RESET}",
        "license":          f"MIT License  ·  © Guille Varela / Nodox Studio",
        "press_continue":   "Press Enter to continue…",
        "checking_mic":     "⟳  Checking microphone access…",
        "mic_ok":           f"  {GREEN}✓  Access granted{RESET}",
        "mic_pending":      f"  {YELLOW}⚠  Permission pending — macOS may have shown a dialog{RESET}",
        "model_note":       "The Whisper model (~75 MB) will download the first time you record.",
        "press_start":      "Press Enter to start…",
    },
    "es": {
        # Header
        "header":           "🎙  Voice Prompt  ·  Claude Code",
        "header_sub":       "por Nodox Studio  ·  Ctrl+C para salir  ·  Cmd+W para cerrar",
        # Recording
        "press_enter":      "Presiona Enter para grabar…",
        "recording":        f"🔴 Grabando…  pulsa {BOLD}Enter{RESET} para terminar",
        "transcribing":     "⟳  Transcribiendo…",
        "engine_whisper":   "[Whisper — local]",
        "engine_google":    "[Google Speech — audio enviado a Google]",
        "engine_fail":      "Whisper falló ({err}), usando Google como fallback…",
        "no_audio":         "✗  No se detectó audio. Intenta de nuevo.",
        "no_speech":        "✗  No se entendió el audio. Intenta de nuevo.",
        # Menu
        "dictated":         "🎤 Dictado",
        "optimized":        "✨ Optimizado",
        "menu_send":        "🚀 Enviar a Claude Code",
        "menu_copy":        "✨ Copiar prompt optimizado",
        "menu_edit":        "✏️  Editar texto",
        "menu_record":      "🔴 Grabar de nuevo",
        "menu_prompt":      "Pulsa un número…",
        "edit_prompt":      "  ✏️  ",
        # Feedback
        "sent":             "✓  Enviado a Claude Code.",
        "copied":           "✓  Copiado. Pega con Cmd+V.",
        "bye":              "👋 Hasta luego! · Cmd+W para cerrar el panel",
        # Loading model
        "loading_model":    "⟳  Cargando modelo Whisper ({model})…",
        "model_ready":      "listo",
        # First run
        "welcome_title":    "Bienvenido — configuración inicial",
        "welcome_what":     "Esta herramienta transcribe tu voz y envía el texto a Claude Code.",
        "privacy_title":    "Privacidad",
        "privacy_local":    f"  {GREEN}✓{RESET}  Audio procesado 100% en local por Whisper — no sale de tu Mac",
        "privacy_delete":   f"  {GREEN}✓{RESET}  Archivos de audio eliminados inmediatamente tras cada transcripción",
        "privacy_no_tele":  f"  {GREEN}✓{RESET}  Sin telemetría, sin analytics, sin cuentas",
        "privacy_google":   f"  {YELLOW}⚠{RESET}  Si Whisper falla, se usa Google Speech API como fallback\n"
                            f"      {DIM}La app te lo indica explícitamente cuando ocurre{RESET}",
        "perms_title":      "Permisos necesarios",
        "perms_mic":        f"  • {YELLOW}Micrófono{RESET}     — macOS mostrará un diálogo la primera vez",
        "perms_access":     f"  • {YELLOW}Accesibilidad{RESET} — para pegar en Claude Code automáticamente\n"
                            f"    {DIM}Sistema → Privacidad y seguridad → Accesibilidad → activa tu terminal{RESET}",
        "support_title":    "Si te resulta útil",
        "support_star":     f"  ⭐  Deja una estrella en el repo → {DIM}github.com/nodox-studio/claude-voice{RESET}",
        "support_coffee":   f"  ☕  Invita a Guille a un café    → {DIM}ko-fi.com/guillevarela{RESET}",
        "support_email":    f"  📧  Dudas y soporte              → {DIM}somos@nodox.studio{RESET}",
        "license":          f"Licencia MIT  ·  © Guille Varela / Nodox Studio",
        "press_continue":   "Pulsa Enter para continuar…",
        "checking_mic":     "⟳  Comprobando acceso al micrófono…",
        "mic_ok":           f"  {GREEN}✓  Acceso concedido{RESET}",
        "mic_pending":      f"  {YELLOW}⚠  Permiso pendiente — macOS puede haber mostrado un diálogo{RESET}",
        "model_note":       "El modelo Whisper (~75 MB) se descargará la primera vez que grabes.",
        "press_start":      "Pulsa Enter para empezar…",
    },
}

def t(key: str, **kwargs) -> str:
    """Returns the translated string for the current language."""
    s = _S[LANG].get(key, _S["en"].get(key, key))
    return s.format(**kwargs) if kwargs else s


# ── Config ────────────────────────────────────────────────────────────────────
WHISPER_MODEL  = "tiny"   # tiny (~75MB) | base (~150MB) | small (~500MB)
AUDIO_RATE     = 16000
AUDIO_CHANNELS = 1
AUDIO_CHUNK    = 1024
_MARKER        = os.path.expanduser("~/.config/voice-prompt/.installed")

# ── Optimizer rules ───────────────────────────────────────────────────────────

# Muletillas ES + EN
FILLERS = [
    r'\beh+\b', r'\bumm*\b', r'\bmmm*\b', r'\bo sea\b', r'\bo sea que\b',
    r'\bbueno\b', r'\bpues\b', r'\bveamos\b', r'\bente+nces\b', r'\bvale\b',
    r'\bya sabes\b', r'\bla verdad\b', r'\ben plan\b', r'\btipo que\b',
    r'\bcomo que\b', r'\ba ver\b', r'\bes que\b', r'\bclaro\b',
    r'\bum+\b', r'\buh+\b', r'\bahh*\b', r'\blike\b', r'\byou know\b',
    r'\bbasically\b', r'\bliterally\b', r'\bi mean\b', r'\bright\b',
]

# Frases de contexto redundante
REDUNDANT = [
    r',?\s*como (siempre|de costumbre)\b',
    r',?\s*como hemos (hablado|visto|dicho|comentado)\b',
    r',?\s*en el (archivo|fichero|código) que (ya )?tienes (abierto|cargado)\b',
    r',?\s*que (ya )?conoces\b',
    r',?\s*as (you know|always|we discussed|mentioned|usual)\b',
    r',?\s*like (we|I) (talked|discussed|mentioned)\b',
    r',?\s*in the (file|code) (you already have|open)\b',
]

# Preambles a eliminar (ES + EN)
FLUFF_START = [
    r'^(puedes|podrías|puedes por favor|podrías por favor|podría)\s+',
    r'^(quiero que|necesito que|me gustaría que|quisiera que|quería que)\s+',
    r'^(por favor[,\s]+)?ayúdame (a|con)\s+',
    r'^haz(me)? el favor de\s+',
    r'^(te pido que|te necesito para que)\s+',
    r'^por favor[,\s]+',
    r'^(can you|could you|would you mind|would you please|please)\s+',
    r'^(i want you to|i need you to|i\'d like you to|i\'d like for you to)\s+',
    r'^(i\'d like|i want|i need|i\'m looking for you to)\s+',
    r'^(help me (to|with)?)\s+',
    r'^please[,\s]+',
]

# Tabla de verbos ES: subjuntivo/infinitivo → imperativo tú
# Se aplica DESPUÉS de eliminar el preamble (ej: "que refactorices" → "Refactoriza")
ES_VERB_MAP = [
    (r'^(que )?(refactorices|refactorizar)\b',       'Refactoriza'),
    (r'^(que )?(crees|crear)\b',                      'Crea'),
    (r'^(que )?(añadas|añadir|agregues|agregar)\b',   'Añade'),
    (r'^(que )?(elimines|eliminar|borres|borrar|quites|quitar)\b', 'Elimina'),
    (r'^(que )?(corrijas|corregir|arregles|arreglar|soluciones|solucionar)\b', 'Corrige'),
    (r'^(que )?(expliques|explicar)\b',               'Explica'),
    (r'^(que )?(implementes|implementar)\b',          'Implementa'),
    (r'^(que )?(escribas|escribir)\b',                'Escribe'),
    (r'^(que )?(generes|generar)\b',                  'Genera'),
    (r'^(que )?(revises|revisar|analices|analizar)\b', 'Revisa'),
    (r'^(que )?(conviertas|convertir|transformes|transformar)\b', 'Convierte'),
    (r'^(que )?(optimices|optimizar|mejores|mejorar)\b', 'Optimiza'),
    (r'^(que )?(modifiques|modificar|cambies|cambiar)\b', 'Modifica'),
    (r'^(que )?(documentes|documentar|comentes|comentar)\b', 'Documenta'),
    (r'^(que )?(muevas|mover)\b',                    'Mueve'),
    (r'^(que )?(renombres|renombrar)\b',              'Renombra'),
    (r'^(que )?(pruebes|probar|testees|testear)\b',   'Prueba'),
    (r'^(que )?(busques|buscar|encuentres|encontrar)\b', 'Busca'),
    (r'^(que )?(listes|listar|muestres|mostrar)\b',  'Muestra'),
    (r'^(que )?(hagas|hacer)\b',                     'Haz'),
    (r'^(que )?(dividas|dividir|separes|separar)\b', 'Divide'),
    (r'^(que )?(combines|combinar|unas|unir|juntes|juntar)\b', 'Combina'),
    (r'^(que )?(actualices|actualizar)\b',            'Actualiza'),
    (r'^(que )?(compruebes|comprobar|verifiques|verificar)\b', 'Verifica'),
    (r'^(que )?(limpies|limpiar)\b',                 'Limpia'),
    (r'^(que )?(configures|configurar|ajustes|ajustar)\b', 'Configura'),
    (r'^(que )?(instales|instalar)\b',               'Instala'),
    (r'^(que )?(despliegues|desplegar|subas|subir)\b', 'Despliega'),
    (r'^(que )?(dividas|dividir|partas|partir)\b',   'Divide'),
    (r'^(que )?(extraigas|extraer|saques|sacar)\b',  'Extrae'),
    (r'^(que )?(migres|migrar)\b',                   'Migra'),
    (r'^(que )?(conectes|conectar|integres|integrar)\b', 'Conecta'),
]

# Conectores de multi-parte (non-capturing: re.split no incluye el separador en el output)
_MULTI_SPLIT = re.compile(
    r'\s*[,;]\s*(?:y además|y también|y luego|y después|además)\s*'
    r'|\s+(?:and also|and then|additionally|furthermore|also)\s+',
    re.IGNORECASE
)

# Pronombres enclíticos pegados a infinitivos: "explicarme" → "explicar"
_ENCLITIC_RE = re.compile(
    r'^((?:que )?[a-záéíóúü]*?(?:ar|er|ir))(me|te|se|le|lo|la|nos|os|les|los|las)\b',
    re.IGNORECASE
)


def _strip_enclitic(text: str) -> str:
    return _ENCLITIC_RE.sub(r'\1', text)


def _apply_verb_map(text: str) -> str:
    """Strip enclitic pronouns then normalize ES verb form → imperative."""
    text = _strip_enclitic(text)
    for pattern, replacement in ES_VERB_MAP:
        m = re.match(pattern, text, flags=re.IGNORECASE)
        if m:
            return replacement + text[m.end():]
    return text

# Palabras que indican pregunta
_QUESTION_STARTERS = (
    "qué", "cómo", "cuándo", "dónde", "por qué", "cuál", "cuáles", "quién",
    "what", "how", "when", "where", "why", "which", "who",
    "is ", "are ", "does ", "do ", "can ", "could ", "should ", "would ",
)

_whisper_model = None


# ── Core functions ─────────────────────────────────────────────────────────────

def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel
        print(f"{BLUE}{t('loading_model', model=WHISPER_MODEL)}{RESET}", end="", flush=True)
        _whisper_model = WhisperModel(WHISPER_MODEL, device="auto", compute_type="int8")
        print(f"  {GREEN}{t('model_ready')}{RESET}")
    return _whisper_model


def record_audio() -> str | None:
    """Records mic until Enter is pressed. Returns path to a temp WAV file."""
    import pyaudio

    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=AUDIO_CHANNELS,
        rate=AUDIO_RATE,
        input=True,
        frames_per_buffer=AUDIO_CHUNK,
    )

    frames = []
    stop_flag = threading.Event()

    def _capture():
        while not stop_flag.is_set():
            data = stream.read(AUDIO_CHUNK, exception_on_overflow=False)
            frames.append(data)

    thread = threading.Thread(target=_capture, daemon=True)
    thread.start()

    print(f"\n{YELLOW}{t('recording')}{RESET}")
    input()

    stop_flag.set()
    thread.join(timeout=1)
    stream.stop_stream()
    stream.close()
    p.terminate()

    if not frames:
        return None

    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp.close()
    with wave.open(tmp.name, "wb") as wf:
        wf.setnchannels(AUDIO_CHANNELS)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(AUDIO_RATE)
        wf.writeframes(b"".join(frames))
    return tmp.name


def transcribe(wav_path: str) -> str | None:
    """Transcribes WAV file. Whisper local first, Google as fallback."""
    print(f"{BLUE}{t('transcribing')}{RESET}", end="", flush=True)

    try:
        model = get_whisper_model()
        segments, _ = model.transcribe(wav_path, language="es", beam_size=1)
        text = " ".join(seg.text.strip() for seg in segments).strip()
        if text:
            print(f"  {GRAY}{t('engine_whisper')}{RESET}")
            return text
    except Exception as e:
        print(f"\n{YELLOW}{t('engine_fail', err=e)}{RESET}")

    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio = r.record(source)
        text = r.recognize_google(audio, language="es-ES")
        print(f"  {GRAY}{t('engine_google')}{RESET}")
        return text
    except Exception:
        print()
        return None


def optimize(text: str) -> str:
    """
    Structures dictated text into a clean, direct prompt.

    Pipeline:
    1. Remove redundant context phrases
    2. Remove filler words
    3. Strip polite preambles ("can you", "quiero que"…)
    4. Normalize ES subjunctive/infinitive → imperative (tú)
    5. Detect and format multi-part requests as numbered list
    6. Fix capitalization and end punctuation
    """
    result = text.strip()

    # 1. Remove redundant context
    for pattern in REDUNDANT:
        result = re.sub(pattern, '', result, flags=re.IGNORECASE)

    # 2. Remove fillers
    for pattern in FILLERS:
        result = re.sub(pattern, ' ', result, flags=re.IGNORECASE)

    # Clean spaces before preamble matching (fillers leave gaps that break ^ anchor)
    result = re.sub(r'\s+', ' ', result).strip()

    # 3. Strip preamble
    for pattern in FLUFF_START:
        m = re.match(pattern, result, flags=re.IGNORECASE)
        if m:
            result = result[m.end():]
            break

    # 4. Strip enclitic pronouns + normalize ES verb forms → imperative
    result = _apply_verb_map(result)

    result = re.sub(r'\s+', ' ', result).strip()

    # 5. Multi-part: split and format as numbered list if 3+ parts
    parts = [p.strip() for p in _MULTI_SPLIT.split(result) if p and p.strip()]
    if len(parts) >= 3:
        def _fmt(p: str) -> str:
            p = _apply_verb_map(p.rstrip('.').strip())
            return (p[0].upper() + p[1:]) if p else p
        return '\n'.join(f'{i + 1}. {_fmt(p)}.' for i, p in enumerate(parts))

    # 6. Capitalize + punctuation
    if result:
        result = result[0].upper() + result[1:]

    if result and result[-1] not in '.?!':
        result += '?' if result.lower().startswith(_QUESTION_STARTERS) else '.'

    return result


def copy_to_clipboard(text: str) -> None:
    subprocess.run(["pbcopy"], input=text.encode("utf-8"), check=True)


def send_to_claude(text: str) -> None:
    """Copies text and pastes it into the left Ghostty split (Claude Code)."""
    copy_to_clipboard(text)
    subprocess.run([
        "osascript",
        "-e", 'tell application "Ghostty" to activate',
        "-e", 'tell application "System Events" to tell process "Ghostty" to key code 123 using {command down, option down}',
        "-e", 'delay 0.3',
        "-e", 'tell application "System Events" to tell process "Ghostty" to keystroke "v" using {command down}',
    ])


def read_key() -> str:
    """Reads a single keypress without waiting for Enter."""
    import tty, termios
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


# ── UI ─────────────────────────────────────────────────────────────────────────

def print_header() -> None:
    print("\033[2J\033[H", end="", flush=True)
    print(f"\n{BOLD}{CYAN}{t('header')}{RESET}")
    print(f"{DIM}{'─' * 44}{RESET}")
    print(f"{DIM}{t('header_sub')}{RESET}\n")


def show_menu(dictated: str, optimized: str) -> None:
    print(f"\n  {GRAY}{t('dictated')}:    {dictated}{RESET}")
    print(f"  {CYAN}{t('optimized')}: {BOLD}{optimized}{RESET}\n")
    print(f"  {BOLD}1{RESET} {t('menu_send')}")
    print(f"  {BOLD}2{RESET} {t('menu_copy')}")
    print(f"  {BOLD}3{RESET} {t('menu_edit')}")
    print(f"  {BOLD}4{RESET} {t('menu_record')}")
    print(f"\n  {DIM}{t('menu_prompt')}{RESET}", end="", flush=True)


def first_run_welcome() -> None:
    print("\033[2J\033[H", end="", flush=True)
    print(f"\n{BOLD}{CYAN}🎙  Voice Prompt for Claude Code{RESET}")
    print(f"{DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"{DIM}by Guille Varela · Nodox Studio · nodox.studio{RESET}\n")

    print(f"{BOLD}{t('welcome_title')}{RESET}\n")
    print(f"  {t('welcome_what')}")

    print(f"\n{BOLD}{t('privacy_title')}{RESET}")
    print(t("privacy_local"))
    print(t("privacy_delete"))
    print(t("privacy_no_tele"))
    print(t("privacy_google"))

    print(f"\n{BOLD}{t('perms_title')}{RESET}")
    print(t("perms_mic"))
    print(t("perms_access"))

    print(f"\n{BOLD}{t('support_title')}{RESET}")
    print(t("support_star"))
    print(t("support_coffee"))
    print(t("support_email"))

    print(f"\n{DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"{DIM}{t('license')}{RESET}\n")

    print(f"  {t('press_continue')}", end="", flush=True)
    input()

    # Trigger microphone permission dialog
    print(f"\n{BLUE}{t('checking_mic')}{RESET}", end="", flush=True)
    try:
        import pyaudio
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000,
                        input=True, frames_per_buffer=1024)
        stream.read(1024, exception_on_overflow=False)
        stream.stop_stream()
        stream.close()
        p.terminate()
        print(t("mic_ok"))
    except Exception:
        print(t("mic_pending"))

    os.makedirs(os.path.dirname(_MARKER), exist_ok=True)
    with open(_MARKER, "w") as f:
        f.write(datetime.date.today().isoformat())

    print(f"\n{DIM}{t('model_note')}{RESET}\n")
    print(f"  {t('press_start')}", end="", flush=True)
    input()


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    from prompt_toolkit import prompt as pt_prompt

    if not os.path.exists(_MARKER):
        first_run_welcome()

    print_header()
    session_count = 0

    while True:
        try:
            if session_count > 0:
                print(f"\n{DIM}{'─' * 44}{RESET}")

            print(f"  {GREEN}►{RESET}  {t('press_enter')}", end="", flush=True)
            input()

            wav_path = record_audio()
            if not wav_path:
                print(f"{RED}{t('no_audio')}{RESET}")
                continue

            try:
                raw = transcribe(wav_path)
            finally:
                os.unlink(wav_path)

            if not raw:
                print(f"{RED}{t('no_speech')}{RESET}")
                continue

            session_count += 1
            optimized = optimize(raw)

            while True:
                show_menu(raw, optimized)
                key = read_key()
                print(f" {key}\n")
                action = {"1": "send", "2": "copy", "3": "edit", "4": "new"}.get(key, "new")

                if action == "send":
                    send_to_claude(optimized)
                    print(f"\n  {GREEN}{t('sent')}{RESET}")
                    break
                elif action == "copy":
                    copy_to_clipboard(optimized)
                    print(f"\n  {GREEN}{t('copied')}{RESET}")
                    break
                elif action == "edit":
                    result = pt_prompt(t("edit_prompt"), default=optimized).strip()
                    if result:
                        optimized = result
                    print()
                else:
                    break

        except KeyboardInterrupt:
            print(f"\n\n  {DIM}{t('bye')}{RESET}\n")
            sys.exit(0)


if __name__ == "__main__":
    main()
