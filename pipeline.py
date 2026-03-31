from generator import EnterpriseGraphGenerator
from config import EnterpriseConfig

from ultra_embedder import UltraEmbedder
from detector import train_detector, evaluate

import torch


def main():
    # -----------------------------
    # 1. Generate graph
    # -----------------------------
    config = EnterpriseConfig()
    generator = EnterpriseGraphGenerator(config)

    graph = generator.generate()
    data = generator.to_pyg()

    print("Graph generated:")
    print(data)

    # -----------------------------
    # 2. Get ULTRA embeddings
    # -----------------------------
    embedder = UltraEmbedder(
        model_path="/home/sonic/ULTRA/ckpts/ultra_3g.pth",
        device="cuda" if torch.cuda.is_available() else "cpu"
    )

    embeddings = embedder.get_embeddings(data)
    print("Embeddings shape:", embeddings.shape)

    # -----------------------------
    # 3. Train detector
    # -----------------------------
    labels = data.y

    model = train_detector(embeddings, labels, epochs=20)

    # -----------------------------
    # 4. Evaluate
    # -----------------------------
    evaluate(model, embeddings, labels)


if __name__ == "__main__":
    main()
