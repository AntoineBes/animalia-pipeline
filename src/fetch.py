import requests
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def get_raw_data_dir():
    return Path(__file__).parent / "data" / "raw"


def fetch_gbif_animal_detail(animal_name):
    url = "https://api.gbif.org/v1/species/search"
    params = {"q": animal_name, "limit": 1}

    try:
        logger.info(f"Recherche '{animal_name}' sur GBIF...")
        response = requests.get(url, params=params)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(
            f"Erreur réseau lors de la "
            f"GBIF pour '{animal_name}': {e}"
        )
        return

    results = response.json().get("results", [])
    if results:
        taxon = results[0]
        usage_key = taxon.get("key")
        logger.info(f"Trouvé '{animal_name}' avec usageKey: {usage_key}")

        detail_url = f"https://api.gbif.org/v1/species/{usage_key}"
        try:
            detail_resp = requests.get(detail_url)
            detail_resp.raise_for_status()
            detail = detail_resp.json()
        except requests.RequestException as e:
            logger.error(
                f"Erreur lors de la récupération du détail "
                f"GBIF pour '{animal_name}': {e}"
            )
            return

        try:
            raw_dir = get_raw_data_dir()
            raw_dir.mkdir(parents=True, exist_ok=True)
            output_path = raw_dir / f"gbif_{animal_name.replace(' ', '_')}.json"
            output_path.write_text(json.dumps(detail, indent=2), encoding="utf8")
            logger.info(f"Détail sauvegardé pour '{animal_name}' : {output_path}")
        except Exception as e:
            logger.error(f"Erreur lors de l'écriture du fichier '{output_path}': {e}")
    else:
        logger.warning(f"Aucun résultat GBIF pour '{animal_name}'")


if __name__ == "__main__":
    import logging

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    for animal in [
        "Cervus elaphus",  # Cerf élaphe
        "Panthera tigris",  # Tigre
        "Varanus komodoensis",  # Dragon de Komodo
        "Aquila chrysaetos",  # Aigle royal
        "Lynx lynx",  # Lynx
        "Python regius",  # Python royal
        "Amphiprion ocellaris",  # Poisson clown
        "Rana ridibunda",  # Grenouille rieuse
        "Salmo salar",  # Saumon Atlantique
        "Bubo bubo",  # Grand-duc d'Europe
    ]:
        fetch_gbif_animal_detail(animal)
