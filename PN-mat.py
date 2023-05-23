import networkx as nx
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET

# Parse the XML file
tree = ET.parse('pathway.xml')
root = tree.getroot()

# Create a directed graph
G = nx.DiGraph()

# Iterate over the entry elements and add nodes to the graph
for entry in root.findall(".//entry[@type='gene']"):
    entry_id = entry.get('id')
    entry_name = entry.get('name')
    G.add_node(entry_id, name=entry_name)

# Iterate over the group elements and add nodes to the graph
for group in root.findall(".//entry[@type='group']"):
    group_id = group.get('id')
    G.add_node(group_id)

    # Iterate over the component elements and add edges to the graph
    for component in group.findall('component'):
        component_id = component.get('id')
        G.add_edge(group_id, component_id)

# Iterate over the relation elements and add edges to the graph
for relation in root.findall(".//relation"):
    entry1 = relation.get('entry1')
    entry2 = relation.get('entry2')
    G.add_edge(entry1, entry2)

# Plot the graph
pos = nx.spring_layout(G)  # Layout algorithm for node positioning
plt.figure(figsize=(20, 20))
nx.draw_networkx(G, pos, with_labels=True, node_size=500, font_size=8)
plt.axis('off')
plt.show()
