from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from stocks.constants import NatureMouvement
from stocks.models import MouvementStock, Valorisation, JournalStock


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
        nature=NatureMouvement.ENTREE,
        reference=None,
        source=None,
        created_by="",
    ):
        if reference is None:
            reference = f"E-{timezone.now().strftime('%Y%m%d%H%M%S%f')}-{article.id}"

        mouvement = MouvementStock(
            reference=reference,
            nature=nature,
            article=article,
            depot=depot,
            quantite=abs(Decimal(quantite)),
            prix_unitaire=prix_unitaire,
            cout_total=abs(Decimal(quantite)) * prix_unitaire if prix_unitaire else None,
            date_mouvement=timezone.now(),
            libelle=libelle,
            emplacement=emplacement,
            lot=lot,
            created_by=created_by,
            valide=True,
        )
        if source is not None:
            mouvement.source = source
        mouvement.save()
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
        nature=NatureMouvement.SORTIE,
        reference=None,
        source=None,
        created_by="",
    ):
        if reference is None:
            reference = f"S-{timezone.now().strftime('%Y%m%d%H%M%S%f')}-{article.id}"

        qte = abs(Decimal(quantite))
        stock_actuel = _stock_article_depot(article, depot)
        if stock_actuel < qte:
            raise ValueError(
                f"Stock insuffisant pour {article.code} @ {depot.code}: "
                f"demandé {qte}, disponible {stock_actuel}"
            )

        mouvement = MouvementStock(
            reference=reference,
            nature=nature,
            article=article,
            depot=depot,
            quantite=-qte,
            prix_unitaire=prix_unitaire,
            cout_total=qte * prix_unitaire if prix_unitaire else None,
            date_mouvement=timezone.now(),
            libelle=libelle,
            emplacement=emplacement,
            lot=lot,
            created_by=created_by,
            valide=True,
        )
        if source is not None:
            mouvement.source = source
        mouvement.save()
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
        source=None,
        created_by="",
    ):
        now_str = timezone.now().strftime('%Y%m%d%H%M%S%f')
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

        sortie = MouvementStockService.sortie_stock(
            article=article,
            depot=depot_source,
            quantite=qte,
            lot=lot,
            libelle=libelle or f"Transfert vers {depot_destination.libelle}",
            reference=f"TRF-S-{now_str}-{article.id}",
            source=source,
            created_by=created_by,
        )

        entree = MouvementStockService.entree_stock(
            article=article,
            depot=depot_destination,
            quantite=qte,
            lot=lot,
            prix_unitaire=sortie.prix_unitaire,
            libelle=libelle or f"Transfert depuis {depot_source.libelle}",
            nature=NatureMouvement.TRANSFERT,
            reference=f"TRF-E-{now_str}-{article.id}",
            source=source,
            created_by=created_by,
        )

        return sortie, entree


def _stock_article_depot(article, depot):
    from django.db.models import Sum, Q
    entrees = MouvementStock.objects.filter(
        article=article, depot=depot, valide=True,
    ).filter(
        Q(nature__in=["ENTREE", "TRANSFERT", "RETOUR", "PRODUCTION"]) | Q(quantite__gt=0),
    ).aggregate(total=Sum("quantite"))["total"] or Decimal("0")

    sorties = MouvementStock.objects.filter(
        article=article, depot=depot, valide=True,
    ).filter(
        Q(nature__in=["SORTIE", "REBUT", "CONSOMMATION"]) | Q(quantite__lt=0),
    ).aggregate(total=Sum("quantite"))["total"] or Decimal("0")

    return abs(entrees) - abs(sorties)


def _journaliser(mouvement, created_by=""):
    stock_avant = _stock_article_depot(mouvement.article, mouvement.depot)
    stock_apres = stock_avant + mouvement.quantite

    JournalStock.objects.create(
        mouvement=mouvement,
        article=mouvement.article,
        depot=mouvement.depot,
        date=mouvement.date_mouvement,
        nature=mouvement.nature,
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
