"""
Module de récupération en masse depuis l'API GBIF.

Ce module permet de récupérer automatiquement un grand nombre d'espèces
animales depuis GBIF, organisées par classe taxonomique (Mammalia, Aves, etc.).
Il utilise la pagination pour parcourir les résultats et filtre les espèces
non pertinentes (bactéries, virus, etc.).

Fonctionnalités:
    - Récupération paginée depuis GBIF
    - Filtrage des espèces non animales
    - Organisation par classe taxonomique
    - Respect du rate limiting de l'API
    - Export groupé au format JSON

Utilisation:
    python fetch_all.py
    # Récupère 100 espèces par classe pour 5 classes
    
    # Ou en tant que module:
    from fetch_all import fetch_all_animals_for_families
    families = ["Mammalia", "Aves"]
    fetch_all_animals_for_families(families, per_family=50)
"""

import requests
import json
import time
from pathlib import Path
import logging
from config import Config

# Configuration du logger pour ce module
logger = logging.getLogger(__name__)


def is_legit_species(entry: dict) -> bool:
    """
    Vérifie si une entrée GBIF correspond à une espèce animale légitime.
    
    Filtre les entrées qui ne sont pas des espèces animales valides:
    - Bactéries, virus, champignons
    - Espèces non classifiées ou non identifiées
    - Hybrides
    - Espèces avec nomenclature incomplète (sp., cf., etc.)
    
    Args:
        entry (dict): Dictionnaire contenant les données GBIF d'une espèce
        
    Returns:
        bool: True si l'espèce est légitime, False sinon
        
    Example:
        >>> entry = {"scientificName": "Panthera tigris"}
        >>> is_legit_species(entry)
        True
        >>> entry = {"scientificName": "Bacteria sp."}
        >>> is_legit_species(entry)
        False
    """
    # Extraction du nom scientifique (en minuscules pour comparaison)
    name = entry.get("scientificName", "").lower()
    
    # Liste des termes à exclure
    excluded_terms = [
        "bacter",           # Bactéries
        "virus",            # Virus
        "fung",             # Champignons (fungi)
        "incertae",         # Incertae sedis (position taxonomique incertaine)
        "unclassified",     # Non classifié
        "unidentified",     # Non identifié
        "sp.",              # Species (espèce non déterminée)
        "hybr.",            # Hybride
    ]
    
    # Vérification: si le nom contient un terme exclu, rejeter
    for excluded in excluded_terms:
        if excluded in name:
            logger.debug(f"Espèce filtrée: {name} (contient '{excluded}')")
            return False
    
    return True


def get_raw_data_dir() -> Path:
    """
    Retourne le chemin absolu vers le répertoire des données brutes.
    
    Returns:
        Path: Chemin absolu vers data/raw/
    """
    return Config.get_raw_data_path()


