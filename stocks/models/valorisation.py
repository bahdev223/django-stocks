from django.db import models


class Valorisation(models.Model):
    article = models.ForeignKey(
        "Article",
        on_delete=models.CASCADE,
        related_name="valorisations",
        verbose_name="Article",
    )
    depot = models.ForeignKey(
        "Depot",
        on_delete=models.CASCADE,
        related_name="valorisations",
        verbose_name="Dépôt",
    )
    methode = models.CharField(
        max_length=10,
        choices=[
            ("PMP", "Prix Moyen Pondéré"),
            ("FIFO", "Premier entré, premier sorti"),
            ("STANDARD", "Coût standard"),
            ("NONE", "Aucune"),
        ],
        default="PMP",
        verbose_name="Méthode",
    )
    cout_unitaire_moyen = models.DecimalField(
        max_digits=18, decimal_places=6, default=0,
        verbose_name="Coût unitaire moyen",
    )
    quantite_totale = models.DecimalField(
        max_digits=18, decimal_places=6, default=0,
        verbose_name="Quantité totale",
    )
    valeur_totale = models.DecimalField(
        max_digits=18, decimal_places=6, default=0,
        verbose_name="Valeur totale",
    )
    derniere_mise_a_jour = models.DateTimeField(
        auto_now=True, verbose_name="Dernière mise à jour",
    )

    class Meta:
        verbose_name = "Valorisation"
        verbose_name_plural = "Valorisations"
        unique_together = [["article", "depot"]]

    def __str__(self):
        return f"{self.article.code} @ {self.depot.code} — {self.methode}"


class CoucheValorisation(models.Model):
    """Couche FIFO — chaque entrée en stock crée une couche avec son prix."""
    article = models.ForeignKey(
        "Article",
        on_delete=models.CASCADE,
        related_name="couches_valorisation",
        verbose_name="Article",
    )
    depot = models.ForeignKey(
        "Depot",
        on_delete=models.CASCADE,
        related_name="couches_valorisation",
        verbose_name="Dépôt",
    )
    quantite_restante = models.DecimalField(
        max_digits=18, decimal_places=6, verbose_name="Quantité restante",
    )
    prix_unitaire = models.DecimalField(
        max_digits=18, decimal_places=6, verbose_name="Prix unitaire",
    )
    date_entree = models.DateTimeField(verbose_name="Date d'entrée")
    mouvement = models.ForeignKey(
        "MouvementStock",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="couches_valorisation",
        verbose_name="Mouvement d'origine",
    )
    lot = models.ForeignKey(
        "Lot",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="couches_valorisation",
        verbose_name="Lot",
    )

    class Meta:
        verbose_name = "Couche de valorisation"
        verbose_name_plural = "Couches de valorisation"
        ordering = ["date_entree", "id"]
        indexes = [
            models.Index(fields=["article", "depot", "date_entree"]),
        ]

    def __str__(self):
        return f"{self.article.code} @ {self.depot.code} — {self.quantite_restante} x {self.prix_unitaire}"
