import unittest
from unittest.mock import patch, MagicMock
import json
from pathlib import Path

from src.send import send_animals_to_api, get_processed_data_dir


class TestSendAnimalsToApi(unittest.TestCase):
    @patch("src.send.requests.post")
    def test_send_animals_ok(self, mock_post):
        rsp = MagicMock()
        rsp.status_code = 201
        rsp.text = "OK"
        mock_post.return_value = rsp

        processed_dir = get_processed_data_dir()
        valid_path = processed_dir / "animals_validated.json"
        error_file = processed_dir / "send_errors.json"
        animal = {"nom": "Cervus elaphus"}
        valid_path.write_text(json.dumps([animal], ensure_ascii=False), encoding="utf8")
        if error_file.exists():
            error_file.unlink()
        send_animals_to_api(str(valid_path))
        self.assertFalse(error_file.exists())
        valid_path.unlink()

    @patch("src.send.requests.post")
    def test_send_animals_error(self, mock_post):
        rsp = MagicMock()
        rsp.status_code = 400
        rsp.text = "Bad Request"
        mock_post.return_value = rsp

        processed_dir = get_processed_data_dir()
        valid_path = processed_dir / "animals_validated.json"
        error_file = processed_dir / "send_errors.json"
        animal = {"nom": "Fake animal"}
        valid_path.write_text(json.dumps([animal], ensure_ascii=False), encoding="utf8")
        if error_file.exists():
            error_file.unlink()
        send_animals_to_api(str(valid_path))
        self.assertTrue(error_file.exists())
        content = json.loads(error_file.read_text(encoding="utf8"))
        self.assertEqual(content[0]["animal"]["nom"], "Fake animal")
        error_file.unlink()
        valid_path.unlink()


if __name__ == "__main__":
    unittest.main()
