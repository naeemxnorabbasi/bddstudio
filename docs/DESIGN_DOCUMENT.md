# Design Document

BDD Studio separates the deterministic BDD engine from rendering and reporting.

Pipeline:

1. Load YAML project.
2. Parse Boolean expressions into an AST.
3. Expand intermediate signals.
4. Build a full ordered BDD using Shannon cofactoring.
5. Reduce by explicit rules:
   - Rule 1: eliminate nodes with identical low/high children.
   - Rule 2: merge isomorphic nodes with same variable, low child, and high child.
6. Emit DOT diagrams and node tables.
7. Optionally render DOT to PNG/SVG/PDF with Graphviz.
8. Write Markdown/HTML reports.

The convention is:

`Node(x, low, high) = (~x & low) | (x & high)`

Low edge is variable value 0. High edge is variable value 1.
