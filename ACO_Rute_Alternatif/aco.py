"""Ant Colony Optimization for a small travel-salesperson problem."""

import itertools
import random
import time


JUMLAH_ITERASI = 100
ALPHA = 1.0
BETA = 3.0
EVAPORASI = 0.5
PHEROMONE_AWAL = 1.0
Q = 100.0


def jalankan_aco_tsp(
    tempat,
    jarak,
    titik_awal,
    tujuan_pertama=None,
    jumlah_semut=10,
    jumlah_iterasi=JUMLAH_ITERASI,
    alpha=ALPHA,
    beta=BETA,
    evaporasi=EVAPORASI,
    seed=42,
):
    """Find a short closed tour visiting each place once with ACO."""
    tempat = list(tempat)
    if len(tempat) < 2 or len(set(tempat)) != len(tempat):
        raise ValueError("Daftar tempat harus berisi minimal dua tempat unik.")
    if titik_awal not in tempat:
        raise ValueError("Titik awal harus ada di dalam daftar tempat.")
    if tujuan_pertama is not None and (
        tujuan_pertama not in tempat or tujuan_pertama == titik_awal
    ):
        raise ValueError(
            "Tujuan pertama harus berbeda dari titik awal dan ada di daftar tempat."
        )
    if jumlah_semut < 1 or jumlah_iterasi < 1:
        raise ValueError("Jumlah semut dan iterasi harus lebih besar dari nol.")
    if alpha < 0 or beta < 0 or not 0 <= evaporasi < 1:
        raise ValueError("Parameter ACO berada di luar rentang yang valid.")

    for kota_a, kota_b in itertools.combinations(tempat, 2):
        bobot = jarak.get((kota_a, kota_b), jarak.get((kota_b, kota_a)))
        if bobot is None or bobot <= 0:
            raise ValueError(f"Jarak positif antara {kota_a} dan {kota_b} diperlukan.")

    rng = random.Random(seed)
    pheromone = {
        (kota_a, kota_b): PHEROMONE_AWAL
        for kota_a, kota_b in itertools.combinations(tempat, 2)
    }
    best_route = None
    best_distance = float("inf")
    start_time = time.perf_counter()

    def distance_between(kota_a, kota_b):
        return jarak.get((kota_a, kota_b), jarak.get((kota_b, kota_a)))

    def pheromone_key(kota_a, kota_b):
        return (kota_a, kota_b) if (kota_a, kota_b) in pheromone else (kota_b, kota_a)

    for _ in range(jumlah_iterasi):
        routes = []
        for _ in range(jumlah_semut):
            route = [titik_awal]
            unvisited = set(tempat)
            unvisited.remove(titik_awal)
            if tujuan_pertama is not None:
                route.append(tujuan_pertama)
                unvisited.remove(tujuan_pertama)
            current = route[-1]

            while unvisited:
                candidates = sorted(unvisited)
                weights = []
                for candidate in candidates:
                    tau = pheromone[pheromone_key(current, candidate)]
                    eta = 1.0 / distance_between(current, candidate)
                    weights.append((tau ** alpha) * (eta ** beta))
                next_place = rng.choices(candidates, weights=weights, k=1)[0]
                route.append(next_place)
                unvisited.remove(next_place)
                current = next_place

            route.append(titik_awal)
            total_distance = sum(
                distance_between(a, b)
                for a, b in zip(route[:-1], route[1:])
            )
            routes.append((route, total_distance))
            if total_distance < best_distance:
                best_route = route.copy()
                best_distance = total_distance

        for edge in pheromone:
            pheromone[edge] *= 1.0 - evaporasi
        for route, total_distance in routes:
            deposit = Q / total_distance
            for kota_a, kota_b in zip(route[:-1], route[1:]):
                pheromone[pheromone_key(kota_a, kota_b)] += deposit

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    return best_route, best_distance, elapsed_ms


def cari_rute_optimal(tempat, jarak, titik_awal, tujuan_pertama=None):
    """Exhaustively find the optimal closed tour for a small place set."""
    tempat = list(tempat)
    if len(tempat) < 2 or len(set(tempat)) != len(tempat):
        raise ValueError("Daftar tempat harus berisi minimal dua tempat unik.")
    if titik_awal not in tempat:
        raise ValueError("Titik awal harus ada di dalam daftar tempat.")
    if tujuan_pertama is not None and (
        tujuan_pertama not in tempat or tujuan_pertama == titik_awal
    ):
        raise ValueError(
            "Tujuan pertama harus berbeda dari titik awal dan ada di daftar tempat."
        )
    tempat_lain = [kota for kota in tempat if kota != titik_awal]
    if tujuan_pertama is not None:
        tempat_lain.remove(tujuan_pertama)

    best_route = None
    best_distance = float("inf")
    for urutan in itertools.permutations(tempat_lain):
        route = [titik_awal]
        if tujuan_pertama is not None:
            route.append(tujuan_pertama)
        route.extend(urutan)
        route.append(titik_awal)
        total_distance = sum(
            jarak.get((a, b), jarak.get((b, a)))
            for a, b in zip(route[:-1], route[1:])
        )
        if total_distance < best_distance:
            best_route = route
            best_distance = total_distance
    return best_route, best_distance
