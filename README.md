# 🦌 Animalia Pipeline

Pipeline ETL automatisé pour la collecte, validation et synchronisation d'espèces animales depuis GBIF vers une API locale.

## 🚀 Fonctionnalités

- **Collecte** : Récupération automatique des données depuis l'API GBIF
- **Transformation** : Normalisation et nettoyage des données brutes
- **Validation** : Validation stricte avec Pydantic (schéma + statuts UICN)
- **Envoi** : Push vers API REST avec gestion d'erreurs complète
- **Configuration** : Gestion centralisée via variables d'environnement
- **Logs** : Journalisation détaillée de toutes les opérations

## 📂 Structure du Projet

```
pipeline/
├── .env.example              # Template de configuration
├── requirements.txt          # Dépendances Python avec versions
├── README.md                 # Ce fichier
├── DOCUMENTATION_TECHNIQUE.txt  # Documentation complète (LIRE EN PRIORITÉ)
│
└── src/
    ├── config.py             # Configuration centralisée
    ├── fetch.py              # Récupération GBIF
    ├── fetch_all.py          # Récupération en masse
    ├── transform.py          # Normalisation des données
    ├── validate.py           # Validation Pydantic
    ├── send.py               # Envoi vers l'API
    ├── main.py               # Orchestrateur principal
    ├── data/                 # Données (raw + processed)
    └── tests/                # Tests unitaires et d'intégration
```

## 🔧 Installation

### Prérequis

