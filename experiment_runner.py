import torch

from config import (
    enterprise_A_config,
    enterprise_B_config,
    enterprise_C_config,
)
from generator import EnterpriseGraphGenerator
from models import GraphSAGEModel
from train import train, evaluate


def prepare_data(config):
    gen = EnterpriseGraphGenerator(config)
    graph = gen.generate()
    return gen.to_pyg()


if __name__ == "__main__":
    torch.manual_seed(42)

    print("Generating datasets...")
    data_A = prepare_data(enterprise_A_config)
    data_B = prepare_data(enterprise_B_config)
    data_C = prepare_data(enterprise_C_config)

    model = GraphSAGEModel(
        in_channels=data_A.num_node_features,
        hidden_channels=64,
    )

    print("\nTraining on Enterprise A...")
    train(model, data_A, epochs=60)

    evaluate(model, data_A, "Enterprise A (In-Domain)")
    evaluate(model, data_B, "Enterprise B (Cross-Domain)")
    evaluate(model, data_C, "Enterprise C (Cross-Domain)")