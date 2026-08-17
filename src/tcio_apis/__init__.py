"""Clients des API tierces communs aux produits TCIO.

Un sous-module par intégration (`tcio_apis.anthropic`, `tcio_apis.pennylane`). Les
secrets ne sont **jamais** portés par ce paquet : ils viennent de l'environnement du
processus, ou d'un fichier de repli désigné par `TCIO_APIS_ENV_DIR` (voir `_env`).
"""
__version__ = "0.1.0"
