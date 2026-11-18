#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
traducir_smali.py
-----------------
Algunos textos de la app no están en strings.xml sino escritos directamente
en el código (botones del partido, avisos, el HUD de rendimiento...). Este
script los reemplaza en los archivos .smali del APK descompilado.

Solo se tocan textos que se MUESTRAN en pantalla (setText, Toast, diálogos).
No se tocan los textos que la app usa para comparar mensajes internos del
motor (por ejemplo "GPU lacks", "No Vulkan", "Failed to"), porque cambiarlos
rompería la detección de errores.

Uso:
    python3 -I scripts/traducir_smali.py <carpeta_apktool>
"""
import sys

# (archivo relativo, texto original exacto en smali, texto en español)
# En smali, "·", "■", etc. van escritos como secuencias de escape.
REEMPLAZOS = [
    # --- Botones dentro del partido (GameActivity) ---
    ("smali/com/pes2017/recomp/GameActivity.smali", '"\\u25a0 STOP REC"', '"\\u25a0 DETENER GRAB."'),
    ("smali/com/pes2017/recomp/GameActivity.smali", '"REC MACRO"', '"GRABAR MACRO"'),
    ("smali/com/pes2017/recomp/GameActivity.smali", '"CAPTURE"', '"CAPTURA"'),
    ("smali/com/pes2017/recomp/GameActivity.smali", '"\\u25a0 STOP 0:00"', '"\\u25a0 DETENER 0:00"'),
    ("smali/S/b0.smali", '"\\u25a0 STOP %d:%02d"', '"\\u25a0 DETENER %d:%02d"'),
    # --- Indicador de rendimiento (HUD) ---
    ("smali/com/pes2017/recomp/GameActivity.smali", '"PES 2017 ANDROID \\u00b7 PERFORMANCE"', '"PES 2017 ANDROID \\u00b7 RENDIMIENTO"'),
    ("smali/com/pes2017/recomp/GameActivity.smali", '"  [\\u25b2 Close]"', '"  [\\u25b2 Cerrar]"'),
    # --- Aviso de ahorro de batería ---
    ("smali/com/pes2017/recomp/GameActivity.smali",
     '"Battery Saver is on: the game runs slower and less smoothly. Turn it off for 60 fps."',
     '"El ahorro de bater\\u00eda est\\u00e1 activado: el juego va m\\u00e1s lento y menos fluido. Desact\\u00edvalo para jugar a 60 FPS."'),
    # --- Teclado en pantalla del juego ---
    ("smali/S/X.smali", '"Enter text"', '"Escribe el texto"'),
    # --- Aviso del renderizador (GPU sin Vulkan 1.3) ---
    ("smali/S/Y.smali", '"Renderer Notice"', '"Aviso del renderizador"'),
    ("smali/S/Y.smali",
     '"\\n\\nYour device GPU does not provide Vulkan 1.3 or VK_KHR_dynamic_rendering. The game will run in headless mode without video output. Check the log for details."',
     '"\\n\\nLa GPU de tu dispositivo no ofrece Vulkan 1.3 ni VK_KHR_dynamic_rendering. El juego se ejecutar\\u00e1 sin imagen (modo headless). Revisa el registro para ver los detalles."'),
    ("smali/S/Y.smali", '"View Log"', '"Ver registro"'),
    ("smali/S/Y.smali", '"Continue Headless"', '"Continuar sin imagen"'),
    # --- Detección automática del juego (menú principal) ---
    ("smali/com/pes2017/recomp/MainActivity.smali", '" other source(s) found."', '" fuente(s) m\\u00e1s encontrada(s)."'),
    ("smali/com/pes2017/recomp/MainActivity.smali", '"Plays from this folder, nothing copied."', '"Se juega desde esta carpeta, sin copiar nada."'),
    ("smali/com/pes2017/recomp/MainActivity.smali", '"Ready for one-click setup."', '"Listo para configurar con un toque."'),
    ("smali/com/pes2017/recomp/MainActivity.smali", '"Game found ("', '"Juego encontrado ("'),
    ("smali/com/pes2017/recomp/MainActivity.smali", '"Choose Game Source ("', '"Elegir origen del juego ("'),
    ("smali/com/pes2017/recomp/MainActivity.smali", '"Choose Another Source"', '"Elegir otro origen"'),
    # --- Mensajes de error comprensibles ---
    ("smali/com/pes2017/recomp/NativeBridge.smali", '"This phone\\\'s CPU lacks "', '"Al procesador de este tel\\u00e9fono le falta "'),
    ("smali/com/pes2017/recomp/NativeBridge.smali", '" (ARMv8.2-A is required)"', '" (se requiere ARMv8.2-A)"'),
    ("smali/S/A0.smali", '"Incomplete copy: expected "', '"Copia incompleta: se esperaban "'),
    ("smali/S/A0.smali", '" bytes, got "', '" bytes y se obtuvieron "'),
    ("smali/S/T.smali", '"Driver requires Android API "', '"El controlador requiere Android API "'),
    ("smali/S/T.smali", '" (device has "', '" (el dispositivo tiene "'),
]


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    base = sys.argv[1].rstrip("/") + "/"
    total = 0
    for archivo, viejo, nuevo in REEMPLAZOS:
        ruta = base + archivo
        contenido = open(ruta, encoding="utf-8").read()
        n = contenido.count(viejo)
        if n == 0:
            print(f"AVISO: no se encontró {viejo} en {archivo} (¿ya traducido?)")
            continue
        open(ruta, "w", encoding="utf-8").write(contenido.replace(viejo, nuevo))
        total += n
    print(f"Listo: {total} textos del código traducidos al español")


if __name__ == "__main__":
    main()
