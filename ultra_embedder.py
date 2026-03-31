import torch
from torch_geometric.data import Data
from ultra.models import Ultra

class UltraEmbedder:
    def __init__(self, model_path, device="cpu"):
        self.device = device

        self.model = Ultra(
            input_dim=64,
            hidden_dims=[64, 64, 64, 64, 64, 64],
            relation_input_dim=64
        ).to(device)

        state = torch.load(model_path, map_location=device)
        self.model.load_state_dict(state["model"], strict=False)
        self.model.eval()

    def get_embeddings(self, data: Data):
        data = data.to(self.device)

        with torch.no_grad():
            # ULTRA forward pass
            node_emb = self.model.entity_model(data.x, data.edge_index, data.edge_type)
        
        return node_emb.cpu()

