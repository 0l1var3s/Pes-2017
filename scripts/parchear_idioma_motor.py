#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
parchear_idioma_motor.py
------------------------
Parchea libpes17.so (el motor del port) para que el juego pueda salir en
ESPAÑOL.

El problema
    En el código del motor (runtime/kernel/misc.cpp, pes_imports.cpp y xam.cpp
    del proyecto oficial dzakyraf/pes2017-recomp) las funciones con las que el
    juego de Xbox 360 pregunta el idioma de la consola devuelven SIEMPRE inglés:
        XGetLanguage()          -> 1 (inglés)
        XamGetLanguage()        -> 1 (inglés)
        ExGetXConfigSetting(3,2)-> 1 (inglés, configuración de usuario)
        XamGetLocaleEx()        -> 6 (región)
    Por eso las pantallas de idioma del juego no ofrecían el español aunque la
    ISO lo traiga.

La solución
    Se reescriben esas funciones (mismo tamaño, mismas direcciones) para que
    lean dos variables de entorno, que la app fija antes de iniciar el juego
    según el ajuste "Idioma del juego":
        PES17_LANGUAGE  -> idioma de Xbox 360 (1 inglés, 5 español, ...)
        PES17_COUNTRY   -> región (22 México, 31 España, 6 la original)
    Si la variable no existe, devuelven lo mismo que antes (1 y 6), así que
    el motor se comporta igual que el original si la app no fija nada.

Uso:
    python3 -I scripts/parchear_idioma_motor.py <libpes17.so> [carpeta_temporal]
"""
import os
import struct
import subprocess
import sys
import tempfile

# Direcciones de libpes17.so de PES 2017 Android 0.2.0 (425cb0d).
# En este .so la dirección virtual del código coincide con la posición en el archivo.
X_GET_LANGUAGE = 0x42DBA1C        # 136 bytes
XAM_GET_LANGUAGE = 0x42E792C      # 136 bytes, seguida de:
XAM_GET_LOCALE_EX = 0x42E79B4     # 136 bytes
EX_GET_XCONFIG_PATCH = 0x42F80C8  # 2 instrucciones dentro de ExGetXConfigSetting
GETENV_PLT = 0x90DDA80

# Instrucciones originales esperadas (para no parchear un .so distinto)
ESPERADO = {
    X_GET_LANGUAGE: 0xA9BE7BFD,          # stp x29, x30, [sp, #-0x20]!
    X_GET_LANGUAGE + 0x50: 0x52800028,   # mov w8, #1   (inglés)
    XAM_GET_LANGUAGE + 0x50: 0x52800028, # mov w8, #1   (inglés)
    XAM_GET_LOCALE_EX + 0x50: 0x528000C8,# mov w8, #6   (región)
    EX_GET_XCONFIG_PATCH: 0x52A02016,    # mov w22, #0x1000000  (inglés, big endian)
    EX_GET_XCONFIG_PATCH + 4: 0x52808015,# mov w21, #0x400
}

ASM_XAM = r"""
    .text
