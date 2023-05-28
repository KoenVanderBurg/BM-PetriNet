import networkx as nx
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class Pathway:
    def __init__(self, name, org, number, title, length):
        self.name = name
        self.org = org
        self.number = number
        self.title = title
        self.length = length
        self.nodes = []
        self.transitions = []
        self.groups = []

class Node:
    def __init__(self, node_type, name, node_id):
        self.type = node_type
        self.name = name
        self.gene_name = None
        self.id = node_id
        self.x = None
        self.y = None
        self.width = None
        self.height = None
        self.tokens = 0
        self.next_nodes = []
        self.prev_nodes = []
    
    def set_gene_name(self, gene_name):
        self.gene_name = gene_name

    def set_graphics(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def add_token(self, count):
        self.tokens += count

    def consume_token(self, count):
        if self.tokens >= count:
            self.tokens -= count
            return True
        return False
    
    def __str__(self):
        return f"Id: {self.id} Node: {self.name} (Tokens: {self.tokens}, Gene: {self.gene_name}, prev: {self.prev_nodes}, next: {self.next_nodes})"


class Transition:
    def __init__(self, entry1, entry2, type):
        self.entry1 = entry1
        self.entry2 = entry2
        self.type = type

    def __str__(self): 
        return f"Transition: {self.entry1} -> {self.entry2} Type: {self.type}"

class Group:
    def __init__(self, group_name):
        self.name = group_name


def get_nodes(root, pathway, graph):
    # Iterate over the entry elements and create nodes
    for entry in root.findall('entry[@type="gene"]'):
        entry_id = int(entry.get('id'))
        entry_name = entry.get('name')
        entry_type = entry.get('type')

        node = Node(node_type=entry_type, name=entry_name, node_id=entry_id)

        # Get gene name from graphics section
        graphics = entry.find('graphics')
        if graphics is not None:
            gene_name = graphics.get('name', '').split(',')[0].strip()
            node.set_gene_name(gene_name)

            nodeX = graphics.get('x')
            nodeY = graphics.get('y')
            nodeWidth = graphics.get('width')
            nodeHeight = graphics.get('height')
            node.set_graphics(nodeX, nodeY, nodeWidth, nodeHeight)

        pathway.nodes.append(node)

    return None

def get_transitions(root, pathway, graph):
    # Iterate over the transition elements and create transitions
    for transition in root.findall('relation'):
        sender = int(transition.get('entry1'))
        receiver = int(transition.get('entry2'))

        # Add the receiver to the nextNodes of the sender.
        for node in pathway.nodes:
            if node.id == sender:
                node.next_nodes.append(receiver)
            if node.id == receiver:
                node.prev_nodes.append(sender)

        subtype = transition.find('subtype')
        subtype_name = subtype.get('name') if subtype is not None else None

        transition_obj = Transition(entry1=sender, entry2=receiver, type=subtype_name)
        pathway.transitions.append(transition_obj)

        graph.add_edge(sender, receiver, type=subtype_name)
    
    return None

def get_groups(root, pathway):
    # Iterate over the group elements and create groups
    for group in root.findall('entry[@type="group"]'):
        group_name = group.get('name')

        group_obj = Group(group_name=group_name)
        pathway.groups.append(group_obj)
    
    return None
    
def load_pathway(root, pathway, graph):
    get_nodes(root, pathway, graph)
    get_transitions(root, pathway, graph)
    get_groups(root, pathway)

    return pathway

def get_starting_nodes(pathway):
    starting_nodes = {}

    for node in pathway.nodes:
        if node.gene_name is not None and node.gene_name.startswith('TLR'):    
            starting_nodes[node.id] = node.next_nodes

    return starting_nodes

def create_node_pairs(nodes):
    pairs = {}
    
    for node in nodes:
        current_id = node.id
        
        for prev_id in node.prev_nodes:
            pairs[(prev_id, current_id)] = True
        
        for next_id in node.next_nodes:
            pairs[(current_id, next_id)] = True
    
    return pairs

def get_transition_pairs(starting_nodes):
    transition_pairs = []
    for key, values in starting_nodes.items():
        for value in values:
            transition_pairs.append((key, value))
    return transition_pairs

def set_initial_tokens(pathway, gene_tokens):
    for node in pathway.nodes:
        if node.gene_name in gene_tokens:
            node.add_token(gene_tokens[node.gene_name])

def update_plot(frame, node_pairs):
    ax.clear()

    color_mappings = {
        'expression': 'blue',
        'activation': 'green',
        'phosphorylation': 'red',
        'binding/association': 'orange',
        'inhibition': 'purple'
    }

    for node in pathway.nodes:
        if node.x is not None and node.y is not None and node.width is not None and node.height is not None:
            x = int(node.x)
            y = int(node.y)
            width = int(node.width)
            height = int(node.height)

            rect = plt.Rectangle((x, y), width, height, facecolor='lightblue', edgecolor='black')
            ax.add_patch(rect)
            ax.text(x + 0.4 * width, y + 0.5 * height, node.gene_name, ha='center', va='center', fontsize=6)
            ax.text(x + 0.7 * width, y + 5, f'({node.tokens})',  fontsize=7)

            for pair in node_pairs:
                if node.id == pair[0]:
                    start_x = x + 0.5 * width
                    start_y = y + 0.5 * height
                    for other_node in pathway.nodes:
                        if other_node.id == pair[1]:
                            end_x = int(other_node.x) + 0.5 * int(other_node.width)
                            end_y = int(other_node.y) + 0.5 * int(other_node.height)
                            relationship_type = None
                            for transition in pathway.transitions:
                                if transition.entry1 == pair[0] and transition.entry2 == pair[1]:
                                    relationship_type = transition.type
                                    break
                            color = color_mappings.get(relationship_type, 'black')
                            ax.plot([start_x + 0.5 * width, end_x - 0.5 * width], [start_y, end_y], color=color)
                            ax.plot(start_x + 0.55 * width, start_y, 'go', markersize=5)
                            ax.plot(end_x - 0.55 * width, end_y, 'ro', markersize=5)

    legend_elements = [
        plt.Line2D([0], [0], color=color, lw=1, label=relationship_type)
        for relationship_type, color in color_mappings.items()
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=7)

    ax.set_aspect('equal')
    ax.set_xlim(0, 1400)
    ax.set_ylim(0, 800)

    ax.set_title('Petri Net Visualization')

    return ax


tree = ET.parse('pathway.xml')
root = tree.getroot()

graph = nx.DiGraph()

pathway = Pathway(
    name=root.get('name'),
    org=root.get('org'),
    number=root.get('number'),
    title=root.get('title'),
    length=len(root)
)

pathway = load_pathway(root, pathway, graph)

# Example usage
gene_tokens = {
    'TLR1': 10,
    'TLR2': 5,
    'TLR3': 3,
    'TLR4': 7,
    'TLR5': 2
}

set_initial_tokens(pathway, gene_tokens)

starting_nodes = get_starting_nodes(pathway)

transition_pairs = get_transition_pairs(starting_nodes)    

node_pairs = create_node_pairs(pathway.nodes)

fig, ax = plt.subplots()

animation = FuncAnimation(fig, update_plot, fargs=(node_pairs,), frames=100, interval=200)

plt.show()
