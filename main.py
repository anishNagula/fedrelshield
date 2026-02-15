from config import enterprise_A_config
from generator import EnterpriseGraphGenerator


gen = EnterpriseGraphGenerator(enterprise_A_config)

graph = gen.generate()
pyg_data = gen.to_pyg()

print("Nodes:", graph.number_of_nodes())
print("Edges:", graph.number_of_edges())
print("Attack instances:", len(graph.graph["attack_instances"]))
print("PyG Data:", pyg_data)