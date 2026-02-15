import random
from typing import Dict, List, Tuple

import networkx as nx
import numpy as np
import torch
from torch_geometric.data import Data

from config import EnterpriseConfig


class EnterpriseGraphGenerator:
    def __init__(self, config: EnterpriseConfig):
        self.config = config
        self.graph = nx.DiGraph()
        self.node_id_counter = 0

        self.node_type_encoding = {
            t: i for i, t in enumerate(config.node_types)
        }
        self.edge_type_encoding = {
            t: i for i, t in enumerate(config.relation_types)
        }

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def generate(self) -> nx.DiGraph:
        self._generate_nodes()
        self._generate_benign_edges()

        num_attacks = random.randint(10, 20)
        self.graph.graph["attack_instances"] = []

        for _ in range(num_attacks):
            self._inject_attack()

        return self.graph

    # --------------------------------------------------
    # Node Generation
    # --------------------------------------------------

    def _generate_nodes(self):
        for node_type, count in self.config.node_counts.items():
            for _ in range(count):
                self.graph.add_node(
                    self.node_id_counter,
                    node_type=node_type,
                    attack_node=0,
                )
                self.node_id_counter += 1

    # --------------------------------------------------
    # Benign Edge Generation
    # --------------------------------------------------

    def _generate_benign_edges(self):
        nodes_by_type = self._group_nodes_by_type()

        # Employee -> Workstation login
        for emp in nodes_by_type["Employee"]:
            num_logins = np.random.poisson(
                self.config.edge_probability_rules["login_lambda"]
            )
            targets = random.sample(
                nodes_by_type["Workstation"],
                min(len(nodes_by_type["Workstation"]), num_logins),
            )
            for t in targets:
                self._add_edge(emp, t, "login_event")

        # Host to Host net flow
        hosts = nodes_by_type["Workstation"] + nodes_by_type["Server"]
        for h in hosts:
            num_net = np.random.poisson(
                self.config.edge_probability_rules["net_lambda"]
            )
            targets = random.sample(hosts, min(len(hosts), num_net))
            for t in targets:
                if h != t:
                    self._add_edge(h, t, "net_flow")

        # Process -> File access
        for p in nodes_by_type["Process"]:
            num_file = np.random.poisson(
                self.config.edge_probability_rules["file_lambda"]
            )
            targets = random.sample(
                nodes_by_type["File"],
                min(len(nodes_by_type["File"]), num_file),
            )
            for t in targets:
                self._add_edge(p, t, "file_touch")

    # --------------------------------------------------
    # Attack Injection
    # --------------------------------------------------

    def _inject_attack(self):
        motif = random.choice(self.config.attack_motif_definitions)

        attack_nodes = []
        attack_edges = []
        boundary_crossed = False

        # ---- Start from Employee ----
        current = self._get_random_node_by_type("Employee")
        attack_nodes.append(current)
        current_type = "Employee"

        def add_step(src, dst, relation):
            nonlocal boundary_crossed
            self._add_edge(src, dst, relation, attack=True)
            attack_edges.append((src, dst))
            attack_nodes.append(dst)

            prev_type = self.graph.nodes[src]["node_type"]
            next_type = self.graph.nodes[dst]["node_type"]

            if self._cross_boundary(prev_type, next_type):
                boundary_crossed = True

        # ==========================================================
        # A1 — Tool-Based Lateral Movement
        # ==========================================================
        if motif == "A1":
            # Employee -> login_event -> Workstation
            ws = self._get_random_node_by_type("Workstation")
            add_step(current, ws, "login_event")

            # Optional extra login spread
            if random.random() < 0.3:
                ws2 = self._get_random_node_by_type("Workstation")
                add_step(ws, ws2, "net_flow")
                ws = ws2

            # Workstation -> net_flow -> Server
            server = self._get_random_node_by_type("Server")
            add_step(ws, server, "net_flow")

            # Optional process activity
            if random.random() < 0.6:
                proc = self._get_random_node_by_type("Process")
                add_step(server, proc, "process_start")

                # Optional file touch (sensitive reach)
                file_node = self._get_random_node_by_type("File")
                add_step(proc, file_node, "file_touch")

        # ==========================================================
        # A2 — Privilege Escalation Pivot
        # ==========================================================
        elif motif == "A2":
            # Employee -> login_event -> Workstation
            ws = self._get_random_node_by_type("Workstation")
            add_step(current, ws, "login_event")

            # Workstation -> process_start -> Process
            proc = self._get_random_node_by_type("Process")
            add_step(ws, proc, "process_start")

            # Optional privilege escalation via spawn
            if random.random() < 0.5:
                proc2 = self._get_random_node_by_type("Process")
                add_step(proc, proc2, "process_spawn")
                proc = proc2

            # Employee -> dc_auth -> DC
            dc = self._get_random_node_by_type("DC")
            add_step(current, dc, "dc_auth")

            # DC -> net_flow -> Server (pivot)
            server = self._get_random_node_by_type("Server")
            add_step(dc, server, "net_flow")

        # ==========================================================
        # A3 — Slow Spread
        # ==========================================================
        elif motif == "A3":
            # Employee -> login_event -> Workstation
            ws1 = self._get_random_node_by_type("Workstation")
            add_step(current, ws1, "login_event")

            # Workstation lateral (optional extra)
            if random.random() < 0.5:
                ws2 = self._get_random_node_by_type("Workstation")
                add_step(ws1, ws2, "net_flow")
                ws1 = ws2

            # Workstation -> login_event -> Server
            server = self._get_random_node_by_type("Server")
            add_step(current, server, "login_event")

        # ----------------------------------------------------------
        # Ensure Sensitive Asset Reach
        # ----------------------------------------------------------
        sensitive_types = self.config.sensitive_asset_types
        if not any(
            self.graph.nodes[n]["node_type"] in sensitive_types
            for n in attack_nodes
        ):
            target_type = random.choice(sensitive_types)
            sensitive_node = self._get_random_node_by_type(target_type)
            add_step(attack_nodes[-1], sensitive_node, "net_flow")

        # ----------------------------------------------------------
        # Enforce Boundary Crossing (if not already crossed)
        # ----------------------------------------------------------
        if not boundary_crossed:
            server = self._get_random_node_by_type("Server")
            add_step(attack_nodes[-1], server, "net_flow")

        # ----------------------------------------------------------
        # Label and store metadata
        # ----------------------------------------------------------
        self._label_attack(attack_nodes, attack_edges)

        self.graph.graph["attack_instances"].append(
            {
                "nodes": attack_nodes,
                "edges": attack_edges,
                "motif": motif,
                "path_length": len(attack_edges),
                "boundary_crossed": boundary_crossed,
            }
        )

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def _group_nodes_by_type(self) -> Dict[str, List[int]]:
        result = {}
        for n, data in self.graph.nodes(data=True):
            t = data["node_type"]
            result.setdefault(t, []).append(n)
        return result

    def _add_edge(
        self,
        src: int,
        dst: int,
        relation: str,
        attack: bool = False,
    ):
        self.graph.add_edge(
            src,
            dst,
            edge_type=relation,
            attack_edge=int(attack),
        )

    def _label_attack(self, nodes, edges):
        for n in set(nodes):
            self.graph.nodes[n]["attack_node"] = 1

        for (u, v) in edges:
            if self.graph.has_edge(u, v):
                self.graph[u][v]["attack_edge"] = 1

    # --------------------------------------------------
    # PyG Export
    # --------------------------------------------------

    def to_pyg(self) -> Data:
        node_features = []
        node_types = []
        node_labels = []

        for n, data in self.graph.nodes(data=True):
            feat = np.random.randn(
                self.config.feature_dimensions
            )
            node_features.append(feat)
            node_types.append(
                self.node_type_encoding[data["node_type"]]
            )
            node_labels.append(data["attack_node"])

        edge_index = []
        edge_types = []
        edge_labels = []

        for u, v, data in self.graph.edges(data=True):
            edge_index.append([u, v])
            edge_types.append(
                self.edge_type_encoding[data["edge_type"]]
            )
            edge_labels.append(data["attack_edge"])

        edge_index = torch.tensor(edge_index).t().contiguous()

        data = Data(
            x=torch.tensor(node_features, dtype=torch.float),
            edge_index=edge_index,
            edge_type=torch.tensor(edge_types),
            node_type=torch.tensor(node_types),
            y=torch.tensor(node_labels),
            edge_label=torch.tensor(edge_labels),
        )

        return data

    def _get_random_node_by_type(self, node_type: str) -> int:
        candidates = [
            n for n, d in self.graph.nodes(data=True)
            if d["node_type"] == node_type
        ]
        return random.choice(candidates)

    def _cross_boundary(self, prev_type: str, next_type: str) -> bool:
        for _, types in self.config.boundary_definition.items():
            if prev_type in types and next_type in types:
                if prev_type != next_type:
                    return True
        return False