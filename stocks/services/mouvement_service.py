from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from stocks.models import (
    MouvementStock,
    Depot,
    Article,
    Lot,
    Valorisation,
    JournalStock,
)


class MouvementStockService:

    @staticmethod
    @transaction.atomic
    def entree_stock(
        article,
        depot,
        quantite,
        prix_unitaire=None,
        lot=None,
        emplacement=None,
        libelle="",
        reference=None,
        bon_reception=None,
        bon_commande=None,
        created_by="",
    ):
        if reference is None:
            reference = f"ENT-{timezone.now().strftime('%Y%m%d%H%M%S%f')}-{article.id}"

        mouvement = MouvementStock.objects.create(
            reference=reference,
            type_mouvement="ENTREE",
            article=article,
            depot=depot,
            quantite=abs(Decimal(quantite)),
            prix_unitaire=prix_unitaire,
            cout_total=abs(Decimal(quantite)) * prix_unitaire if prix_unitaire else None,
            date_mouvement=timezone.now(),
            libelle=libelle,
            emplacement=emplacement,
            lot=lot,
            bon_reception=bon_reception,
            bon_commande=bon_commande,
            created_by=created_by,
            valide=True,
        )
        _journaliser(mouvement, created_by)
        if prix_unitaire:
            _mettre_a_jour_valorisation(article, depot, abs(Decimal(quantite)), prix_unitaire)
        return mouvement

    @staticmethod
    @transaction.atomic
    def sortie_stock(
        article,
        depot,
        quantite,
        prix_unitaire=None,
        lot=None,
        emplacement=None,
        libelle="",
        reference=None,
        bon_livraison=None,
        created_by="",
    ):
        if reference is None:
            reference = f"SOR-{timezone.now().strftime('%Y%m%d%H%M%S%f')}-{article.id}"

        qte = abs(Decimal(quantite))
        stock_actuel = _stock_article_depot(article, depot)
        if stock_actuel < qte:
            raise ValueError(
                f"Stock insuffisant pour {article.code} @ {depot.code}: "
                f"demandé {qte}, disponible {stock_actuel}"
            )

        mouvement = MouvementStock.objects.create(
            reference=reference,
            type_mouvement="SORTIE",
            article=article,
            depot=depot,
            quantite=-qte,
            prix_unitaire=prix_unitaire,
            cout_total=qte * prix_unitaire if prix_unitaire else None,
            date_mouvement=timezone.now(),
            libelle=libelle,
            emplacement=emplacement,
            lot=lot,
            bon_livraison=bon_livraison,
            created_by=created_by,
            valide=True,
        )
        _journaliser(mouvement, created_by)
        return mouvement

    @staticmethod
    @transaction.atomic
    def transferer(
        article,
        depot_source,
        depot_destination,
        quantite,
        lot=None,
        libelle="",
        reference=None,
        created_by="",
    ):
        if reference is None:
            now_str = timezone.now().strftime('%Y%m%d%H%M%S%f')
            reference = f"TRF-{now_str}-{article.id}"

        qte = abs(Decimal(quantite))
        if _stock_article_depot(article, depot_source) < qte and lot is None:
            raise ValueError(
                f"Stock insuffisant pour transfert de {article.code} @ {depot_source.code}: "
                f"demandé {qte}, disponible {_stock_article_depot(article, depot_source)}"
            )

        if lot and lot.quantite_restante < qte:
            raise ValueError(
                f"Quantité restante insuffisante dans le lot {lot.numero_lot}: "
                f"demandé {qte}, restant {lot.quantite_restante}"
            )

        sortie = MouvementStock.objects.create(
            reference=reference,
            type_mouvement="TRANSFERT",
            article=article,
            depot=depot_source,
            depot_destination=depot_destination,
            quantite=-qte,
            lot=lot,
            date_mouvement=timezone.now(),
            libelle=libelle or f"Transfert vers {depot_destination.libelle}",
            created_by=created_by,
            valide=True,
        )
        _journaliser(sortie, created_by)

        entree = MouvementStock.objects.create(
            reference=f"{reference}-DEST",
            type_mouvement="ENTREE",
            article=article,
            depot=depot_destination,
            depot_destination=depot_source,
            quantite=qte,
            lot=lot,
            date_mouvement=timezone.now(),
            libelle=libelle or f"Transfert depuis {depot_source.libelle}",
            created_by=created_by,
            valide=True,
        )
        _journaliser(entree, created_by)

        return sortie

    @staticmethod
    @transaction.atomic
    def valider_mouvement(mouvement_id, created_by=""):
        mouvement = MouvementStock.objects.get(id=mouvement_id)
        if mouvement.valide:
            return mouvement
        mouvement.valide = True
        mouvement.save(update_fields=["valide"])
        _journaliser(mouvement, created_by)

        if mouvement.prix_unitaire and mouvement.type_mouvement == "ENTREE":
            _mettre_a_jour_valorisation(
                mouvement.article,
                mouvement.depot,
                abs(mouvement.quantite),
                mouvement.prix_unitaire,
            )
        return mouvement


def _stock_article_depot(article, depot):
    from django.db.models import Sum
    entrees = MouvementStock.objects.filter(
        article=article, depot=depot, valide=True,
        type_mouvement__in=["ENTREE", "TRANSFERT"],
    ).aggregate(total=Sum("quantite"))["total"] or Decimal("0")

    sorties = MouvementStock.objects.filter(
        article=article, depot=depot, valide=True,
        type_mouvement__in=["SORTIE", "REBUT"],
    ).aggregate(total=Sum("quantite"))["total"] or Decimal("0")

    return entrees - abs(sorties)


def _journaliser(mouvement, created_by=""):
    stock_avant = _stock_article_depot(mouvement.article, mouvement.depot)

    if mouvement.type_mouvement in ("ENTREE",):
        stock_apres = stock_avant + abs(mouvement.quantite)
    elif mouvement.type_mouvement == "TRANSFERT":
        stock_apres = stock_avant - abs(mouvement.quantite)
    else:
        stock_apres = stock_avant - abs(mouvement.quantite)

    JournalStock.objects.create(
        mouvement=mouvement,
        article=mouvement.article,
        depot=mouvement.depot,
        date=mouvement.date_mouvement,
        type_mouvement=mouvement.type_mouvement,
        quantite=mouvement.quantite,
        stock_avant=stock_avant,
        stock_apres=stock_apres,
        cout_unitaire=mouvement.prix_unitaire,
        libelle=mouvement.libelle,
        created_by=created_by or mouvement.created_by,
    )


def _mettre_a_jour_valorisation(article, depot, quantite, prix_unitaire):
    valorisation, created = Valorisation.objects.get_or_create(
        article=article,
        depot=depot,
        defaults={
            "methode": article.methode_valorisation,
            "cout_unitaire_moyen": prix_unitaire,
            "quantite_totale": quantite,
            "valeur_totale": quantite * prix_unitaire,
        },
    )
    if not created:
        valorisation.mettre_a_jour_pmp(quantite, prix_unitaire)
