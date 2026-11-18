#!/usr/bin/env bash
# =============================================================================
# construir_apk.sh — Genera el APK en español a partir del APK original.
#
# Uso:
#   PES_LLAVE_PASS='contraseña' scripts/construir_apk.sh \
#       <apk_original> <apktool.jar> <uber-apk-signer.jar> <llave.jks> <salida.apk>
#
# Pasos:
#   1. Descompila el APK original con apktool.
#   2. Traduce los textos (traduccion/strings_es419.xml + textos del código).
#   3. Aplica las mejoras (estabilidad, idioma, perfil S24 Ultra, notch, ID nuevo,
#      quita el código de apkvision).
#   4. Aplica el rediseño moderno y minimalista.
#   5. Parchea el motor (libpes17.so) para que el juego pueda salir en español.
#   6. Compila, alinea y firma con la llave propia.
# =============================================================================
set -euo pipefail

if [ $# -ne 5 ] || [ -z "${PES_LLAVE_PASS:-}" ]; then
  sed -n 2,20p "$0"; exit 1
fi
APK="$1"; APKTOOL="$2"; FIRMADOR="$3"; LLAVE="$4"; SALIDA="$5"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
TRABAJO="$(mktemp -d)"
trap 'rm -rf "$TRABAJO"' EXIT

echo "== 1/6 Descompilando"
java -jar "$APKTOOL" d -f -o "$TRABAJO/dec" "$APK" >/dev/null

echo "== 2/6 Traduciendo"
python3 -I "$REPO/scripts/aplicar_traduccion.py" "$TRABAJO/dec" "$REPO/traduccion/strings_es419.xml"
python3 -I "$REPO/scripts/traducir_smali.py" "$TRABAJO/dec"

echo "== 3/6 Mejoras"
python3 -I "$REPO/scripts/aplicar_mejoras.py" "$TRABAJO/dec" "$REPO/parches"

echo "== 4/6 Rediseño de la interfaz"
python3 -I "$REPO/scripts/redisenar_interfaz.py" "$TRABAJO/dec" "$REPO/parches"

echo "== 5/6 Idioma en el motor"
mkdir -p "$TRABAJO/asm"
python3 -I "$REPO/scripts/parchear_idioma_motor.py" "$TRABAJO/dec/lib/arm64-v8a/libpes17.so" "$TRABAJO/asm"

echo "== 6/6 Compilando y firmando"
java -jar "$APKTOOL" b "$TRABAJO/dec" -o "$TRABAJO/sin_firmar.apk" >/dev/null
java -jar "$FIRMADOR" -a "$TRABAJO/sin_firmar.apk" -o "$TRABAJO/firmado" \
  --ks "$LLAVE" --ksAlias pes2017es --ksPass "$PES_LLAVE_PASS" --ksKeyPass "$PES_LLAVE_PASS" | grep -E "verified|ERROR" || true
cp "$TRABAJO"/firmado/*.apk "$SALIDA"
sha256sum "$SALIDA"
