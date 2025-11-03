import requests
import json
import time
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def is_legit_species(entry):
    name = entry.get("scientificName", "").lower()
    if any(
        excl in name
        for excl in [
            "bacter",
            "virus",
            "fung",
            "incertae",
            "unclassified",
            "unidentified",
            "sp.",
            "hybr.",
        ]
    ):
        return False
    return True


def get_raw_data_dir():
    return Path(__file__).parent / "data" / "raw"


def fetch_all_animals_for_families(families, per_family=100, max_records=500):
    results_by_family = {}

    for family in families:
        logger.info(f"Recherche de {per_family} animaux dans la classe '{family}'")
        all_species = []
        offset, fetched = 0, 0

        while len(all_species) < per_family and fetched < max_records:
            url = "https://api.gbif.org/v1/species/search"
            params = {
                "rank": "species",
                "class": family,
                "limit": min(100, per_family - len(all_species)),
                "offset": offset,
            }
            try:
                resp = requests.get(url, params=params)
                resp.raise_for_status()
                batch = [
                    sp for sp in resp.json().get("results", []) if is_legit_species(sp)
                ]
            except requests.RequestException as e:
                logger.error(
                    f"Erreur réseau/fetch pour {family} (offset {offset}) : {e}"
                )
                break
            except Exception as e:
                logger.exception(
                    f"Erreur inattendue lors du parsing ou du filtrage pour {family} (offset {offset})"
                )
                break

            all_species.extend(batch)
            fetched += len(batch)
            offset += 100
            logger.info(f"  → Page offset {offset} | cumul : {len(all_species)}")

            if not batch:
                logger.info(
                    f"Fin des résultats paginés pour '{family}' (pas de nouveaux batchs)"
                )
                break
            time.sleep(0.2)

        results_by_family[family] = all_species[:per_family]
        logger.info(
            f"Classe '{family}': {len(all_species[:per_family])} espèces retenues"
        )

    try:
        raw_dir = get_raw_data_dir()
        raw_dir.mkdir(parents=True, exist_ok=True)
        out_path = raw_dir / "gbif_full_batch.json"
        out_path.write_text(
            json.dumps(results_by_family, indent=2, ensure_ascii=False), encoding="utf8"
        )
        logger.info(f"Exporté dans {out_path.resolve()}")
    except Exception as e:
        logger.error(f"Erreur lors de l'écriture de 'gbif_full_batch.json' : {e}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    families = ["Mammalia", "Aves", "Reptilia", "Actinopterygii", "Amphibia"]
    fetch_all_animals_for_families(families, per_family=100, max_records=500)
