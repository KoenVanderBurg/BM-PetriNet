import networkx as nx
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button 
import random

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


    def transfer_tokens(pathway):
        transfer_info = []

        for node in pathway.nodes:
            # Check if the node has more than one next node and if it is not an inhibition transition
            if len(node.next_nodes) > 1 and not any(transition.type == 'inhibition' for transition in pathway.transitions if transition.entry1 == node.id):
                num_next_nodes = len(node.next_nodes)
                transferred_tokens = node.tokens

                if node.consume_token(transferred_tokens):
                    # Calculate the number of tokens to transfer to each next node and the remaining tokens to transfer to the last next node.
                    tokens_to_transfer = transferred_tokens // num_next_nodes
                    remaining_tokens = transferred_tokens % num_next_nodes

                    # Add the next nodes and the number of tokens to transfer to the transfer_info list.
                    for next_node_id in node.next_nodes[:-1]:
                        next_node = next((n for n in pathway.nodes if n.id == next_node_id), None)
                        if next_node is not None:
                            transfer_info.append((node, next_node, tokens_to_transfer))
                    
                    # Add the last next node and the number of tokens to transfer to the transfer_info list.
                    last_next_node_id = node.next_nodes[-1]
                    last_next_node = next((n for n in pathway.nodes if n.id == last_next_node_id), None)
                    if last_next_node is not None:
                        transfer_info.append((node, last_next_node, tokens_to_transfer + remaining_tokens))
           
            elif len(node.next_nodes) == 1:
                next_node_id = node.next_nodes[0]
                next_node = next((n for n in pathway.nodes if n.id == next_node_id), None)
                if next_node is not None:
                    relationship_type = None
                    for transition in pathway.transitions:
                        if transition.entry1 == node.id and transition.entry2 == next_node.id:
                            relationship_type = transition.type
                            break

                    if relationship_type in ['activation', 'expression', 'binding/association']:
                        transferred_tokens = node.tokens
                        if node.consume_token(transferred_tokens):
                            transfer_info.append((node, next_node, transferred_tokens))

        # for node, nnode, ttokens in transfer_info:
        #     print(f"{node.gene_name} ({node.id}) -> {nnode.gene_name} ({nnode.id}) ({ttokens})")

        # Shuffle the transfer_info list to randomize the firing order
        random.shuffle(transfer_info)

        print("New token distribution step: ")
        print("---------------------------------------------------------")

        # Perform the token transfers
        for node, next_node, transferred_tokens in transfer_info:
            next_node.add_token(transferred_tokens)
            if transferred_tokens > 0:
                # Print the token transfer information
                print(f" ({transferred_tokens}) tokens {node.gene_name} ({node.id}) -> {next_node.gene_name} ({next_node.id}), {next_node.gene_name} tokens: {next_node.tokens}, next nodes: {next_node.next_nodes}")



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

            nodeX =int(graphics.get('x')) * 1.5
            nodeY =int(graphics.get('y')) * 1.5
            nodeWidth =int( graphics.get('width')) * 1.75
            nodeHeight = int(graphics.get('height')) * 1.2
            node.set_graphics(nodeX, nodeY, nodeWidth, nodeHeight)

        pathway.nodes.append(node)

    return None

def get_transitions(root, pathway, graph):
    # Iterate over the transition elements and create transitions
    for transition in root.findall('relation'):
        sender = int(transition.get('entry1'))
        receiver = int(transition.get('entry2'))

        # if sender or receiver > 190 skip this transition
        if sender > 190 or receiver > 190:
            continue

        # Add the receiver to the nextNodes of the sender.
        for node in pathway.nodes:
            if node.id == sender:
                node.next_nodes.append(receiver)
                # print(f"Added {receiver}  next_nodes of {sender}")
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
            if any(n.id == prev_id for n in nodes):  # Check if previous node exists in the list
                pairs[(prev_id, current_id)] = True

        for next_id in node.next_nodes:
            next_node = next((n for n in nodes if n.id == next_id), None)  # Find the next node by ID
            if next_node and next_node.type != 'group':  # Only consider non-group next nodes
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


def update_plot(frame, pathway, node_pairs):
    ax.clear()

    if frame != 0:
        pathway.transfer_tokens()

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
            if node.tokens > 0:
                ax.text(x + 0.7 * width, y + 5, f'{node.tokens}',  fontsize=7, color='red')
            else: 
                ax.text(x + 0.7 * width, y + 5, f'{node.tokens}',  fontsize=7, color='black')
            
            # add the frame counter to the plot area
            ax.text(0.5, 0.95, f'Frame: {frame}', transform=ax.transAxes, fontsize=10, verticalalignment='top', horizontalalignment='center')

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
    ax.set_xlim(0, 1800)
    ax.set_ylim(0, 1200)

    ax.set_title('Petri Net Visualization')
    plt.draw()

    return ax


def next_frame(event):
    global frame_index
    frame_index += 1
    if frame_index >= 100:
        frame_index = 0
    # animation._draw_next_frame(frame_index)
    update_plot(frame_index, pathway, node_pairs)


# Start of main program
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

# Initialize the pathway object. 
pathway = load_pathway(root, pathway, graph)



# Set the initial tokens for the genes
gene_tokens = {
    'TLR1': 10,
    'TLR3': 3,
    'TLR4': 7,
    'TLR5': 2
}
set_initial_tokens(pathway, gene_tokens)

# Create the node pairs for the visualization of all the nodes.
node_pairs = create_node_pairs(pathway.nodes)

# for node1, node2 in node_pairs:
#     print(f'{node1} -> {node2}')

fig, ax = plt.subplots()
frame_index = 0

# Create the next frame button to display the each frame of the pathway.
next_frame_button_ax = plt.axes([0.8, 0.02, 0.1, 0.05])
next_frame_button = Button(next_frame_button_ax, 'Next Frame', color='lightgray', hovercolor='skyblue')
next_frame_button.on_clicked(next_frame)


# Create the plot for the pathway.
update_plot(frame_index, pathway, node_pairs)
plt.show()


# animation = FuncAnimation(fig, update_plot, fargs=(node_pairs,), frames=100, interval=200, blit = False)
## Get the starting nodes and their transition pairs (TLR) specific. 
# starting_nodes = get_starting_nodes(pathway)
# transition_pairs = get_transition_pairs(starting_nodes)    