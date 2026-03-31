import torch
import torch.nn as nn
import torch.nn.functional as F


class SimpleDetector(nn.Module):
    def __init__(self, in_dim):
        super().__init__()
        self.fc1 = nn.Linear(in_dim, 32)
        self.fc2 = nn.Linear(32, 1)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        return self.fc2(x).squeeze()  # ❗ no sigmoid


def train_detector(embeddings, labels, epochs=20):
    model = SimpleDetector(embeddings.size(1))

    # ✅ handle imbalance
    num_pos = labels.sum().item()
    num_neg = len(labels) - num_pos
    pos_weight = torch.tensor(num_neg / (num_pos + 1e-6))

    loss_fn = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)

    for epoch in range(epochs):
        logits = model(embeddings)
        loss = loss_fn(logits, labels.float())

        opt.zero_grad()
        loss.backward()
        opt.step()

        if epoch % 5 == 0:
            print(f"Epoch {epoch}, Loss: {loss.item():.4f}")

    return model


def evaluate(model, embeddings, labels):
    with torch.no_grad():
        logits = model(embeddings)
        preds = (torch.sigmoid(logits) > 0.5).int()

        acc = (preds == labels).float().mean()

        print("Accuracy:", acc.item())
