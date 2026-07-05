from django.db import models
from stocks.constants import NatureMouvement, StatutDocument


class BonCommande(models.Model):
    reference = models.CharField(max_length=100, unique=True, verbose_name="Référence")
    fournisseur = models.CharField(max_length=500, verbose_name="Fournisseur")
    date_commande = models.DateField(verbose_name="Date de commande")
    date_livraison_prevue = models.DateField(
        null=True, blank=True, verbose_name="Livraison prévue le",
    )
    statut = models.CharField(
        max_length=20,
        choices=StatutDocument.choices,
        default=StatutDocument.BROUILLON,
        verbose_name="Statut",
    )
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        verbose_name = "Bon de commande"
        verbose_name_plural = "Bons de commande"
        ordering = ["-date_commande"]

    def __str__(self):
        return f"BC {self.reference} — {self.fournisseur}"


class BonReception(models.Model):
    reference = models.CharField(max_length=100, unique=True, verbose_name="Référence")
    bon_commande = models.ForeignKey(
        BonCommande,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="receptions",
        verbose_name="Bon de commande lié",
    )
    date_reception = models.DateField(verbose_name="Date de réception")
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")

    class Meta:
        verbose_name = "Bon de réception"
        verbose_name_plural = "Bons de réception"
        ordering = ["-date_reception"]

    def __str__(self):
        return f"BR {self.reference}"


class BonLivraison(models.Model):
    reference = models.CharField(max_length=100, unique=True, verbose_name="Référence")
    destinataire = models.CharField(max_length=500, verbose_name="Destinataire")
    date_livraison = models.DateField(verbose_name="Date de livraison")
    notes = models.TextField(blank=True, verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")

    class Meta:
        verbose_name = "Bon de livraison"
        verbose_name_plural = "Bons de livraison"
        ordering = ["-date_livraison"]

    def __str__(self):
        return f"BL {self.reference}"


class LigneMouvement(models.Model):
    article = models.ForeignKey(
        "Article",
        on_delete=models.PROTECT,
        related_name="lignes_mouvement",
        verbose_name="Article",
    )
    quantite = models.DecimalField(max_digits=18, decimal_places=6, verbose_name="Quantité")
    prix_unitaire = models.DecimalField(
        max_digits=18, decimal_places=6, null=True, blank=True,
        verbose_name="Prix unitaire",
    )

    class Meta:
        verbose_name = "Ligne de mouvement"
        verbose_name_plural = "Lignes de mouvement"
        abstract = True


class MouvementStock(models.Model):
    reference = models.CharField(max_length=100, unique=True, verbose_name="Référence")
    type_mouvement = models.CharField(
        max_length=20,
        choices=NatureMouvement.choices,
        verbose_name="Type de mouvement",
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
    depot_destination = models.ForeignKey(
        "Depot",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="mouvements_entrants",
        verbose_name="Dépôt de destination",
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

    bon_commande = models.ForeignKey(
        BonCommande,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mouvements",
        verbose_name="Bon de commande",
    )
    bon_reception = models.ForeignKey(
        BonReception,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mouvements",
        verbose_name="Bon de réception",
    )
    bon_livraison = models.ForeignKey(
        BonLivraison,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mouvements",
        verbose_name="Bon de livraison",
    )

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
            models.Index(fields=["type_mouvement"]),
            models.Index(fields=["date_mouvement"]),
            models.Index(fields=["valide"]),
        ]

    def __str__(self):
        return f"{self.reference} — {self.type_mouvement} {self.quantite} x {self.article.code}"
