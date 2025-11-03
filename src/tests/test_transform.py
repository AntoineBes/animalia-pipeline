import unittest
from src.transform import transform_gbif_species


class TestTransform(unittest.TestCase):

    def test_transform_empty(self):
        raw_data = []
        result = transform_gbif_species(raw_data)
        self.assertEqual(result, [])

    def test_transform_gbif_species(self):
        raw_data = [
            {
                "scientificName": "Cervus elaphus",
                "vernacularName": "Cerf élaphe",
                "rank": "species",
                "order": "Artiodactyla",
                "family": "Cervidae",
                "genus": "Cervus",
                "description": "Le cerf élaphe est un grand cervidé...",
            }
        ]
        result = transform_gbif_species(raw_data)
        expected = [
            {
                "nom": "Cervus elaphus",
                "nom_commum": "Cerf élaphe",
                "rang": "species",
                "statutUICN": None,
                "ordre": "Artiodactyla",
                "famille": "Cervidae",
                "genre": "Cervus",
                "descriptions": "Le cerf élaphe est un grand cervidé...",
                "imageUrl": None,
            }
        ]
        self.assertEqual(result, expected)
        if __name__ == "__main__":
            unittest.main()
