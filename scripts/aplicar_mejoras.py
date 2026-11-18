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
  2. IDIOMA DEL JUEGO: selector en Ajustes (español latinoamericano, de
     España o inglés) que la app le pasa al motor parcheado.
     (El rediseño de la interfaz está en scripts/redisenar_interfaz.py.)
  3. ADAPTACIÓN A LA PANTALLA: en Android 9+ el partido usa también la zona
     del notch / cámara perforada (antes quedaba una franja negra).
  4. GALAXY S24 ULTRA: perfil optimizado que se aplica en el primer inicio
     (ver Estabilidad.perfilS24 en parches/Estabilidad.smali).
  5. SIN CÓDIGO DE APKVISION: se quita el código que el sitio de descarga
     agregó al APK (forzaba el idioma inglés, mostraba un aviso "APKVISION.ORG"
     y consultaba "actualizaciones" por internet abriendo el navegador).
  6. ID NUEVO: cambia el paquete a com.pes2017.recomp.es (y los "authorities"
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
    for clase in ("Estabilidad.smali", "Estabilidad$Idioma.smali"):
        shutil.copy(os.path.join(parches, clase),
                    os.path.join(base, "smali/com/pes2017/recomp", clase))
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


def mejora_idioma(base):
    # a) GameActivity: justo después de PES17_FULLSCREEN le pasamos al motor el
    #    idioma elegido (PES17_LANGUAGE / PES17_COUNTRY). v6 = GameActivity, v12 = NativeBridge.
    ruta = os.path.join(base, "smali/com/pes2017/recomp/GameActivity.smali")
    viejo = ('    const-string v0, "PES17_FULLSCREEN"\n\n'
             '    const-string v1, "1"\n\n'
             '    invoke-virtual {v12, v0, v1}, Lcom/pes2017/recomp/NativeBridge;->nativeSetOption(Ljava/lang/String;Ljava/lang/String;)V\n')
    reemplazar(ruta, viejo, viejo +
               '\n    # [ES] Idioma del juego elegido en Ajustes\n'
               '    invoke-static {v6, v12}, Lcom/pes2017/recomp/Estabilidad;->opcionesMotor(Landroid/content/Context;Lcom/pes2017/recomp/NativeBridge;)V\n')

    # b) SettingsActivity: al final de onCreate conectamos el selector de idioma
    ruta = os.path.join(base, "smali/com/pes2017/recomp/SettingsActivity.smali")
    viejo = ('    invoke-direct {v2, v0, v7}, LS/k1;-><init>(Landroid/widget/TextView;Lcom/pes2017/recomp/SettingsActivity;)V\n\n'
             '    invoke-virtual {v1, v2}, Landroid/view/View;->setOnClickListener(Landroid/view/View$OnClickListener;)V\n\n'
             '    return-void\n')
    reemplazar(ruta, viejo, viejo.replace('    return-void\n',
               '    # [ES] Selector "Idioma del juego"\n'
               '    invoke-static {v7}, Lcom/pes2017/recomp/Estabilidad;->configurarIdioma(Landroid/app/Activity;)V\n\n'
               '    return-void\n'))

    # c) Ids nuevos del selector
    ruta = os.path.join(base, "res/values/ids.xml")
    reemplazar(ruta, "</resources>",
               '    <item type="id" name="idioma_juego" />\n'
               '    <item type="id" name="idioma_latam" />\n'
               '    <item type="id" name="idioma_espana" />\n'
               '    <item type="id" name="idioma_ingles" />\n</resources>')

    # d) Sección "Idioma del juego" al principio de la pestaña de controles
    ruta = os.path.join(base, "res/layout/activity_settings.xml")
    ancla = ('<LinearLayout android:orientation="vertical" android:id="@id/page_controls" '
             'android:layout_width="fill_parent" android:layout_height="wrap_content">')
    boton = ('<RadioButton android:textColor="@color/pes_text" android:id="@id/idioma_{0}" '
             'android:layout_width="fill_parent" android:layout_height="wrap_content" '
             'android:minHeight="44.0dip" android:text="@string/idioma_{0}" />')
    seccion = (ancla +
               '\n                    <!-- [ES] Idioma del juego (lo lee el motor parcheado) -->'
               '\n                    <TextView android:layout_width="fill_parent" android:layout_height="wrap_content" '
               'android:text="@string/section_language" style="@style/SectionHeading" />'
               '\n                    <LinearLayout style="@style/SettingGroup">'
               '\n                        <RadioGroup android:orientation="vertical" android:id="@id/idioma_juego" '
               'android:layout_width="fill_parent" android:layout_height="wrap_content">'
               + "".join("\n                            " + boton.format(x) for x in ("latam", "espana", "ingles")) +
               '\n                        </RadioGroup>'
               '\n                        <TextView android:layout_width="fill_parent" android:layout_height="wrap_content" '
               'android:text="@string/idioma_hint" style="@style/SettingHint" />'
               '\n                    </LinearLayout>')
    reemplazar(ruta, ancla, seccion)
    print("  [ok] Idioma del juego: selector en Ajustes y opción para el motor")


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


def mejora_s24_y_quitar_apkvision(base):
    ruta = os.path.join(base, "smali/com/pes2017/recomp/MainActivity.smali")
    # En lugar del código de apkvision, llamamos al perfil del S24 Ultra.
    # Va justo después de super.onCreate() y ANTES de que la app elija su
    # perfil automático, así ese perfil no pisa nuestros valores.
    reemplazar(ruta,
               "    invoke-static/range {p0 .. p0}, Lorg/apkvision/port135145/Entry;->show(Landroid/app/Activity;)V",
               "    # [ES] Se quitó el código de apkvision (forzaba inglés y mostraba avisos)\n"
               "    # [ES] Perfil optimizado para Galaxy S24 Ultra (solo en el primer inicio)\n"
               "    invoke-static {p0}, Lcom/pes2017/recomp/Estabilidad;->perfilS24(Landroid/content/Context;)V")
    # Borramos las clases de apkvision, que ya nadie usa
    for carpeta in ("smali_classes3/org/apkvision", "smali_classes2/io/avm"):
        shutil.rmtree(os.path.join(base, carpeta), ignore_errors=True)
    # Si una carpeta smali_classesN quedó sin clases, la borramos completa
    # (si no, apktool genera un classesN.dex vacío)
    for carpeta in ("smali_classes2", "smali_classes3"):
        ruta_c = os.path.join(base, carpeta)
        vacia = not any(f.endswith(".smali") for _, _, fs in os.walk(ruta_c) for f in fs)
        if os.path.isdir(ruta_c) and vacia:
            shutil.rmtree(ruta_c)
    print("  [ok] Perfil Galaxy S24 Ultra y código de apkvision quitado")


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
    reemplazar(yml, "versionName: 0.2.0 (425cb0d)", "versionName: 0.2.0-es.2 (425cb0d)")
    # versionCode mayor que el de la versión ES anterior (40), para que se
    # instale encima como actualización conservando ajustes y partidas
    reemplazar(yml, "versionCode: 40", "versionCode: 42")
    print(f"  [ok] ID nuevo: {PAQUETE_NUEVO}")


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    base, parches = sys.argv[1], sys.argv[2]
    mejora_estabilidad(base, parches)
    mejora_idioma(base)
    mejora_pantalla(base)
    mejora_s24_y_quitar_apkvision(base)
    mejora_id(base)
    print("Listo: todas las mejoras aplicadas")


if __name__ == "__main__":
    main()
