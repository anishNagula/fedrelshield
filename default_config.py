from config import EnterpriseConfig


def build_default_config():
    return EnterpriseConfig(
        name="enterprise_sim",

        # -------------------------
        # Node / relation types
        # -------------------------
        node_types=[
            "User", "Host", "Process", "File",
            "Service", "Container", "DomainController"
        ],

        relation_types=[
            "login_event", "process_start", "file_touch",
            "socket_connect", "api_call", "service_invocation"
        ],

        # -------------------------
        # Canonical mappings
        # -------------------------
        canonical_node_map={
            "User": "User",
            "Host": "Host",
            "Process": "Process",
            "File": "File",
            "Service": "Service",
            "Container": "Container",
            "DomainController": "DomainController"
        },

        canonical_relation_map={r: r for r in [
            "login_event", "process_start", "file_touch",
            "socket_connect", "api_call", "service_invocation"
        ]},

        # -------------------------
        # Scale this UP later
        # -------------------------
        node_counts={
            "User": 200,
            "Host": 400,
            "Process": 800,
            "File": 800,
            "Service": 300,
            "Container": 300,
            "DomainController": 20
        },

        # not used heavily right now
        edge_probability_rules={},

        # -------------------------
        # Attack motifs (reuse yours)
        # -------------------------
        attack_motif_definitions=[
            "A1", "A2", "A3",
            "B1", "B2", "B3",
            "C1", "C2", "C3"
        ],

        sensitive_asset_types=[
            "DomainController", "Service"
        ],

        boundary_definition={
            "enterprise": [
                "User", "Host", "Process", "File",
                "Service", "Container", "DomainController"
            ]
        },

        feature_dimensions=64
    )
