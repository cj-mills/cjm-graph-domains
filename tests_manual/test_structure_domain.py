import sys
import os
import uuid
from pathlib import Path

# Add path to find local libs
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cjm_graph_plugin_system.core import SourceRef, GraphNode, GraphEdge
from cjm_graph_domains.domains.structure import Document, Segment
from cjm_graph_domains.domains.relations import StructureRelations

def title(msg):
    print(f"\n{'='*60}\n{msg}\n{'='*60}")

def verify_structure_logic():
    title("TEST: Structure Domain Logic (The Narrative Spine)")

    # 1. Setup SourceRef
    ref = SourceRef("plugin_test", "transcriptions", "job_123")

    # 2. Create Document Root
    doc = Document(title="1. Laying Plans", media_type="audio")
    doc_node = doc.to_graph_node(sources=[ref])
    print(f"Created Document: {doc_node.properties['title']} ({doc_node.id})")

    # 3. Simulate Segmentation (Raw Text -> Segment Objects)
    raw_segments = [
        ("Laying Plans", "title"),
        ("Sun Tzu said,", "content"),
        ("The art of war is of vital importance to the State.", "content")
    ]
    
    nodes = [doc_node]
    edges = []
    
    print("\n--- Building Spine ---")
    previous_node = None
    
    for i, (text, role) in enumerate(raw_segments):
        # Create Segment
        seg = Segment(index=i, text=text, role=role)
        seg_node = seg.to_graph_node(sources=[ref])
        nodes.append(seg_node)
        
        print(f"  [{i}] {role.upper()}: {text[:30]}...")
        
        # Link: Segment -> Document (Containment)
        edges.append(GraphEdge(
            id=str(uuid.uuid4()),
            source_id=seg_node.id,
            target_id=doc_node.id,
            relation_type=StructureRelations.PART_OF
        ))
        
        # Link: Sequential (The Spine)
        if previous_node:
            # Segment(N-1) -> NEXT -> Segment(N)
            edges.append(GraphEdge(
                id=str(uuid.uuid4()),
                source_id=previous_node.id,
                target_id=seg_node.id,
                relation_type=StructureRelations.NEXT
            ))
            print(f"      Lked: {previous_node.properties['text'][:10]}... -> NEXT -> {seg_node.properties['text'][:10]}...")
        else:
            # Document -> STARTS_WITH -> Segment(0)
            edges.append(GraphEdge(
                id=str(uuid.uuid4()),
                source_id=doc_node.id,
                target_id=seg_node.id,
                relation_type=StructureRelations.STARTS_WITH
            ))
            print(f"      Root: Document -> STARTS_WITH -> {seg_node.properties['text'][:10]}...")
            
        previous_node = seg_node

    # 4. Verify Integrity
    print("\n--- Verifying Integrity ---")
    assert len(nodes) == 4 # Doc + 3 Segments
    assert len(edges) == 3 + 3 # 3 PART_OF + 1 STARTS_WITH + 2 NEXT
    
    # Check that Segment 0 is the start
    start_edge = next(e for e in edges if e.relation_type == "STARTS_WITH")
    assert start_edge.source_id == doc_node.id
    
    print(f"Total Nodes: {len(nodes)}")
    print(f"Total Edges: {len(edges)}")
    print("[PASS] Structure logic valid.")

if __name__ == "__main__":
    verify_structure_logic()