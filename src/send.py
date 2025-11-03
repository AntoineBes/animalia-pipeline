import json
import requests
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
API_URL = "http://localhost:3000/animaux"


def get_processed_data_dir():
    return Path(__file__).parent / "data" / "processed"


def send_animals_to_api(json_file_path):
    try:
        animals = json.loads(Path(json_file_path).read_text(encoding="utf8"))
    except Exception as e:
        logger.error(f"Erreur lors de la lecture du fichier {json_file_path} : {e}")
        return

    success_count = 0
    error_list = []

    for animal in animals:
        try:
            resp = requests.post(API_URL, json=animal)
            if resp.status_code in (200, 201):
                logger.info(f"Enregistré : {animal.get('nom')}")
                success_count += 1
            else:
                logger.error(
                    f"Erreur API: {resp.status_code} - {resp.text} pour {animal.get('nom')}"
                )
                error_list.append(
                    {
                        "animal": animal,
                        "response": resp.text,
                        "status_code": resp.status_code,
                    }
                )
        except Exception as e:
            logger.exception(f"Exception lors de l’envoi pour {animal.get('nom')}")
            error_list.append({"animal": animal, "exception": str(e)})

    logger.info(f"Total enregistrés : {success_count}, erreurs : {len(error_list)}")

    if error_list:
        processed_dir = get_processed_data_dir()
        processed_dir.mkdir(parents=True, exist_ok=True)
        error_file = processed_dir / "send_errors.json"
        try:
            error_file.write_text(
                json.dumps(error_list, indent=2, ensure_ascii=False), encoding="utf8"
            )
            logger.warning(
                f"Des erreurs ont été rencontrées, dossier : {error_file.resolve()}"
            )
        except Exception as e:
            logger.error(f"Impossible d'écrire le rapport d'erreurs : {e}")


if __name__ == "__main__":
    import logging

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    send_animals_to_api(str(get_processed_data_dir() / "animals_validated.json"))
