.class public final Lcom/pes2017/recomp/Estabilidad;
.super Ljava/lang/Object;
.source "Estabilidad.java"

# ============================================================================
# Clase agregada en la versión en español.
#
# memoriaBaja(contexto, valorGuardado):
#   Devuelve si se debe activar el "Modo de poca memoria" (PES17_NO_SHADOW).
#
#   La propia app recomienda activarlo en teléfonos de 6 GB de RAM o menos,
#   porque Android cierra el partido en segundo plano cuando falta memoria.
#   Aquí se activa solo en ese caso:
#     * si el usuario ya lo tenía activado -> se respeta (true);
#     * si el usuario personalizó sus ajustes (perfil "CUSTOM") -> se respeta
#       lo que eligió, no se toca nada;
#     * si no, y el teléfono tiene 6.5 GiB de RAM total o menos (los teléfonos
#       de "6 GB" reportan unos 5.5 GiB) -> se activa (true).
# ============================================================================

.method public constructor <init>()V
    .locals 0
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V
    return-void
.end method

.method public static memoriaBaja(Landroid/content/Context;Z)Z
    .locals 6

    # Si ya está activado, no hay nada que decidir
    if-eqz p1, :cond_revisar
    return p1

    :cond_revisar
    :try_start_0
    # Leemos el perfil de calidad guardado en las preferencias "pes17"
    const-string v0, "pes17"
    const/4 v1, 0x0
    invoke-virtual {p0, v0, v1}, Landroid/content/Context;->getSharedPreferences(Ljava/lang/String;I)Landroid/content/SharedPreferences;
    move-result-object v0

    const-string v2, "performancePreset"
    const-string v3, ""
    invoke-interface {v0, v2, v3}, Landroid/content/SharedPreferences;->getString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;
    move-result-object v0

    # Perfil personalizado: se respeta la decisión del usuario
    const-string v2, "CUSTOM"
    invoke-virtual {v2, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v2
    if-eqz v2, :cond_medir
    return p1

    :cond_medir
    # Medimos la RAM total del teléfono
    const-string v0, "activity"
    invoke-virtual {p0, v0}, Landroid/content/Context;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;
    move-result-object v0
    check-cast v0, Landroid/app/ActivityManager;
    if-nez v0, :cond_hay_servicio
    return p1

    :cond_hay_servicio
    new-instance v2, Landroid/app/ActivityManager$MemoryInfo;
    invoke-direct {v2}, Landroid/app/ActivityManager$MemoryInfo;-><init>()V
    invoke-virtual {v0, v2}, Landroid/app/ActivityManager;->getMemoryInfo(Landroid/app/ActivityManager$MemoryInfo;)V
    iget-wide v2, v2, Landroid/app/ActivityManager$MemoryInfo;->totalMem:J

    # Umbral: 6.5 GiB = 0x1A0000000 bytes
    const-wide v4, 0x1a0000000L
    cmp-long v0, v2, v4
    if-gtz v0, :cond_normal
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    # Poca RAM: activamos el modo de poca memoria
    const/4 v0, 0x1
    return v0

    :cond_normal
    return p1

    # Ante cualquier error inesperado, dejamos el valor tal como estaba
    :catch_0
    return p1
.end method

# ============================================================================
# perfilS24(contexto)  — versión 2, enfocada en 60 FPS estables
#   Perfil para el Samsung Galaxy S24 Ultra (modelos SM-S928*: Snapdragon 8
#   Gen 3 for Galaxy, GPU Adreno 750, 12 GB de RAM, pantalla 3120x1440 a 120 Hz).
#
#   La versión 1 subía la escena al 100%, activaba FSR y la pantalla
#   panorámica: más carga que el perfil "Alto" que el autor del port calibró
#   para la Adreno 7xx. Esta versión vuelve a esa calibración oficial y suma
#   lo que ayuda a sostener 60 FPS:
#     * Escena al 75% (valor oficial: 44% menos píxeles, casi igual a la vista).
#     * MSAA activado (líneas de la cancha sin cortes), FSR desactivado.
#     * Límite 60 FPS, sin generación de cuadros, pantalla fija a 60 Hz.
#     * Bajar la calidad al calentarse: activado (el S24 Ultra baja la GPU
#       cuando se calienta; así pierde nitidez en vez de fluidez).
#     * Compilar todos los shaders al arrancar: el primer arranque tarda unos
#       minutos, pero el partido ya no tiene tirones por shaders.
#     * Pantalla panorámica desactivada: estira menús y marcador, y dibuja más
#       estadio (más trabajo). Se puede activar en Ajustes > Pantalla.
#     * Modo de poca memoria desactivado (tiene 12 GB).
#
#   Se aplica UNA vez (marca "es_perfil_s24_v2"), también encima del perfil
#   v1 de la versión anterior. Después se puede cambiar todo libremente.
# ============================================================================
.method public static perfilS24(Landroid/content/Context;)V
    .locals 5

    :try_start_0
    # ¿Es un Galaxy S24 Ultra? (SM-S928B, SM-S928U, SM-S928N, SM-S9280...)
    sget-object v0, Landroid/os/Build;->MODEL:Ljava/lang/String;
    if-eqz v0, :cond_fin
    const-string v1, "SM-S928"
    invoke-virtual {v0, v1}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z
    move-result v1
    if-eqz v1, :cond_fin

    const-string v0, "pes17"
    const/4 v1, 0x0
    invoke-virtual {p0, v0, v1}, Landroid/content/Context;->getSharedPreferences(Ljava/lang/String;I)Landroid/content/SharedPreferences;
    move-result-object v0

    # Si ya se aplicó esta versión del perfil, no hacemos nada
    const-string v2, "es_perfil_s24_v2"
    invoke-interface {v0, v2}, Landroid/content/SharedPreferences;->contains(Ljava/lang/String;)Z
    move-result v3
    if-nez v3, :cond_fin

    invoke-interface {v0}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;
    move-result-object v0

    const/4 v1, 0x1
    invoke-interface {v0, v2, v1}, Landroid/content/SharedPreferences$Editor;->putBoolean(Ljava/lang/String;Z)Landroid/content/SharedPreferences$Editor;

    # Los valores del perfil "Alto" oficial: se muestra como "Alto"
    const-string v2, "performancePreset"
    const-string v3, "HIGH"
    invoke-interface {v0, v2, v3}, Landroid/content/SharedPreferences$Editor;->putString(Ljava/lang/String;Ljava/lang/String;)Landroid/content/SharedPreferences$Editor;

    const-string v2, "sceneScale"
    const/16 v3, 0x4b
    invoke-interface {v0, v2, v3}, Landroid/content/SharedPreferences$Editor;->putInt(Ljava/lang/String;I)Landroid/content/SharedPreferences$Editor;

    const-string v2, "fpsLimit"
    const/16 v3, 0x3c
    invoke-interface {v0, v2, v3}, Landroid/content/SharedPreferences$Editor;->putInt(Ljava/lang/String;I)Landroid/content/SharedPreferences$Editor;

    const-string v2, "renderScale"
    const/4 v3, 0x1
    invoke-interface {v0, v2, v3}, Landroid/content/SharedPreferences$Editor;->putInt(Ljava/lang/String;I)Landroid/content/SharedPreferences$Editor;

    # Activados
    const/4 v3, 0x1
    const-string v2, "multisampling"
    invoke-interface {v0, v2, v3}, Landroid/content/SharedPreferences$Editor;->putBoolean(Ljava/lang/String;Z)Landroid/content/SharedPreferences$Editor;
    const-string v2, "heatScale"
    invoke-interface {v0, v2, v3}, Landroid/content/SharedPreferences$Editor;->putBoolean(Ljava/lang/String;Z)Landroid/content/SharedPreferences$Editor;
    const-string v2, "prefer60Hz"
    invoke-interface {v0, v2, v3}, Landroid/content/SharedPreferences$Editor;->putBoolean(Ljava/lang/String;Z)Landroid/content/SharedPreferences$Editor;
    const-string v2, "prewarmAllShaders"
    invoke-interface {v0, v2, v3}, Landroid/content/SharedPreferences$Editor;->putBoolean(Ljava/lang/String;Z)Landroid/content/SharedPreferences$Editor;
    const-string v2, "perfHint"
    invoke-interface {v0, v2, v3}, Landroid/content/SharedPreferences$Editor;->putBoolean(Ljava/lang/String;Z)Landroid/content/SharedPreferences$Editor;

    # Desactivados
    const/4 v3, 0x0
    const-string v2, "fsr"
    invoke-interface {v0, v2, v3}, Landroid/content/SharedPreferences$Editor;->putBoolean(Ljava/lang/String;Z)Landroid/content/SharedPreferences$Editor;
    const-string v2, "widescreen"
    invoke-interface {v0, v2, v3}, Landroid/content/SharedPreferences$Editor;->putBoolean(Ljava/lang/String;Z)Landroid/content/SharedPreferences$Editor;
    const-string v2, "lowMemory"
    invoke-interface {v0, v2, v3}, Landroid/content/SharedPreferences$Editor;->putBoolean(Ljava/lang/String;Z)Landroid/content/SharedPreferences$Editor;
    const-string v2, "loadScale"
    invoke-interface {v0, v2, v3}, Landroid/content/SharedPreferences$Editor;->putBoolean(Ljava/lang/String;Z)Landroid/content/SharedPreferences$Editor;
    const-string v2, "cap30"
    invoke-interface {v0, v2, v3}, Landroid/content/SharedPreferences$Editor;->putBoolean(Ljava/lang/String;Z)Landroid/content/SharedPreferences$Editor;
    const-string v2, "frameGenerationExperimental"
    invoke-interface {v0, v2, v3}, Landroid/content/SharedPreferences$Editor;->putBoolean(Ljava/lang/String;Z)Landroid/content/SharedPreferences$Editor;
    const-string v2, "blackGuard"
    invoke-interface {v0, v2, v3}, Landroid/content/SharedPreferences$Editor;->putBoolean(Ljava/lang/String;Z)Landroid/content/SharedPreferences$Editor;

    invoke-interface {v0}, Landroid/content/SharedPreferences$Editor;->apply()V
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    :cond_fin
    return-void

    # Si algo falla, la app sigue con sus valores normales
    :catch_0
    return-void
.end method

# ============================================================================
# Idioma del juego
#   Preferencia "gameLanguage" (archivo "pes17"):
#     "latam"  -> español, región México  (PES17_LANGUAGE=5, PES17_COUNTRY=22)
#     "espana" -> español, región España  (PES17_LANGUAGE=5, PES17_COUNTRY=31)
#     "ingles" -> inglés, región original (PES17_LANGUAGE=1, PES17_COUNTRY=6)
#   El motor parcheado (scripts/parchear_idioma_motor.py) lee esas variables
#   cuando el juego pregunta el idioma de la "consola".
# ============================================================================

# Devuelve el idioma guardado; por defecto "latam"
.method public static idiomaGuardado(Landroid/content/Context;)Ljava/lang/String;
    .locals 3
    const-string v0, "pes17"
    const/4 v1, 0x0
    invoke-virtual {p0, v0, v1}, Landroid/content/Context;->getSharedPreferences(Ljava/lang/String;I)Landroid/content/SharedPreferences;
    move-result-object v0
    const-string v1, "gameLanguage"
    const-string v2, "latam"
    invoke-interface {v0, v1, v2}, Landroid/content/SharedPreferences;->getString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;
    move-result-object v0
    if-nez v0, :cond_ok
    move-object v0, v2
    :cond_ok
    return-object v0
.end method

# Guarda el idioma elegido
.method public static guardarIdioma(Landroid/content/Context;Ljava/lang/String;)V
    .locals 2
    const-string v0, "pes17"
    const/4 v1, 0x0
    invoke-virtual {p0, v0, v1}, Landroid/content/Context;->getSharedPreferences(Ljava/lang/String;I)Landroid/content/SharedPreferences;
    move-result-object v0
    invoke-interface {v0}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;
    move-result-object v0
    const-string v1, "gameLanguage"
    invoke-interface {v0, v1, p1}, Landroid/content/SharedPreferences$Editor;->putString(Ljava/lang/String;Ljava/lang/String;)Landroid/content/SharedPreferences$Editor;
    invoke-interface {v0}, Landroid/content/SharedPreferences$Editor;->apply()V
    return-void
.end method

# Llamado por GameActivity antes de iniciar el motor
.method public static opcionesMotor(Landroid/content/Context;Lcom/pes2017/recomp/NativeBridge;)V
    .locals 5

    :try_start_0
    invoke-static {p0}, Lcom/pes2017/recomp/Estabilidad;->idiomaGuardado(Landroid/content/Context;)Ljava/lang/String;
    move-result-object v0

    # Por defecto: español latinoamericano (México)
    const-string v1, "5"
    const-string v2, "22"

    const-string v3, "espana"
    invoke-virtual {v3, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v4
    if-eqz v4, :cond_no_espana
    const-string v2, "31"
    :cond_no_espana

    const-string v3, "ingles"
    invoke-virtual {v3, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v4
    if-eqz v4, :cond_no_ingles
    const-string v1, "1"
    const-string v2, "6"
    :cond_no_ingles

    const-string v3, "PES17_LANGUAGE"
    invoke-virtual {p1, v3, v1}, Lcom/pes2017/recomp/NativeBridge;->nativeSetOption(Ljava/lang/String;Ljava/lang/String;)V
    const-string v3, "PES17_COUNTRY"
    invoke-virtual {p1, v3, v2}, Lcom/pes2017/recomp/NativeBridge;->nativeSetOption(Ljava/lang/String;Ljava/lang/String;)V
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    return-void

    :catch_0
    return-void
.end method

# Llamado al final de SettingsActivity.onCreate: conecta el selector de idioma
# (RadioGroup "idioma_juego" con botones "idioma_latam", "idioma_espana",
# "idioma_ingles" del layout de Ajustes).
.method public static configurarIdioma(Landroid/app/Activity;)V
    .locals 6

    :try_start_0
    invoke-virtual {p0}, Landroid/content/Context;->getResources()Landroid/content/res/Resources;
    move-result-object v0
    invoke-virtual {p0}, Landroid/content/Context;->getPackageName()Ljava/lang/String;
    move-result-object v1

    const-string v2, "idioma_juego"
    const-string v3, "id"
    invoke-virtual {v0, v2, v3, v1}, Landroid/content/res/Resources;->getIdentifier(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I
    move-result v2
    if-eqz v2, :cond_fin

    invoke-virtual {p0, v2}, Landroid/app/Activity;->findViewById(I)Landroid/view/View;
    move-result-object v2
    check-cast v2, Landroid/widget/RadioGroup;
    if-eqz v2, :cond_fin

    # Marcamos el botón del idioma guardado ("idioma_" + valor)
    invoke-static {p0}, Lcom/pes2017/recomp/Estabilidad;->idiomaGuardado(Landroid/content/Context;)Ljava/lang/String;
    move-result-object v4
    new-instance v5, Ljava/lang/StringBuilder;
    const-string v3, "idioma_"
    invoke-direct {v5, v3}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V
    invoke-virtual {v5, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    invoke-virtual {v5}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v4
    const-string v3, "id"
    invoke-virtual {v0, v4, v3, v1}, Landroid/content/res/Resources;->getIdentifier(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I
    move-result v4
    if-eqz v4, :cond_listener
    invoke-virtual {v2, v4}, Landroid/widget/RadioGroup;->check(I)V

    :cond_listener
    # Al cambiar la opción, se guarda (se aplica al siguiente inicio del juego)
    new-instance v3, Lcom/pes2017/recomp/Estabilidad$Idioma;
    invoke-direct {v3, p0}, Lcom/pes2017/recomp/Estabilidad$Idioma;-><init>(Landroid/content/Context;)V
    invoke-virtual {v2, v3}, Landroid/widget/RadioGroup;->setOnCheckedChangeListener(Landroid/widget/RadioGroup$OnCheckedChangeListener;)V
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    :cond_fin
    return-void

    :catch_0
    return-void
.end method
