import random
from generator import EnterpriseGraphGenerator
from config import enterprise_A_config  # you can change this

def export_ultra_format():
    gen = EnterpriseGraphGenerator(enterprise_A_config)
    graph = gen.generate()

    triplets = []

    for u, v, data in graph.edges(data=True):
        relation = data["edge_type"]
        triplets.append((str(u), relation, str(v)))

    random.shuffle(triplets)

    n = len(triplets)
    train = triplets[:int(0.7 * n)]
    valid = triplets[int(0.7 * n):int(0.85 * n)]
    test  = triplets[int(0.85 * n):]

    def write(file, data):
        with open(file, "w") as f:
            for h, r, t in data:
                f.write(f"{h} {r} {t}\n")

    write("train.txt", train)
    write("valid.txt", valid)
    write("test.txt", test)

    print(f"Done. Total triplets: {n}")

if __name__ == "__main__":
    export_ultra_format()
