"""Configuration du client Anthropic (clé API + modèle).

Source des valeurs : l'environnement (`ANTHROPIC_*`), avec repli sur `anthropic.env`
dans `TCIO_APIS_ENV_DIR` si le produit en déclare un. Voir `tcio_apis._env`.
"""
from .. import _env

# Modèle par défaut : Haiku (vision, économique).
DEFAULT_MODEL = "claude-haiku-4-5"

_FICHIER = "anthropic.env"
_PREFIXE = "ANTHROPIC"


def _valeurs():
    return _env.charger(_PREFIXE, _FICHIER)


def get_api_key():
    return _valeurs().get("ANTHROPIC_API_KEY") or None


def get_model():
    return _valeurs().get("ANTHROPIC_MODEL") or DEFAULT_MODEL


def is_configured():
    return bool(get_api_key())
