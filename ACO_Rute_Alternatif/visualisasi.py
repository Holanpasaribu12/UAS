"""Matplotlib visualization for the road graph and selected route."""

import matplotlib.pyplot as plt
import networkx as nx

from network import POSISI_NODE


def gambar_jaringan(graph, jalur_ditutup, rute_terbaik=None):
    fig, ax = plt.subplots(figsize=(10, 5.5))

    nx.draw_networkx_edges(
        graph,
        POSISI_NODE,
        ax=ax,
        edge_color="gray",
        width=2,
    )

    for u, v in jalur_ditutup:
        x1, y1 = POSISI_NODE[u]
        x2, y2 = POSISI_NODE[v]
        ax.plot(
            [x1, x2],
            [y1, y2],
            color="red",
            linestyle="--",
            linewidth=2.5,
        )
        ax.text(
            (x1 + x2) / 2,
            (y1 + y2) / 2 + 0.15,
            "DITUTUP",
            color="red",
            fontsize=8,
            ha="center",
        )

    if rute_terbaik and len(rute_terbaik) > 1:
        edge_rute = list(zip(rute_terbaik[:-1], rute_terbaik[1:]))
        nx.draw_networkx_edges(
            graph,
            POSISI_NODE,
            edgelist=edge_rute,
            ax=ax,
            edge_color="green",
            width=4,
        )

    nx.draw_networkx_nodes(
        graph,
        POSISI_NODE,
        ax=ax,
        node_size=850,
        node_color="lightblue",
        edgecolors="black",
    )
    nx.draw_networkx_labels(
        graph,
        POSISI_NODE,
        ax=ax,
        font_size=12,
        font_weight="bold",
    )

    label_jarak = {
        (u, v): data["weight"]
        for u, v, data in graph.edges(data=True)
    }
    nx.draw_networkx_edge_labels(
        graph,
        POSISI_NODE,
        edge_labels=label_jarak,
        ax=ax,
        font_size=9,
    )

    ax.set_title("Jaringan Jalan dan Rute Alternatif")
    ax.axis("off")
    fig.tight_layout()
    return fig