"""
Orchestrateur principal du pipeline Animalia.

Ce module coordonne l'exécution complète du pipeline ETL:
1. FETCH: Récupération des données depuis GBIF
2. TRANSFORM: Normalisation et nettoyage
3. VALIDATE: Validation avec Pydantic
4. SEND: Envoi vers l'API cible

Chaque étape est exécutée séquentiellement avec gestion d'erreurs.
En cas d'échec d'une étape, le pipeline s'arrête.

Utilisation:
    # Avec l'espèce par défaut (Cervus elaphus)
    python main.py
    
    # Avec une espèce spécifique
    python main.py "Panthera tigris"
    
    # Ou en tant que module
    from main import run_pipeline
    run_pipeline("Aquila chrysaetos")
"""

import sys
from pathlib import Path
import json
import logging

# Import des modules du pipeline
from fetch import fetch_gbif_animal_detail, get_raw_data_dir
from transform import transform_gbif_species, export_to_json
from validate import validate_animals
from send import send_animals_to_api
from config import Config

# Configuration du logger pour ce module
logger = logging.getLogger(__name__)


def run_pipeline(animal_name: str = "Cervus elaphus") -> bool:
    """
    Exécute le pipeline complet pour une espèce donnée.
    
    Le pipeline suit ces étapes:
    1. FETCH: Télécharge les données GBIF pour l'espèce
    2. TRANSFORM: Normalise les données au format attendu
    3. VALIDATE: Valide les données avec le schéma Pydantic
    4. SEND: Envoie les données validées à l'API
    
    Args:
        animal_name (str): Nom scientifique de l'espèce à traiter.
            Par défaut: "Cervus elaphus" (Cerf élaphe)
            
    Returns:
        bool: True si le pipeline s'est exécuté avec succès, False sinon
        
    Example:
        >>> success = run_pipeline("Panthera tigris")
        >>> if success:
        ...     print("Pipeline terminé avec succès")
        
    Note:
        En cas d'erreur à une étape, le pipeline s'arrête et retourne False.
        Les logs détaillent l'étape et la raison de l'échec.
    """
    logger.info("=" * 70)
    logger.info(f"DÉMARRAGE DU PIPELINE POUR: {animal_name}")
    logger.info("=" * 70)
    
    # ========================================
    # ÉTAPE 1: FETCH - Récupération GBIF
    # ========================================
    logger.info("")
    logger.info("┌" + "─" * 68 + "┐")
    logger.info("│" + " ÉTAPE 1/4: FETCH - Récupération depuis GBIF".ljust(68) + "│")
    logger.info("└" + "─" * 68 + "┘")
    
    try:
        # Récupération des données depuis l'API GBIF
        fetch_gbif_animal_detail(animal_name)
        
        # Vérification que le fichier a bien été créé
        raw_dir = get_raw_data_dir()
        fetch_file = raw_dir / f"gbif_{animal_name.replace(' ', '_')}.json"
        
        if not fetch_file.exists():
            logger.error(f"Le fichier {fetch_file} n'a pas été créé")
            return False
            
        logger.info(f"✓ Données récupérées: {fetch_file}")
        
    except Exception as e:
        logger.error(f"✗ Erreur lors du fetch: {e}")
        return False

    # ========================================
    # ÉTAPE 2: TRANSFORM - Normalisation
    # ========================================
    logger.info("")
    logger.info("┌" + "─" * 68 + "┐")
    logger.info("│" + " ÉTAPE 2/4: TRANSFORM - Normalisation des données".ljust(68) + "│")
    logger.info("└" + "─" * 68 + "┘")
    
    try:
        # Chargement des données brutes
        with open(fetch_file, "r", encoding="utf8") as f:
            gbif_data = json.load(f)
        
        # Transformation (attend une liste)
        transformed = transform_gbif_species([gbif_data])
        
        # Préparation du fichier de sortie
        transformed_dir = Config.get_processed_data_path()
        transformed_dir.mkdir(parents=True, exist_ok=True)
        transformed_file = (
            transformed_dir / f"{animal_name.replace(' ', '_')}_transformed.json"
        )
        
        # Export des données transformées
        export_to_json(transformed, str(transformed_file))
        
        logger.info(
            f"✓ Transformation terminée: {transformed_file} "
            f"({len(transformed)} animaux)"
        )
        
    except Exception as e:
        logger.error(f"✗ Erreur à l'étape Transform: {e}")
        logger.exception("Détails de l'erreur:")
        return False

    # ========================================
    # ÉTAPE 3: VALIDATE - Validation Pydantic
    # ========================================
    logger.info("")
    logger.info("┌" + "─" * 68 + "┐")
    logger.info("│" + " ÉTAPE 3/4: VALIDATE - Validation des données".ljust(68) + "│")
    logger.info("└" + "─" * 68 + "┘")
    
    try:
        # Validation avec Pydantic
        validated_file = transformed_dir / "animals_validated.json"
        validate_animals(str(transformed_file), output_dir=str(transformed_dir))
        
        # Vérification que des données ont été validées
        if not validated_file.exists():
            logger.error("Aucune donnée validée n'a été générée")
            return False
            
        # Vérification qu'il y a au moins un animal valide
        with open(validated_file, "r", encoding="utf8") as f:
            validated_data = json.load(f)
            
        if not validated_data:
            logger.error("Aucun animal valide après validation")
            return False
        
        logger.info(
            f"✓ Validation terminée: {validated_file} "
            f"({len(validated_data)} animaux valides)"
        )
        
    except Exception as e:
        logger.error(f"✗ Erreur à l'étape Validate: {e}")
        logger.exception("Détails de l'erreur:")
        return False

    # ========================================
    # ÉTAPE 4: SEND - Envoi vers l'API
    # ========================================
    logger.info("")
    logger.info("┌" + "─" * 68 + "┐")
    logger.info("│" + " ÉTAPE 4/4: SEND - Envoi vers l'API".ljust(68) + "│")
    logger.info("└" + "─" * 68 + "┘")
    
    try:
        # Envoi des données validées vers l'API
        send_animals_to_api(str(validated_file))
        logger.info(f"✓ Envoi terminé pour {validated_file}")
        
    except Exception as e:
        logger.error(f"✗ Erreur à l'étape Send: {e}")
        logger.exception("Détails de l'erreur:")
        return False

    # ========================================
    # PIPELINE TERMINÉ AVEC SUCCÈS
    # ========================================
    logger.info("")
    logger.info("=" * 70)
    logger.info("✓ PIPELINE TERMINÉ AVEC SUCCÈS")
    logger.info("=" * 70)
    
    return True


# Point d'entrée principal du script
if __name__ == "__main__":
    # Configuration du système de logging
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format=Config.LOG_FORMAT
    )
    
    # Détermination de l'espèce à traiter
    if len(sys.argv) > 1:
        # Espèce fournie en argument
        animal_name = sys.argv[1]
        logger.info(f"Espèce spécifiée: {animal_name}")
    else:
        # Espèce par défaut
        animal_name = "Cervus elaphus"
        logger.info(f"Utilisation de l'espèce par défaut: {animal_name}")
    
    # Affichage de la configuration
    if not Config.PRODUCTION_MODE:
        Config.display_config()
    
    # Exécution du pipeline
    success = run_pipeline(animal_name)
    
    # Code de sortie approprié
    sys.exit(0 if success else 1)
