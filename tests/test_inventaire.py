from decimal import Decimal
from django.test import TestCase
from stocks.models import (
    TypeArticle, Unite, ComportementArticle, Depot, SourceOperation,
)
from stocks.services import ArticleService, MouvementStockService, InventaireService


class InventaireServiceTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        SourceOperation.seed()

    def setUp(self):
        TypeArticle.objects.create(code="MATIERE_PREMIERE", libelle="Matière première")
        Unite.objects.create(code="KG", libelle="Kilogramme")
        self.comp = ComportementArticle.creer_defaut()
        self.article = ArticleService.creer_article(
            code="FAR", designation="Farine",
            type_article_code="MATIERE_PREMIERE",
            unite_code="KG",
        )
        self.depot = Depot.objects.create(code="MAG", libelle="Magasin")
        self.src_achat = SourceOperation.objects.get(code="ACHAT")

    def test_inventaire_avec_ecart_positif(self):
        MouvementStockService.entree_stock(
            article=self.article, depot=self.depot,
            quantite=100, prix_unitaire=Decimal("1.00"),
            source_operation=self.src_achat,
        )
        inventaire = InventaireService.creer_inventaire(
            reference="INV-JUL-2026",
            depot=self.depot,
        )
        InventaireService.ajouter_ligne(
            inventaire=inventaire,
            article=self.article,
            quantite_reelle=105,
        )
        InventaireService.valider_inventaire(inventaire, created_by="admin")

        stock = ArticleService.get_stock_disponible(self.article, self.depot)
        self.assertEqual(stock, Decimal("105"))

    def test_inventaire_avec_ecart_negatif(self):
        MouvementStockService.entree_stock(
            article=self.article, depot=self.depot,
            quantite=100, prix_unitaire=Decimal("1.00"),
            source_operation=self.src_achat,
        )
        inventaire = InventaireService.creer_inventaire(
            reference="INV-JUL-2026-B",
            depot=self.depot,
        )
        InventaireService.ajouter_ligne(
            inventaire=inventaire,
            article=self.article,
            quantite_reelle=90,
        )
        InventaireService.valider_inventaire(inventaire, created_by="admin")

        stock = ArticleService.get_stock_disponible(self.article, self.depot)
        self.assertEqual(stock, Decimal("90"))
