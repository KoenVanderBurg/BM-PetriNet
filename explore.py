import xml.etree.ElementTree as ET

# Parse the XML file
tree = ET.parse('pathway.xml')
root = tree.getroot()

# Iterate over the 'entry' elements
for entry in root.findall('entry'):
    entry_id = entry.get('id') # Right id 
    entry_name = entry.get('name') #  Right name 
    entry_type = entry.get('type') # Right type
    entry_link = entry.get('link')

    # Extract the 'graphics' element within the 'entry'
    graphics = entry.find('graphics')
    graphics_name = graphics.get('name')
    graphics_fgcolor = graphics.get('fgcolor')
    graphics_bgcolor = graphics.get('bgcolor')
    graphics_type = graphics.get('type')
    graphics_x = graphics.get('x')
    graphics_y = graphics.get('y')
    graphics_width = graphics.get('width')
    graphics_height = graphics.get('height')


    # Print the extracted information
    print(f"Entry ID: {entry_id}")
    print(f"Entry Name: {entry_name}")
    print(f"Entry Type: {entry_type}")
    print(f"Entry Link: {entry_link}")
    print(f"Graphics Name: {graphics_name}")
    print(f"Graphics Foreground Color: {graphics_fgcolor}")
    print(f"Graphics Background Color: {graphics_bgcolor}")
    print(f"Graphics Type: {graphics_type}")
    print(f"Graphics X: {graphics_x}")
    print(f"Graphics Y: {graphics_y}")
    print(f"Graphics Width: {graphics_width}")
    print(f"Graphics Height: {graphics_height}")
    print("----")

# iterate over the 'relation' elements
for relation in root.findall('relation'):
    relation_entry1 = relation.get('entry1') # Right entry1
    relation_entry2 = relation.get('entry2') # Right entry2

    # Extract the 'subtype' element within the 'relation'
    subtype = relation.find('subtype')
    subtype_name = subtype.get('name') if subtype is not None else None # Right subtype name

    # Print the extracted information
    print(f"Relation Entry1: {relation_entry1}")
    print(f"Relation Entry2: {relation_entry2}")
    print(f"Subtype Name: {subtype_name}")
    print("----")