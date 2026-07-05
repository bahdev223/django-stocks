from decimal import Decimal
from django.test import TestCase
from stocks.models import (
    Article, TypeArticle, CategorieArticle, Unite, ComportementArticle,
    Depot, Emplacement, Lot, NumeroSerie, MouvementStock,
    Inventaire, LigneInventaire, Valorisation,
    Nomenclature, ComposantNomenclature,
)
from stocks.constants import COMPORTEMENT_PAR_DEFAUT


class TypeArticleModelTest(TestCase):
    def test_creation_type_article(self):
        t = TypeArticle.objects.create(code="MATIERE_PREMIERE", libelle="Matière première")
        self.assertEqual(str(t), "MATIERE_PREMIERE — Matière première")


class CategorieArticleModelTest(TestCase):
    def test_creation_categorie_avec_parent(self):
        parent = CategorieArticle.objects.create(nom="Alimentaire", code="ALIM")
        enfant = CategorieArticle.objects.create(nom="Farines", code="FAR", parent=parent)
        self.assertEqual(enfant.parent, parent)
        self.assertIn(enfant, parent.enfants.all())


class UniteModelTest(TestCase):
    def test_creation_unite(self):
        u = Unite.objects.create(code="KG", libelle="Kilogramme")
        self.assertEqual(str(u), "KG (Kilogramme)")


class ComportementArticleModelTest(TestCase):
    def test_comportement_defaut(self):
        c = ComportementArticle.creer_defaut()
        for key, val in COMPORTEMENT_PAR_DEFAUT.items():
            self.assertEqual(getattr(c, key), val, f"{key} should be {val}")

    def test_str_comportement(self):
        c = ComportementArticle.objects.create(
            stockable=True, vendable=True, achetable=True,
        )
        self.assertIn("Stockable", str(c))
        self.assertIn("Vendable", str(c))


class ArticleModelTest(TestCase):
    def setUp(self):
        self.type_art = TypeArticle.objects.create(
            code="PRODUIT_FINI", libelle="Produit fini"
        )
        self.unite = Unite.objects.create(code="UN", libelle="Unité")
        self.comportement = ComportementArticle.creer_defaut()
        self.article = Article.objects.create(
            code="ART-001",
            designation="Article test",
            type_article=self.type_art,
            unite_defaut=self.unite,
            comportement=self.comportement,
        )

    def test_creation_article(self):
        self.assertEqual(str(self.article), "[ART-001] Article test")
        self.assertTrue(self.article.est_stockable)
        self.assertTrue(self.article.est_vendable)

    def test_proprietes_comportement(self):
        self.comportement.perissable = True
        self.comportement.save()
        self.article.refresh_from_db()
        self.assertTrue(self.article.est_perissable)


class DepotEmplacementModelTest(TestCase):
    def test_depot_et_emplacement(self):
        depot = Depot.objects.create(code="MAG", libelle="Magasin principal")
        emp = Emplacement.objects.create(depot=depot, code="A1", libelle="Allée A, rayon 1")
        self.assertEqual(str(depot), "[MAG] Magasin principal")
        self.assertEqual(str(emp), "MAG / A1")


class LotModelTest(TestCase):
    def setUp(self):
        self.type_art = TypeArticle.objects.create(code="MP", libelle="M.P.")
        self.unite = Unite.objects.create(code="KG", libelle="Kg")
        self.c = ComportementArticle.creer_defaut()
        self.article = Article.objects.create(
            code="FAR", designation="Farine",
            type_article=self.type_art, unite_defaut=self.unite,
            comportement=self.c,
        )

    def test_creation_lot(self):
        lot = Lot.objects.create(
            numero_lot="LOT-2026-001",
            article=self.article,
            quantite_initiale=500,
            quantite_restante=480,
        )
        self.assertEqual(str(lot), "Lot LOT-2026-001 — FAR")
        self.assertIn(lot, self.article.lots.all())

    def test_numeroserie(self):
        lot = Lot.objects.create(
            numero_lot="LOT-NS-001",
            article=self.article,
            quantite_initiale=1,
            quantite_restante=1,
        )
        depot = Depot.objects.create(code="DEP", libelle="Dépôt")
        ns = NumeroSerie.objects.create(
            numero="SN-001", article=self.article,
            lot=lot, depot_actuel=depot,
        )
        self.assertEqual(str(ns), "SN-001")


class MouvementStockModelTest(TestCase):
    def setUp(self):
        self.type_art = TypeArticle.objects.create(code="MP", libelle="M.P.")
        self.unite = Unite.objects.create(code="KG", libelle="Kg")
        self.c = ComportementArticle.creer_defaut()
        self.article = Article.objects.create(
            code="FAR", designation="Farine",
            type_article=self.type_art, unite_defaut=self.unite,
            comportement=self.c,
        )
        self.depot = Depot.objects.create(code="MAG", libelle="Magasin")

    def test_creation_mouvement(self):
        mvt = MouvementStock.objects.create(
            reference="MVT-001",
            nature="ENTREE",
            article=self.article,
            depot=self.depot,
            quantite=100,
            date_mouvement="2026-07-05 12:00:00+00:00",
        )
        self.assertIn("MVT-001", str(mvt))
        self.assertFalse(mvt.valide)


class InventaireModelTest(TestCase):
    def setUp(self):
        self.depot = Depot.objects.create(code="MAG", libelle="Magasin")
        self.type_art = TypeArticle.objects.create(code="MP", libelle="M.P.")
        self.unite = Unite.objects.create(code="UN", libelle="Unité")
        self.c = ComportementArticle.creer_defaut()
        self.article = Article.objects.create(
            code="ART", designation="Art",
            type_article=self.type_art, unite_defaut=self.unite,
            comportement=self.c,
        )

    def test_ligne_inventaire_ecart(self):
        inv = Inventaire.objects.create(
            reference="INV-001", depot=self.depot,
            date_inventaire="2026-07-05",
        )
        ligne = LigneInventaire.objects.create(
            inventaire=inv, article=self.article,
            quantite_theorique=10, quantite_reelle=12,
        )
        self.assertEqual(ligne.ecart, 2)


class NomenclatureModelTest(TestCase):
    def setUp(self):
        self.type_art = TypeArticle.objects.create(code="PF", libelle="Produit fini")
        self.unite = Unite.objects.create(code="UN", libelle="Unité")
        self.c = ComportementArticle.creer_defaut()
        self.article_compose = Article.objects.create(
            code="GATEAU", designation="Gâteau",
            type_article=self.type_art, unite_defaut=self.unite,
            comportement=self.c,
        )
        self.article_composant = Article.objects.create(
            code="FARINE", designation="Farine",
            type_article=self.type_art, unite_defaut=self.unite,
            comportement=self.c,
        )

    def test_nomenclature_avec_composants(self):
        bom = Nomenclature.objects.create(
            code="BOM-GATEAU-001",
            libelle="Recette gâteau chocolat",
            article_compose=self.article_compose,
        )
        ComposantNomenclature.objects.create(
            nomenclature=bom,
            article=self.article_composant,
            quantite=Decimal("0.500"),
        )
        self.assertEqual(bom.composants.count(), 1)
        self.assertEqual(
            str(bom.composants.first()),
            "BOM-GATEAU-001 \u2192 FARINE x0.500000",
        )
