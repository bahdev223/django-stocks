# django-stocks

**Moteur universel de gestion des articles et des mouvements de stock pour Django.**

Ce package ne connaît **pas le métier**. Il répond à une seule question :

> **"Pourquoi la quantité de cet article a-t-elle changé ?"**

Pas *"Quel document métier a provoqué ce changement ?"*

---

## Architecture

Le moteur distingue deux concepts indépendants :

| Concept | Rôle | Exemples |
|---------|------|----------|
| **Nature du mouvement** | Ce qui arrive au stock | `ENTREE`, `SORTIE`, `TRANSFERT`, `AJUSTEMENT` |
| **Opération source** | Qui a demandé ce mouvement | `ACHAT`, `VENTE`, `PRODUCTION`, `CASSE`, `DON`, `INVENTAIRE` |

Un mouvement n'est jamais *"une vente"* ou *"un achat"*. Il est :

```
Nature : SORTIE
Source : VENTE
```

Le stock ignore ce qu'est une vente ou une facture. Il sait seulement qu'un objet externe est à l'origine.

### Traçabilité

- **`source_operation`** — FK vers `SourceOperation` (enumération extensible)
- **`source`** — `GenericForeignKey` (content_type + object_id) vers l'objet métier

Les deux peuvent être combinés :

| Mouvement | Nature | Source op. | GFK source |
|-----------|--------|------------|------------|
| Vente de 4 pains | SORTIE | VENTE | Facture #42 |
| Réception farine | ENTREE | ACHAT | Réception #7 |
| Casse bouteille | SORTIE | CASSE | — |
| Ajustement inventaire | ENTREE | INVENTAIRE | Inventaire #12 |

---

## Modèles

| Modèle | Rôle |
|--------|------|
| `Article` | Code, désignation, type, catégorie, unité, comportement, valorisation |
| `TypeArticle` | `MATIERE_PREMIERE`, `PRODUIT_FINI`, `CONSOMMABLE`, etc. |
| `CategorieArticle` | Arborescence (parent/enfant) |
| `Unite` | KG, L, UN, etc. |
| `ComportementArticle` | Drapeaux : stockable, vendable, périssable, lot, N° série |
| `SourceOperation` | Opération source : `ACHAT`, `VENTE`, `PRODUCTION`, etc. — extensible |
| `Depot` | Lieu de stockage physique (magasin, boutique, camion, atelier) |
| `Emplacement` | Position dans un dépôt (allée, rayon, casier) |
| `Lot` | Traçabilité par lot (date péremption, qté restante) |
| `NumeroSerie` | Suivi individuel par N° de série |
| `MouvementStock` | Entrée, sortie, transfert, ajustement — avec source op. + GFK |
| `Inventaire` + `LigneInventaire` | Comptage physique avec validation et ajustement automatique |
| `Valorisation` | PMP par article/dépôt |
| `JournalStock` | Audit trail : stock avant/après chaque mouvement |
| `Nomenclature` / `ComposantNomenclature` | BOM pour production future |

---

## Utilisation

```python
from stocks.models import (
    TypeArticle, Unite, ComportementArticle, Depot, SourceOperation
)
from stocks.services import ArticleService, MouvementStockService

# Amorcer les sources système (ACHAT, VENTE, PRODUCTION, …)
SourceOperation.seed()

# Dépendances
TypeArticle.objects.create(code="MATIERE_PREMIERE", libelle="Matière première")
Unite.objects.create(code="KG", libelle="Kilogramme")
comportement = ComportementArticle.creer_defaut()
depot = Depot.objects.create(code="MAG", libelle="Magasin principal")
src_achat = SourceOperation.objects.get(code="ACHAT")

# Créer un article
farine = ArticleService.creer_article(
    code="FAR-001",
    designation="Farine de blé T55",
    type_article_code="MATIERE_PREMIERE",
    unite_code="KG",
)

# Entrée de stock (Achat)
MouvementStockService.entree_stock(
    article=farine,
    depot=depot,
    quantite=500,
    prix_unitaire=Decimal("0.85"),
    source_operation=src_achat,
    libelle="Réception fournisseur",
)

# Sortie de stock (Production)
src_prod = SourceOperation.objects.get(code="PRODUCTION")
MouvementStockService.sortie_stock(
    article=farine,
    depot=depot,
    quantite=30,
    source_operation=src_prod,
    libelle="Consommation boulangerie",
)

# Transfert entre dépôts
depot_boutique = Depot.objects.create(code="BOU", libelle="Boutique")
MouvementStockService.transferer(
    article=farine,
    depot_source=depot,
    depot_destination=depot_boutique,
    quantite=100,
)
```

### Ajouter une source personnalisée

```python
SourceOperation.objects.create(
    code="MISSION_HUMANITAIRE",
    nom="Mission humanitaire",
    systeme=False,
)
```

---

## Intégration avec les modules métier

```python
from stocks.services import MouvementStockService
from stocks.models import SourceOperation

# Dans django-ventes
facture = Facture.objects.get(pk=42)
MouvementStockService.sortie_stock(
    article=pain,
    depot=depot_boutique,
    quantite=4,
    source_operation=SourceOperation.objects.get(code="VENTE"),
    source=facture,                # lien vers l'objet métier via GFK
    created_by="admin",
)
```

---

## Tests

```bash
python runtests.py
```

23 tests — couvre : Article, entrée/sortie/transfert, stock insuffisant, inventaire (écart +/‑), PMP, journal, nomenclature, NumeroSerie.

---

## Licence

MIT
