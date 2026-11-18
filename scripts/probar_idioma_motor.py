#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
probar_idioma_motor.py
----------------------
Prueba el parche de idioma EJECUTANDO las funciones de libpes17.so en un
emulador de CPU ARM64 (Unicorn), sin teléfono.

Para cada combinación de variables de entorno llama a:
  * XGetLanguage, XamGetLanguage, XamGetLocaleEx  -> revisa el valor en r3
  * ExGetXConfigSetting(3, 2)                      -> revisa el idioma escrito
    en el búfer del juego (4 bytes en big endian)
getenv, guest::Base y TraceImport se reemplazan por funciones falsas.

Uso:  python3 scripts/probar_idioma_motor.py <libpes17.so parcheado>
Requiere: pip install unicorn
"""
import struct
import sys

from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM, UC_HOOK_CODE
from unicorn.arm64_const import (UC_ARM64_REG_X0, UC_ARM64_REG_X8, UC_ARM64_REG_X30,
                                 UC_ARM64_REG_SP, UC_ARM64_REG_PC, UC_ARM64_REG_W22, UC_ARM64_REG_W21)
try:
    from unicorn import UC_CPU_ARM64_MAX
except ImportError:
    from unicorn.arm64_const import UC_CPU_ARM64_MAX

X_GET_LANGUAGE, XAM_GET_LANGUAGE, XAM_GET_LOCALE_EX = 0x42DBA1C, 0x42E792C, 0x42E79B4
EX_GET_XCONFIG, XCONFIG_IDIOMA = 0x42F8024, 0x42E7968
GETENV, GUEST_BASE, TRACE_IMPORT = 0x90DDA80, 0x42BFCD8, 0x42D5504
CODIGO_INI, CODIGO_FIN = 0x42B0000, 0x4320000
PLT_PAGINA = 0x90DD000
DATOS = 0x9A80000          # contadores globales que usan las funciones (ldaddal)
PILA, CTX, ENTORNO, INVITADO, FIN = 0x1000000, 0x2000000, 0x3000000, 0x4000000, 0x5000000


def preparar(so):
    uc = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
    uc.ctl_set_cpu_model(UC_CPU_ARM64_MAX)       # incluye instrucciones atómicas LSE
    uc.mem_map(CODIGO_INI, CODIGO_FIN - CODIGO_INI)
    uc.mem_write(CODIGO_INI, so[CODIGO_INI:CODIGO_FIN])
    uc.mem_map(PLT_PAGINA, 0x2000)
    uc.mem_write(PLT_PAGINA, b"\xc0\x03\x5f\xd6" * (0x2000 // 4))   # ret
    for base in (DATOS, PILA, CTX, ENTORNO, INVITADO, FIN):
        uc.mem_map(base, 0x10000)
    return uc


def llamar(uc, funcion, entorno, ctx=b"", x8=0):
    """Ejecuta una función con el entorno dado; devuelve el emulador al terminar."""
    def gancho(uc, direccion, tamano, _):
        if direccion == GETENV:
            nombre = uc.mem_read(uc.reg_read(UC_ARM64_REG_X0), 32).split(b"\0")[0].decode()
            if nombre in entorno:
                uc.mem_write(ENTORNO, entorno[nombre].encode() + b"\0")
                uc.reg_write(UC_ARM64_REG_X0, ENTORNO)
            else:
                uc.reg_write(UC_ARM64_REG_X0, 0)
        elif direccion == GUEST_BASE:
            uc.reg_write(UC_ARM64_REG_X0, INVITADO)
            uc.reg_write(UC_ARM64_REG_PC, uc.reg_read(UC_ARM64_REG_X30))
        elif direccion == TRACE_IMPORT:
            uc.reg_write(UC_ARM64_REG_PC, uc.reg_read(UC_ARM64_REG_X30))
    h = uc.hook_add(UC_HOOK_CODE, gancho)
    uc.mem_write(CTX, ctx.ljust(0x100, b"\0"))
    uc.mem_write(INVITADO, b"\xee" * 0x100)
    uc.reg_write(UC_ARM64_REG_SP, PILA + 0x8000)
    uc.reg_write(UC_ARM64_REG_X0, CTX)
    uc.reg_write(UC_ARM64_REG_X8, x8)
    uc.reg_write(UC_ARM64_REG_X30, FIN)
    uc.emu_start(funcion, FIN, count=100000)
    uc.hook_del(h)
    return uc


def main():
    so = open(sys.argv[1], "rb").read()
    uc = preparar(so)
    casos = [
        ({}, 1, 6),                                              # sin variables: igual que el original
        ({"PES17_LANGUAGE": "5", "PES17_COUNTRY": "22"}, 5, 22),  # español latinoamericano
        ({"PES17_LANGUAGE": "5", "PES17_COUNTRY": "31"}, 5, 31),  # español de España
        ({"PES17_LANGUAGE": "1", "PES17_COUNTRY": "6"}, 1, 6),    # inglés
        ({"PES17_LANGUAGE": "x", "PES17_COUNTRY": ""}, 1, 6),     # valores inválidos -> por defecto
    ]
    errores = 0
    for entorno, idioma, pais in casos:
        r = {}
        for nombre, funcion in (("XGetLanguage", X_GET_LANGUAGE), ("XamGetLanguage", XAM_GET_LANGUAGE),
                                ("XamGetLocaleEx", XAM_GET_LOCALE_EX)):
            # Se llama varias veces: los contadores internos no deben afectar el resultado
            for _ in range(5):
                llamar(uc, funcion, entorno)
            r[nombre] = struct.unpack("<Q", bytes(uc.mem_read(CTX, 8)))[0]
        # Ayudante de ExGetXConfigSetting: debe conservar x8
        llamar(uc, XCONFIG_IDIOMA, entorno, x8=0x1234ABCD)
        ayudante_ok = (uc.reg_read(UC_ARM64_REG_W22) == struct.unpack(">I", struct.pack("<I", idioma))[0]
                       and uc.reg_read(UC_ARM64_REG_W21) == 0x400 and uc.reg_read(UC_ARM64_REG_X8) == 0x1234ABCD)
        # ExGetXConfigSetting completo: categoría 3, ajuste 2, búfer en +0x40, tamaño 4
        ctx = bytearray(0x100)
        struct.pack_into("<I", ctx, 0x00, 3)
        struct.pack_into("<I", ctx, 0x20, 2)
        struct.pack_into("<I", ctx, 0x28, 0x40)
        struct.pack_into("<I", ctx, 0x30, 4)
        for _ in range(5):
            llamar(uc, EX_GET_XCONFIG, entorno, bytes(ctx))
        xconfig = struct.unpack(">I", bytes(uc.mem_read(INVITADO + 0x40, 4)))[0]

        ok = (r["XGetLanguage"] == idioma and r["XamGetLanguage"] == idioma and
              r["XamGetLocaleEx"] == pais and ayudante_ok and xconfig == idioma)
        errores += not ok
        print(f"{'OK ' if ok else 'MAL'} entorno={entorno} -> XGetLanguage={r['XGetLanguage']} "
              f"XamGetLanguage={r['XamGetLanguage']} XamGetLocaleEx={r['XamGetLocaleEx']} "
              f"ExGetXConfigSetting(3,2)={xconfig} ayudante={'ok' if ayudante_ok else 'MAL'}")
    print("TODAS LAS PRUEBAS PASARON" if not errores else f"{errores} PRUEBAS FALLARON")
    sys.exit(1 if errores else 0)


if __name__ == "__main__":
    main()
