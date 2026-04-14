import os
import sys
import json
from pathlib import Path

# Fix PYTHONPATH to include .venv libraries and prioritize security_venv
sys.path.insert(0, str(Path('security_venv/lib/python3.9/site-packages').resolve()))
sys.path.append(str(Path('.venv/lib/python3.14/site-packages').resolve()))

from graphify.detect import detect
from graphify.extract import extract, collect_files
from graphify.build import build_from_json
from graphify.cluster import cluster, score_all
from graphify.export import to_json, to_html

def run_pipeline(target_path):
    out_dir = Path("graphify-out")
    out_dir.mkdir(exist_ok=True)
    
    print(f"--- Step 1: Detect files in {target_path} ---")
    detection = detect(Path(target_path))
    print(f"Found {detection['total_files']} files ({detection['total_words']} words)")
    
    print("--- Step 2: Structural extraction (AST) ---")
    code_files = []
    for f in detection.get('files', {}).get('code', []):
        code_files.extend(collect_files(Path(f)) if Path(f).is_dir() else [Path(f)])
    
    extraction = extract(code_files)
    print(f"Extracted {len(extraction['nodes'])} nodes, {len(extraction['edges'])} edges")
    
    print("--- Step 3: Build & Cluster ---")
    G = build_from_json(extraction)
    communities = cluster(G)
    cohesion = score_all(G, communities)
    
    print(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges, {len(communities)} communities")
    
    print("--- Step 4: Export ---")
    to_json(G, communities, str(out_dir / "graph.json"))
    to_html(G, communities, str(out_dir / "graph.html"))
    print(f"HTML graph written to {out_dir}/graph.html")
    
    return G

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    run_pipeline(path)
