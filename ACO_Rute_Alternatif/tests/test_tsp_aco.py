import itertools
import unittest

from aco import cari_rute_optimal, jalankan_aco_tsp
from network import (
    TEMPAT_WISATA,
    TITIK_AWAL,
    buat_matriks_jarak,
    jarak_haversine,
)


class TspAcoTests(unittest.TestCase):
    def setUp(self):
        self.places = ["A", "B", "C", "D"]
        self.distances = {
            ("A", "B"): 2,
            ("A", "C"): 9,
            ("A", "D"): 10,
            ("B", "C"): 6,
            ("B", "D"): 4,
            ("C", "D"): 3,
        }

    def test_aco_returns_closed_tour_visiting_each_place_once(self):
        route, distance, _ = jalankan_aco_tsp(
            self.places,
            self.distances,
            "A",
            jumlah_semut=5,
            jumlah_iterasi=10,
            seed=42,
        )

        self.assertEqual(route[0], "A")
        self.assertEqual(route[-1], "A")
        self.assertEqual(set(route[:-1]), set(self.places))
        self.assertGreater(distance, 0)

    def test_aco_is_reproducible_for_the_same_seed(self):
        first = jalankan_aco_tsp(
            self.places,
            self.distances,
            "A",
            jumlah_semut=5,
            jumlah_iterasi=10,
            seed=42,
        )
        second = jalankan_aco_tsp(
            self.places,
            self.distances,
            "A",
            jumlah_semut=5,
            jumlah_iterasi=10,
            seed=42,
        )

        self.assertEqual(first[:2], second[:2])

    def test_exhaustive_search_checks_all_tours_and_returns_minimum(self):
        route, distance = cari_rute_optimal(
            self.places,
            self.distances,
            "A",
        )
        all_routes = []
        for order in itertools.permutations(["B", "C", "D"]):
            candidate = ("A", *order, "A")
            length = sum(
                self.distances.get((a, b), self.distances.get((b, a)))
                for a, b in zip(candidate[:-1], candidate[1:])
            )
            all_routes.append((candidate, length))

        self.assertEqual(distance, min(length for _, length in all_routes))
        self.assertEqual(route[0], "A")
        self.assertEqual(route[-1], "A")

    def test_real_tourist_places_have_pairwise_distances(self):
        distances = buat_matriks_jarak(TEMPAT_WISATA)
        expected_edges = len(TEMPAT_WISATA) * (len(TEMPAT_WISATA) - 1) // 2

        self.assertEqual(len(distances), expected_edges)
        self.assertEqual(TITIK_AWAL, "Gedung Sate")
        self.assertGreater(
            jarak_haversine(
                TEMPAT_WISATA["Gedung Sate"],
                TEMPAT_WISATA["Braga"],
            ),
            0,
        )

    def test_invalid_start_is_rejected(self):
        with self.assertRaises(ValueError):
            jalankan_aco_tsp(self.places, self.distances, "unknown")

    def test_aco_keeps_selected_first_destination(self):
        route, _, _ = jalankan_aco_tsp(
            self.places,
            self.distances,
            "A",
            tujuan_pertama="C",
            jumlah_semut=5,
            jumlah_iterasi=10,
            seed=42,
        )

        self.assertEqual(route[0], "A")
        self.assertEqual(route[1], "C")
        self.assertEqual(route[-1], "A")
        self.assertEqual(set(route[:-1]), set(self.places))

    def test_exhaustive_search_respects_selected_first_destination(self):
        route, distance = cari_rute_optimal(
            self.places,
            self.distances,
            "A",
            tujuan_pertama="C",
        )
        valid_routes = []
        for order in itertools.permutations(["B", "D"]):
            candidate = ("A", "C", *order, "A")
            length = sum(
                self.distances.get((a, b), self.distances.get((b, a)))
                for a, b in zip(candidate[:-1], candidate[1:])
            )
            valid_routes.append((candidate, length))

        self.assertEqual(route[1], "C")
        self.assertEqual(distance, min(length for _, length in valid_routes))

    def test_start_cannot_be_selected_as_first_destination(self):
        with self.assertRaises(ValueError):
            jalankan_aco_tsp(self.places, self.distances, "A", tujuan_pertama="A")
        with self.assertRaises(ValueError):
            cari_rute_optimal(self.places, self.distances, "A", tujuan_pertama="A")


if __name__ == "__main__":
    unittest.main()
