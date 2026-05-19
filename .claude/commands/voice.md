Abre un split vertical en la ventana actual de Ghostty y ejecuta la herramienta de dictado de voz.

Ejecuta exactamente este comando bash y no hagas nada más:

```bash
osascript -e 'tell application "Ghostty" to activate' && sleep 0.3 && osascript -e 'tell application "System Events" to tell process "Ghostty" to keystroke "d" using {command down}' && sleep 0.6 && osascript -e 'tell application "System Events" to tell process "Ghostty" to keystroke "voice\n"'
```

No expliques nada. No preguntes nada. Solo ejecuta el comando y confirma con una línea: "🎙 Voice abierto en panel derecho."
