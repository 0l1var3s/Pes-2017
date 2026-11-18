.class public final Lcom/pes2017/recomp/Estabilidad$Idioma;
.super Ljava/lang/Object;
.source "Estabilidad.java"

# implements
.implements Landroid/widget/RadioGroup$OnCheckedChangeListener;

# ============================================================================
# Escucha el selector "Idioma del juego" de Ajustes.
# Del botón marcado ("idioma_latam", "idioma_espana", "idioma_ingles") toma
# lo que va después de "idioma_" y lo guarda como preferencia gameLanguage.
# ============================================================================

# instance fields
.field private final contexto:Landroid/content/Context;

.method public constructor <init>(Landroid/content/Context;)V
    .locals 0
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V
    iput-object p1, p0, Lcom/pes2017/recomp/Estabilidad$Idioma;->contexto:Landroid/content/Context;
    return-void
.end method

.method public final onCheckedChanged(Landroid/widget/RadioGroup;I)V
    .locals 4

    :try_start_0
    iget-object v0, p0, Lcom/pes2017/recomp/Estabilidad$Idioma;->contexto:Landroid/content/Context;
    invoke-virtual {v0}, Landroid/content/Context;->getResources()Landroid/content/res/Resources;
    move-result-object v1
    invoke-virtual {v1, p2}, Landroid/content/res/Resources;->getResourceEntryName(I)Ljava/lang/String;
    move-result-object v1

    const-string v2, "idioma_"
    invoke-virtual {v1, v2}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z
    move-result v3
    if-eqz v3, :cond_fin

    invoke-virtual {v2}, Ljava/lang/String;->length()I
    move-result v3
    invoke-virtual {v1, v3}, Ljava/lang/String;->substring(I)Ljava/lang/String;
    move-result-object v1

    invoke-static {v0, v1}, Lcom/pes2017/recomp/Estabilidad;->guardarIdioma(Landroid/content/Context;Ljava/lang/String;)V
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    :cond_fin
    return-void

    :catch_0
    return-void
.end method
