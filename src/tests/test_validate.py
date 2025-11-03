import unittest
import json
from pathlib import Path
from src.validate import validate_animals


class TestValidate(unittest.TestCase):
    def setUp(self):
        self.processed_dir = Path(__file__).parent.parent / "data" / "processed"
        self.processed_dir.mkdir(parents=True, exist_ok=True)

        self.valid_data = [
            {
                "nom": "Cervus elaphus",
                "nom_commum": "Cerf élaphe",
                "rang": "species",
                "statutUICN": "LC",
                "ordre": "Artiodactyla",
                "famille": "Cervidae",
                "genre": "Cervus",
                "descriptions": "Grand mammifère européen.",
                "imageUrl": None,
            }
        ]
        self.invalid_data = [
            {
                "nom": "Bizarre fish",
                "nom_commum": 123,
                "rang": "species",
                "statutUICN": "XX",
                "ordre": None,
                "famille": None,
                "genre": None,
                "descriptions": "",
                "imageUrl": None,
            }
        ]

        self.valid_path = self.processed_dir / "tmp_valid.json"
        self.invalid_path = self.processed_dir / "tmp_invalid.json"
        self.valid_path.write_text(
            json.dumps(self.valid_data, ensure_ascii=False), encoding="utf8"
        )
        self.invalid_path.write_text(
            json.dumps(self.invalid_data, ensure_ascii=False), encoding="utf8"
        )

        self.validated_path = self.processed_dir / "animals_validated.json"
        self.errors_path = self.processed_dir / "animals_validation_errors.json"

    def tearDown(self):
        for f in [
            self.valid_path,
            self.invalid_path,
            self.validated_path,
            self.errors_path,
        ]:
            try:
                f.unlink()
            except Exception:
                pass

    def test_validate_animals_valid(self):
        validate_animals(str(self.valid_path), output_dir=self.processed_dir)
        result = json.loads(self.validated_path.read_text(encoding="utf8"))
        self.assertEqual(len(result), 1)
        self.assertFalse(self.errors_path.exists())

    def test_validate_animals_invalid(self):
        validate_animals(str(self.invalid_path), output_dir=self.processed_dir)
        self.assertTrue(self.errors_path.exists())
        errors = json.loads(self.errors_path.read_text(encoding="utf8"))
        self.assertEqual(len(errors), 1)
        self.assertIn("statut uicn inconnu", errors[0]["error"].lower())
        result = json.loads(self.validated_path.read_text(encoding="utf8"))
        self.assertEqual(len(result), 0)


if __name__ == "__main__":
    unittest.main()
