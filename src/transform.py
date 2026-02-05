"""
Module de transformation des données GBIF brutes.

Ce module charge les fichiers JSON bruts récupérés depuis GBIF,
normalise les données, élimine les doublons et exporte le résultat
dans un format standardisé pour la validation.

Fonctionnalités:
    - Chargement de multiples fichiers JSON GBIF
    - Transformation des données brutes en format normalisé
    - Élimination des doublons par nom scientifique
    - Export au format JSON

Utilisation:
    python transform.py
    # Transforme tous les fichiers gbif_*.json du dossier data/raw/
    
    # Ou en tant que module:
    from transform import transform_gbif_species, export_to_json
    data = load_all_jsons_in_folder("data/raw/")
    transformed = transform_gbif_species(data)
    export_to_json(transformed, "output.json")
"""

import json
from pathlib import Path
import pandas as pd
import logging
from config import Config

# Configuration du logger pour ce module
logger = logging.getLogger(__name__)


def load_all_jsons_in_folder(folder_path: str) -> list:
    """
    Charge tous les fichiers JSON GBIF d'un dossier.
    
    Recherche tous les fichiers correspondant au pattern 'gbif_*.json'
    dans le dossier spécifié et charge leur contenu.
    
    Args:
        folder_path (str): Chemin vers le dossier contenant les fichiers JSON
        
    Returns:
        list: Liste des données JSON chargées (un élément par fichier)
        
    Example:
        >>> data = load_all_jsons_in_folder("data/raw/")
        >>> print(f"{len(data)} fichiers chargés")
        10 fichiers chargés
    """
    data = []
    
    try:
        # Recherche de tous les fichiers gbif_*.json
        folder = Path(folder_path)
        json_files = list(folder.glob("gbif_*.json"))
        
        logger.info(f"Recherche de fichiers dans {folder_path}...")
        
        # Chargement de chaque fichier
        for json_file in json_files:
            try:
                with open(json_file, "r", encoding="utf8") as f:
                    content = json.load(f)
                    data.append(content)
                    logger.debug(f"Fichier chargé: {json_file.name}")
                    
            except json.JSONDecodeError as e:
                logger.error(
                    f"Erreur de format JSON dans {json_file.name}: {e}"
                )
            except Exception as e:
                logger.error(
                    f"Erreur lors de la lecture du fichier {json_file.name}: {e}"
                )
                
    except Exception as e:
        logger.error(
            f"Erreur lors de la recherche des fichiers dans {folder_path}: {e}"
        )
    
    logger.info(f"{len(data)} fichier(s) gbif_*.json chargé(s) depuis {folder_path}")
    return data