- Python 3.11+ ([Télécharger](https://www.python.org/downloads/))
- pip (gestionnaire de paquets Python)
- Accès Internet (pour GBIF)

### Étapes d'installation

1. **Créer un environnement virtuel** (recommandé) :
   ```bash
   python -m venv .venv
   ```

2. **Activer l'environnement virtuel** :
   - Windows PowerShell :
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - Windows CMD :
     ```cmd
     .venv\Scripts\activate.bat
     ```
   - Linux/macOS :
     ```bash
     source .venv/bin/activate
     ```

3. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer l'environnement** :
   ```bash
   # Copier le fichier d'exemple
   copy .env.example .env  # Windows
   # cp .env.example .env  # Linux/macOS

   # Éditer .env avec vos paramètres
   notepad .env  # Windows
   # nano .env   # Linux/macOS
   ```

   Variables principales à configurer :
   ```env
   API_URL=http://localhost:3000/animaux
   HTTP_TIMEOUT=30
   LOG_LEVEL=INFO
   ```

## ▶️ Utilisation

### Pipeline complet

Exécuter le pipeline pour une espèce :

```bash
# Espèce par défaut (Cervus elaphus)
python src/main.py

# Espèce spécifique
python src/main.py "Panthera tigris"
```

### Modules individuels

Exécuter chaque étape séparément :

```bash
# 1. Récupération GBIF
python src/fetch.py

# 2. Transformation
python src/transform.py

# 3. Validation
python src/validate.py

# 4. Envoi vers l'API
python src/send.py

# 📦 Récupération en masse
python src/fetch_all.py
```

### Tester la configuration

```bash
python src/config.py
```

## 🧪 Tests

### Lancer tous les tests

```bash
python -m unittest discover src/tests -v
```

### Tests individuels

```bash
# Test de récupération
python -m unittest src/tests/test_fetch.py

# Test de transformation
python -m unittest src/tests/test_transform.py

# Test de validation
python -m unittest src/tests/test_validate.py

# Test d'envoi API
python -m unittest src/tests/test_send.py

# Test d'intégration complet
python -m unittest src/tests/test_pipeline_integration.py
```

## 📊 Flux de Données

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   GBIF API  │────▶│    FETCH    │────▶│  TRANSFORM  │────▶│  VALIDATE   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                          │                    │                    │
                          ▼                    ▼                    ▼
                    data/raw/          data/processed/      animals_validated
                    gbif_*.json        *_transformed.json       .json
                                                                    │
                                                                    ▼
                                                            ┌─────────────┐
                                                            │  SEND (API) │
                                                            └─────────────┘
```

## 📝 Modèle de Données

```json
{
  "nom": "Cervus elaphus",           // OBLIGATOIRE
  "nom_commun": "Cerf élaphe",       // Optionnel
  "rang": "species",                 // Optionnel
  "statutUICN": "LC",                // Optionnel (validé)
  "ordre": "Artiodactyla",           // Optionnel
  "famille": "Cervidae",             // Optionnel
  "genre": "Cervus",                 // Optionnel
  "descriptions": "...",             // Optionnel
  "imageUrl": "https://..."          // Optionnel
}
```

**Statuts UICN valides** : `EX`, `EW`, `CR`, `EN`, `VU`, `NT`, `LC`, `DD`

## 🔒 Configuration

Toute la configuration est centralisée dans le fichier `.env`. Voir `.env.example` pour les options disponibles.

**Variables principales** :
- `API_URL` : URL de l'API cible
- `HTTP_TIMEOUT` : Timeout des requêtes (secondes)
- `GBIF_API_URL` : URL de l'API GBIF
- `LOG_LEVEL` : Niveau de logging (DEBUG, INFO, WARNING, ERROR)
- `PRODUCTION_MODE` : Active/désactive les logs verbeux

## 🚨 Dépannage

### Problèmes courants

**ImportError: No module named 'dotenv'**
```bash
pip install python-dotenv
```

**API GBIF inaccessible**
- Vérifier la connexion Internet
- Augmenter `HTTP_TIMEOUT` dans `.env`

**API cible retourne 404/500**
- Vérifier que l'API est démarrée
- Tester : `curl -X POST http://localhost:3000/animaux`
- Vérifier `API_URL` dans `.env`

**Aucune donnée validée**
- Consulter `data/processed/animals_validation_errors.json`
- Vérifier la qualité des données GBIF

### Activer les logs détaillés

```env
# Dans .env
LOG_LEVEL=DEBUG
```

## 📚 Documentation

- **[DOCUMENTATION_TECHNIQUE.txt](DOCUMENTATION_TECHNIQUE.txt)** : Documentation complète (architecture, processus, installation, tests, production)
- **Docstrings** : Chaque module contient des docstrings détaillées en français
- **Commentaires** : Code commenté pour une meilleure maintenabilité

## 🏭 Mise en Production

**⚠️ IMPORTANT** : Avant de déployer en production, consulter la section "8. MISE EN PRODUCTION" dans `DOCUMENTATION_TECHNIQUE.txt`.

**Points critiques** :
- Configurer `PRODUCTION_MODE=true` dans `.env`
- Utiliser `LOG_LEVEL=WARNING` ou `ERROR`
- Configurer l'URL de l'API de production
- Augmenter les timeouts selon la latence réseau
- Implémenter un système de sauvegarde
- Configurer un cron job ou scheduler
- Mettre en place du monitoring (logs, métriques, alertes)

## 🛠️ Technologies Utilisées

- **Python 3.11+** : Langage principal
- **Pydantic** : Validation de données
- **Requests** : Requêtes HTTP
- **Pandas** : Manipulation de données
- **Python-dotenv** : Gestion de configuration
- **Unittest** : Framework de tests

## 📧 Contact

**Auteur** : antoine95560@hotmail.fr

Pour signaler un bug ou demander une fonctionnalité, créer une issue ou envoyer un email avec :
- Description du problème
- Logs d'erreur
- Configuration (.env anonymisée)
- Version de Python

## 📄 Licence

Ce projet est fourni tel quel pour usage interne.

---

**✨ Nouveau dans cette version (v2.0)** :
- ✅ Configuration centralisée avec variables d'environnement
- ✅ Code entièrement commenté en français
- ✅ Documentation technique complète
- ✅ Correction du bug `nom_commum` → `nom_commun`
- ✅ Gestion d'erreurs améliorée
- ✅ Timeouts configurables
- ✅ Logs structurés et détaillés