import pytest
import matplotlib.pyplot as plt
import os

from KGML_PetriNet.pathway import Pathway
import KGML_PetriNet as PN

# Load the test data
@pytest.fixture
def pathway():
    pathway = os.path.join(os.getcwd(), 'pathway.xml')
    return Pathway(pathway)

# Test the pathway class
def test_pathway_nodes(pathway):
    # for node in pathway.nodes.values():
        # print(node)
    # print(len(pathway.nodes))
    assert len(pathway.nodes) > 0

def test_pathway_groups(pathway):
    # for group in pathway.groups.values():
    #     print(group)
    # print(len(pathway.groups))

    assert len(pathway.groups) > 0

def test_pathway_transitions(pathway):
    # for transition in pathway.transitions:
    #     print(transition)
    # print(len(pathway.transitions))
    
    assert len(pathway.transitions) > 0