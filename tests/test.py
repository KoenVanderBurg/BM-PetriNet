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
    assert len(pathway.nodes) > 0

def test_pathway_groups(pathway):

    assert len(pathway.groups) > 0

def test_pathway_transitions(pathway):

    assert len(pathway.transitions) > 0
