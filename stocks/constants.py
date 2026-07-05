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
    AJUSTEMENT = "AJUSTEMENT", "Ajustement"
    INVENTAIRE = "INVENTAIRE", "Inventaire"
    PRODUCTION = "PRODUCTION", "Production"
    CONSOMMATION = "CONSOMMATION", "Consommation"
    RETOUR = "RETOUR", "Retour"
    REBUT = "REBUT", "Mise au rebut"


class SensMouvement(models.TextChoices):
    ENTREE = "ENTREE", "Entrée"
    SORTIE = "SORTIE", "Sortie"


class MethodeValorisation(models.TextChoices):
    PMP = "PMP", "Prix Moyen Pondéré"
    FIFO = "FIFO", "Premier entré, premier sorti"
    DMP = "DMP", "Dernier prix d'achat"
    NONE = "NONE", "Aucune valorisation"


class CategorieUnite(models.TextChoices):
    MASSE = "MASSE", "Masse"
    VOLUME = "VOLUME", "Volume"
    UNITE = "UNITE", "Unité"
    LONGUEUR = "LONGUEUR", "Longueur"
    SURFACE = "SURFACE", "Surface"
    TEMPS = "TEMPS", "Temps"
    MONNAIE = "MONNAIE", "Monnaie"
    AUTRE = "AUTRE", "Autre"


class StatutInventaire(models.TextChoices):
    BROUILLON = "BROUILLON", "Brouillon"
    EN_COURS = "EN_COURS", "En cours"
    VALIDE = "VALIDE", "Validé"
    ANNULE = "ANNULE", "Annulé"


COMPORTEMENT_PAR_DEFAUT = {
    "stockable": True,
    "vendable": True,
    "achetable": True,
    "perissable": False,
    "lot_obligatoire": False,
    "numero_serie": False,
    "inventoriable": True,
}


SENS_PAR_NATURE = {
    NatureMouvement.ENTREE: SensMouvement.ENTREE,
    NatureMouvement.SORTIE: SensMouvement.SORTIE,
    NatureMouvement.TRANSFERT: SensMouvement.SORTIE,
    NatureMouvement.AJUSTEMENT: SensMouvement.ENTREE,
    NatureMouvement.INVENTAIRE: SensMouvement.ENTREE,
    NatureMouvement.PRODUCTION: SensMouvement.ENTREE,
    NatureMouvement.CONSOMMATION: SensMouvement.SORTIE,
    NatureMouvement.RETOUR: SensMouvement.ENTREE,
    NatureMouvement.REBUT: SensMouvement.SORTIE,
}
