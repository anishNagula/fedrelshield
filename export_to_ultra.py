import random
from generator import EnterpriseGraphGenerator
from config import enterprise_A_config

def export_ultra_format():
    gen = EnterpriseGraphGenerator(enterprise_A_config)
    graph = gen.generate()

    triplets = []
    entities = set()
    relations = set()

    for u, v, data in graph.edges(data=True):
        r = data["edge_type"]
        triplets.append((str(u), r, str(v)))
        entities.add(str(u))
        entities.add(str(v))
        relations.add(r)

    # Create mappings
    entity2id = {e: i for i, e in enumerate(sorted(entities))}
    relation2id = {r: i for i, r in enumerate(sorted(relations))}

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

    # Write dicts
    with open("entities.dict", "w") as f:
        for e, i in entity2id.items():
            f.write(f"{i}\t{e}\n")

    with open("relations.dict", "w") as f:
        for r, i in relation2id.items():
            f.write(f"{i}\t{r}\n")

    print("Export complete.")

if __name__ == "__main__":
    export_ultra_format()
