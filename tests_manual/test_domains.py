import sys
import os
import uuid
import json
from pathlib import Path

# Add path to find local libs
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cjm_graph_plugin_system.core import SourceRef, GraphNode
from cjm_graph_domains.domains.knowledge import Person, Work, Concept, Quote
from cjm_graph_domains.domains.relations import KnowledgeRelations

def title(msg):
    print(f"\n{'='*60}\n{msg}\n{'='*60}")

def verify_domain_logic():
    title("TEST: Domain Schema Logic")

    # 1. Test Person (Standard 'name' field)
    print("--- Testing Person Schema ---")
    try:
        p = Person(name="Sun Tzu", role="General", era="Ancient China")
        print(f"  Created Person: {p.name}")
        
        # Convert to GraphNode
        node = p.to_graph_node()
        print(f"  -> Converted to Node: {node.label}")
        print(f"  -> Properties: {node.properties}")
        
        assert node.label == "Person"
        assert node.properties['name'] == "Sun Tzu"
        assert node.properties['role'] == "General"
        assert 'id' not in node.properties, "ID should not be in properties"
        print("  [PASS] Person logic valid.")
        
    except Exception as e:
        print(f"  [FAIL] Person logic failed: {e}")
        raise e

    # 2. Test Work (Normalization: 'title' -> 'name')
    print("\n--- Testing Work Schema (Normalization) ---")
    try:
        # Create SourceRef for provenance
        ref = SourceRef("plugin_a", "table_b", "row_1")
        
        w = Work(title="The Art of War", author_name="Sun Tzu", year=-500)
        node = w.to_graph_node(sources=[ref])
        
        print(f"  Created Work: {w.title}")
        print(f"  -> Properties: {node.properties}")
        
        # Verify normalization logic
        assert node.properties['title'] == "The Art of War"
        assert node.properties['name'] == "The Art of War", "Name normalization failed!"
        assert len(node.sources) == 1
        assert node.sources[0].plugin_name == "plugin_a"
        print("  [PASS] Work normalization & SourceRef valid.")
        
    except Exception as e:
        print(f"  [FAIL] Work logic failed: {e}")
        raise e

    # 3. Test Quote (Normalization: 'text' -> 'name' truncation)
    print("\n--- Testing Quote Schema (Truncation) ---")
    long_text = "The art of war is of vital importance to the State. It is a matter of life and death, a road either to safety or to ruin."
    q = Quote(text=long_text)
    node = q.to_graph_node()
    
    print(f"  Quote Name (Truncated): {node.properties['name']}")
    assert len(node.properties['name']) <= 50
    assert node.properties['name'] == long_text[:50]
    print("  [PASS] Quote truncation valid.")

    # 4. Test Relations Registry
    print("\n--- Testing Relations Registry ---")
    rels = KnowledgeRelations.all()
    print(f"  Available Relations: {rels}")
    assert "AUTHORED" in rels
    assert "DISCUSSES" in rels
    print("  [PASS] Relations registry valid.")

if __name__ == "__main__":
    try:
        verify_domain_logic()
        title("ALL TESTS PASSED")
    except AssertionError as e:
        print(f"\n!!! ASSERTION FAILED !!!\n{e}")
    except Exception as e:
        print(f"\n!!! ERROR !!!\n{e}")