import unittest
from pathlib import Path
import json
from src.main import run_pipeline


class TestPipelineIntegration(unittest.TestCase):

    def setUp(self):
        self.data_raw = Path("data/raw/gbif_Cervus_elaphus.json")
        self.transformed_file = Path("data/processed/Cervus_elaphus_transformed.json")
        self.validated_file = Path("data/processed/animals_validated.json")
        self.errors_file = Path("data/processed/animals_validation_errors.json")

        for f in [self.transformed_file, self.validated_file, self.errors_file]:
            if f.exists():
                f.unlink()

    def test_full_pipeline_on_cervus(self):
        run_pipeline("Cervus elaphus")

        self.assertTrue(self.transformed_file.exists(), "Transformed file missing!")
        self.assertTrue(self.validated_file.exists(), "Validated file missing!")

        with open(self.validated_file, encoding="utf8") as f:
            animals = json.load(f)
        self.assertGreaterEqual(len(animals), 1)
        self.assertEqual(animals[0]["nom"], "Cervus elaphus")

    def tearDown(self):
        for f in [self.transformed_file, self.validated_file, self.errors_file]:
            if f.exists():
                f.unlink()


if __name__ == "__main__":
    unittest.main()
