"""Chargement des secrets d'intégration : l'environnement d'abord, un fichier en repli.

Le paquet ne suppose **aucun** emplacement de fichier : c'est le produit qui décide.
Deux sources, dans cet ordre de priorité :

1. **les variables d'environnement du processus** — la voie normale en conteneur, et
   celle que remplissent les variables partagées de l'ordonnanceur ;
2. **à défaut, un fichier `<nom>.env`** dans le répertoire désigné par la variable
   d'environnement `TCIO_APIS_ENV_DIR`, si elle est posée. C'est le mode de
   compatibilité qui permet à un produit non encore conteneurisé de continuer à
   lire ses fichiers de secrets en place, sans rien déplacer.

⛔ **Une variable d'environnement vide ne masque jamais la valeur du fichier.** Une
variable posée à la chaîne vide est le symptôme habituel d'une configuration
d'ordonnanceur incomplète ; la traiter comme une valeur ferait passer une
intégration correctement configurée pour non configurée, ce qui est le pire des
deux échecs possibles puisqu'il est silencieux.
"""
import os
from pathlib import Path


def repertoire_env():
    """Répertoire de repli des fichiers `.env`, ou None si le produit n'en déclare pas."""
    chemin = os.environ.get("TCIO_APIS_ENV_DIR")
    return Path(chemin) if chemin else None


def _lire_fichier(chemin):
    """Lit un fichier au format `CLE=valeur`. Fichier absent ou illisible → dict vide."""
    valeurs = {}
    try:
        texte = chemin.read_text(encoding="utf-8")
    except OSError:          # absent, ou droits insuffisants : « non configuré », pas une erreur
        return valeurs
    for ligne in texte.splitlines():
        ligne = ligne.strip()
        if ligne and not ligne.startswith("#") and "=" in ligne:
            cle, valeur = ligne.split("=", 1)
            valeurs[cle.strip()] = valeur.strip()
    return valeurs


def charger(prefixe, fichier):
    """Renvoie les valeurs de configuration d'une intégration.

    `prefixe` : préfixe des variables retenues (ex. « ANTHROPIC »).
    `fichier` : nom du fichier de repli (ex. « anthropic.env »), cherché dans
    `TCIO_APIS_ENV_DIR` uniquement si cette variable est posée.
    """
    repertoire = repertoire_env()
    valeurs = _lire_fichier(repertoire / fichier) if repertoire else {}
    for cle, valeur in os.environ.items():
        if cle.startswith(prefixe) and valeur:
            valeurs[cle] = valeur
    return valeurs
