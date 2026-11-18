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
# perfilS24(contexto):
#   Perfil optimizado para el Samsung Galaxy S24 Ultra (modelos SM-S928*:
#   Snapdragon 8 Gen 3 for Galaxy, GPU Adreno 750, 12 GB de RAM, pantalla
#   QHD+ 3120x1440 de 19.5:9 a 120 Hz con cámara perforada).
#
#   Se aplica UNA sola vez, en el primer inicio, y solo si el usuario todavía
#   no configuró nada. Después se pueden cambiar todos los ajustes libremente.
#     * Calidad de renderizado del partido al 100% (la Adreno 750 sobra para
#       la escena de 1280x720 de la consola).
#     * FSR activado: escala con nitidez de 720p a la pantalla QHD+.
#     * Suavizado de bordes (MSAA) activado.
#     * Multiplicador interno 1x: 2x se puede probar, pero calienta mucho.
#     * Bajar la calidad al calentarse: ACTIVADO (el S24 Ultra limita la GPU
#       cuando se calienta; así se pierde nitidez en vez de fluidez).
#     * Pantalla fija a 60 Hz: el juego va a 60 FPS; 120 Hz solo gasta batería
#       y hace irregular el ritmo de los cuadros.
#     * Pantalla panorámica: llena la pantalla 19.5:9 sin barras negras.
#     * Modo de poca memoria desactivado (tiene 12 GB).
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

    # Si ya se aplicó antes, no hacemos nada
    const-string v2, "es_perfil_s24"
    invoke-interface {v0, v2}, Landroid/content/SharedPreferences;->contains(Ljava/lang/String;)Z
    move-result v3
    if-nez v3, :cond_fin

    # ¿El usuario ya tiene un perfil elegido? (v4 = true si NO tiene)
    const-string v3, "performancePreset"
    const-string v4, ""
    invoke-interface {v0, v3, v4}, Landroid/content/SharedPreferences;->getString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;
    move-result-object v4
    invoke-virtual {v4}, Ljava/lang/String;->isEmpty()Z
    move-result v4

    invoke-interface {v0}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;
    move-result-object v0

    # Marcamos que ya se revisó este teléfono
    const/4 v1, 0x1
    invoke-interface {v0, v2, v1}, Landroid/content/SharedPreferences$Editor;->putBoolean(Ljava/lang/String;Z)Landroid/content/SharedPreferences$Editor;

    # Si el usuario ya tenía ajustes, solo guardamos la marca
    if-eqz v4, :cond_guardar

    const-string v2, "performancePreset"
    const-string v3, "CUSTOM"
    invoke-interface {v0, v2, v3}, Landroid/content/SharedPreferences$Editor;->putString(Ljava/lang/String;Ljava/lang/String;)Landroid/content/SharedPreferences$Editor;

    const-string v2, "sceneScale"
    const/16 v3, 0x64
    invoke-interface {v0, v2, v3}, Landroid/content/SharedPreferences$Editor;->putInt(Ljava/lang/String;I)Landroid/content/SharedPreferences$Editor;

    const-string v2, "renderScale"
    const/4 v3, 0x1
    invoke-interface {v0, v2, v3}, Landroid/content/SharedPreferences$Editor;->putInt(Ljava/lang/String;I)Landroid/content/SharedPreferences$Editor;

    const/4 v3, 0x1
    const-string v2, "multisampling"
    invoke-interface {v0, v2, v3}, Landroid/content/SharedPreferences$Editor;->putBoolean(Ljava/lang/String;Z)Landroid/content/SharedPreferences$Editor;
    const-string v2, "fsr"
    invoke-interface {v0, v2, v3}, Landroid/content/SharedPreferences$Editor;->putBoolean(Ljava/lang/String;Z)Landroid/content/SharedPreferences$Editor;
    const-string v2, "heatScale"
    invoke-interface {v0, v2, v3}, Landroid/content/SharedPreferences$Editor;->putBoolean(Ljava/lang/String;Z)Landroid/content/SharedPreferences$Editor;
    const-string v2, "prefer60Hz"
    invoke-interface {v0, v2, v3}, Landroid/content/SharedPreferences$Editor;->putBoolean(Ljava/lang/String;Z)Landroid/content/SharedPreferences$Editor;
    const-string v2, "widescreen"
    invoke-interface {v0, v2, v3}, Landroid/content/SharedPreferences$Editor;->putBoolean(Ljava/lang/String;Z)Landroid/content/SharedPreferences$Editor;

    const/4 v3, 0x0
    const-string v2, "lowMemory"
    invoke-interface {v0, v2, v3}, Landroid/content/SharedPreferences$Editor;->putBoolean(Ljava/lang/String;Z)Landroid/content/SharedPreferences$Editor;
    const-string v2, "loadScale"
    invoke-interface {v0, v2, v3}, Landroid/content/SharedPreferences$Editor;->putBoolean(Ljava/lang/String;Z)Landroid/content/SharedPreferences$Editor;

    :cond_guardar
    invoke-interface {v0}, Landroid/content/SharedPreferences$Editor;->apply()V
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    :cond_fin
    return-void

    # Si algo falla, la app sigue con sus valores normales
    :catch_0
    return-void
.end method
