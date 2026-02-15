from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class EnterpriseConfig:
    name: str

    # Node / Relation schema
    node_types: List[str]
    relation_types: List[str]

    # Canonical mappings (enterprise -> global)
    canonical_node_map: Dict[str, str]
    canonical_relation_map: Dict[str, str]

    # Size
    node_counts: Dict[str, int]

    # Generation parameters
    edge_probability_rules: Dict[str, float]

    # Attack configuration
    attack_motif_definitions: List[str]
    sensitive_asset_types: List[str]
    boundary_definition: Dict[str, List[str]]

    # Features
    feature_dimensions: int


# ✅ ENTERPRISE A CONFIG
enterprise_A_config = EnterpriseConfig(
    name="Enterprise_A",

    node_types=[
        "Employee",
        "Workstation",
        "Server",
        "Process",
        "File",
        "DC",
    ],

    relation_types=[
        "login_event",
        "process_start",
        "process_spawn",
        "file_touch",
        "net_flow",
        "dc_auth",
    ],

    canonical_node_map={
        "Employee": "User",
        "Workstation": "Host",
        "Server": "Host",
        "Process": "Process",
        "File": "File",
        "DC": "DomainController",
    },

    canonical_relation_map={
        "login_event": "AUTH",
        "process_start": "EXEC",
        "process_spawn": "SPAWN",
        "file_touch": "ACCESS",
        "net_flow": "NET",
        "dc_auth": "DC_AUTH",
    },

    node_counts={
        "Employee": 80,
        "Workstation": 280,
        "Server": 20,
        "Process": 100,
        "File": 80,
        "DC": 1,
    },

    edge_probability_rules={
        "login_lambda": 5,
        "net_lambda": 3,
        "file_lambda": 4,
    },

    attack_motif_definitions=[
        "A1",
        "A2",
        "A3",
    ],

    sensitive_asset_types=[
        "Server",
        "DC",
        "File",
    ],

    boundary_definition={
        "user_to_host": ["Employee", "Workstation", "Server"],
        "host_to_dc": ["Server", "DC"],
    },

    feature_dimensions=16,
)