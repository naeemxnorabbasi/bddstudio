# GUI Features, Limitations, and Future Work

## Features in v0.5

- Local CAD-style browser GUI.
- YAML project editor.
- Built-in 3×2 multiplier example.
- Project validation.
- Build button for BDD/ROBDD generation.
- Output selector.
- Diagram selector.
- PNG preview when Graphviz is installed.
- Node-table inspector.
- Reduction-log inspector.
- Truth-table inspector.
- HTML report launcher.
- Local run folders for reproducible artifacts.

## Current limitations

- The GUI is a professional MVP, not yet a full commercial CAD application.
- Diagram pan/zoom is handled by browser scrolling, not a dedicated SVG canvas.
- It previews PNG diagrams primarily; SVG viewing is available through artifacts but not yet a rich interactive canvas.
- Reduction-step diagrams are currently coarse: initial and final DOT diagrams are produced, while detailed event logs are textual. A future version should generate a DOT/PNG snapshot after every individual reduction event.
- The parser supports a small Boolean subset, not full SystemVerilog.
- Multi-bit vectors and arithmetic operators are not yet supported directly.
- Large BDDs can still become very large.

## High-value future work

1. **Interactive SVG graph canvas**
   - zoom
   - pan
   - fit-to-screen
   - node selection
   - edge highlighting

2. **Reduction timeline**
   - slider from initial BDD to final ROBDD
   - before/after comparison for each rule application
   - highlighted removed/merged nodes

3. **Variable-order experiments**
   - drag-and-drop variable order
   - rebuild and compare node counts
   - side-by-side ROBDD comparison

4. **Equivalence checking mode**
   - compare two outputs/functions
   - show identical final ROBDD roots under same order

5. **SystemVerilog import**
   - parse `assign` statements directly
   - support simple `always_comb`
   - still require bit-level Boolean expressions

6. **Pedagogical mode**
   - guided questions
   - hide/show hints
   - worksheet generation
   - solution-key export

7. **Better packaging**
   - one-file executable using PyInstaller
   - optional macOS `.app`
   - optional bundled Graphviz runtime

8. **Multi-output sharing**
   - shared global BDD manager
   - visual subgraph reuse across outputs

