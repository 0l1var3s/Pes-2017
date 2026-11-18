#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aplicar_mejoras.py
------------------
Aplica sobre el APK descompilado (carpeta de apktool) las mejoras de la
versión en español:

  1. ESTABILIDAD: agrega la clase Estabilidad.smali y la conecta en
     GameActivity para activar el "Modo de poca memoria" en teléfonos de
     6 GB de RAM o menos (evita que Android cierre el partido).
  2. INTERFAZ: textos del menú que se ajustan solos al espacio (los textos en
     español son más largos), panel de detalles más legible y con más
     espacio, pestañas de Ajustes en hasta 2 líneas y pistas más grandes.
  3. ADAPTACIÓN A LA PANTALLA: en Android 9+ el partido usa también la zona
     del notch / cámara perforada (antes quedaba una franja negra).
  4. ID NUEVO: cambia el paquete a com.pes2017.recomp.es (y los "authorities"
     y el permiso interno) para poder instalarla junto a la original.

Uso:
    python3 -I scripts/aplicar_mejoras.py <carpeta_apktool> <carpeta_parches>
"""
import os
import shutil
import sys

PAQUETE_ORIGINAL = "com.pes2017.recomp"
PAQUETE_NUEVO = "com.pes2017.recomp.es"


def reemplazar(ruta, viejo, nuevo, veces=1):
    """Reemplaza un texto exacto y verifica cuántas veces aparecía."""
    texto = open(ruta, encoding="utf-8").read()
    n = texto.count(viejo)
    if n != veces:
        sys.exit(f"ERROR en {ruta}: se esperaban {veces} apariciones de:\n{viejo}\n...y hay {n}")
    open(ruta, "w", encoding="utf-8").write(texto.replace(viejo, nuevo))


def mejora_estabilidad(base, parches):
    # Copiamos la clase nueva junto a las demás clases de la app
    shutil.copy(os.path.join(parches, "Estabilidad.smali"),
                os.path.join(base, "smali/com/pes2017/recomp/Estabilidad.smali"))
    # Justo después de leer la preferencia "lowMemory" pasamos el valor por
    # Estabilidad.memoriaBaja(). v6 es la GameActivity (un Context).
    ruta = os.path.join(base, "smali/com/pes2017/recomp/GameActivity.smali")
    viejo = (
        '    const-string v4, "lowMemory"\n\n'
        '    iget-object v0, v0, LS/X0;->a:Landroid/content/SharedPreferences;\n\n'
        '    const/4 v5, 0x0\n\n'
        '    invoke-interface {v0, v4, v5}, Landroid/content/SharedPreferences;->getBoolean(Ljava/lang/String;Z)Z\n\n'
        '    move-result v0\n'
    )
    nuevo = viejo + (
        '\n    # [ES] Activa el modo de poca memoria en teléfonos de 6 GB o menos\n'
        '    invoke-static {v6, v0}, Lcom/pes2017/recomp/Estabilidad;->memoriaBaja(Landroid/content/Context;Z)Z\n\n'
        '    move-result v0\n'
    )
    reemplazar(ruta, viejo, nuevo)
    print("  [ok] Estabilidad: modo de poca memoria automático")


def mejora_interfaz(base):
    estilos = os.path.join(base, "res/values/styles.xml")

    # Menú principal: el texto se achica solo si no cabe (mínimo 10sp) y
    # nunca se corta en dos líneas.
    reemplazar(estilos,
               '        <item name="android:letterSpacing">0.04</item>\n    </style>',
               '        <item name="android:letterSpacing">0.04</item>\n'
               '        <item name="android:maxLines">1</item>\n'
               '        <item name="android:autoSizeTextType">uniform</item>\n'
               '        <item name="android:autoSizeMinTextSize">10.0sp</item>\n'
               '        <item name="android:autoSizeMaxTextSize">17.0sp</item>\n'
               '        <item name="android:autoSizeStepGranularity">1.0sp</item>\n'
               '    </style>')

    # Pestañas de Ajustes: "GRÁFICOS Y RENDIMIENTO" es largo, permitimos 2 líneas
    reemplazar(estilos,
               '        <item name="android:minHeight">34.0dip</item>\n        <item name="android:layout_weight">1.0</item>',
               '        <item name="android:minHeight">38.0dip</item>\n        <item name="android:layout_weight">1.0</item>\n'
               '        <item name="android:maxLines">2</item>\n'
               '        <item name="android:paddingStart">4.0dip</item>\n'
               '        <item name="android:paddingEnd">4.0dip</item>')

    # Pistas de ajustes: un punto más grandes y con más interlineado
    reemplazar(estilos,
               '    <style name="SettingHint">\n        <item name="android:textSize">11.0sp</item>',
               '    <style name="SettingHint">\n        <item name="android:textSize">12.0sp</item>\n'
               '        <item name="android:lineSpacingExtra">2.0dip</item>')

    # Pantalla principal (horizontal y vertical)
    for nombre in ("res/layout/activity_main.xml", "res/layout-port/activity_main.xml"):
        ruta = os.path.join(base, nombre)
        # Botón JUGAR: tamaño máximo mayor para que destaque
        reemplazar(ruta,
                   'android:textSize="19.0sp" android:textColor="@color/pes_red" android:id="@id/play"',
                   'android:textSize="19.0sp" android:autoSizeMaxTextSize="21.0sp" android:textColor="@color/pes_red" android:id="@id/play"')
        # Etiqueta de versión legible
        reemplazar(ruta, 'android:textSize="9.0sp" android:textColor="@color/pes_muted" android:gravity="end" android:id="@id/version_tag"',
                   'android:textSize="10.0sp" android:textColor="@color/pes_muted" android:gravity="end" android:id="@id/version_tag"')
        # Texto del panel de detalles: más grande y con más líneas visibles
        reemplazar(ruta, 'android:textSize="11.0sp" android:textColor="@color/pes_text" android:ellipsize="end" android:id="@id/detail_text"',
                   'android:textSize="12.0sp" android:textColor="@color/pes_text" android:ellipsize="end" android:id="@id/detail_text"')
        reemplazar(ruta, 'android:maxLines="6" android:lineSpacingExtra="2.0dip"',
                   'android:maxLines="9" android:lineSpacingExtra="2.0dip"')
        reemplazar(ruta, 'android:textSize="11.0sp" android:textColor="@color/pes_blue" android:ellipsize="end" android:id="@id/status"',
                   'android:textSize="12.0sp" android:textColor="@color/pes_blue" android:ellipsize="end" android:id="@id/status"')
        reemplazar(ruta, 'android:maxLines="5" android:lineSpacingExtra="2.0dip"',
                   'android:maxLines="7" android:lineSpacingExtra="2.0dip"')
        # Interruptor "empezar al abrir": un poco más grande para tocarlo fácil
        reemplazar(ruta, 'android:textSize="10.0sp" android:textColor="@color/pes_muted" android:id="@id/direct_launch_switch"',
                   'android:textSize="11.0sp" android:textColor="@color/pes_muted" android:id="@id/direct_launch_switch"')

    # En horizontal el panel dejaba 96dp vacíos a la derecha: lo reducimos
    reemplazar(os.path.join(base, "res/layout/activity_main.xml"),
               'android:layout_weight="0.9" android:layout_marginStart="4.0dip" android:layout_marginEnd="96.0dip"',
               'android:layout_weight="1.0" android:layout_marginStart="4.0dip" android:layout_marginEnd="56.0dip"')
    print("  [ok] Interfaz: textos adaptables y panel más legible")


def mejora_pantalla(base):
    # Android 9+ (API 28): el partido ocupa también la zona del notch.
    ruta = os.path.join(base, "res/values-v28/styles.xml")
    reemplazar(ruta, "</resources>",
               '    <!-- [ES] El partido usa toda la pantalla, incluida la zona del notch -->\n'
               '    <style name="Theme.PES17.Game" parent="@style/Theme.AppCompat.NoActionBar">\n'
               '        <item name="android:textColorPrimary">#ffeaf1ff</item>\n'
               '        <item name="android:textColorSecondary">#ff8fa0c2</item>\n'
               '        <item name="android:windowBackground">@android:color/black</item>\n'
               '        <item name="colorAccent">@color/pes_gold</item>\n'
               '        <item name="colorPrimary">#ff0e1a36</item>\n'
               '        <item name="colorPrimaryDark">#ff070d1c</item>\n'
               '        <item name="android:windowLayoutInDisplayCutoutMode">shortEdges</item>\n'
               '    </style>\n</resources>')
    print("  [ok] Pantalla: partido a pantalla completa con notch")


def mejora_id(base):
    ruta = os.path.join(base, "AndroidManifest.xml")
    # Paquete (ID de la app)
    reemplazar(ruta, f'package="{PAQUETE_ORIGINAL}"', f'package="{PAQUETE_NUEVO}"')
    # Permiso interno de androidx (debe ser único por app)
    reemplazar(ruta, f'{PAQUETE_ORIGINAL}.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION',
               f'{PAQUETE_NUEVO}.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION', veces=2)
    # "Authorities" de los proveedores de contenido (también deben ser únicos)
    reemplazar(ruta, f'android:authorities="{PAQUETE_ORIGINAL}.captures"',
               f'android:authorities="{PAQUETE_NUEVO}.captures"')
    reemplazar(ruta, f'android:authorities="{PAQUETE_ORIGINAL}.androidx-startup"',
               f'android:authorities="{PAQUETE_NUEVO}.androidx-startup"')
    # Nombre de versión con sufijo para identificarla
    yml = os.path.join(base, "apktool.yml")
    reemplazar(yml, "versionName: 0.2.0 (425cb0d)", "versionName: 0.2.0-es (425cb0d)")
    print(f"  [ok] ID nuevo: {PAQUETE_NUEVO}")


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    base, parches = sys.argv[1], sys.argv[2]
    mejora_estabilidad(base, parches)
    mejora_interfaz(base)
    mejora_pantalla(base)
    mejora_id(base)
    print("Listo: todas las mejoras aplicadas")


if __name__ == "__main__":
    main()
