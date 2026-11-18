#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aplicar_traduccion.py
---------------------
Reemplaza los textos en inglés de res/values/strings.xml (del APK
descompilado con apktool) por la traducción al español latinoamericano de
traduccion/strings_es419.xml.

Se reemplaza el archivo "por defecto" (values/) a propósito: así la app se ve
en español aunque el teléfono esté configurado en otro idioma.

Antes de escribir, el script verifica que cada cadena traducida tenga
exactamente los mismos marcadores de formato (%1$s, %2$d, %%, ...) que la
original. Si no coinciden, la app podría cerrarse al mostrar ese texto, así
que el script se detiene con error.

Uso:
    python3 -I scripts/aplicar_traduccion.py <carpeta_apktool> <strings_es419.xml>
"""
import re
import sys
import xml.etree.ElementTree as ET

# Marcadores de formato de Java/Android: %1$s, %2$d, %1$.1f, %d, %s y %%
FORMATO = re.compile(r"%(?:\d+\$)?[-#+ 0,(]*\d*(?:\.\d+)?[sdfx]|%%")


def marcadores(texto: str):
    """Devuelve la lista ordenada de marcadores de formato de un texto."""
    return sorted(FORMATO.findall(texto))


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    carpeta, archivo_es = sys.argv[1], sys.argv[2]
    ruta_strings = carpeta.rstrip("/") + "/res/values/strings.xml"

    original = open(ruta_strings, encoding="utf-8").read()

    # Leemos la traducción con el parser XML (los comentarios se ignoran).
    traducciones = {}
    atributos = {}
    for el in ET.parse(archivo_es).getroot().iter("string"):
        nombre = el.get("name")
        # Volvemos a obtener el texto "crudo" (con \n y \' sin interpretar)
        traducciones[nombre] = None
        atributos[nombre] = el.attrib
    crudo_es = open(archivo_es, encoding="utf-8").read()
    for nombre, valor in re.findall(r'<string name="([^"]+)"[^>]*>(.*?)</string>', crudo_es, re.S):
        traducciones[nombre] = valor

    errores = []
    reemplazos = 0

    def reemplazar(m):
        nonlocal reemplazos
        nombre, attrs, valor = m.group(1), m.group(2), m.group(3)
        if nombre not in traducciones:
            return m.group(0)
        nuevo = traducciones[nombre]
        # Comparamos los marcadores del original y de la traducción
        # (se omite si la cadena está marcada formatted="false": ahí el % es literal)
        if 'formatted="false"' not in attrs and marcadores(valor) != marcadores(nuevo):
            errores.append(f"{nombre}: original {marcadores(valor)} vs traducción {marcadores(nuevo)}")
        reemplazos += 1
        return f'<string name="{nombre}"{attrs}>{nuevo}</string>'

    resultado = re.sub(r'<string name="([^"]+)"([^>]*)>(.*?)</string>', reemplazar, original, flags=re.S)

    faltan = set(traducciones) - set(re.findall(r'<string name="([^"]+)"', original))
    if faltan:
        errores.append("Cadenas traducidas que no existen en el original: " + ", ".join(sorted(faltan)))

    if errores:
        print("ERROR: la traducción tiene problemas, no se escribió nada:")
        for e in errores:
            print("  -", e)
        sys.exit(2)

    open(ruta_strings, "w", encoding="utf-8").write(resultado)
    print(f"Listo: {reemplazos} textos traducidos al español en {ruta_strings}")


if __name__ == "__main__":
    main()
