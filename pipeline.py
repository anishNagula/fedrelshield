def main():
    config = build_default_config()
    generator = EnterpriseGraphGenerator(config)

    graph = generator.generate()
    data = generator.to_pyg()

    print("Graph generated:", data)

    embedder = UltraEmbedder(
        model_path="/home/sonic/ULTRA/ckpts/ultra_3g.pth",
        device="cuda" if torch.cuda.is_available() else "cpu"
    )

    embeddings = embedder.get_embeddings(data)

    print("Embeddings shape:", embeddings.shape)
    print("Embedding mean:", embeddings.mean().item())
    print("Embedding std:", embeddings.std().item())

    labels = data.y

    model = train_detector(embeddings, labels, epochs=20)
    evaluate(model, embeddings, labels)
