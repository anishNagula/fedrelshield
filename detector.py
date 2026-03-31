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
        return torch.sigmoid(self.fc2(x)).squeeze()


def train_detector(embeddings, labels, epochs=20):
    model = SimpleDetector(embeddings.size(1))
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.BCELoss()

    for epoch in range(epochs):
        preds = model(embeddings)
        loss = loss_fn(preds, labels.float())

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if epoch % 5 == 0:
            print(f"Epoch {epoch} Loss: {loss.item():.4f}")

    return model


def evaluate(model, embeddings, labels):
    with torch.no_grad():
        preds = model(embeddings)
        preds = (preds > 0.5).int()

        acc = (preds == labels).float().mean()
        print(f"Accuracy: {acc.item():.4f}")

