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
# ✅ ENTERPRISE B CONFIG
enterprise_B_config = EnterpriseConfig(
    name="Enterprise_B",

    node_types=[
        "User",
        "Host",
        "Subnet",
        "InternalService",
        "DC",
    ],

    relation_types=[
        "session_open",
        "socket_connect",
        "cross_subnet",
        "api_call",
        "dc_session",
    ],

    canonical_node_map={
        "User": "User",
        "Host": "Host",
        "Subnet": "Host",
        "InternalService": "Service",
        "DC": "DomainController",
    },

    canonical_relation_map={
        "session_open": "AUTH",
        "socket_connect": "NET",
        "cross_subnet": "NET",
        "api_call": "SERVICE_CALL",
        "dc_session": "DC_AUTH",
    },

    node_counts={
        "User": 60,
        "Host": 200,
        "Subnet": 4,
        "InternalService": 80,
        "DC": 1,
    },

    edge_probability_rules={
        "session_lambda": 4,
        "socket_lambda": 3,
        "api_lambda": 4,
    },

    attack_motif_definitions=[
        "B1",
        "B2",
        "B3",
    ],

    sensitive_asset_types=[
        "Host",
        "InternalService",
        "DC",
    ],

    boundary_definition={
        "subnet_boundary": ["Host", "Subnet"],
        "dc_boundary": ["Host", "DC"],
    },

    feature_dimensions=16,
)
# ✅ ENTERPRISE C CONFIG
enterprise_C_config = EnterpriseConfig(
    name="Enterprise_C",

    node_types=[
        "Identity",
        "VM",
        "Container",
        "Microservice",
        "StorageBucket",
    ],

    relation_types=[
        "auth_session",
        "container_spawn",
        "east_west_traffic",
        "service_invocation",
        "storage_access",
    ],

    canonical_node_map={
        "Identity": "User",
        "VM": "Host",
        "Container": "Container",
        "Microservice": "Service",
        "StorageBucket": "File",
    },

    canonical_relation_map={
        "auth_session": "AUTH",
        "container_spawn": "SPAWN",
        "east_west_traffic": "NET",
        "service_invocation": "SERVICE_CALL",
        "storage_access": "ACCESS",
    },

    node_counts={
        "Identity": 70,
        "VM": 60,
        "Container": 200,
        "Microservice": 120,
        "StorageBucket": 40,
    },

    edge_probability_rules={
        "auth_lambda": 3,
        "traffic_lambda": 6,
        "service_lambda": 5,
    },

    attack_motif_definitions=[
        "C1",
        "C2",
        "C3",
    ],

    sensitive_asset_types=[
        "StorageBucket",
        "Microservice",
    ],

    boundary_definition={
        "vm_container": ["VM", "Container"],
        "service_storage": ["Microservice", "StorageBucket"],
    },

    feature_dimensions=16,
)