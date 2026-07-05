from django.db import models
from stocks.constants import SOURCES_SYSTEME


class SourceOperation(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Code")
    nom = models.CharField(max_length=255, verbose_name="Nom")
    active = models.BooleanField(default=True, verbose_name="Active")
    systeme = models.BooleanField(default=False, verbose_name="Système")

    class Meta:
        verbose_name = "Opération source"
        verbose_name_plural = "Opérations source"
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} — {self.nom}"

    @classmethod
    def seed(cls):
        for code, nom in SOURCES_SYSTEME.items():
            cls.objects.get_or_create(
                code=code,
                defaults={"nom": nom, "systeme": True},
            )
