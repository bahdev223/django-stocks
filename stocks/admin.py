from django.contrib import admin
from stocks.models import (
    Article, TypeArticle, CategorieArticle, Unite, ComportementArticle,
    Depot, Emplacement, Lot, NumeroSerie, SourceOperation,
    MouvementStock,
    Inventaire, LigneInventaire,
    Valorisation, JournalStock,
    Nomenclature, ComposantNomenclature,
)


@admin.register(TypeArticle)
class TypeArticleAdmin(admin.ModelAdmin):
    list_display = ["code", "libelle"]
    search_fields = ["code", "libelle"]


@admin.register(CategorieArticle)
class CategorieArticleAdmin(admin.ModelAdmin):
    list_display = ["code", "nom", "parent"]
    search_fields = ["code", "nom"]


@admin.register(Unite)
class UniteAdmin(admin.ModelAdmin):
    list_display = ["code", "libelle", "categorie"]
    search_fields = ["code", "libelle"]


@admin.register(ComportementArticle)
class ComportementArticleAdmin(admin.ModelAdmin):
    list_display = [
        "stockable", "vendable", "achetable",
        "perissable", "lot_obligatoire", "numero_serie", "inventoriable",
    ]
    search_fields = ["id"]


@admin.register(SourceOperation)
class SourceOperationAdmin(admin.ModelAdmin):
    list_display = ["code", "nom", "active", "systeme"]
    list_filter = ["active", "systeme"]
    search_fields = ["code", "nom"]


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = [
        "code", "designation", "type_article", "unite_defaut",
        "comportement", "methode_valorisation", "actif",
    ]
    list_filter = ["type_article", "actif", "methode_valorisation", "categorie"]
    search_fields = ["code", "designation"]
    autocomplete_fields = ["type_article", "categorie", "unite_defaut", "comportement"]


@admin.register(Depot)
class DepotAdmin(admin.ModelAdmin):
    list_display = ["code", "libelle", "est_actif"]
    search_fields = ["code", "libelle"]
    list_filter = ["est_actif"]


@admin.register(Emplacement)
class EmplacementAdmin(admin.ModelAdmin):
    list_display = ["depot", "code", "libelle"]
    search_fields = ["code", "libelle"]
    autocomplete_fields = ["depot"]


@admin.register(Lot)
class LotAdmin(admin.ModelAdmin):
    list_display = [
        "numero_lot", "article", "quantite_initiale",
        "quantite_restante", "date_peremption",
    ]
    list_filter = ["actif"]
    search_fields = ["numero_lot", "article__code"]
    autocomplete_fields = ["article"]


@admin.register(NumeroSerie)
class NumeroSerieAdmin(admin.ModelAdmin):
    list_display = ["numero", "article", "lot", "depot_actuel", "est_disponible"]
    list_filter = ["est_disponible"]
    search_fields = ["numero", "article__code"]


@admin.register(MouvementStock)
class MouvementStockAdmin(admin.ModelAdmin):
    list_display = [
        "reference", "nature", "article", "depot",
        "quantite", "prix_unitaire", "date_mouvement", "source_op", "valide",
    ]
    list_filter = ["nature", "source_operation", "valide", "date_mouvement"]
    search_fields = ["reference", "article__code", "libelle"]
    autocomplete_fields = ["article", "depot", "lot", "source_operation"]

    def source_op(self, obj):
        return obj.source_operation.code if obj.source_operation else ""
    source_op.short_description = "Op. source"


class LigneInventaireInline(admin.TabularInline):
    model = LigneInventaire
    extra = 1
    autocomplete_fields = ["article", "lot"]


@admin.register(Inventaire)
class InventaireAdmin(admin.ModelAdmin):
    list_display = ["reference", "depot", "date_inventaire", "statut"]
    list_filter = ["statut", "date_inventaire"]
    search_fields = ["reference"]
    autocomplete_fields = ["depot"]
    inlines = [LigneInventaireInline]


@admin.register(Valorisation)
class ValorisationAdmin(admin.ModelAdmin):
    list_display = [
        "article", "depot", "methode",
        "cout_unitaire_moyen", "quantite_totale", "valeur_totale",
    ]
    autocomplete_fields = ["article", "depot"]


@admin.register(JournalStock)
class JournalStockAdmin(admin.ModelAdmin):
    list_display = [
        "date", "article", "depot", "nature",
        "quantite", "stock_avant", "stock_apres",
    ]
    list_filter = ["nature", "date"]
    search_fields = ["article__code", "libelle"]
    autocomplete_fields = ["article", "depot"]


class ComposantNomenclatureInline(admin.TabularInline):
    model = ComposantNomenclature
    extra = 1
    autocomplete_fields = ["article"]


@admin.register(Nomenclature)
class NomenclatureAdmin(admin.ModelAdmin):
    list_display = ["code", "libelle", "article_compose", "quantite_produite", "actif"]
    list_filter = ["actif"]
    search_fields = ["code", "libelle"]
    autocomplete_fields = ["article_compose"]
    inlines = [ComposantNomenclatureInline]


@admin.register(ComposantNomenclature)
class ComposantNomenclatureAdmin(admin.ModelAdmin):
    list_display = ["nomenclature", "article", "quantite", "perte"]
    autocomplete_fields = ["nomenclature", "article"]
