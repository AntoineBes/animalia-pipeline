"""
Module de récupération des données depuis l'API GBIF.

Ce module permet de rechercher et télécharger les informations détaillées
d'espèces animales depuis la base de données GBIF (Global Biodiversity Information Facility).

Fonctionnalités:
    - Recherche d'espèces par nom scientifique
    - Récupération des détails taxonomiques complets
    - Sauvegarde des données brutes au format JSON
    
Utilisation:
    python fetch.py
    # Récupère les données pour une liste d'espèces prédéfinies
    
    # Ou en tant que module:
    from fetch import fetch_gbif_animal_detail
    fetch_gbif_animal_detail("Cervus elaphus")
"""

import requests
import json
from pathlib import Path
import logging
from config import Config

# Configuration du logger pour ce module
logger = logging.getLogger(__name__)


def get_raw_data_dir() -> Path:
    """
    Retourne le chemin absolu vers le répertoire des données brutes.
    
    Le répertoire est créé automatiquement s'il n'existe pas.
    
    Returns:
        Path: Chemin absolu vers le dossier data/raw/
        
    Example:
        >>> raw_dir = get_raw_data_dir()
        >>> print(raw_dir)
        /chemin/vers/pipeline/src/data/raw
    """
    return Config.get_raw_data_path()


def fetch_gbif_animal_detail(animal_name: str) -> None:
    """
    Récupère les détails complets d'une espèce depuis l'API GBIF.
    
    Cette fonction effectue deux requêtes:
    1. Recherche de l'espèce par nom pour obtenir son identifiant (usageKey)
    2. Récupération des détails complets via l'identifiant
    
    Les données sont sauvegardées dans data/raw/gbif_{nom_espece}.json
    
    Args:
        animal_name (str): Nom scientifique de l'espèce (ex: "Cervus elaphus")
        
    Returns:
        None: Les données sont sauvegardées sur disque
        
    Raises:
        requests.RequestException: En cas d'erreur réseau ou API
        
    Example:
        >>> fetch_gbif_animal_detail("Panthera tigris")
        # Crée le fichier data/raw/gbif_Panthera_tigris.json
    """
    # Construction de l'URL de recherche GBIF
    search_url = f"{Config.GBIF_API_URL}/species/search"
    params = {"q": animal_name, "limit": 1}

    try:
        logger.info(f"Recherche de '{animal_name}' sur GBIF...")
        
        # Requête de recherche avec timeout configuré
        response = requests.get(
            search_url,
            params=params,
            timeout=Config.HTTP_TIMEOUT
        )
        response.raise_for_status()  # Lève une exception si code HTTP 4xx/5xx
        
    except requests.RequestException as e:
        logger.error(
            f"Erreur réseau lors de la recherche GBIF pour '{animal_name}': {e}"
        )
        return

    # Extraction des résultats de recherche
    results = response.json().get("results", [])
    
    if not results:
        logger.warning(f"Aucun résultat GBIF trouvé pour '{animal_name}'")
        return
    
    # Récupération du premier résultat (le plus pertinent)
    taxon = results[0]
    usage_key = taxon.get("key")
    logger.info(f"Espèce '{animal_name}' trouvée avec usageKey: {usage_key}")

    # Construction de l'URL pour les détails complets
    detail_url = f"{Config.GBIF_API_URL}/species/{usage_key}"
    
    try:
        # Requête pour récupérer les détails complets
        detail_resp = requests.get(detail_url, timeout=Config.HTTP_TIMEOUT)
        detail_resp.raise_for_status()
        detail = detail_resp.json()
        
    except requests.RequestException as e:
        logger.error(
            f"Erreur lors de la récupération des détails GBIF pour '{animal_name}': {e}"
        )
        return

    # Sauvegarde des données brutes
    try:
        # Création du répertoire de destination si nécessaire
        raw_dir = get_raw_data_dir()
        raw_dir.mkdir(parents=True, exist_ok=True)
        
        # Nom du fichier: gbif_Nom_Espece.json (espaces remplacés par _)
        output_path = raw_dir / f"gbif_{animal_name.replace(' ', '_')}.json"
        
        # Écriture du JSON avec indentation pour lisibilité
        output_path.write_text(
            json.dumps(detail, indent=2, ensure_ascii=False),
            encoding="utf8"
        )
        
        logger.info(f"Détails sauvegardés pour '{animal_name}': {output_path}")
        
    except Exception as e:
        logger.error(
            f"Erreur lors de l'écriture du fichier '{output_path}': {e}"
        )


# Point d'entrée principal du script
if __name__ == "__main__":
    # Configuration du système de logging
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format=Config.LOG_FORMAT
    )
    
    # Liste d'espèces à récupérer (exemples variés de différentes classes)
    animals_to_fetch = [
        "Cervus elaphus",           # Cerf élaphe (Mammifère)
        "Panthera tigris",          # Tigre (Mammifère)
        "Varanus komodoensis",      # Dragon de Komodo (Reptile)
        "Aquila chrysaetos",        # Aigle royal (Oiseau)
        "Lynx lynx",                # Lynx (Mammifère)
        "Python regius",            # Python royal (Reptile)
        "Amphiprion ocellaris",     # Poisson clown (Poisson)
        "Rana ridibunda",           # Grenouille rieuse (Amphibien)
        "Salmo salar",              # Saumon Atlantique (Poisson)
        "Bubo bubo",                # Grand-duc d'Europe (Oiseau)
    ]
    
    # Récupération des données pour chaque espèce
    logger.info(f"Début de la récupération de {len(animals_to_fetch)} espèces")
    for animal in animals_to_fetch:
        fetch_gbif_animal_detail(animal)
    
    logger.info("Récupération terminée")
