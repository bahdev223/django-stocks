# django-stocks

Moteur universel de gestion des articles et des mouvements de stock pour Django.

## Philosophie

Ce package ne connaît **pas le métier**. Il ne sait pas s'il travaille pour une école, une boulangerie, un hôpital ou un supermarché.

Il manipule uniquement :

- **Article** (pas `Produit`)
- **Dépôt** / **Emplacement**
- **Lot** / **Numéro de série**
- **Mouvement de stock** (entrée, sortie, transfert, inventaire, rebut)
- **Valorisation** (PMP, FIFO, DMP)
- **Journal de stock**
- **Nomenclature** (BOM pour la production future)

## Concepts clés

### Article

Point d'entrée du modèle. Un article possède :

- Un **type** (`MATIERE_PREMIERE`, `PRODUIT_FINI`, `CONSOMMABLE`, `FOURNITURE`, etc.)
- Un **comportement** (stockable, vendable, achetable, périssable, lot obligatoire, n° de série)
- Une **méthode de valorisation** (PMP par défaut)
- Une **catégorie** (arborescente via FK parent)
- Une **unité** par défaut

### Type d'article

Classification sémantique qui permet au moteur de s'adapter sans connaître le domaine métier.

### Comportement

Propriétés qui déterminent comment le moteur traite l'article :

| Propriété | Défaut | Description |
|-----------|--------|-------------|
| `stockable` | True | Peut être stocké physiquement |
| `vendable` | True | Peut être vendu |
| `achetable` | True | Peut être acheté |
| `perissable` | False | A une date de péremption |
| `lot_obligatoire` | False | Doit être tracé par lot |
| `numero_serie` | False | Suivi individuel par N° de série |
| `inventoriable` | True | Doit être compté en inventaire |

### Mouvements

Quatre opérations de base, implémentées dans `MouvementStockService` :

1. **`entree_stock`** — Réception / achat
2. **`sortie_stock`** — Vente / consommation
3. **`transferer`** — Transfert entre dépôts
4. **`valider_mouvement`** — Validation différée

Chaque mouvement journalise automatiquement l'écriture dans le `JournalStock` et met à jour la valorisation (PMP).

### Valorisation

- Chaque couple `(article, depot)` a une valorisation.
- La méthode PMP recalcule le prix moyen pondéré à chaque entrée.
- `ValorisationService` permet de revaloriser et de consulter le stock valorisé.

## Installation

```python
INSTALLED_APPS = [
    ...
    "stocks",
]
```

```
python manage.py migrate stocks
```

## Utilisation minimale

```python
from stocks.models import TypeArticle, Unite, ComportementArticle
from stocks.services import ArticleService, MouvementStockService

# Créer les dépendances
type_mp = TypeArticle.objects.create(code="MATIERE_PREMIERE", libelle="Matière première")
unite_kg = Unite.objects.create(code="KG", libelle="Kilogramme")
comportement = ComportementArticle.creer_defaut()

# Créer un article
farine = ArticleService.creer_article(
    code="FAR-001",
    designation="Farine de blé T55",
    type_article_code="MATIERE_PREMIERE",
    unite_code="KG",
    comportement=comportement,
)

# Créer un dépôt
depot = Depot.objects.create(code="MAG", libelle="Magasin principal")

# Entrée de stock
MouvementStockService.entree_stock(
    article=farine,
    depot=depot,
    quantite=500,
    prix_unitaire=Decimal("0.85"),
    libelle="Réception fournisseur",
)
```

## Tests

```bash
python -m pytest tests/
```

## Licence

MIT
