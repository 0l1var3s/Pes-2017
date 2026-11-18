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
