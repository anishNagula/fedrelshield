import numpy as np
from collections import Counter


def analyze_graph(graph, name="Graph"):
    print(f"\n===== {name} Distribution Analysis =====")

    # -----------------------------
    # Node Type Distribution
    # -----------------------------
    node_types = [
        data["node_type"]
        for _, data in graph.nodes(data=True)
    ]
    node_type_counts = Counter(node_types)

    print("\nNode Type Distribution:")
    total_nodes = graph.number_of_nodes()
    for k, v in node_type_counts.items():
        print(f"{k}: {v} ({v/total_nodes:.2%})")

    # -----------------------------
    # Edge Type Distribution
    # -----------------------------
    edge_types = [
        data["edge_type"]
        for _, _, data in graph.edges(data=True)
    ]
    edge_type_counts = Counter(edge_types)

    print("\nEdge Type Distribution:")
    total_edges = graph.number_of_edges()
    for k, v in edge_type_counts.items():
        print(f"{k}: {v} ({v/total_edges:.2%})")

    # -----------------------------
    # Degree Statistics
    # -----------------------------
    degrees = [deg for _, deg in graph.degree()]
    print("\nDegree Statistics:")
    print(f"Average Degree: {np.mean(degrees):.2f}")
    print(f"Max Degree: {np.max(degrees)}")
    print(f"Min Degree: {np.min(degrees)}")

    # -----------------------------
    # Attack Ratios
    # -----------------------------
    attack_nodes = sum(
        data["attack_node"]
        for _, data in graph.nodes(data=True)
    )
    attack_edges = sum(
        data["attack_edge"]
        for _, _, data in graph.edges(data=True)
    )

    print("\nAttack Statistics:")
    print(
        f"Attack Nodes: {attack_nodes} "
        f"({attack_nodes/total_nodes:.2%})"
    )
    print(
        f"Attack Edges: {attack_edges} "
        f"({attack_edges/total_edges:.2%})"
    )

    print("=====================================")