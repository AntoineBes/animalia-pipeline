from pydantic import BaseModel, Field, field_validator
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class AnimalModel(BaseModel):
    nom: str = Field(..., json_schema_extra={"example": "Cervus elaphus"})
    nom_commum: Optional[str] = Field(
        None, json_schema_extra={"example": "Cerf élaphe"}
    )
    rang: Optional[str] = Field(None, json_schema_extra={"example": "species"})
    statutUICN: Optional[str] = Field(None, json_schema_extra={"example": "LC"})
    ordre: Optional[str]
    famille: Optional[str]
    genre: Optional[str]
    descriptions: Optional[str]
    imageUrl: Optional[str] = Field(None, json_schema_extra={"example": "https://..."})

    @field_validator("statutUICN")
    def statut_ok(cls, v):
        if v and v not in ["EX", "EW", "CR", "EN", "VU", "NT", "LC", "DD"]:
            raise ValueError(f"Statut UICN inconnu: {v}")
        return v


def validate_animals(json_path: str, output_dir=None):
    import json
    from pathlib import Path

    try:
        data = json.loads(Path(json_path).read_text(encoding="utf8"))
    except Exception as e:
        logger.error(f"Erreur lors de la lecture de {json_path} : {e}")
        return

    validated = []
    errors = []
    for item in data:
        try:
            animal = AnimalModel(**item)
            validated.append(animal.model_dump())
        except Exception as e:
            errors.append({"record": item, "error": str(e)})
    logger.info(f"{len(validated)} animaux valides, {len(errors)} erreurs")

    if output_dir is None:
        out_dir = Path("data/processed/")
    else:
        out_dir = Path(output_dir)

    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "animals_validated.json").write_text(
            json.dumps(validated, indent=2, ensure_ascii=False), encoding="utf8"
        )
        if errors:
            (out_dir / "animals_validation_errors.json").write_text(
                json.dumps(errors, indent=2, ensure_ascii=False), encoding="utf8"
            )
            logger.warning(
                f"Erreurs de validation exportées dans {out_dir / 'animals_validation_errors.json'}"
            )
        logger.info(f"Validation exportée dans {out_dir / 'animals_validated.json'}")
    except Exception as e:
        logger.error(
            f"Erreur lors de l'écriture des fichiers validés dans {out_dir}: {e}"
        )


if __name__ == "__main__":
    import logging

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    validate_animals("data/processed/animals_transformed.json")
