"""
Module de configuration centralisé pour le pipeline Animalia.

Ce module charge les variables d'environnement depuis un fichier .env
et fournit des valeurs par défaut pour tous les paramètres de configuration.

Utilisation:
    from config import Config
    
    # Accéder aux paramètres
    api_url = Config.API_URL
    timeout = Config.HTTP_TIMEOUT
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Charger le fichier .env s'il existe (à la racine du projet)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Config:
    """
    Classe de configuration centralisée.
    
    Toutes les variables sont chargées depuis l'environnement avec des valeurs
    par défaut appropriées pour le développement local.
    """
    
    # ---- API Configuration ----
    # URL de l'API cible pour l'envoi des données validées
    API_URL = os.getenv("API_URL", "http://localhost:3000/animaux")
    
    # Timeout pour les requêtes HTTP (en secondes)
    HTTP_TIMEOUT = int(os.getenv("HTTP_TIMEOUT", "30"))
    
    # ---- GBIF Configuration ----
    # URL de base de l'API GBIF
    GBIF_API_URL = os.getenv("GBIF_API_URL", "https://api.gbif.org/v1")
    
    # Délai entre les requêtes GBIF pour éviter le rate limiting (en secondes)
    GBIF_RATE_LIMIT_DELAY = float(os.getenv("GBIF_RATE_LIMIT_DELAY", "0.2"))
    
    # ---- Logging Configuration ----
    # Niveau de log : DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Format des logs
    LOG_FORMAT = os.getenv(
        "LOG_FORMAT",
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    
    # ---- Data Directories ----
    # Répertoire pour les données brutes (relatives au dossier src/)
    RAW_DATA_DIR = os.getenv("RAW_DATA_DIR", "data/raw")
    
    # Répertoire pour les données traitées (relatives au dossier src/)
    PROCESSED_DATA_DIR = os.getenv("PROCESSED_DATA_DIR", "data/processed")
    
    # ---- Pipeline Configuration ----
    # Nombre maximum d'animaux à récupérer par famille (fetch_all.py)
    MAX_ANIMALS_PER_FAMILY = int(os.getenv("MAX_ANIMALS_PER_FAMILY", "100"))
    
    # Nombre maximum de records à parcourir avant d'arrêter (fetch_all.py)
    MAX_RECORDS_LIMIT = int(os.getenv("MAX_RECORDS_LIMIT", "500"))
    
    # ---- Production Settings ----
    # Mode de production (désactive certains logs verbeux)
    PRODUCTION_MODE = os.getenv("PRODUCTION_MODE", "false").lower() == "true"
    
    # Activer les retry automatiques en cas d'échec réseau
    ENABLE_RETRY = os.getenv("ENABLE_RETRY", "true").lower() == "true"
    
    # Nombre de tentatives en cas d'échec
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    
    @classmethod
    def get_raw_data_path(cls) -> Path:
        """
        Retourne le chemin absolu vers le répertoire des données brutes.
        
        Returns:
            Path: Chemin absolu vers data/raw/
        """
        return Path(__file__).parent / cls.RAW_DATA_DIR
    
    @classmethod
    def get_processed_data_path(cls) -> Path:
        """
        Retourne le chemin absolu vers le répertoire des données traitées.
        
        Returns:
            Path: Chemin absolu vers data/processed/
        """
        return Path(__file__).parent / cls.PROCESSED_DATA_DIR
    
    @classmethod
    def display_config(cls):
        """
        Affiche la configuration actuelle (utile pour le debugging).
        """
        print("=" * 60)
        print("CONFIGURATION DU PIPELINE ANIMALIA")
        print("=" * 60)
        print(f"API_URL: {cls.API_URL}")
        print(f"HTTP_TIMEOUT: {cls.HTTP_TIMEOUT}s")
        print(f"GBIF_API_URL: {cls.GBIF_API_URL}")
        print(f"GBIF_RATE_LIMIT_DELAY: {cls.GBIF_RATE_LIMIT_DELAY}s")
        print(f"LOG_LEVEL: {cls.LOG_LEVEL}")
        print(f"RAW_DATA_DIR: {cls.get_raw_data_path()}")
        print(f"PROCESSED_DATA_DIR: {cls.get_processed_data_path()}")
        print(f"MAX_ANIMALS_PER_FAMILY: {cls.MAX_ANIMALS_PER_FAMILY}")
        print(f"MAX_RECORDS_LIMIT: {cls.MAX_RECORDS_LIMIT}")
        print(f"PRODUCTION_MODE: {cls.PRODUCTION_MODE}")
        print(f"ENABLE_RETRY: {cls.ENABLE_RETRY}")
        print(f"MAX_RETRIES: {cls.MAX_RETRIES}")
        print("=" * 60)


# Exécution en tant que script pour afficher la configuration
if __name__ == "__main__":
    Config.display_config()
