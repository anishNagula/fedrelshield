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

        num_attacks = random.randint(10, 20)
        self.graph.graph["attack_instances"] = []

        for _ in range(num_attacks):
            self._inject_attack()

        return self.graph

    # ==========================================================
    # NODE GENERATION
    # ==========================================================

    def _generate_nodes(self):
        for node_type, count in self.config.node_counts.items():
            for _ in range(count):
                self.graph.add_node(
                    self.node_id_counter,
                    node_type=node_type,
                    attack_node=0,
                )
                self.node_id_counter += 1

    # ==========================================================
    # BENIGN EDGE GENERATION (simple generic baseline)
    # ==========================================================

    def _generate_benign_edges(self):
        nodes_by_type = self._group_nodes_by_type()

        # Simple probabilistic wiring within allowed relations
        for relation in self.config.relation_types:
            for _ in range(500):
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
    # ATTACK INJECTION
    # ==========================================================

    def _inject_attack(self):
        motif = random.choice(self.config.attack_motif_definitions)

        attack_nodes: List[int] = []
        attack_edges: List[Tuple[int, int]] = []
        boundary_crossed = False

        def add_step(src, dst, relation):
            nonlocal boundary_crossed
            self._add_edge(src, dst, relation, attack=True)
            attack_edges.append((src, dst))
            attack_nodes.append(dst)

            prev_type = self.graph.nodes[src]["node_type"]
            next_type = self.graph.nodes[dst]["node_type"]

            if self._cross_boundary(prev_type, next_type):
                boundary_crossed = True

        # ======================================================
        # ENTERPRISE A MOTIFS
        # ======================================================

        if motif in ["A1", "A2", "A3"]:
            current = self._get_random_node_by_type("Employee")
            attack_nodes.append(current)

        if motif == "A1":
            ws = self._get_random_node_by_type("Workstation")
            add_step(current, ws, "login_event")

            if random.random() < 0.3:
                ws2 = self._get_random_node_by_type("Workstation")
                add_step(ws, ws2, "net_flow")
                ws = ws2

            server = self._get_random_node_by_type("Server")
            add_step(ws, server, "net_flow")

            if random.random() < 0.6:
                proc = self._get_random_node_by_type("Process")
                add_step(server, proc, "process_start")

                file_node = self._get_random_node_by_type("File")
                add_step(proc, file_node, "file_touch")

        elif motif == "A2":
            ws = self._get_random_node_by_type("Workstation")
            add_step(current, ws, "login_event")

            proc = self._get_random_node_by_type("Process")
            add_step(ws, proc, "process_start")

            if random.random() < 0.5:
                proc2 = self._get_random_node_by_type("Process")
                add_step(proc, proc2, "process_spawn")
                proc = proc2

            dc = self._get_random_node_by_type("DC")
            add_step(current, dc, "dc_auth")

            server = self._get_random_node_by_type("Server")
            add_step(dc, server, "net_flow")

        elif motif == "A3":
            ws1 = self._get_random_node_by_type("Workstation")
            add_step(current, ws1, "login_event")

            if random.random() < 0.5:
                ws2 = self._get_random_node_by_type("Workstation")
                add_step(ws1, ws2, "net_flow")
                ws1 = ws2

            server = self._get_random_node_by_type("Server")
            add_step(current, server, "login_event")

        # ======================================================
        # ENTERPRISE B MOTIFS
        # ======================================================

        elif motif in ["B1", "B2", "B3"]:
            current = self._get_random_node_by_type("User")
            attack_nodes.append(current)

        if motif == "B1":
            host1 = self._get_random_node_by_type("Host")
            add_step(current, host1, "session_open")

            host2 = self._get_random_node_by_type("Host")
            add_step(host1, host2, "socket_connect")

            subnet = self._get_random_node_by_type("Subnet")
            add_step(host2, subnet, "cross_subnet")

            host3 = self._get_random_node_by_type("Host")
            add_step(subnet, host3, "socket_connect")

        elif motif == "B2":
            host = self._get_random_node_by_type("Host")
            add_step(current, host, "session_open")

            service1 = self._get_random_node_by_type("InternalService")
            add_step(host, service1, "api_call")

            if random.random() < 0.6:
                service2 = self._get_random_node_by_type("InternalService")
                add_step(service1, service2, "api_call")
                service1 = service2

            service3 = self._get_random_node_by_type("InternalService")
            add_step(service1, service3, "api_call")

        elif motif == "B3":
            host = self._get_random_node_by_type("Host")
            add_step(current, host, "session_open")

            dc = self._get_random_node_by_type("DC")
            add_step(current, dc, "dc_session")

        # ======================================================
        # ENTERPRISE C MOTIFS
        # ======================================================

        elif motif in ["C1", "C2"]:
            current = self._get_random_node_by_type("Identity")
            attack_nodes.append(current)

        if motif == "C1":
            vm = self._get_random_node_by_type("VM")
            add_step(current, vm, "auth_session")

            container = self._get_random_node_by_type("Container")
            add_step(vm, container, "container_spawn")

            container2 = self._get_random_node_by_type("Container")
            add_step(container, container2, "east_west_traffic")

            service = self._get_random_node_by_type("Microservice")
            add_step(container2, service, "service_invocation")

            bucket = self._get_random_node_by_type("StorageBucket")
            add_step(service, bucket, "storage_access")

        elif motif == "C2":
            vm = self._get_random_node_by_type("VM")
            add_step(current, vm, "auth_session")

            container = self._get_random_node_by_type("Container")
            add_step(vm, container, "container_spawn")

            service = self._get_random_node_by_type("Microservice")
            add_step(container, service, "service_invocation")

            for _ in range(random.randint(1, 3)):
                next_service = self._get_random_node_by_type("Microservice")
                add_step(service, next_service, "service_invocation")
                service = next_service

        elif motif == "C3":
            container = self._get_random_node_by_type("Container")
            attack_nodes.append(container)

            for _ in range(random.randint(3, 4)):
                next_container = self._get_random_node_by_type("Container")
                add_step(container, next_container, "east_west_traffic")
                container = next_container

            service = self._get_random_node_by_type("Microservice")
            add_step(container, service, "service_invocation")

        # ======================================================
        # Sensitive Asset Enforcement
        # ======================================================

        sensitive_types = self.config.sensitive_asset_types
        if not any(
            self.graph.nodes[n]["node_type"] in sensitive_types
            for n in attack_nodes
        ):
            target_type = random.choice(sensitive_types)
            sensitive_node = self._get_random_node_by_type(target_type)
            add_step(attack_nodes[-1], sensitive_node,
                     self.config.relation_types[0])

        # Force boundary if none crossed
        if not boundary_crossed:
            node_types = list(self.config.node_types)
            t = random.choice(node_types)
            node = self._get_random_node_by_type(t)
            add_step(attack_nodes[-1], node,
                     self.config.relation_types[0])

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

    def _cross_boundary(self, prev_type: str, next_type: str) -> bool:
        for _, types in self.config.boundary_definition.items():
            if prev_type in types and next_type in types:
                if prev_type != next_type:
                    return True
        return False

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
    # PyG EXPORT
    # ==========================================================

    def to_pyg(self) -> Data:
        node_features = []
        node_types = []
        node_labels = []

        for _, data in self.graph.nodes(data=True):
            feat = np.random.randn(self.config.feature_dimensions)
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

        return Data(
            x=torch.from_numpy(np.array(node_features)).float(),
            edge_index=edge_index,
            edge_type=torch.tensor(edge_types),
            node_type=torch.tensor(node_types),
            y=torch.tensor(node_labels),
            edge_label=torch.tensor(edge_labels),
        )