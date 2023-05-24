import networkx as nx
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET

# Parse the XML file
tree = ET.parse('pathway.xml')
root = tree.getroot()

# Create a directed graph
G = nx.DiGraph()

# Define colors for different groups
group_colors = {
    '191': '#F2C0B8',  # Light pink
    '192': '#D2E2F3',  # Light blue
    '193': '#D8F3D2',  # Light green
    '194': '#F3D8D8',  # Light red
    '195': '#F3F3D8',  # Light yellow
    '196': '#F3E6D8',  # Light orange
}

# Iterate over the entry elements and add nodes to the graph
for entry in root.findall(".//entry[@type='gene']"):
    entry_id = entry.get('id')
    entry_name = entry.get('name')
    G.add_node(entry_id, name=entry_id)

    # # Get ID and name from graphics section
    # graphics = entry.find('graphics')
    # if graphics is not None:
    #     graphics_id = graphics.get('name', '')
    #     G.nodes[entry_id]['graphics_id'] = graphics_id

# Iterate over the group elements and assign colors to component nodes
for group in root.findall(".//entry[@type='group']"):
    group_id = group.get('id')

    # Iterate over the component elements and add nodes to the graph
    for component in group.findall('component'):
        component_id = component.get('id')
        G.add_node(component_id)

        # Assign color attribute to component node
        G.nodes[component_id]['color'] = group_colors.get(group_id, 'gray')

# Iterate over the relation elements and add edges to the graph
for relation in root.findall(".//relation"):
    entry1 = relation.get('entry1')
    entry2 = relation.get('entry2')
    subtype = relation.find("./subtype")
    subtype_name = subtype.get('name') if subtype is not None else ''
    G.add_edge(entry1, entry2, subtype_name=subtype_name)

for edge in G.edges.data():
    print(edge)

# Plot the graph with colored nodes and labels
pos = nx.spring_layout(G)  # Layout algorithm for node positioning
node_colors = [G.nodes[node].get('color', 'gray') for node in G.nodes]
node_labels = {node: G.nodes[node].get('name', '') for node in G.nodes}
edge_labels = {(edge[0], edge[1]): '' for edge in G.edges}

plt.figure(figsize=(12, 8))
nx.draw_networkx(G, pos, with_labels=False, node_size=500, node_color=node_colors)
nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=8)

# Draw edge labels
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

plt.axis('off')
plt.show()