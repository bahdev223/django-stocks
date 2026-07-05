from decimal import Decimal
from django.test import TestCase
from stocks.models import (
    TypeArticle, Unite, ComportementArticle, Article,
    Depot, Valorisation, JournalStock,
)
from stocks.services import (
    ArticleService, MouvementStockService, ValorisationService,
)


class ArticleServiceTest(TestCase):
    def setUp(self):
        TypeArticle.objects.create(code="MATIERE_PREMIERE", libelle="Matière première")
        TypeArticle.objects.create(code="PRODUIT_FINI", libelle="Produit fini")
        Unite.objects.create(code="KG", libelle="Kilogramme")
        self.comportement = ComportementArticle.creer_defaut()
        self.depot = Depot.objects.create(code="MAG", libelle="Magasin principal")

    def test_creer_article_avec_comportement_defaut(self):
        article = ArticleService.creer_article(
            code="FAR-001",
            designation="Farine de blé T55",
            type_article_code="MATIERE_PREMIERE",
            unite_code="KG",
        )
        self.assertEqual(article.code, "FAR-001")
        self.assertEqual(article.type_article.code, "MATIERE_PREMIERE")
        self.assertTrue(article.est_stockable)

    def test_stock_disponible_apres_entree(self):
        article = ArticleService.creer_article(
            code="FAR-002",
            designation="Farine test",
            type_article_code="MATIERE_PREMIERE",
            unite_code="KG",
        )
        MouvementStockService.entree_stock(
            article=article, depot=self.depot,
            quantite=100, prix_unitaire=Decimal("0.85"),
        )
        stock = ArticleService.get_stock_disponible(article, self.depot)
        self.assertEqual(stock, Decimal("100"))


class MouvementStockServiceTest(TestCase):
    def setUp(self):
        TypeArticle.objects.create(code="MATIERE_PREMIERE", libelle="Matière première")
        Unite.objects.create(code="KG", libelle="Kilogramme")
        Unite.objects.create(code="UN", libelle="Unité")
        self.comp = ComportementArticle.creer_defaut()
        self.article = ArticleService.creer_article(
            code="FAR", designation="Farine",
            type_article_code="MATIERE_PREMIERE",
            unite_code="KG",
        )
        self.depot_a = Depot.objects.create(code="MAG-A", libelle="Magasin A")
        self.depot_b = Depot.objects.create(code="MAG-B", libelle="Magasin B")

    def test_entree_et_sortie(self):
        MouvementStockService.entree_stock(
            article=self.article, depot=self.depot_a,
            quantite=100, prix_unitaire=Decimal("1.00"),
        )
        MouvementStockService.sortie_stock(
            article=self.article, depot=self.depot_a,
            quantite=30,
        )
        stock = ArticleService.get_stock_disponible(self.article, self.depot_a)
        self.assertEqual(stock, Decimal("70"))

    def test_sortie_stock_insuffisant(self):
        with self.assertRaises(ValueError):
            MouvementStockService.sortie_stock(
                article=self.article, depot=self.depot_a,
                quantite=10,
            )

    def test_transfert_entre_depots(self):
        MouvementStockService.entree_stock(
            article=self.article, depot=self.depot_a,
            quantite=50, prix_unitaire=Decimal("1.00"),
        )
        MouvementStockService.transferer(
            article=self.article,
            depot_source=self.depot_a,
            depot_destination=self.depot_b,
            quantite=20,
        )
        stock_a = ArticleService.get_stock_disponible(self.article, self.depot_a)
        self.assertEqual(stock_a, Decimal("30"))

    def test_journal_ecritures(self):
        MouvementStockService.entree_stock(
            article=self.article, depot=self.depot_a,
            quantite=50, prix_unitaire=Decimal("2.00"),
            created_by="admin",
        )
        journal_count = JournalStock.objects.filter(
            article=self.article, depot=self.depot_a,
        ).count()
        self.assertEqual(journal_count, 1)

    def test_multiple_entrees_pmp(self):
        MouvementStockService.entree_stock(
            article=self.article, depot=self.depot_a,
            quantite=100, prix_unitaire=Decimal("1.00"),
        )
        MouvementStockService.entree_stock(
            article=self.article, depot=self.depot_a,
            quantite=100, prix_unitaire=Decimal("2.00"),
        )
        valorisation = Valorisation.objects.get(
            article=self.article, depot=self.depot_a,
        )
        self.assertEqual(valorisation.cout_unitaire_moyen, Decimal("1.50"))


class ValorisationServiceTest(TestCase):
    def setUp(self):
        TypeArticle.objects.create(code="PRODUIT_FINI", libelle="Produit fini")
        Unite.objects.create(code="UN", libelle="Unité")
        ComportementArticle.creer_defaut()
        self.article = ArticleService.creer_article(
            code="ART", designation="Article",
            type_article_code="PRODUIT_FINI",
            unite_code="UN",
        )
        self.depot = Depot.objects.create(code="DEP", libelle="Dépôt")

    def test_calcul_stock_valorise(self):
        MouvementStockService.entree_stock(
            article=self.article, depot=self.depot,
            quantite=10, prix_unitaire=Decimal("5.00"),
        )
        result = ValorisationService.calculer_stock_valorise(self.article)
        self.assertEqual(result["quantite_totale"], Decimal("10"))
        self.assertEqual(result["valeur_totale"], Decimal("50"))
