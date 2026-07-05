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
            ("DMP", "Dernier prix d'achat"),
            ("NONE", "Aucune"),
        ],
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
        return f"{self.article.code} @ {self.depot.code} — PMP={self.cout_unitaire_moyen}"

    def mettre_a_jour_pmp(self, quantite_entree, prix_unitaire_entree):
        ancienne_valeur = self.quantite_totale * self.cout_unitaire_moyen
        nouvelle_valeur = quantite_entree * prix_unitaire_entree
        nouvelle_quantite = self.quantite_totale + quantite_entree
        if nouvelle_quantite > 0:
            self.cout_unitaire_moyen = (
                ancienne_valeur + nouvelle_valeur
            ) / nouvelle_quantite
        self.quantite_totale = nouvelle_quantite
        self.valeur_totale = self.quantite_totale * self.cout_unitaire_moyen
        self.save(update_fields=["cout_unitaire_moyen", "quantite_totale", "valeur_totale"])
