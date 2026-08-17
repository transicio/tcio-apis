"""Configuration du client Pennylane (chargement des tokens — mono ou multi-entreprises).

Source des valeurs : l'environnement (`PENNYLANE_*`), avec repli sur `pennylane.env`
dans `TCIO_APIS_ENV_DIR` si le produit en déclare un. Voir `tcio_apis._env`.
"""
from .. import _env

BASE_URL = "https://app.pennylane.com/api/external/v2"

_FICHIER = "pennylane.env"
_PREFIXE = "PENNYLANE"


def _valeurs():
    return _env.charger(_PREFIXE, _FICHIER)


def get_token():
    """Token principal (cas mono-entreprise)."""
    return _valeurs().get("PENNYLANE_API_TOKEN") or None


def get_tokens():
    """Tous les tokens (multi-entreprises) : PENNYLANE_API_TOKEN + PENNYLANE_TOKEN_*.

    Chaque token correspond à une entreprise Pennylane ; le nom/id de l'entreprise
    est lu dynamiquement via /me (pas besoin de le mettre dans le nom de variable).
    """
    valeurs = _valeurs()
    tokens = []
    principal = valeurs.get("PENNYLANE_API_TOKEN")
    if principal:
        tokens.append(principal)
    for cle in sorted(valeurs):
        if cle.startswith("PENNYLANE_TOKEN_") and valeurs[cle] and valeurs[cle] not in tokens:
            tokens.append(valeurs[cle])
    return tokens
