"""Ant Colony Optimization route search."""

import random
import time

import networkx as nx

from network import NODE_AWAL, NODE_TUJUAN


JUMLAH_SEMUT = 10
JUMLAH_ITERASI = 50
PHEROMONE_AWAL = 1.0
ALPHA = 1.0
BETA = 2.0
EVAPORASI = 0.5
Q = 100.0


def jalankan_aco(
    graph,
    seed=42,
    jumlah_semut=JUMLAH_SEMUT,
    jumlah_iterasi=JUMLAH_ITERASI,
):
    """
    Find a route from A to G using pheromone and inverse-distance heuristics.

    Returns (best_route, best_distance, elapsed_time_ms). The route and
    distance are None if the destination cannot be reached.
    """
    rng = random.Random(seed)

    if not nx.has_path(graph, NODE_AWAL, NODE_TUJUAN):
        return None, None, 0.0

    pheromone = {
        (u, v): PHEROMONE_AWAL
        for u, v in graph.edges()
    }

    best_route = None
    best_distance = float("inf")
    waktu_mulai = time.perf_counter()

    for _ in range(jumlah_iterasi):
        semua_rute = []

        for _ in range(jumlah_semut):
            current = NODE_AWAL
            route = [current]
            visited = {current}

            while current != NODE_TUJUAN:
                kandidat = [
                    node
                    for node in graph.neighbors(current)
                    if node not in visited
                ]

                if not kandidat:
                    route = None
                    break

                bobot_probabilitas = []

                for next_node in kandidat:
                    edge = (current, next_node)
                    edge_balik = (next_node, current)
                    tau = pheromone.get(
                        edge,
                        pheromone.get(edge_balik, PHEROMONE_AWAL),
                    )
                    jarak = graph[current][next_node]["weight"]
                    eta = 1.0 / jarak
                    nilai = (tau ** ALPHA) * (eta ** BETA)
                    bobot_probabilitas.append(nilai)

                total = sum(bobot_probabilitas)

                if total <= 0:
                    route = None
                    break

                pilihan = rng.choices(
                    kandidat,
                    weights=bobot_probabilitas,
                    k=1,
                )[0]
                route.append(pilihan)
                visited.add(pilihan)
                current = pilihan

            if route is None:
                continue

            panjang = sum(
                graph[u][v]["weight"]
                for u, v in zip(route[:-1], route[1:])
            )
            semua_rute.append((route, panjang))

            if panjang < best_distance:
                best_distance = panjang
                best_route = route.copy()

        for edge in pheromone:
            pheromone[edge] *= 1.0 - EVAPORASI

        for route, panjang in semua_rute:
            tambahan = Q / panjang

            for u, v in zip(route[:-1], route[1:]):
                edge = (u, v)
                edge_balik = (v, u)

                if edge in pheromone:
                    pheromone[edge] += tambahan
                elif edge_balik in pheromone:
                    pheromone[edge_balik] += tambahan

    waktu_ms = (time.perf_counter() - waktu_mulai) * 1000

    if best_route is None:
        return None, None, waktu_ms

    return best_route, best_distance, waktu_ms