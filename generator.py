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

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    def generate(self) -> nx.DiGraph:
        self._generate_nodes()
        self._generate_benign_edges()

        # MUCH larger number of attacks
        num_attacks = random.randint(150, 300)
        self.graph.graph["attack_instances"] = []

        for _ in range(num_attacks):
            self._inject_attack()

        return self.graph

    # ==========================================================
    # NODE GENERATION (SCALED UP)
    # ==========================================================

    def _generate_nodes(self):
        for node_type, count in self.config.node_counts.items():
            scaled_count = count * 5   # 🔥 scale nodes 5x
            for _ in range(scaled_count):
                self.graph.add_node(
                    self.node_id_counter,
                    node_type=node_type,
                    attack_node=0,
                )
                self.node_id_counter += 1

    # ==========================================================
    # BENIGN EDGE GENERATION (DENSE + STRUCTURED)
    # ==========================================================

    def _generate_benign_edges(self):
        nodes_by_type = self._group_nodes_by_type()

        # 🔥 Increase edges massively
        for relation in self.config.relation_types:
            for _ in range(5000):
                src = random.choice(list(self.graph.nodes))
                dst = random.choice(list(self.graph.nodes))

                if src != dst:
                    self.graph.add_edge(
                        src,
                        dst,
                        edge_type=relation,
                        attack_edge=0,
                    )

    # ==========================================================
    # ATTACK INJECTION (STRUCTURED + REPEATABLE)
    # ==========================================================

    def _inject_attack(self):
        motif = random.choice(self.config.attack_motif_definitions)

        attack_nodes: List[int] = []
        attack_edges: List[Tuple[int, int]] = []

        def add_step(src, dst, relation):
            self._add_edge(src, dst, relation, attack=True)
            attack_edges.append((src, dst))
            attack_nodes.append(dst)

        # -----------------------------
        # STRONG PATTERN: repeated flows
        # -----------------------------

        if motif.startswith("A"):
            user = self._get_random_node_by_type("Employee")
            ws = self._get_random_node_by_type("Workstation")
            server = self._get_random_node_by_type("Server")

            add_step(user, ws, "login_event")
            add_step(ws, server, "net_flow")

            # 🔥 repeatable escalation pattern
            for _ in range(2):
                proc = self._get_random_node_by_type("Process")
                add_step(server, proc, "process_start")

                file_node = self._get_random_node_by_type("File")
                add_step(proc, file_node, "file_touch")

        elif motif.startswith("B"):
            user = self._get_random_node_by_type("User")
            host1 = self._get_random_node_by_type("Host")
            host2 = self._get_random_node_by_type("Host")

            add_step(user, host1, "session_open")
            add_step(host1, host2, "socket_connect")

            # 🔥 consistent lateral movement
            for _ in range(3):
                next_host = self._get_random_node_by_type("Host")
                add_step(host2, next_host, "socket_connect")
                host2 = next_host

        elif motif.startswith("C"):
            identity = self._get_random_node_by_type("Identity")
            vm = self._get_random_node_by_type("VM")

            add_step(identity, vm, "auth_session")

            # 🔥 structured container chain
            container = self._get_random_node_by_type("Container")
            add_step(vm, container, "container_spawn")

            for _ in range(3):
                next_container = self._get_random_node_by_type("Container")
                add_step(container, next_container, "east_west_traffic")
                container = next_container

            service = self._get_random_node_by_type("Microservice")
            add_step(container, service, "service_invocation")

        self._label_attack(attack_nodes, attack_edges)

    # ==========================================================
    # HELPERS
    # ==========================================================

    def _group_nodes_by_type(self) -> Dict[str, List[int]]:
        result = {}
        for n, data in self.graph.nodes(data=True):
            result.setdefault(data["node_type"], []).append(n)
        return result

    def _get_random_node_by_type(self, node_type: str) -> int:
        candidates = [
            n for n, d in self.graph.nodes(data=True)
            if d["node_type"] == node_type
        ]
        return random.choice(candidates)

    def _add_edge(self, src, dst, relation, attack=False):
        self.graph.add_edge(
            src,
            dst,
            edge_type=relation,
            attack_edge=int(attack),
        )

    def _label_attack(self, nodes, edges):
        for n in set(nodes):
            self.graph.nodes[n]["attack_node"] = 1

        for u, v in edges:
            if self.graph.has_edge(u, v):
                self.graph[u][v]["attack_edge"] = 1

    # ==========================================================
    # PyG EXPORT (LESS RANDOM, MORE SIGNAL)
    # ==========================================================

    def to_pyg(self) -> Data:
        node_features = []
        node_labels = []

        for _, data in self.graph.nodes(data=True):
            feat = np.zeros(self.config.feature_dimensions)

            # 🔥 encode node type strongly
            feat[0] = self.node_type_encoding[data["node_type"]] / len(self.node_type_encoding)

            # 🔥 attack signal
            feat[1] = data["attack_node"]

            node_features.append(feat)
            node_labels.append(data["attack_node"])

        x = np.array(node_features)

        edge_index = []
        edge_types = []
        edge_labels = []

        for u, v, data in self.graph.edges(data=True):
            edge_index.append([u, v])
            edge_types.append(self.edge_type_encoding[data["edge_type"]])
            edge_labels.append(data["attack_edge"])

        edge_index = torch.tensor(edge_index).t().contiguous()

        return Data(
            x=torch.from_numpy(x).float(),
            edge_index=edge_index,
            edge_type=torch.tensor(edge_types),
            y=torch.tensor(node_labels),
            edge_label=torch.tensor(edge_labels),
        )

