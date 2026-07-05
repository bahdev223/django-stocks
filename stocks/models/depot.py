from django.db import models


class Depot(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Code")
    libelle = models.CharField(max_length=255, verbose_name="Libellé")
    adresse = models.TextField(blank=True, verbose_name="Adresse")
    est_actif = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")

    class Meta:
        verbose_name = "Dépôt"
        verbose_name_plural = "Dépôts"
        ordering = ["code"]

    def __str__(self):
        return f"[{self.code}] {self.libelle}"


class Emplacement(models.Model):
    depot = models.ForeignKey(
        Depot,
        on_delete=models.CASCADE,
        related_name="emplacements",
        verbose_name="Dépôt",
    )
    code = models.CharField(max_length=50, verbose_name="Code")
    libelle = models.CharField(max_length=255, verbose_name="Libellé")
    description = models.TextField(blank=True, verbose_name="Description")

    class Meta:
        verbose_name = "Emplacement"
        verbose_name_plural = "Emplacements"
        ordering = ["depot", "code"]
        unique_together = [["depot", "code"]]

    def __str__(self):
        return f"{self.depot.code} / {self.code}"
