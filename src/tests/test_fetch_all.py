import unittest
from unittest.mock import patch, MagicMock
import json

from src.fetch_all import fetch_all_animals_for_families, get_raw_data_dir


class TestFetchAll(unittest.TestCase):
    @patch("src.fetch_all.requests.get")
    @patch("src.fetch_all.time.sleep")
    def test_fetch_all_animals_for_families(self, mock_sleep, mock_get):
        families = ["Mammalia", "Aves"]
        resp1 = MagicMock()
        resp1.raise_for_status = MagicMock()
        resp1.json.return_value = {"results": [{"scientificName": "Cervus elaphus"}]}
        resp2 = MagicMock()
        resp2.raise_for_status = MagicMock()
        resp2.json.return_value = {"results": [{"scientificName": "Corvus corax"}]}
        mock_get.side_effect = [
            resp1,
            resp2,
            MagicMock(json=lambda: {"results": []}),
            MagicMock(json=lambda: {"results": []}),
        ]
        out_file = get_raw_data_dir() / "gbif_full_batch.json"
        if out_file.exists():
            out_file.unlink()
        fetch_all_animals_for_families(families, per_family=1, max_records=2)
        self.assertTrue(out_file.exists())
        data = json.loads(out_file.read_text(encoding="utf8"))
        self.assertIn("Mammalia", data)
        self.assertIn("Aves", data)
        self.assertEqual(data["Mammalia"][0]["scientificName"], "Cervus elaphus")
        self.assertEqual(data["Aves"][0]["scientificName"], "Corvus corax")
        out_file.unlink()

    def test_is_legit_species(self):
        from src.fetch_all import is_legit_species

        assert is_legit_species({"scientificName": "Cervus elaphus"})
        assert not is_legit_species({"scientificName": "Bacteria sp."})
        assert not is_legit_species({"scientificName": "Fungus unclassified"})


if __name__ == "__main__":
    unittest.main()
