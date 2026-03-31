import sys
import torch
from types import SimpleNamespace

sys.path.append("/home/sonic/ULTRA")

from ultra import util


class UltraEmbedder:
    def __init__(self, model_path, device="cpu"):
        self.device = device

        cfg = SimpleNamespace()

        cfg.model = SimpleNamespace()

        cfg.model.entity_model = SimpleNamespace(
            class_="EntityNBFNet",
            input_dim=64,
            hidden_dims=[64, 64, 64, 64, 64, 64],
            message_func="distmult",
            aggregate_func="sum",
            layer_norm=True,
            short_cut=True
        )

        cfg.model.relation_model = SimpleNamespace(
            class_="RelNBFNet",
            input_dim=64,
            hidden_dims=[64, 64, 64, 64, 64, 64],
            message_func="distmult",
            aggregate_func="sum",
            layer_norm=True,
            short_cut=True
        )

        cfg.train = SimpleNamespace()
        cfg.train.gpus = None

        self.model = util.build_model(cfg).to(device)

        state = torch.load(model_path, map_location=device)
        self.model.load_state_dict(state["model"], strict=False)

        self.model.eval()

    def get_embeddings(self, data):
        data = data.to(self.device)

        x = data.x

        # ✅ Properly run through ALL entity_model layers
        with torch.no_grad():
            for layer in self.model.entity_model.layers:
                x = layer(
                    input=x,
                    query=None,
                    boundary=None,
                    edge_index=data.edge_index,
                    edge_type=data.edge_type,
                    size=None
                )

        return x.cpu()
