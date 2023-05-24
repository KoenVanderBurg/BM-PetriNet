import networkx as nx
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import numpy as np

class Pathway:
    def __init__(self, name, org, number, title, length):
        self.name = name
        self.org = org
        self.number = number
        self.title = title
        self.nodes = []
        self.transitions = []
        self.groups = []

class Node:
    def __init__(self, node_type, name, node_id):
        self.type = node_type
        self.name = name
        self.id = node_id
        self.tokens = 0
        self.nextNodes= [] # Next nodes in the transition pathway.
        self.prevNodes = [] # Prev node in transition pathway.
    
    def add_token(self, count):
        self.tokens += count

    def consume_token(self, count):
        if self.tokens >= count:
            self.tokens -= count
            return True
        return False
    
    def __str__(self):
        return f"Id: {self.id} Node: {self.name} (Tokens: {self.tokens})"


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
        entry_id =int( entry.get('id'))
        entry_name = entry.get('name')
        entry_type = entry.get('type')

        # Create a node object and add it to the pathway
        node = Node(node_type=entry_type, name=entry_name, node_id=entry_id)

        pathway.nodes.append(node)

        # Add the node as a graph node in networkx
        graph.add_node(entry_id, name=entry_name)


    return None

def get_transitions(root, pathway, graph):
    # Iterate over the transition elements and create transitions
    for transition in root.findall('relation'):
        sender = int(transition.get('entry1'))
        receiver = int(transition.get('entry2'))


        # Add the receiver to the nextNodes of the sender.
        for node in pathway.nodes:
            if node.id == sender:
                node.nextNodes.append(receiver)
                print(f'Added {receiver} to {node.id} nextNodes')
            if node.id == receiver:
                node.prevNodes.append(sender)
                print(f'Added {sender} to {node.id} prevNodes')

        # Extract the 'subtype' element within the 'transition'
        subtype = transition.find('subtype')
        subtype_name = subtype.get('name') if subtype is not None else None

        # Create a transition object and add it to the pathway
        transition_obj = Transition(entry1=sender, entry2=receiver, type=subtype_name)
        pathway.transitions.append(transition_obj)

        # Add the transition as a graph edge in networkx
        graph.add_edge(sender, receiver, type=subtype_name)
    
    return None

def get_groups(root, pathway):

    # Iterate over the group elements and create groups
    for group in root.findall('entry[@type="group"]'):
        group_name = group.get('name')

        # Create a group object and add it to the pathway
        group_obj = Group(group_name=group_name)
        pathway.groups.append(group_obj)
    
    return None
    
def load_pathway(root, pathway, graph ):

    # Get the nodes
    get_nodes(root, pathway, graph)

    # Get the transitions
    get_transitions(root, pathway, graph)

    # Get the groups
    get_groups(root, pathway)

    return pathway

# Parse the XML file
tree = ET.parse('pathway.xml')
root = tree.getroot()

# Create a graph object using networkx
graph = nx.DiGraph()

# Create a pathway object
pathway = Pathway(
    name=root.get('name'),
    org=root.get('org'),
    number=root.get('number'),
    title=root.get('title'),
    length = len(root)
    )

load_pathway(root, pathway, graph)


# Perform graph visualization using networkx
# Add your visualization code here using the graph object G

for item in pathway.nodes:
    print(item)

for item in pathway.transitions:
    print(item)



nx.draw(graph, with_labels=True)
plt.show()