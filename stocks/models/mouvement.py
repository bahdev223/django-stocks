from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from stocks.constants import NatureMouvement


class MouvementStock(models.Model):
    reference = models.CharField(max_length=100, unique=True, verbose_name="Référence")
    nature = models.CharField(
        max_length=20,
        choices=NatureMouvement.choices,
        verbose_name="Nature du mouvement",
    )
    article = models.ForeignKey(
        "Article",
        on_delete=models.PROTECT,
        related_name="mouvements",
        verbose_name="Article",
    )
    depot = models.ForeignKey(
        "Depot",
        on_delete=models.PROTECT,
        related_name="mouvements",
        verbose_name="Dépôt",
    )
    emplacement = models.ForeignKey(
        "Emplacement",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mouvements",
        verbose_name="Emplacement",
    )
    lot = models.ForeignKey(
        "Lot",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mouvements",
        verbose_name="Lot",
    )
    quantite = models.DecimalField(
        max_digits=18, decimal_places=6, verbose_name="Quantité",
    )
    prix_unitaire = models.DecimalField(
        max_digits=18, decimal_places=6, null=True, blank=True,
        verbose_name="Prix unitaire",
    )
    cout_total = models.DecimalField(
        max_digits=18, decimal_places=6, null=True, blank=True,
        verbose_name="Coût total",
    )
    date_mouvement = models.DateTimeField(verbose_name="Date du mouvement")
    libelle = models.CharField(max_length=500, blank=True, verbose_name="Libellé")
    valide = models.BooleanField(default=False, verbose_name="Validé")

    source_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Type de source",
    )
    source_object_id = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="ID source",
    )
    source = GenericForeignKey("source_content_type", "source_object_id")

    created_by = models.CharField(
        max_length=255, blank=True, verbose_name="Créé par",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")

    class Meta:
        verbose_name = "Mouvement de stock"
        verbose_name_plural = "Mouvements de stock"
        ordering = ["-date_mouvement"]
        indexes = [
            models.Index(fields=["article", "depot"]),
            models.Index(fields=["nature"]),
            models.Index(fields=["date_mouvement"]),
            models.Index(fields=["valide"]),
            models.Index(fields=["source_content_type", "source_object_id"]),
        ]

    def __str__(self):
        return f"{self.reference} — {self.nature} {self.quantite} x {self.article.code}"
