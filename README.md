# tcio-apis

Clients des **API tierces** communs à tous les produits TCIO. Un produit installe ce
paquet au lieu de recopier le code d'intégration : une correction du client Pennylane
se fait ici, une fois, et chaque produit la prend en montant de version.

## Ce que ce paquet contient — et ce qu'il ne contient pas

| Contient | Ne contient pas |
|---|---|
| Le code qui parle à une API **tierce** (Anthropic, Pennylane, …) | Les clients vers **nos propres** services (BO ↔ portail) : ils restent dans le produit |
| La configuration : quelle variable porte quelle clé | ⛔ **Aucun secret.** Jamais. Ce dépôt est partagé |

## Installation

```bash
pip install "tcio-apis[anthropic] @ git+ssh://git@github.com/transicio/tcio-apis@v0.1.0"
```

L'**épinglage sur une étiquette de version est obligatoire**. Une bibliothèque partagée
qu'un produit ne peut pas *ne pas* mettre à jour est un couplage déguisé : chaque produit
doit choisir son moment.

Les intégrations déclarent leurs dépendances en option (`[anthropic]`, `[tout]`) : un
produit qui n'appelle que Pennylane n'installe pas le SDK Anthropic.

## D'où viennent les secrets

Le paquet ne lit **aucun fichier de son propre répertoire**. Deux sources, dans l'ordre :

1. **les variables d'environnement du processus** — la voie normale, et celle que
   remplissent les variables partagées de l'ordonnanceur ;
2. **à défaut, un fichier `<nom>.env`** dans le répertoire désigné par
   `TCIO_APIS_ENV_DIR`, si le produit pose cette variable. C'est le mode de
   compatibilité qui permet à un produit non encore conteneurisé de garder ses fichiers
   de secrets là où ils sont.

Une variable d'environnement **vide** ne masque jamais la valeur du fichier : une variable
posée à la chaîne vide est le symptôme d'une configuration incomplète, et la traiter comme
une valeur ferait passer une intégration configurée pour non configurée — un échec
silencieux, donc le pire.

### Exemple : le back-office, non encore conteneurisé

`config/settings.py` pose une seule ligne, et les fichiers `common/APIs/*.env` existants
continuent de fonctionner sans être déplacés :

```python
os.environ.setdefault("TCIO_APIS_ENV_DIR", str(BASE_DIR / "common" / "APIs"))
```

Le jour où le BO passera en conteneur, il suffira de retirer cette ligne et de fournir
les clés par l'environnement.

## Variables attendues

| Intégration | Variables | Fichier de repli |
|---|---|---|
| `tcio_apis.anthropic` | `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL` *(optionnel)* | `anthropic.env` |
| `tcio_apis.pennylane` | `PENNYLANE_API_TOKEN`, `PENNYLANE_TOKEN_*` *(multi-entreprises)* | `pennylane.env` |

## Ajouter une intégration

Un sous-paquet `tcio_apis/<service>/` avec `config.py` (qui appelle `_env.charger`),
`client.py`, et un `__init__.py` qui expose la surface publique. Rien d'autre : pas de
fichier de secrets, pas de lecture de chemin en dur.

## Versionnage

Version sémantique. Une rupture de surface publique impose un incrément majeur — les
produits épinglent, ils ne subissent pas.
