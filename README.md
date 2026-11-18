# PES 2017 (port recompilado) — Versión en español latinoamericano

Modificación del APK `PES-2017-v0.2.0-425cb0d` (launcher del port recompilado
de PES 2017 para Android, motor Vulkan arm64). Incluye los scripts para volver
a generar el APK modificado a partir del original.

> Esta app **no incluye datos del juego**: necesitas tu propia copia de
> PES 2017 (imagen `.iso` o carpeta con `default.xex` y los `.cpk`).

## Validación del APK original

| Dato | Valor |
|---|---|
| Paquete original | `com.pes2017.recomp` |
| Versión | 0.2.0 (425cb0d), versionCode 40 |
| Android mínimo | 8.0 (API 26), objetivo API 35 |
| Arquitectura | solo `arm64-v8a` |
| Requisitos | Vulkan 1.3 (`android.hardware.vulkan.version` obligatorio) |
| Motor | `libpes17.so` (157 MB) + hooks nativos |
| Interfaz | Kotlin + layouts XML clásicos |

El RAR (2 partes) se extrajo bien y el APK se decompiló y recompiló sin errores.

## Cambios

1. **Español latinoamericano** — `traduccion/strings_es419.xml`
   * Los 306 textos propios de la app traducidos y con comentarios en español.
   * Reemplazan los textos por defecto, así que la app se ve en español aunque
     el teléfono esté en otro idioma.
   * 27 textos más que estaban fijos en el código (botones CAPTURA / GRABAR MACRO,
     HUD, aviso de ahorro de batería, aviso de Vulkan, etc.):
     `scripts/traducir_smali.py`.
   * Se verifican automáticamente los marcadores `%1$s`, `%2$d`, `%%` para que
     ningún texto pueda cerrar la app.
2. **Interfaz** — `scripts/aplicar_mejoras.py`
   * El menú principal ajusta solo el tamaño del texto (los textos en español
     son más largos) y nunca los corta.
   * El panel de detalles tiene texto más grande, más líneas visibles y usa mejor
     el espacio en horizontal.
   * Las pestañas de Ajustes pueden ocupar 2 líneas y las ayudas tienen letra más grande.
3. **Estabilidad y adaptación gráfica**
   * `parches/Estabilidad.smali`: en teléfonos de **6 GB de RAM o menos** se
     activa solo el *Modo de poca memoria* (PES17_NO_SHADOW), como recomienda
     la propia app, para que Android no cierre el partido. Si personalizaste
     los ajustes (perfil "Personalizado"), se respeta lo que elegiste.
   * En Android 9 o superior el partido usa **toda la pantalla, incluida la zona
     del notch / cámara perforada**.
   * Los perfiles automáticos (Bajo/Medio/Alto según el teléfono) de la app
     original se mantienen. Como el ID es nuevo, arrancan desde cero y se
     vuelven a detectar en el primer inicio.
4. **Optimizado para Galaxy S24 Ultra** (`Estabilidad.perfilS24`, modelos `SM-S928*`).
   En el primer inicio, si todavía no configuraste nada, se aplica:
   * Calidad de renderizado del partido **100%** (la Adreno 750 tiene margen de sobra).
   * **FSR** activado: escala con nitidez de 720p a la pantalla QHD+ (3120×1440).
   * **MSAA** activado (líneas de la cancha sin cortes).
   * **Bajar calidad al calentarse** activado: cuando el S24 Ultra se calienta
     pierde algo de nitidez en vez de tirones.
   * **Pantalla fija a 60 Hz**: el juego va a 60 FPS; 120 Hz solo gasta batería.
   * **Pantalla panorámica**: llena la pantalla 19.5:9 sin barras negras
     (los menús se estiran a lo ancho; se puede desactivar en Ajustes → Pantalla).
   * Multiplicador interno en 1x. Puedes probar 2x (2560×1440) en Ajustes,
     pero calienta bastante.
   Después puedes cambiar todo libremente; el perfil queda como "Personalizado".
5. **Código de apkvision quitado.** El sitio de descarga había agregado código
   al APK que **forzaba el idioma inglés**, mostraba un aviso "APKVISION.ORG" y
   consultaba "actualizaciones" por internet abriendo el navegador. No es parte
   del port y se eliminó.
6. **ID distinto** — `com.pes2017.recomp.es`, nombre **"PES 2017 ES"**. Se
   instala **junto** a la original sin borrarla (también se cambiaron los
   *authorities* y el permiso interno, que si no chocarían al instalar).

## Cómo regenerarlo

```bash
java -jar apktool.jar d original.apk -o dec
python3 -I scripts/aplicar_traduccion.py dec traduccion/strings_es419.xml
python3 -I scripts/traducir_smali.py dec
python3 -I scripts/aplicar_mejoras.py dec parches
java -jar apktool.jar b dec -o sin_firmar.apk
java -jar uber-apk-signer.jar -a sin_firmar.apk --ks pes2017-es.jks --ksAlias pes2017es
```

Usa siempre la **misma llave** (`pes2017-es.jks`) para firmar versiones nuevas.
Si no, Android no deja actualizar encima de la anterior. La llave no se sube al
repositorio (ver `.gitignore`).

## Notas

* Las partidas guardadas y los ajustes de la versión ES son independientes de
  los de la original. Para pasar tus partidas usa *Ajustes → Archivos del juego →
  Respaldar partidas* en la original y *Restaurar partidas* en la ES.
* El botón de "Buscar actualizaciones" apunta a la versión oficial en inglés.
  Si la instalas, se agrega como la app original, no encima de esta.