def transform_gbif_species(raw_data: list) -> list:
    """
    Transforme les données brutes GBIF en format normalisé.
    
    Cette fonction:
    - Extrait les champs pertinents de chaque espèce
    - Normalise les valeurs (None pour les champs vides)
    - Élimine les doublons basés sur le nom scientifique
    - Retourne une liste de dictionnaires standardisés
    
    Args:
        raw_data (list): Liste de dictionnaires contenant les données GBIF brutes
        
    Returns:
        list: Liste de dictionnaires normalisés avec les champs:
            - nom: Nom scientifique (obligatoire)
            - nom_commun: Nom vernaculaire (optionnel)
            - rang: Rang taxonomique (species, genus, etc.)
            - statutUICN: Statut de conservation UICN
            - ordre: Ordre taxonomique
            - famille: Famille taxonomique
            - genre: Genre taxonomique
            - descriptions: Description de l'espèce
            - imageUrl: URL d'une image (non fourni par GBIF)
            
    Example:
        >>> raw = [{"scientificName": "Cervus elaphus", "family": "Cervidae"}]
        >>> result = transform_gbif_species(raw)
        >>> print(result[0]["nom"])
        Cervus elaphus
    """
    records = []
    seen = set()  # Ensemble pour tracker les noms scientifiques déjà traités
    
    logger.info(f"Transformation de {len(raw_data)} enregistrement(s) GBIF...")
    
    for item in raw_data:
        # Extraction du nom scientifique (clé primaire)
        nom_sci = item.get("scientificName")
        
        # Filtrage: ignorer les entrées sans nom ou déjà vues
        if not nom_sci:
            logger.warning("Enregistrement ignoré: pas de nom scientifique")
            continue
            
        if nom_sci in seen:
            logger.debug(f"Doublon ignoré: {nom_sci}")
            continue
        
        # Marquer ce nom comme traité
        seen.add(nom_sci)
        
        # Construction de l'enregistrement normalisé
        record = {
            # Nom scientifique (obligatoire)
            "nom": nom_sci,
            
            # Nom commun/vernaculaire (optionnel)
            "nom_commun": item.get("vernacularName") or None,
            
            # Rang taxonomique (species, genus, family, etc.)
            "rang": item.get("rank"),
            
            # Statut UICN (sera validé plus tard)
            # GBIF ne fournit pas toujours cette info
            "statutUICN": None,
            
            # Classification taxonomique
            "ordre": item.get("order") or None,
            "famille": item.get("family") or None,
            "genre": item.get("genus") or None,
            
            # Description (rarement fournie par GBIF)
            "descriptions": item.get("description") or None,
            
            # URL d'image (non fournie par cette API)
            "imageUrl": None,
        }
        
        records.append(record)
    
    logger.info(
        f"{len(records)} animaux transformés "
        f"({len(raw_data) - len(records)} doublons/invalides filtrés)"
    )
    
    return records


def export_to_json(data: list, out_file: str) -> None:
    """
    Exporte les données transformées au format JSON.
    
    Crée le répertoire de destination si nécessaire et écrit
    les données avec indentation pour une meilleure lisibilité.
    
    Args:
        data (list): Liste de dictionnaires à exporter
        out_file (str): Chemin du fichier de sortie
        
    Returns:
        None: Les données sont écrites sur disque
        
    Raises:
        Exception: En cas d'erreur d'écriture
        
    Example:
        >>> data = [{"nom": "Cervus elaphus", "famille": "Cervidae"}]
        >>> export_to_json(data, "data/processed/animals.json")
        # Crée le fichier avec les données formatées
    """
    try:
        # Création du répertoire parent si nécessaire
        output_path = Path(out_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Écriture du JSON avec formatage
        with open(output_path, "w", encoding="utf8") as f:
            json.dump(
                data,
                f,
                indent=2,              # Indentation pour lisibilité
                ensure_ascii=False     # Préserver les caractères accentués
            )
        
        logger.info(
            f"{len(data)} enregistrement(s) exporté(s) vers {output_path}"
        )
        
    except Exception as e:
        logger.error(
            f"Erreur lors de l'écriture du fichier {out_file}: {e}"
        )
        raise


# Point d'entrée principal du script
if __name__ == "__main__":
    # Configuration du système de logging
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format=Config.LOG_FORMAT
    )
    
    logger.info("=" * 60)
    logger.info("TRANSFORMATION DES DONNÉES GBIF")
    logger.info("=" * 60)
    
    # Chemins des données
    raw_folder = Config.get_raw_data_path()
    processed_folder = Config.get_processed_data_path()
    output_file = processed_folder / "animals_transformed.json"
    
    # Étape 1: Chargement des données brutes
    logger.info(f"Chargement depuis: {raw_folder}")
    raw_data = load_all_jsons_in_folder(str(raw_folder))
    
    if not raw_data:
        logger.warning("Aucune donnée à transformer. Vérifiez le dossier data/raw/")
        exit(0)
    
    # Étape 2: Transformation
    transformed_data = transform_gbif_species(raw_data)
    
    # Étape 3: Export
    logger.info(f"Export vers: {output_file}")
    export_to_json(transformed_data, str(output_file))
    
    logger.info("=" * 60)
    logger.info("TRANSFORMATION TERMINÉE")
    logger.info("=" * 60)
