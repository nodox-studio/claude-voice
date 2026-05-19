#!/bin/zsh
# install.sh — Instalador de Voice Prompt para Claude Code
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$SCRIPT_DIR/.venv"
BIN="$HOME/.local/bin/voice"
COMMANDS_DIR="$HOME/.claude/commands"
MARKER="$HOME/.config/voice-prompt/.installed"

# ── Colores ────────────────────────────────────────────────────────────────────
BOLD="\033[1m"; CYAN="\033[36m"; GREEN="\033[32m"
YELLOW="\033[33m"; DIM="\033[2m"; RESET="\033[0m"

clear
echo ""
echo "${BOLD}${CYAN}🎙  Voice Prompt for Claude Code${RESET}"
echo "${DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo ""
echo "${BOLD}Qué hace esta herramienta${RESET}"
echo "  Dicta tus prompts con voz en lugar de escribirlos."
echo "  El audio se transcribe en tu Mac y se pega directamente"
echo "  en Claude Code — sin interrumpir tu flujo de trabajo."
echo ""
echo "${BOLD}Qué se va a instalar${RESET}"
echo "  • portaudio        — driver de micrófono (via Homebrew)"
echo "  • faster-whisper   — transcripción local offline (~75 MB)"
echo "  • pyaudio          — captura de audio desde el micrófono"
echo "  • SpeechRecognition — biblioteca auxiliar de audio"
echo ""
echo "${BOLD}Permisos que pedirá macOS${RESET}"
echo "  • ${YELLOW}Micrófono${RESET}      — para grabar tu voz"
echo "    → Aparecerá un diálogo de macOS la primera vez que grabes"
echo "  • ${YELLOW}Accesibilidad${RESET}  — para pegar en Claude Code automáticamente"
echo "    → Deberás habilitarlo manualmente:"
echo "    ${DIM}Sistema → Privacidad y seguridad → Accesibilidad${RESET}"
echo ""
echo "${BOLD}Privacidad${RESET}"
echo "  ${GREEN}✓${RESET}  Audio procesado 100% en local — Whisper corre en tu Mac"
echo "  ${GREEN}✓${RESET}  Los archivos de audio se eliminan inmediatamente tras transcribir"
echo "  ${GREEN}✓${RESET}  Sin telemetría, sin analytics, sin datos enviados a ningún servidor"
echo "  ${YELLOW}⚠${RESET}  Si Whisper falla (error técnico), se usa Google Speech como fallback"
echo "      En ese caso el audio se envía a Google — la herramienta te lo indica claramente"
echo ""
echo "${DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
printf "${BOLD}¿Continuar con la instalación?${RESET} [S/n] "
read -r confirm
confirm="${confirm:-S}"
if [[ ! "$confirm" =~ ^[SsYy]$ ]]; then
  echo "\nInstalación cancelada."
  exit 0
fi

echo ""

# ── 1. Verificar Python ────────────────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
  echo "✗  Necesitas Python 3.10+. Instálalo con:"
  echo "   brew install python"
  exit 1
fi

PY_VERSION=$(python3 -c 'import sys; print(sys.version_info.minor)')
if (( PY_VERSION < 10 )); then
  echo "✗  Python 3.10+ requerido (tienes 3.${PY_VERSION}). Actualiza con: brew upgrade python"
  exit 1
fi

# ── 2. Instalar portaudio ──────────────────────────────────────────────────────
if ! brew list portaudio &>/dev/null 2>&1; then
  echo "⟳  Instalando portaudio…"
  brew install portaudio
  echo "✓  portaudio instalado"
else
  echo "✓  portaudio ya instalado"
fi

# ── 3. Crear entorno virtual ───────────────────────────────────────────────────
echo "⟳  Creando entorno virtual Python…"
python3 -m venv "$VENV"
echo "✓  Entorno virtual creado"

# ── 4. Instalar dependencias Python ───────────────────────────────────────────
echo "⟳  Instalando dependencias Python (puede tardar 1-2 min)…"
"$VENV/bin/pip" install --quiet --upgrade pip
"$VENV/bin/pip" install --quiet -r "$SCRIPT_DIR/requirements.txt"
echo "✓  Dependencias instaladas"

# ── 5. Instalar comando `voice` ────────────────────────────────────────────────
echo "⟳  Instalando comando voice…"
mkdir -p "$HOME/.local/bin"
cat > "$BIN" << VOICESCRIPT
#!/bin/zsh
"$VENV/bin/python3" "$SCRIPT_DIR/voice_prompt.py" "\$@"
exit
VOICESCRIPT
chmod +x "$BIN"
echo "✓  Comando voice disponible en ~/.local/bin/voice"

# ── 6. Instalar slash command /voice ──────────────────────────────────────────
if [ -d "$COMMANDS_DIR" ]; then
  cp "$SCRIPT_DIR/.claude/commands/voice.md" "$COMMANDS_DIR/voice.md"
  echo "✓  Slash command /voice instalado en Claude Code"
fi

# ── 7. Marcar primera instalación ─────────────────────────────────────────────
mkdir -p "$(dirname "$MARKER")"
date +%Y-%m-%d > "$MARKER"

# ── Resumen final ─────────────────────────────────────────────────────────────
echo ""
echo "${DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo "${GREEN}${BOLD}✓  Instalación completa${RESET}"
echo ""
echo "${BOLD}Cómo usar${RESET}"
echo "  voice      → desde cualquier terminal"
echo "  /voice     → desde Claude Code (abre panel lateral automático)"
echo ""
echo "${BOLD}Antes de usar por primera vez${RESET}"
echo "  1. Ejecuta ${BOLD}voice${RESET} — macOS pedirá permiso de ${YELLOW}micrófono${RESET}"
echo "  2. Ve a ${BOLD}Sistema → Privacidad y seguridad → Accesibilidad${RESET}"
echo "     y activa tu terminal para habilitar el envío automático a Claude Code"
echo ""
echo "${DIM}El modelo Whisper (~75 MB) se descargará la primera vez que grabes.${RESET}"
echo ""
