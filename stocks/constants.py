from django.db import models


class TypesArticle(models.TextChoices):
    MATIERE_PREMIERE = "MATIERE_PREMIERE", "Matière première"
    PRODUIT_FINI = "PRODUIT_FINI", "Produit fini"
    PRODUIT_SEMI_FINI = "PRODUIT_SEMI_FINI", "Produit semi-fini"
    EMBALLAGE = "EMBALLAGE", "Emballage"
    CONSOMMABLE = "CONSOMMABLE", "Consommable"
    FOURNITURE = "FOURNITURE", "Fourniture"
    PIECE_DETACHEE = "PIECE_DETACHEE", "Pièce détachée"
    SERVICE_STOCKABLE = "SERVICE_STOCKABLE", "Service stockable"
    AUTRE = "AUTRE", "Autre"


class NatureMouvement(models.TextChoices):
    ENTREE = "ENTREE", "Entrée"
    SORTIE = "SORTIE", "Sortie"
    TRANSFERT = "TRANSFERT", "Transfert"
    INVENTAIRE = "INVENTAIRE", "Inventaire"
    REBUT = "REBUT", "Mise au rebut"
    AJUSTEMENT = "AJUSTEMENT", "Ajustement"


class MethodeValorisation(models.TextChoices):
    PMP = "PMP", "Prix Moyen Pondéré"
    FIFO = "FIFO", "Premier entré, premier sorti"
    DMP = "DMP", "Dernier prix d'achat"
    NONE = "NONE", "Aucune valorisation"


class StatutDocument(models.TextChoices):
    BROUILLON = "BROUILLON", "Brouillon"
    CONFIRME = "CONFIRME", "Confirmé"
    VALIDE = "VALIDE", "Validé"
    ANNULE = "ANNULE", "Annulé"


class CategorieUnite(models.TextChoices):
    MASSE = "MASSE", "Masse"
    VOLUME = "VOLUME", "Volume"
    UNITE = "UNITE", "Unité"
    LONGUEUR = "LONGUEUR", "Longueur"
    SURFACE = "SURFACE", "Surface"
    TEMPS = "TEMPS", "Temps"
    MONNAIE = "MONNAIE", "Monnaie"
    AUTRE = "AUTRE", "Autre"


COMPORTEMENT_PAR_DEFAUT = {
    "stockable": True,
    "vendable": True,
    "achetable": True,
    "perissable": False,
    "lot_obligatoire": False,
    "numero_serie": False,
    "inventoriable": True,
}
