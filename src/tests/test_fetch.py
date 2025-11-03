import unittest
from unittest.mock import patch, MagicMock
import json

from src.fetch import fetch_gbif_animal_detail, get_raw_data_dir


class TestFetchGbifDetail(unittest.TestCase):
    @patch("src.fetch.requests.get")
    def test_fetch_success(self, mock_get):
        search_response = MagicMock()
        search_response.raise_for_status = MagicMock()
        search_response.json.return_value = {"results": [{"key": 12345}]}
        detail_response = MagicMock()
        detail_response.raise_for_status = MagicMock()
        detail_response.json.return_value = {
            "scientificName": "Cervus elaphus",
            "key": 12345,
        }
        mock_get.side_effect = [search_response, detail_response]

        raw_dir = get_raw_data_dir()
        out_file = raw_dir / "gbif_Cervus_elaphus.json"
        if out_file.exists():
            out_file.unlink()
        fetch_gbif_animal_detail("Cervus elaphus")
        self.assertTrue(out_file.exists())
        content = json.loads(out_file.read_text(encoding="utf8"))
        self.assertEqual(content["scientificName"], "Cervus elaphus")
        out_file.unlink()

    @patch("src.fetch.requests.get")
    def test_fetch_no_result(self, mock_get):
        search_response = MagicMock()
        search_response.raise_for_status = MagicMock()
        search_response.json.return_value = {"results": []}
        mock_get.return_value = search_response

        raw_dir = get_raw_data_dir()
        out_file = raw_dir / "gbif_BadAnimal.json"
        if out_file.exists():
            out_file.unlink()
        fetch_gbif_animal_detail("BadAnimal")
        self.assertFalse(out_file.exists())


if __name__ == "__main__":
    unittest.main()
