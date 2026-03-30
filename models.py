import torch
import torch.nn.functional as F
from torch import nn


class RelGraphSAGE(nn.Module):
    def __init__(self, in_channels, num_relations, hidden_channels=64):
        super().__init__()

        self.num_relations = num_relations

        # relation-specific transformations
        self.rel_weights = nn.ModuleList([
            nn.Linear(in_channels, hidden_channels)
            for _ in range(num_relations)
        ])

        self.lin_self = nn.Linear(in_channels, hidden_channels)
        self.lin_out = nn.Linear(hidden_channels, 1)

    def forward(self, x, edge_index, edge_type):
        row, col = edge_index

        out = torch.zeros(x.size(0), self.lin_self.out_features, device=x.device)

        # apply relation-specific transforms
        for rel in range(self.num_relations):
            mask = (edge_type == rel)
            if mask.sum() == 0:
                continue

            src = row[mask]
            dst = col[mask]

            messages = self.rel_weights[rel](x[src])
            out.index_add_(0, dst, messages)

        # add self node contribution
        out = out + self.lin_self(x)

        out = F.relu(out)

        return self.lin_out(out).squeeze(-1)
