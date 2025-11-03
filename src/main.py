from src.fetch import fetch_gbif_animal_detail, get_raw_data_dir
from src.transform import transform_gbif_species, export_to_json
from src.validate import validate_animals
from src.send import send_animals_to_api
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)


def run_pipeline(animal_name="Cervus elaphus"):
    logger.info("---- FETCH ----")
    try:
        fetch_gbif_animal_detail(animal_name)
        raw_dir = get_raw_data_dir()
        fetch_file = raw_dir / f"gbif_{animal_name.replace(' ','_')}.json"
    except Exception as e:
        logger.error(f"Erreur lors du fetch : {e}")
        return

    logger.info("---- TRANSFORM ----")
    try:
        with open(fetch_file, "r", encoding="utf8") as f:
            gbif_data = json.load(f)
        transformed = transform_gbif_species([gbif_data])
        transformed_dir = Path("data/processed")
        transformed_dir.mkdir(parents=True, exist_ok=True)
        transformed_file = (
            transformed_dir / f"{animal_name.replace(' ','_')}_transformed.json"
        )
        export_to_json(transformed, str(transformed_file))
        logger.info(
            f"Transform terminé : {transformed_file} ({len(transformed)} animaux)"
        )
    except Exception as e:
        logger.error(f"Erreur à l'étape Transform : {e}")
        return

    logger.info("---- VALIDATE ----")
    try:
        validated_file = transformed_dir / "animals_validated.json"
        validate_animals(str(transformed_file))
        logger.info(f"Validation terminée : {validated_file}")
    except Exception as e:
        logger.error(f"Erreur à l'étape Validate : {e}")
        return

    logger.info("---- SEND ----")
    try:
        send_animals_to_api(str(validated_file))
        logger.info(f"Envoi vers API terminé ({validated_file})")
    except Exception as e:
        logger.error(f"Erreur à l'étape Send : {e}")


if __name__ == "__main__":
    run_pipeline("Cervus elaphus")
