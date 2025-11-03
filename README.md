🦌 Animalia Pipeline

Collecte, validation et synchronisation d’espèces animales, du GBIF vers une API locale.

🚀 Fonctionnalités principales

Collecte des données scientifiques via GBIF.

Transformation et nettoyage des données brutes.

Validation stricte via Pydantic.

Envoi vers une API conforme via HTTP POST.

Logs détaillés, robustesse et sécurité de bout en bout.

📂 Structure du projet
text
```
├─ src/
│  ├─ fetch.py             # Récupération GBIF
│  ├─ transform.py         # Normalisation
│  ├─ validate.py          # Validation
│  ├─ send.py              # Push API
│  ├─ main.py              # Orchestration
│  └─ tests/               # Tests unitaires/integration
└─ data/
   ├─ raw/
   └─ processed/
```
🔧 Prérequis
Python 3.11+ (recommandé)

Installez les dépendances :

```
pip install -r requirements.txt
pip install flake8 black
▶️ Exécuter le pipeline complet
bash
python src/main.py "Cervus elaphus"
Résultats dans data/raw/ et data/processed/.
```
📚 Scripts en détail

fetch.py : Téléchargement des données brutes depuis GBIF

transform.py : Nettoyage et normalisation des données

validate.py : Vérification et validation stricte du format des animaux

send.py : Envoi des animaux validés vers l’API cible

main.py : Orchestrateur, lance toute la chaîne

💡 Jeu de données test

Disponible dans le repo pour tous les tests :
```
data/raw/gbif_Cervus_elaphus.json

data/processed/animals_transformed.json

data/processed/animals_validated.json

data/processed/animals_validation_errors.json
```
🧪 Lancer les tests

bash
python -m unittest discover src/tests
(Ou avec pytest si installé)

🧹 Qualité code et lint

bash
black src/
flake8 src/
⚡ CI/CD intégrée
Workflow GitHub Actions disponible :

Lint (black, flake8)

Tests automatisés

Exécution réelle du pipeline (mode test/simulation)

🔒 Sécurité & robustesse

Gestion des erreurs : try/except sur tous les accès disque/réseau

Logs via Python logging (niveau paramétrable)

Fichiers ouverts et créés en toute sécurité, nettoyage automatique

⚙️ Personnalisation

Changer l’espèce : argument direct dans le main

Étendre en batch, multi-utilisateur, API distante aisément

Pour aller plus loin
Ajouter des datas/photos, batch d’especies, IA de classification...

Documenter chaque module via docstring détaillées

Contact : antoine95560@hotmail.fr