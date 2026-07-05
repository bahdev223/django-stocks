from django.db import models


class JournalStock(models.Model):
    mouvement = models.ForeignKey(
        "MouvementStock",
        on_delete=models.PROTECT,
        related_name="ecritures_journal",
        verbose_name="Mouvement",
    )
    article = models.ForeignKey(
        "Article",
        on_delete=models.PROTECT,
        related_name="ecritures_journal",
        verbose_name="Article",
    )
    depot = models.ForeignKey(
        "Depot",
        on_delete=models.PROTECT,
        related_name="ecritures_journal",
        verbose_name="Dépôt",
    )
    date = models.DateTimeField(verbose_name="Date")
    nature = models.CharField(
        max_length=20, verbose_name="Nature du mouvement",
    )
    quantite = models.DecimalField(
        max_digits=18, decimal_places=6, verbose_name="Quantité",
    )
    stock_avant = models.DecimalField(
        max_digits=18, decimal_places=6, verbose_name="Stock avant",
    )
    stock_apres = models.DecimalField(
        max_digits=18, decimal_places=6, verbose_name="Stock après",
    )
    cout_unitaire = models.DecimalField(
        max_digits=18, decimal_places=6, null=True, blank=True,
        verbose_name="Coût unitaire",
    )
    libelle = models.CharField(max_length=500, blank=True, verbose_name="Libellé")
    created_by = models.CharField(
        max_length=255, blank=True, verbose_name="Créé par",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")

    class Meta:
        verbose_name = "Écriture du journal de stock"
        verbose_name_plural = "Journal de stock"
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["article", "depot"]),
            models.Index(fields=["date"]),
        ]

    def __str__(self):
        return f"{self.date} — {self.article.code} — {self.nature} ({self.quantite})"
