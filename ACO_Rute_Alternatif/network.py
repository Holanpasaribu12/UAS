"""Road network data and graph construction for the ACO simulation."""

import networkx as nx


NODE_AWAL = "A"
NODE_TUJUAN = "G"

# Each tuple contains (starting node, ending node, simulated distance).
DAFTAR_JALUR = [
    ("A", "B", 4),
    ("A", "C", 3),
    ("B", "C", 2),
    ("B", "D", 5),
    ("C", "D", 4),
    ("C", "E", 6),
    ("D", "E", 2),
    ("D", "F", 4),
    ("E", "F", 1),
    ("E", "G", 5),
    ("F", "G", 3),
]

POSISI_NODE = {
    "A": (0, 2),
    "B": (1, 3),
    "C": (1, 1),
    "D": (2, 3),
    "E": (3, 2),
    "F": (4, 3),
    "G": (5, 2),
}

# Keep the same closures across runs so scenario results remain comparable.
SKENARIO = {
    "S1 - Kondisi Normal": [],
    "S2 - Gangguan Ringan": [("C", "E")],
    "S3 - Gangguan Sedang": [("C", "E"), ("D", "F")],
    "S4 - Gangguan Tinggi": [
        ("C", "E"),
        ("D", "F"),
        ("E", "G"),
    ],
}


def buat_graph(jalur_ditutup):
    """Build the active undirected road graph after closing selected edges."""
    graph = nx.Graph()

    for u, v, jarak in DAFTAR_JALUR:
        graph.add_edge(u, v, weight=jarak)

    for u, v in jalur_ditutup:
        if graph.has_edge(u, v):
            graph.remove_edge(u, v)

    return graph