def fetch_all_animals_for_families(
    families: list,
    per_family: int = 100,
    max_records: int = 500
) -> None:
    """
    Récupère un ensemble d'espèces pour plusieurs classes taxonomiques.
    
    Cette fonction parcourt l'API GBIF de manière paginée pour récupérer
    un nombre défini d'espèces pour chaque classe taxonomique fournie.
    Les résultats sont filtrés et exportés dans un fichier JSON unique.
    
    Args:
        families (list): Liste des classes taxonomiques à récupérer
            Exemples: ["Mammalia", "Aves", "Reptilia", "Amphibia"]
        per_family (int): Nombre d'espèces à récupérer par classe.
            Par défaut: 100
        max_records (int): Nombre maximum de records à parcourir avant d'arrêter.
            Évite les boucles infinies. Par défaut: 500
            
    Returns:
        None: Les données sont sauvegardées dans data/raw/gbif_full_batch.json
        
    Example:
        >>> families = ["Mammalia", "Aves"]
        >>> fetch_all_animals_for_families(families, per_family=50)
        # Récupère 50 mammifères et 50 oiseaux
        
    Note:
        La fonction respecte un délai entre les requêtes (Config.GBIF_RATE_LIMIT_DELAY)
        pour éviter de surcharger l'API GBIF.
    """
    # Dictionnaire pour stocker les résultats par classe
    results_by_family = {}

    # Parcours de chaque classe taxonomique
    for family in families:
        logger.info(
            f"Recherche de {per_family} espèces dans la classe '{family}'..."
        )
        
        all_species = []  # Liste des espèces collectées pour cette classe
        offset = 0        # Position de départ pour la pagination
        fetched = 0       # Nombre total de records parcourus
        
        # Boucle de pagination
        while len(all_species) < per_family and fetched < max_records:
            # Construction de l'URL et des paramètres
            url = f"{Config.GBIF_API_URL}/species/search"
            params = {
                "rank": "species",                          # Uniquement les espèces
                "class": family,                            # Classe taxonomique
                "limit": min(100, per_family - len(all_species)),  # Taille de page
                "offset": offset,                           # Position de pagination
            }
            
            try:
                # Requête HTTP avec timeout
                logger.debug(f"Requête GBIF: {family}, offset={offset}")
                resp = requests.get(url, params=params, timeout=Config.HTTP_TIMEOUT)
                resp.raise_for_status()
                
                # Extraction et filtrage des résultats
                results = resp.json().get("results", [])
                batch = [sp for sp in results if is_legit_species(sp)]
                
                logger.debug(
                    f"Page récupérée: {len(results)} résultats, "
                    f"{len(batch)} après filtrage"
                )
                
            except requests.RequestException as e:
                logger.error(
                    f"Erreur réseau pour {family} (offset {offset}): {e}"
                )
                break  # Arrêt pour cette classe en cas d'erreur
                
            except Exception as e:
                logger.exception(
                    f"Erreur inattendue pour {family} (offset {offset})"
                )
                break

            # Ajout des espèces filtrées à la collection
            all_species.extend(batch)
            fetched += len(batch)
            offset += 100  # Pagination GBIF par blocs de 100
            
            logger.info(
                f"  → Page offset {offset} | "
                f"Cumul: {len(all_species)}/{per_family}"
            )

            # Condition d'arrêt: plus de résultats disponibles
            if not batch:
                logger.info(
                    f"Fin des résultats paginés pour '{family}' "
                    "(pas de nouveaux résultats)"
                )
                break
            
            # Respect du rate limiting (délai entre requêtes)
            time.sleep(Config.GBIF_RATE_LIMIT_DELAY)

        # Limitation au nombre demandé et stockage
        results_by_family[family] = all_species[:per_family]
        logger.info(
            f"✓ Classe '{family}': {len(all_species[:per_family])} espèces retenues"
        )

    # Export des résultats dans un fichier JSON unique
    try:
        raw_dir = get_raw_data_dir()
        raw_dir.mkdir(parents=True, exist_ok=True)
        out_path = raw_dir / "gbif_full_batch.json"
        
        # Écriture du JSON avec formatage
        out_path.write_text(
            json.dumps(results_by_family, indent=2, ensure_ascii=False),
            encoding="utf8"
        )
        
        # Calcul du total d'espèces
        total_species = sum(len(species) for species in results_by_family.values())
        
        logger.info("=" * 60)
        logger.info(f"✓ Export terminé: {out_path.resolve()}")
        logger.info(f"✓ Total: {total_species} espèces dans {len(families)} classes")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Erreur lors de l'écriture de 'gbif_full_batch.json': {e}")


# Point d'entrée principal du script
if __name__ == "__main__":
    # Configuration du système de logging
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format=Config.LOG_FORMAT
    )
    
    logger.info("=" * 70)
    logger.info("RÉCUPÉRATION EN MASSE DEPUIS GBIF")
    logger.info("=" * 70)
    
    # Classes taxonomiques à récupérer
    families = [
        "Mammalia",         # Mammifères
        "Aves",             # Oiseaux
        "Reptilia",         # Reptiles
        "Actinopterygii",   # Poissons à nageoires rayonnées
        "Amphibia",         # Amphibiens
    ]
    
    logger.info(f"Classes ciblées: {', '.join(families)}")
    logger.info(f"Espèces par classe: {Config.MAX_ANIMALS_PER_FAMILY}")
    logger.info(f"Limite de parcours: {Config.MAX_RECORDS_LIMIT} records")
    logger.info("")
    
    # Lancement de la récupération
    fetch_all_animals_for_families(
        families,
        per_family=Config.MAX_ANIMALS_PER_FAMILY,
        max_records=Config.MAX_RECORDS_LIMIT
    )
    
    logger.info("")
    logger.info("=" * 70)
    logger.info("RÉCUPÉRATION TERMINÉE")
    logger.info("=" * 70)
