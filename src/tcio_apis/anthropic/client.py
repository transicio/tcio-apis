"""Accès au SDK Anthropic officiel. Import paresseux : aucune dépendance dure au chargement."""
from . import config


def available():
    """Vrai si une clé API est configurée ET que le paquet `anthropic` est installé."""
    if not config.is_configured():
        return False
    try:
        import anthropic  # noqa: F401
    except ImportError:
        return False
    return True


def get_client(timeout=30.0, max_retries=1):
    """Renvoie un client anthropic.Anthropic prêt à l'emploi."""
    import anthropic

    key = config.get_api_key()
    if not key:
        raise RuntimeError(
            "Clé API Anthropic absente — pose ANTHROPIC_API_KEY dans l'environnement "
            "(ou dans anthropic.env du répertoire TCIO_APIS_ENV_DIR)."
        )
    return anthropic.Anthropic(api_key=key, timeout=timeout, max_retries=max_retries)
