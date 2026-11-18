#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
redisenar_interfaz.py
---------------------
Rediseño moderno y minimalista del launcher:

  * Tema OSCURO (fondo #0D1117, tarjetas #161B22) con UN solo color de acento
    (verde esmeralda #34D399), en lugar del estilo "menú de PES" claro con
    degradados azul marino, rojo y dorado.
  * Tarjetas y botones con esquinas redondeadas, sin degradados ni barras.
  * Tipografía limpia: sin cursivas, sin MAYÚSCULAS forzadas, tamaños legibles.
  * Sin las imágenes de jugadores de fondo.
  * Diálogos oscuros y barra de estado del mismo color que el fondo.

El código de la app solo usa los "tokens" de color (pes_*) y fondos (bg_*),
así que cambiándolos se rediseñan todas las pantallas sin tocar la lógica.
Las pantallas principales (activity_main) se reemplazan completas por las de
parches/res/, que conservan todos los id que usa MainActivity.

Uso:
    python3 -I scripts/redisenar_interfaz.py <carpeta_apktool> <carpeta_parches>
"""
import os
import re
import shutil
import sys

# ---- Paleta -------------------------------------------------------------------
COLORES = {
    "pes_page": "#ff0d1117",     # fondo de pantalla
    "pes_panel": "#ff161b22",    # tarjetas
    "pes_row": "#ff1c2129",      # cajas dentro de tarjetas
    "pes_line": "#ff2a313c",     # bordes y divisores
    "pes_text": "#ffe6edf3",     # texto principal
    "pes_muted": "#ff8b949e",    # texto secundario
    "pes_on_dark": "#ffe6edf3",  # texto sobre fondos oscuros (pestañas)
    "pes_navy": "#ff0d1117",     # color primario del tema (barras del sistema)
    "pes_red": "#ff34d399",      # acento (interruptores, barras deslizantes)
    "pes_gold": "#ff34d399",     # acento (opción elegida del menú y pestañas)
    "pes_blue": "#ffc9d1d9",     # texto del estado (panel de detalles)
    "pes_garnet": "#fff87171",   # errores
}

# ---- Estilos (se reemplazan completos) -----------------------------------------
ESTILOS = {
    "Theme.PES17": ("@style/Theme.AppCompat.NoActionBar", {
        "android:textColorPrimary": "@color/pes_text",
        "android:textColorSecondary": "@color/pes_muted",
        "android:buttonStyle": "@style/PanelButton",
        "android:windowBackground": "@color/pes_page",
        "android:statusBarColor": "@color/pes_page",
        "android:navigationBarColor": "@color/pes_page",
        "android:windowLightStatusBar": "false",
        "buttonStyle": "@style/PanelButton",
        "colorAccent": "@color/pes_red",
        "colorControlActivated": "@color/pes_red",
        "colorControlNormal": "@color/pes_muted",
        "colorPrimary": "@color/pes_navy",
        "colorPrimaryDark": "@color/pes_navy",
    }),
    "MenuEntry": (None, {
        "android:textSize": "16.0sp",
        "android:textStyle": "normal",
        "android:textColor": "@color/pes_text",
        "android:gravity": "start|center",
        "android:background": "@android:color/transparent",
        "android:layout_width": "fill_parent",
        "android:layout_height": "0.0dip",
        "android:minHeight": "0.0dip",
        "android:layout_weight": "1.0",
        "android:layout_marginTop": "1.0dip",
        "android:layout_marginBottom": "1.0dip",
        "android:drawablePadding": "12.0dip",
        "android:textAllCaps": "false",
        "android:drawableStart": "@drawable/ic_menu_cursor_space",
        "android:fontFamily": "sans-serif-medium",
        "android:paddingStart": "14.0dip",
        "android:paddingEnd": "14.0dip",
        "android:stateListAnimator": "@null",
        "android:letterSpacing": "0.0",
        "android:maxLines": "1",
        "android:autoSizeTextType": "uniform",
        "android:autoSizeMinTextSize": "11.0sp",
        "android:autoSizeMaxTextSize": "16.0sp",
        "android:autoSizeStepGranularity": "1.0sp",
    }),
    "PanelButton": ("@style/Widget.AppCompat.Button", {
        "android:textSize": "14.0sp",
        "android:textStyle": "normal",
        "android:textColor": "@color/pes_text",
        "android:background": "@drawable/bg_button_action",
        "android:minHeight": "44.0dip",
        "android:paddingStart": "16.0dip",
        "android:paddingEnd": "16.0dip",
        "android:textAllCaps": "false",
        "android:fontFamily": "sans-serif-medium",
        "android:stateListAnimator": "@null",
    }),
    "TabEntry": (None, {
        "android:textSize": "13.0sp",
        "android:textStyle": "normal",
        "android:textColor": "@color/pes_on_dark",
        "android:gravity": "center",
        "android:background": "@android:color/transparent",
        "android:layout_width": "0.0dip",
        "android:layout_height": "wrap_content",
        "android:minHeight": "40.0dip",
        "android:layout_weight": "1.0",
        "android:layout_marginStart": "3.0dip",
        "android:layout_marginEnd": "3.0dip",
        "android:maxLines": "2",
        "android:paddingStart": "6.0dip",
        "android:paddingEnd": "6.0dip",
        "android:textAllCaps": "false",
        "android:fontFamily": "sans-serif-medium",
        "android:stateListAnimator": "@null",
    }),
    "BackButton": (None, {
        "android:textSize": "15.0sp",
        "android:textStyle": "normal",
        "android:textColor": "@color/pes_text",
        "android:background": "@android:color/transparent",
        "android:minWidth": "0.0dip",
        "android:minHeight": "40.0dip",
        "android:textAllCaps": "false",
        "android:fontFamily": "sans-serif-medium",
        "android:paddingStart": "8.0dip",
        "android:paddingEnd": "14.0dip",
        "android:stateListAnimator": "@null",
    }),
    "SectionHeading": (None, {
        "android:textSize": "12.0sp",
        "android:textStyle": "bold",
        "android:textColor": "@color/pes_muted",
        "android:background": "@android:color/transparent",
        "android:paddingTop": "2.0dip",
        "android:paddingBottom": "2.0dip",
        "android:layout_marginTop": "22.0dip",
        "android:textAllCaps": "true",
        "android:letterSpacing": "0.1",
        "android:fontFamily": "sans-serif-medium",
        "android:paddingStart": "6.0dip",
    }),
    "SettingGroup": (None, {
        "android:orientation": "vertical",
        "android:background": "@drawable/bg_setting_group",
        "android:paddingStart": "12.0dip",
        "android:paddingEnd": "12.0dip",
        "android:paddingTop": "8.0dip",
        "android:paddingBottom": "8.0dip",
        "android:layout_width": "fill_parent",
        "android:layout_height": "wrap_content",
        "android:layout_marginTop": "8.0dip",
    }),
    "SettingLabel": (None, {
        "android:textSize": "15.0sp",
        "android:textStyle": "normal",
        "android:textColor": "@color/pes_text",
        "android:background": "@android:color/transparent",
        "android:paddingTop": "10.0dip",
        "android:paddingBottom": "4.0dip",
        "android:layout_marginTop": "2.0dip",
        "android:fontFamily": "sans-serif-medium",
        "android:paddingStart": "4.0dip",
    }),
    "SettingSwitch": (None, {
        "android:textSize": "15.0sp",
        "android:textStyle": "normal",
        "android:textColor": "@color/pes_text",
        "android:background": "@android:color/transparent",
        "android:minHeight": "48.0dip",
        "android:paddingTop": "6.0dip",
        "android:paddingBottom": "4.0dip",
        "android:layout_marginTop": "2.0dip",
        "android:fontFamily": "sans-serif-medium",
        "android:paddingStart": "4.0dip",
        "android:paddingEnd": "4.0dip",
    }),
    "SettingHint": (None, {
        "android:textSize": "12.5sp",
        "android:textColor": "@color/pes_muted",
        "android:lineSpacingExtra": "3.0dip",
        "android:paddingTop": "0.0dip",
        "android:paddingBottom": "8.0dip",
        "android:paddingStart": "4.0dip",
        "android:paddingEnd": "4.0dip",
    }),
}


def leer(ruta):
    return open(ruta, encoding="utf-8").read()


def escribir(ruta, texto):
    open(ruta, "w", encoding="utf-8").write(texto)


def estilo_xml(nombre, padre, items):
    attr_padre = f' parent="{padre}"' if padre else ""
    cuerpo = "".join(f'        <item name="{k}">{v}</item>\n' for k, v in items.items())
    return f'<style name="{nombre}"{attr_padre}>\n{cuerpo}    </style>'


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    base, parches = sys.argv[1], sys.argv[2]
    res = os.path.join(base, "res")

    # 1) Fondos, indicadores y pantallas principales nuevas
    origen = os.path.join(parches, "res")
    copiados = 0
    for carpeta, _, archivos in os.walk(origen):
        for archivo in archivos:
            rel = os.path.relpath(os.path.join(carpeta, archivo), origen)
            destino = os.path.join(res, rel)
            os.makedirs(os.path.dirname(destino), exist_ok=True)
            shutil.copy(os.path.join(carpeta, archivo), destino)
            copiados += 1
    print(f"  [ok] {copiados} archivos de diseño copiados")

    # 2) Paleta de colores
    ruta = os.path.join(res, "values/colors.xml")
    texto = leer(ruta)
    for nombre, valor in COLORES.items():
        texto, n = re.subn(rf'<color name="{nombre}">[^<]*</color>', f'<color name="{nombre}">{valor}</color>', texto)
        if n != 1:
            sys.exit(f"ERROR: no se encontró el color {nombre}")
    escribir(ruta, texto)
    print("  [ok] Paleta oscura con acento verde")

    # 3) Estilos
    ruta = os.path.join(res, "values/styles.xml")
    texto = leer(ruta)
    for nombre, (padre, items) in ESTILOS.items():
        patron = rf'<style name="{re.escape(nombre)}"( parent="[^"]*")?>.*?</style>'
        m = re.search(patron, texto, re.S)
        if not m:
            sys.exit(f"ERROR: no se encontró el estilo {nombre}")
        if padre is None and m.group(1):
            padre = m.group(1).split('"')[1]
        texto = texto[:m.start()] + estilo_xml(nombre, padre, items) + texto[m.end():]
    escribir(ruta, texto)
    print("  [ok] Estilos: sin cursivas, sin mayúsculas forzadas, botones redondeados")

    # 4) Títulos de pantallas que usaban azul marino como color de texto
    for carpeta in ("layout", "layout-port"):
        for archivo in os.listdir(os.path.join(res, carpeta)):
            ruta = os.path.join(res, carpeta, archivo)
            texto = leer(ruta)
            nuevo = texto.replace('android:textColor="@color/pes_navy"', 'android:textColor="@color/pes_text"')
            if nuevo != texto:
                escribir(ruta, nuevo)

    # 5) Ajustes: sin imagen de jugadores y sin "tarjeta dentro de tarjeta"
    ruta = os.path.join(res, "layout/activity_settings.xml")
    texto = leer(ruta)
    texto, n = re.subn(r'\s*<ImageView [^>]*@drawable/launcher_players[^>]*/>', "", texto)
    if n != 1:
        sys.exit("ERROR: no se encontró la imagen de fondo de Ajustes")
    viejo = ('<LinearLayout android:orientation="vertical" android:background="@drawable/bg_panel" '
             'android:paddingBottom="10.0dip"')
    if texto.count(viejo) != 1:
        sys.exit("ERROR: no se encontró el contenedor de Ajustes")
    texto = texto.replace(viejo, '<LinearLayout android:orientation="vertical" android:paddingBottom="24.0dip"')
    escribir(ruta, texto)
    print("  [ok] Pantalla de Ajustes despejada")


if __name__ == "__main__":
    main()
