import torch
import torch.nn.functional as F
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)

from models import GraphSAGEModel


def train(model, data, epochs=50, lr=0.01):
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    model.train()
    for epoch in range(epochs):
        optimizer.zero_grad()

        logits = model(data.x, data.edge_index)
        loss = F.binary_cross_entropy_with_logits(
            logits,
            data.y.float(),
        )

        loss.backward()
        optimizer.step()

        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}, Loss: {loss.item():.4f}")


def evaluate(model, data, name="Dataset"):
    model.eval()
    with torch.no_grad():
        logits = model(data.x, data.edge_index)
        probs = torch.sigmoid(logits)
        preds = (probs > 0.5).int()

    y_true = data.y.cpu().numpy()
    y_pred = preds.cpu().numpy()

    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    cm = confusion_matrix(y_true, y_pred)

    print(f"\n===== Evaluation on {name} =====")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print("Confusion Matrix:")
    print(cm)

    return precision, recall, f1, cm