inicio:
// ---- XamGetLanguage: r3 = idioma ------------------------------------------
xam_get_language:
    stp x29, x30, [sp, #-0x20]!
    str x19, [sp, #0x10]
    mov x29, sp
    mov x19, x0                 // x0 = PPCContext*, r3 está en el offset 0
    bl  valor_idioma
    str x0, [x19]
    ldr x19, [sp, #0x10]
    ldp x29, x30, [sp], #0x20
    ret

// w0 = PES17_LANGUAGE o 1 (inglés) si no existe
valor_idioma:
    adr x0, s_idioma
    mov w1, #1
    b   leer_numero_env

// w0 = PES17_COUNTRY o 6 (la región original) si no existe
valor_pais:
    adr x0, s_pais
    mov w1, #6
    b   leer_numero_env

// Usado por ExGetXConfigSetting (ajuste 2 = idioma):
// w22 = idioma en big endian (32 bits), w21 = ancho 4 en big endian (16 bits).
// Conserva x8 (tamaño del búfer), que la función original usa después.
xconfig_idioma:
    stp x29, x30, [sp, #-0x20]!
    mov x29, sp
    str x8, [sp, #0x10]
    bl  valor_idioma
    rev w22, w0
    mov w21, #0x400
    ldr x8, [sp, #0x10]
    ldp x29, x30, [sp], #0x20
    ret

s_idioma: .asciz "PES17_LANGUAGE"
s_pais:   .asciz "PES17_COUNTRY"
    .balign 4
    .org 0x88, 0

// ---- XamGetLocaleEx: r3 = región ------------------------------------------
xam_get_locale_ex:
    stp x29, x30, [sp, #-0x20]!
    str x19, [sp, #0x10]
    mov x29, sp
    mov x19, x0
    bl  valor_pais
    str x0, [x19]
    ldr x19, [sp, #0x10]
    ldp x29, x30, [sp], #0x20
    ret

// leer_numero_env(x0 = nombre, w1 = valor por defecto) -> w0
// Lee getenv(nombre) y convierte 1 o 2 dígitos; si no hay, devuelve w1.
leer_numero_env:
    stp x29, x30, [sp, #-0x20]!
    mov x29, sp
    str x1, [sp, #0x10]
    bl  inicio + (GETENV_PLT - BASE)
    ldr x1, [sp, #0x10]
    cbz x0, 2f
    ldrb w9, [x0]
    sub w9, w9, #0x30
    cmp w9, #9
    b.hi 2f
    ldrb w10, [x0, #1]
    sub w10, w10, #0x30
    cmp w10, #9
    b.hi 1f
    mov w11, #10
    madd w9, w9, w11, w10
1:  mov w0, w9
    b   3f
2:  mov w0, w1
3:  ldp x29, x30, [sp], #0x20
    ret
    .org 0x110, 0
"""

ASM_XGET = r"""
    .text
inicio:
// ---- XGetLanguage: r3 = idioma (usa valor_idioma de XamGetLanguage) -------
    stp x29, x30, [sp, #-0x20]!
    str x19, [sp, #0x10]
    mov x29, sp
    mov x19, x0
    bl  inicio + (VALOR_IDIOMA - BASE)
    str x0, [x19]
    ldr x19, [sp, #0x10]
    ldp x29, x30, [sp], #0x20
    ret
    .org 0x88, 0
"""

ASM_XCONFIG = r"""
    .text
inicio:
// ---- Dentro de ExGetXConfigSetting, ajuste 2 (idioma) ----------------------
    bl  inicio + (XCONFIG_IDIOMA - BASE)
    nop
"""


def ensamblar(asm, base, simbolos, tmp):
    """Ensambla con llvm-mc y devuelve (bytes, tabla de símbolos)."""
    defs = "".join(f"    .set {k}, {v:#x}\n" for k, v in {**simbolos, "BASE": base}.items())
    fuente = os.path.join(tmp, "parche.s")
    objeto = os.path.join(tmp, "parche.o")
    binario = os.path.join(tmp, "parche.bin")
    open(fuente, "w").write(defs + asm)
    subprocess.run(["llvm-mc", "-triple=aarch64-linux-android", "-filetype=obj", "-o", objeto, fuente], check=True)
    relocs = subprocess.run(["llvm-readelf", "-r", objeto], capture_output=True, text=True).stdout
    if "R_AARCH64" in relocs:
        sys.exit("ERROR: el parche quedó con relocaciones sin resolver:\n" + relocs)
    subprocess.run(["llvm-objcopy", "-O", "binary", "--only-section=.text", objeto, binario], check=True)
    nm = subprocess.run(["llvm-nm", objeto], capture_output=True, text=True).stdout
    tabla = {}
    for linea in nm.splitlines():
        partes = linea.split()
        if len(partes) == 3:
            tabla[partes[2]] = int(partes[0], 16)
    return open(binario, "rb").read(), tabla


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    ruta = sys.argv[1]
    tmp = sys.argv[2] if len(sys.argv) > 2 else tempfile.mkdtemp()
    datos = bytearray(open(ruta, "rb").read())

    # 1) Verificamos que es el .so esperado
    for direccion, palabra in ESPERADO.items():
        actual = struct.unpack_from("<I", datos, direccion)[0]
        if actual != palabra:
            sys.exit(f"ERROR: en {direccion:#x} hay {actual:#010x} y se esperaba {palabra:#010x}. "
                     "¿Es otra versión de libpes17.so, o ya está parcheado?")

    # 2) XamGetLanguage + XamGetLocaleEx (contiguas, 0x110 bytes)
    codigo, tabla = ensamblar(ASM_XAM, XAM_GET_LANGUAGE, {"GETENV_PLT": GETENV_PLT}, tmp)
    assert len(codigo) == 0x110, len(codigo)
    datos[XAM_GET_LANGUAGE:XAM_GET_LANGUAGE + 0x110] = codigo
    valor_idioma = XAM_GET_LANGUAGE + tabla["valor_idioma"]
    xconfig_idioma = XAM_GET_LANGUAGE + tabla["xconfig_idioma"]

    # 3) XGetLanguage (0x88 bytes)
    codigo, _ = ensamblar(ASM_XGET, X_GET_LANGUAGE, {"VALOR_IDIOMA": valor_idioma}, tmp)
    assert len(codigo) == 0x88, len(codigo)
    datos[X_GET_LANGUAGE:X_GET_LANGUAGE + 0x88] = codigo

    # 4) ExGetXConfigSetting: 2 instrucciones
    codigo, _ = ensamblar(ASM_XCONFIG, EX_GET_XCONFIG_PATCH, {"XCONFIG_IDIOMA": xconfig_idioma}, tmp)
    assert len(codigo) == 8, len(codigo)
    datos[EX_GET_XCONFIG_PATCH:EX_GET_XCONFIG_PATCH + 8] = codigo

    open(ruta, "wb").write(datos)
    print("Listo: motor parcheado para leer el idioma (PES17_LANGUAGE) y la región (PES17_COUNTRY)")


if __name__ == "__main__":
    main()
