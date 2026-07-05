from decimal import Decimal
from django.test import TestCase, override_settings
from stocks.models import (
    TypeArticle, Unite, ComportementArticle, Article,
    Depot, SourceOperation, CoucheValorisation,
)
from stocks.services import ArticleService, MouvementStockService
from stocks.valorisation import ValuationRegistry, PMPStrategy, FIFOStrategy, StandardCostStrategy
from stocks.valorisation.base import BaseValuationStrategy


class ValuationStrategyRegistryTest(TestCase):
    def test_strategies_enregistrees(self):
        self.assertIsNotNone(ValuationRegistry.get_strategy("PMP"))
        self.assertIsNotNone(ValuationRegistry.get_strategy("FIFO"))
        self.assertIsNotNone(ValuationRegistry.get_strategy("STANDARD"))
        self.assertIsNotNone(ValuationRegistry.get_strategy("INCONNU"))

    def test_fallback_sur_pmp(self):
        strategy = ValuationRegistry.get_strategy("INCONNU")
        self.assertIs(strategy, PMPStrategy)


class PMPStrategyTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        SourceOperation.seed()

    def setUp(self):
        TypeArticle.objects.create(code="MATIERE_PREMIERE", libelle="M.P.")
        Unite.objects.create(code="KG", libelle="Kg")
        self.article = ArticleService.creer_article(
            code="FAR", designation="Farine",
            type_article_code="MATIERE_PREMIERE",
            unite_code="KG",
            methode_valorisation="PMP",
        )
        self.depot = Depot.objects.create(code="MAG", libelle="Magasin")
        self.src = SourceOperation.objects.get(code="ACHAT")

    def test_pmp_deux_entrees(self):
        MouvementStockService.entree_stock(
            article=self.article, depot=self.depot,
            quantite=100, prix_unitaire=Decimal("1.00"),
            source_operation=self.src,
        )
        MouvementStockService.entree_stock(
            article=self.article, depot=self.depot,
            quantite=100, prix_unitaire=Decimal("2.00"),
            source_operation=self.src,
        )
        from stocks.models import Valorisation
        v = Valorisation.objects.get(article=self.article, depot=self.depot)
        self.assertEqual(v.cout_unitaire_moyen, Decimal("1.50"))
        self.assertEqual(v.quantite_totale, Decimal("200"))
        self.assertEqual(v.valeur_totale, Decimal("300"))

    def test_pmp_sortie_conserve_pmp(self):
        MouvementStockService.entree_stock(
            article=self.article, depot=self.depot,
            quantite=100, prix_unitaire=Decimal("2.00"),
            source_operation=self.src,
        )
        MouvementStockService.sortie_stock(
            article=self.article, depot=self.depot,
            quantite=30, source_operation=SourceOperation.objects.get(code="VENTE"),
        )
        from stocks.models import Valorisation
        v = Valorisation.objects.get(article=self.article, depot=self.depot)
        self.assertEqual(v.cout_unitaire_moyen, Decimal("2.00"))
        self.assertEqual(v.quantite_totale, Decimal("70"))


class FIFOStrategyTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        SourceOperation.seed()

    def setUp(self):
        TypeArticle.objects.create(code="MATIERE_PREMIERE", libelle="M.P.")
        Unite.objects.create(code="UN", libelle="Unité")
        self.article = ArticleService.creer_article(
            code="ART", designation="Article FIFO",
            type_article_code="MATIERE_PREMIERE",
            unite_code="UN",
            methode_valorisation="FIFO",
        )
        self.depot = Depot.objects.create(code="MAG", libelle="Magasin")
        self.src = SourceOperation.objects.get(code="ACHAT")

    def test_fifo_entrees_creent_couches(self):
        MouvementStockService.entree_stock(
            article=self.article, depot=self.depot,
            quantite=10, prix_unitaire=Decimal("1.00"),
            source_operation=self.src,
        )
        MouvementStockService.entree_stock(
            article=self.article, depot=self.depot,
            quantite=10, prix_unitaire=Decimal("2.00"),
            source_operation=self.src,
        )
        couches = CoucheValorisation.objects.filter(
            article=self.article, depot=self.depot,
        ).order_by("date_entree")
        self.assertEqual(couches.count(), 2)
        self.assertEqual(couches[0].prix_unitaire, Decimal("1.00"))
        self.assertEqual(couches[1].prix_unitaire, Decimal("2.00"))

    def test_fifo_sortie_consume_premiere_couche(self):
        MouvementStockService.entree_stock(
            article=self.article, depot=self.depot,
            quantite=10, prix_unitaire=Decimal("1.00"),
            source_operation=self.src,
        )
        MouvementStockService.entree_stock(
            article=self.article, depot=self.depot,
            quantite=10, prix_unitaire=Decimal("2.00"),
            source_operation=self.src,
        )
        MouvementStockService.sortie_stock(
            article=self.article, depot=self.depot,
            quantite=8, source_operation=SourceOperation.objects.get(code="VENTE"),
        )
        couche1 = CoucheValorisation.objects.filter(
            article=self.article, depot=self.depot,
        ).order_by("date_entree")[0]
        self.assertEqual(couche1.quantite_restante, Decimal("2"))

    def test_fifo_sortie_plusieurs_couches(self):
        MouvementStockService.entree_stock(
            article=self.article, depot=self.depot,
            quantite=10, prix_unitaire=Decimal("1.00"),
            source_operation=self.src,
        )
        MouvementStockService.entree_stock(
            article=self.article, depot=self.depot,
            quantite=10, prix_unitaire=Decimal("2.00"),
            source_operation=self.src,
        )
        MouvementStockService.sortie_stock(
            article=self.article, depot=self.depot,
            quantite=15, source_operation=SourceOperation.objects.get(code="VENTE"),
        )
        couches = CoucheValorisation.objects.filter(
            article=self.article, depot=self.depot,
            quantite_restante__gt=0,
        )
        only = couches.get()
        self.assertEqual(only.prix_unitaire, Decimal("2.00"))
        self.assertEqual(only.quantite_restante, Decimal("5"))


class CustomStrategyViaSettingsTest(TestCase):
    def test_strategie_personnalisee_via_settings(self):
        class CoutFixeStrategy(BaseValuationStrategy):
            method_code = "FIXE"
            method_name = "Coût fixe (test)"

            @classmethod
            def enregistrer_entree(cls, valorisation, quantite, prix_unitaire, mouvement=None):
                pass

            @classmethod
            def enregistrer_sortie(cls, valorisation, quantite, mouvement=None):
                return quantite * cls.get_cout_unitaire(valorisation)

            @classmethod
            def get_cout_unitaire(cls, valorisation):
                return Decimal("999")

            @classmethod
            def get_valeur_totale(cls, valorisation):
                return cls.get_cout_unitaire(valorisation) * valorisation.quantite_totale

            @classmethod
            def initialiser(cls, valorisation, quantite, prix_unitaire):
                valorisation.cout_unitaire_moyen = Decimal("999")
                valorisation.quantite_totale = quantite
                valorisation.valeur_totale = quantite * Decimal("999")
                valorisation.save()

        ValuationRegistry.register(CoutFixeStrategy)
        strategy = ValuationRegistry.get_strategy("FIXE")
        self.assertIsNotNone(strategy)
        self.assertEqual(strategy, CoutFixeStrategy)


class StandardCostStrategyTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        SourceOperation.seed()

    def setUp(self):
        TypeArticle.objects.create(code="PRODUIT_FINI", libelle="Produit fini")
        Unite.objects.create(code="UN", libelle="Unité")
        self.article = ArticleService.creer_article(
            code="CALE", designation="Cahier lignes",
            type_article_code="PRODUIT_FINI",
            unite_code="UN",
            methode_valorisation="STANDARD",
        )
        self.depot = Depot.objects.create(code="MAG", libelle="Magasin")
        self.src = SourceOperation.objects.get(code="ACHAT")

    def test_cout_standard_inchange_apres_entree(self):
        MouvementStockService.entree_stock(
            article=self.article, depot=self.depot,
            quantite=100, prix_unitaire=Decimal("1.00"),
            source_operation=self.src,
        )
        from stocks.models import Valorisation
        v = Valorisation.objects.get(article=self.article, depot=self.depot)
        self.assertEqual(v.cout_unitaire_moyen, Decimal("1.00"))
        MouvementStockService.entree_stock(
            article=self.article, depot=self.depot,
            quantite=50, prix_unitaire=Decimal("2.00"),
            source_operation=self.src,
        )
        v.refresh_from_db()
        self.assertEqual(v.cout_unitaire_moyen, Decimal("1.00"))
        self.assertEqual(v.quantite_totale, Decimal("150"))
