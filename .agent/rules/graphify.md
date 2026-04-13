# Global Rule: Project Knowledge Graph

This project has a `graphify` knowledge graph located at `graphify-out/`.

### 🛡️ Compliance Requirements
Before starting any significant architectural change, refactoring, or cross-module feature, you MUST:
1.  **Consult the Map**: Read `graphify-out/GRAPH_REPORT.md` to identify the "God Nodes" (central hubs) and surprising dependencies.
2.  **Verify Impact**: Use the graph context to ensure that changes to high-connectivity nodes don't have unintended downstream effects.
3.  **Update the Graph**: If you make significant structural changes (new modules, major API shifts), remind the user to re-run `./scripts/generate-graph.sh .` or offer to run it yourself to keep the cache current.

### 🔍 Quick Reference
- **Graph Visualization**: `graphify-out/graph.html` (for user reference).
- **Core Insights**: `graphify-out/GRAPH_REPORT.md`.
- **Raw Data**: `graphify-out/graph.json`.
