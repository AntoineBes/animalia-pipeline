"""
Module d'envoi des données validées vers l'API cible.

Ce module prend les données animales validées et les envoie une par une
à l'API REST configurée. Il gère les erreurs réseau, les échecs d'API
et génère un rapport détaillé des problèmes rencontrés.

Fonctionnalités:
    - Envoi HTTP POST vers l'API configurée
    - Gestion des erreurs et retry (si configuré)
    - Génération de rapports d'erreurs
    - Logging détaillé de chaque opération

Utilisation:
    python send.py
    # Envoie data/processed/animals_validated.json vers l'API
    
    # Ou en tant que module:
    from send import send_animals_to_api
    send_animals_to_api("chemin/vers/validated.json")
"""

import json
import requests
from pathlib import Path
import logging
from config import Config

# Configuration du logger pour ce module
logger = logging.getLogger(__name__)


def get_processed_data_dir() -> Path:
    """
    Retourne le chemin absolu vers le répertoire des données traitées.
    
    Returns:
        Path: Chemin absolu vers data/processed/
        
    Example:
        >>> processed_dir = get_processed_data_dir()
        >>> print(processed_dir)
        /chemin/vers/pipeline/src/data/processed
    """
    return Config.get_processed_data_path()


def send_animals_to_api(json_file_path: str) -> None:
    """
    Envoie les animaux validés vers l'API REST configurée.
    
    Cette fonction:
    1. Charge le fichier JSON des animaux validés
    2. Envoie chaque animal individuellement via POST
    3. Gère les erreurs HTTP et réseau
    4. Génère un rapport d'erreurs si nécessaire
    
    Args:
        json_file_path (str): Chemin vers le fichier JSON des animaux validés
        
    Returns:
        None: Les résultats sont loggés et les erreurs exportées
        
    Fichiers générés (en cas d'erreur):
        - send_errors.json: Détails des erreurs d'envoi
        
    Example:
        >>> send_animals_to_api("data/processed/animals_validated.json")
        # Envoie chaque animal à l'API configurée
        
    Note:
        L'URL de l'API est configurée via la variable d'environnement API_URL
        ou utilise http://localhost:3000/animaux par défaut.
    """
    # Étape 1: Chargement du fichier JSON
    try:
        animals = json.loads(Path(json_file_path).read_text(encoding="utf8"))
        logger.info(
            f"Fichier chargé: {json_file_path} ({len(animals)} animaux à envoyer)"
        )
    except FileNotFoundError:
        logger.error(f"Fichier introuvable: {json_file_path}")
        return
    except json.JSONDecodeError as e:
        logger.error(f"Erreur de format JSON dans {json_file_path}: {e}")
        return
    except Exception as e:
        logger.error(f"Erreur lors de la lecture du fichier {json_file_path}: {e}")
        return

    # Compteurs pour le suivi
    success_count = 0  # Nombre d'envois réussis
    error_list = []    # Liste des erreurs rencontrées

    # Étape 2: Envoi de chaque animal individuellement
    logger.info(f"Envoi vers l'API: {Config.API_URL}")
    
    for index, animal in enumerate(animals):
        animal_name = animal.get('nom', 'SANS NOM')
        
        try:
            # Envoi de la requête POST avec timeout
            resp = requests.post(
                Config.API_URL,
                json=animal,
                timeout=Config.HTTP_TIMEOUT
            )
            
            # Vérification du code de statut HTTP
            if resp.status_code in (200, 201):
                # Succès: 200 OK ou 201 Created
                logger.info(f"✓ [{index+1}/{len(animals)}] Enregistré: {animal_name}")
                success_count += 1
                
            else:
                # Erreur HTTP (4xx, 5xx)
                logger.error(
                    f"✗ [{index+1}/{len(animals)}] Erreur API {resp.status_code} "
                    f"pour {animal_name}: {resp.text}"
                )
                error_list.append({
                    "index": index,
                    "animal": animal,
                    "error_type": "HTTP_ERROR",
                    "status_code": resp.status_code,
                    "response": resp.text
                })
                
        except requests.Timeout:
            # Timeout de la requête
            logger.error(
                f"✗ [{index+1}/{len(animals)}] Timeout lors de l'envoi de {animal_name}"
            )
            error_list.append({
                "index": index,
                "animal": animal,
                "error_type": "TIMEOUT",
                "error": f"Timeout après {Config.HTTP_TIMEOUT}s"
            })
            
        except requests.ConnectionError as e:
            # Erreur de connexion (API non disponible)
            logger.error(
                f"✗ [{index+1}/{len(animals)}] Erreur de connexion pour {animal_name}: {e}"
            )
            error_list.append({
                "index": index,
                "animal": animal,
                "error_type": "CONNECTION_ERROR",
                "error": str(e)
            })
            
        except Exception as e:
            # Autres erreurs inattendues
            logger.exception(
                f"✗ [{index+1}/{len(animals)}] Exception lors de l'envoi de {animal_name}"
            )
            error_list.append({
                "index": index,
                "animal": animal,
                "error_type": "UNEXPECTED_ERROR",
                "exception": str(e)
            })

    # Étape 3: Résumé des opérations
    logger.info("=" * 60)
    logger.info(
        f"RÉSUMÉ: {success_count}/{len(animals)} envoyés avec succès, "
        f"{len(error_list)} erreurs"
    )
    logger.info("=" * 60)

    # Étape 4: Export du rapport d'erreurs (si nécessaire)
    if error_list:
        processed_dir = get_processed_data_dir()
        processed_dir.mkdir(parents=True, exist_ok=True)
        error_file = processed_dir / "send_errors.json"
        
        try:
            error_file.write_text(
                json.dumps(error_list, indent=2, ensure_ascii=False),
                encoding="utf8"
            )
            logger.warning(
                f"⚠ Rapport d'erreurs généré: {error_file.resolve()}"
            )
        except Exception as e:
            logger.error(f"Impossible d'écrire le rapport d'erreurs: {e}")
    else:
        logger.info("✓ Tous les animaux ont été envoyés avec succès")


# Point d'entrée principal du script
if __name__ == "__main__":
    # Configuration du système de logging
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format=Config.LOG_FORMAT
    )
    
    logger.info("=" * 60)
    logger.info("ENVOI DES DONNÉES VERS L'API")
    logger.info("=" * 60)
    
    # Chemin du fichier des animaux validés
    validated_file = get_processed_data_dir() / "animals_validated.json"
    
    logger.info(f"Fichier source: {validated_file}")
    logger.info(f"API cible: {Config.API_URL}")
    
    # Vérification de l'existence du fichier
    if not validated_file.exists():
        logger.error(
            f"Le fichier {validated_file} n'existe pas. "
            "Exécutez d'abord validate.py"
        )
        exit(1)
    
    # Envoi des données
    send_animals_to_api(str(validated_file))
    
    logger.info("=" * 60)
    logger.info("ENVOI TERMINÉ")
    logger.info("=" * 60)
