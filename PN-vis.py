import xml.etree.ElementTree as ET


# Parse the XML file
tree = ET.parse('pathway.xml')
root = tree.getroot()



class Place:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.tokens = 0

    def add_tokens(self, count):
        self.tokens += count

    def consume_tokens(self, count):
        if self.tokens >= count:
            self.tokens -= count
            return True
        return False

    def __str__(self):
        return f"Place: {self.name} (Tokens: {self.tokens})"


class Transition:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __str__(self):
        return f"Transition: {self.name}"


class Arc:
    def __init__(self, source, target):
        self.source = source
        self.target = target

    def __str__(self):
        return f"Arc: {self.source} -> {self.target}"


class Group:
    def __init__(self, id, components):
        self.id = id
        self.components = components

    def __str__(self):
        return f"Group: {self.id} ({len(self.components)} components)"



# Create places, transitions, groups, and arcs based on XML components
places = {}
transitions = {}
groups = {}
arcs = []

for entry in root.findall('.//entry'):
    entry_id = entry.get('id')
    entry_name = entry.get('name')
    
    if entry_name.startswith('path:'):
        # Skip pathway component
        continue
    
    if entry.get('type') == 'gene':
        if entry_id not in places:
            # Create place
            place = Place(entry_id, entry_name)
            places[entry_id] = place
        else:
            # Create transition
            transition = Transition(entry_id, entry_name)
            transitions[entry_id] = transition
    
    if entry.get('type') == 'group':
        group_id = entry_id
        group_components = [c.get('id') for c in entry.findall('.//component')]
        group = Group(group_id, group_components)
        groups[group_id] = group

for relation in root.findall('.//relation'):
    entry1_id = relation.get('entry1')
    entry2_id = relation.get('entry2')
    
    entry1_name = places[entry1_id].name if entry1_id in places else transitions[entry1_id].name
    entry2_name = places[entry2_id].name if entry2_id in places else transitions[entry2_id].name
    
    arc_description = f"Relation: {entry1_name} -> {entry2_name}"
    arc = Arc(entry1_name, entry2_name)
    arcs.append(arc)
    
    print(arc_description)

# Print the Petri net representation
for place in places.values():
    print(place)

for transition in transitions.values():
    print(transition)

for group in groups.values():
    print(group)

for arc in arcs:
    print(arc)
