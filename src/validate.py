"""
Module de validation des données animales avec Pydantic.

Ce module définit le schéma de validation strict pour les données d'espèces
animales et valide les fichiers JSON transformés avant leur envoi à l'API.

Fonctionnalités:
    - Modèle Pydantic pour la validation de schéma
    - Validation du statut UICN (liste de conservation)
    - Génération de rapports d'erreurs détaillés
    - Export des données validées et des erreurs

Utilisation:
    python validate.py
    # Valide data/processed/animals_transformed.json
    
    # Ou en tant que module:
    from validate import validate_animals
    validate_animals("chemin/vers/fichier.json", output_dir="sortie/")
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
import logging
import json
from pathlib import Path
from config import Config

# Configuration du logger pour ce module
logger = logging.getLogger(__name__)


class AnimalModel(BaseModel):
    """
    Modèle de validation Pydantic pour une espèce animale.
    
    Ce modèle définit le schéma strict que doivent respecter les données
    avant d'être envoyées à l'API. Il valide les types, les formats et
    certaines contraintes métier (comme les statuts UICN valides).
    
    Attributes:
        nom (str): Nom scientifique de l'espèce (OBLIGATOIRE)
        nom_commun (str, optional): Nom vernaculaire/commun
        rang (str, optional): Rang taxonomique (species, genus, etc.)
        statutUICN (str, optional): Statut de conservation UICN
        ordre (str, optional): Ordre taxonomique
        famille (str, optional): Famille taxonomique
        genre (str, optional): Genre taxonomique
        descriptions (str, optional): Description de l'espèce
        imageUrl (str, optional): URL d'une image de l'espèce
        
    Example:
        >>> animal = AnimalModel(
        ...     nom="Cervus elaphus",
        ...     nom_commun="Cerf élaphe",
        ...     statutUICN="LC"
        ... )
        >>> print(animal.nom)
        Cervus elaphus
    """
    
    # Nom scientifique (obligatoire, ne peut pas être None ou vide)
    nom: str = Field(
        ...,  # ... signifie "obligatoire"
        json_schema_extra={"example": "Cervus elaphus"}
    )
    
    # Nom commun/vernaculaire (optionnel)
    # CORRECTION: nom_commum -> nom_commun (typo corrigée)
    nom_commun: Optional[str] = Field(
        None,
        json_schema_extra={"example": "Cerf élaphe"}
    )
    
    # Rang taxonomique (optionnel)
    rang: Optional[str] = Field(
        None,
        json_schema_extra={"example": "species"}
    )
    
    # Statut de conservation UICN (optionnel mais validé si présent)
    statutUICN: Optional[str] = Field(
        None,
        json_schema_extra={"example": "LC"}
    )
    
    # Classification taxonomique (tous optionnels)
    ordre: Optional[str] = None
    famille: Optional[str] = None
    genre: Optional[str] = None
    
    # Informations supplémentaires (optionnelles)
    descriptions: Optional[str] = None
    imageUrl: Optional[str] = Field(
        None,
        json_schema_extra={"example": "https://example.com/image.jpg"}
    )

    @field_validator("statutUICN")
    def statut_ok(cls, v):
        """
        Validateur personnalisé pour le statut UICN.
        
        Vérifie que le statut UICN, s'il est fourni, fait partie
        de la liste officielle des statuts de conservation.
        
        Statuts UICN valides:
            - EX: Éteint (Extinct)
            - EW: Éteint à l'état sauvage (Extinct in the Wild)
            - CR: En danger critique (Critically Endangered)
            - EN: En danger (Endangered)
            - VU: Vulnérable (Vulnerable)
            - NT: Quasi menacé (Near Threatened)
            - LC: Préoccupation mineure (Least Concern)
            - DD: Données insuffisantes (Data Deficient)
        
        Args:
            v: Valeur du statut UICN à valider
            
        Returns:
            str: La valeur validée
            
        Raises:
            ValueError: Si le statut n'est pas dans la liste officielle
        """
        # Liste officielle des statuts UICN
        statuts_valides = ["EX", "EW", "CR", "EN", "VU", "NT", "LC", "DD"]
        
        # Validation uniquement si une valeur est fournie
        if v and v not in statuts_valides:
            raise ValueError(
                f"Statut UICN inconnu: {v}. "
                f"Statuts valides: {', '.join(statuts_valides)}"
            )
        
        return v


def validate_animals(json_path: str, output_dir: str = None) -> None:
    """
    Valide un fichier JSON d'animaux avec le modèle Pydantic.
    
    Cette fonction:
    1. Charge le fichier JSON
    2. Valide chaque enregistrement avec AnimalModel
    3. Sépare les données valides des erreurs
    4. Exporte les résultats dans deux fichiers distincts
    
    Args:
        json_path (str): Chemin vers le fichier JSON à valider
        output_dir (str, optional): Répertoire de sortie. 
            Par défaut: data/processed/
            
    Returns:
        None: Les résultats sont écrits sur disque
        
    Fichiers générés:
        - animals_validated.json: Données valides
        - animals_validation_errors.json: Erreurs de validation (si présentes)
        
    Example:
        >>> validate_animals("data/processed/animals_transformed.json")
        # Génère animals_validated.json et animals_validation_errors.json
    """
    # Étape 1: Chargement du fichier JSON
    try:
        data = json.loads(Path(json_path).read_text(encoding="utf8"))
        logger.info(f"Fichier chargé: {json_path} ({len(data)} enregistrements)")
    except FileNotFoundError:
        logger.error(f"Fichier introuvable: {json_path}")
        return
    except json.JSONDecodeError as e:
        logger.error(f"Erreur de format JSON dans {json_path}: {e}")
        return
    except Exception as e:
        logger.error(f"Erreur lors de la lecture de {json_path}: {e}")
        return

    # Étape 2: Validation de chaque enregistrement
    validated = []  # Liste des animaux valides
    errors = []     # Liste des erreurs de validation
    
    for index, item in enumerate(data):
        try:
            # Tentative de validation avec Pydantic
            animal = AnimalModel(**item)
            
            # Si succès, ajouter aux données validées
            validated.append(animal.model_dump())
            
        except Exception as e:
            # En cas d'erreur, enregistrer l'erreur avec le contexte
            error_record = {
                "index": index,              # Position dans le fichier
                "record": item,              # Données originales
                "error": str(e),             # Message d'erreur
                "error_type": type(e).__name__  # Type d'erreur
            }
            errors.append(error_record)
            logger.warning(
                f"Enregistrement {index} invalide ({item.get('nom', 'SANS NOM')}): {e}"
            )
    
    # Résumé de la validation
    logger.info(
        f"Validation terminée: {len(validated)} valides, {len(errors)} erreurs"
    )

    # Étape 3: Détermination du répertoire de sortie
    if output_dir is None:
        out_dir = Config.get_processed_data_path()
    else:
        out_dir = Path(output_dir)

    # Étape 4: Export des résultats
    try:
        # Création du répertoire si nécessaire
        out_dir.mkdir(parents=True, exist_ok=True)
        
        # Export des données validées
        validated_file = out_dir / "animals_validated.json"
        validated_file.write_text(
            json.dumps(validated, indent=2, ensure_ascii=False),
            encoding="utf8"
        )
        logger.info(f"✓ Données validées exportées: {validated_file}")
        
        # Export des erreurs (seulement s'il y en a)
        if errors:
            errors_file = out_dir / "animals_validation_errors.json"
            errors_file.write_text(
                json.dumps(errors, indent=2, ensure_ascii=False),
                encoding="utf8"
            )
            logger.warning(
                f"⚠ Erreurs de validation exportées: {errors_file}"
            )
        else:
            logger.info("✓ Aucune erreur de validation")
            
    except Exception as e:
        logger.error(
            f"Erreur lors de l'écriture des fichiers dans {out_dir}: {e}"
        )


# Point d'entrée principal du script
if __name__ == "__main__":
    # Configuration du système de logging
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format=Config.LOG_FORMAT
    )
    
    logger.info("=" * 60)
    logger.info("VALIDATION DES DONNÉES")
    logger.info("=" * 60)
    
    # Chemin du fichier à valider
    input_file = Config.get_processed_data_path() / "animals_transformed.json"
    
    logger.info(f"Validation de: {input_file}")
    
    # Validation
    validate_animals(str(input_file))
    
    logger.info("=" * 60)
    logger.info("VALIDATION TERMINÉE")
    logger.info("=" * 60)
