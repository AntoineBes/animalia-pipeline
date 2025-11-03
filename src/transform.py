import json
from pathlib import Path
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def load_all_jsons_in_folder(folder_path: str):
    data = []
    try:
        for json_file in Path(folder_path).glob("gbif_*.json"):
            try:
                with open(json_file, "r", encoding="utf8") as f:
                    data.append(json.load(f))
            except Exception as e:
                logger.error(f"Erreur lors de la lecture du fichier {json_file} : {e}")
    except Exception as e:
        logger.error(
            f"Erreur lors de la recherche des fichiers dans {folder_path} : {e}"
        )
    logger.info(f"{len(data)} fichiers gbif_*.json chargés depuis {folder_path}")
    return data


def transform_gbif_species(raw_data):
    records = []
    seen = set()
    for item in raw_data:
        nom_sci = item.get("scientificName")
        if nom_sci in seen or not nom_sci:
            continue
        seen.add(nom_sci)
        record = {
            "nom": nom_sci,
            "nom_commum": item.get("vernacularName") or None,
            "rang": item.get("rank"),
            "statutUICN": None,
            "ordre": item.get("order") or None,
            "famille": item.get("family") or None,
            "genre": item.get("genus") or None,
            "descriptions": item.get("description") or None,
            "imageUrl": None,
        }
        records.append(record)
    logger.info(f"{len(records)} animaux transformés (après filtrage uniques)")
    return records


def export_to_json(data, out_file):
    try:
        Path(out_file).parent.mkdir(parents=True, exist_ok=True)
        with open(out_file, "w", encoding="utf8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"{len(data)} enregistrements exportés sous {out_file}")
    except Exception as e:
        logger.error(f"Erreur lors de l'écriture du fichier {out_file} : {e}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    raw = load_all_jsons_in_folder("data/raw/")
    transformed = transform_gbif_species(raw)
    export_to_json(transformed, "data/processed/animals_transformed.json")
