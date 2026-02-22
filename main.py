import random
import torch
import numpy as np
from config import (
    enterprise_A_config,
    enterprise_B_config,
    enterprise_C_config,
)
from generator import EnterpriseGraphGenerator
from analysis import analyze_graph


def run_enterprise(cfg):
    print(f"\n\n######## {cfg.name} ########")

    gen = EnterpriseGraphGenerator(cfg)
    graph = gen.generate()
    pyg_data = gen.to_pyg()

    print("\nGraph Summary:")
    print("Nodes:", graph.number_of_nodes())
    print("Edges:", graph.number_of_edges())
    print("Attack Instances:",
          len(graph.graph["attack_instances"]))

    analyze_graph(graph, name=cfg.name)

    return graph, pyg_data


torch.manual_seed(42)
random.seed(42)
np.random.seed(42)


if __name__ == "__main__":
    for cfg in [
        enterprise_A_config,
        enterprise_B_config,
        enterprise_C_config,
    ]:
        run_enterprise(cfg)