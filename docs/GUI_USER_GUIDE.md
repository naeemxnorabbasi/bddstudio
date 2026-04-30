# BDD Studio CAD GUI User Guide

BDD Studio v0.5 adds a professional local browser-based GUI on top of the deterministic BDD/ROBDD engine.

## Launch

```bash
bddstudio serve
```

The tool opens:

```text
http://127.0.0.1:8765
```

No cloud service is used. The GUI runs locally on your machine.

## Main panels

The GUI is organized like a small CAD workbench:

1. **Project YAML panel**  
   Edit inputs, intermediate equations, outputs, variable order, and render options.

2. **Diagram viewer**  
   Select an output bit and a diagram stage. The viewer shows generated PNG diagrams when Graphviz is installed.

3. **Inspector**  
   View the build summary, final ROBDD node table, structured reduction log, and truth table.

## Typical workflow

```bash
bddstudio serve
```

Then in the GUI:

1. Click **Load 3×2 Multiplier**.
2. Click **Check**.
3. Select desired formats: PNG, SVG, PDF.
4. Click **Build Diagrams**.
5. Use the Output and Diagram selectors to inspect BDD/ROBDD stages.
6. Click **Open HTML Report** to view the generated report.

## Graphviz

The GUI always generates DOT files. For PNG/SVG/PDF preview, Graphviz must be installed.

On macOS:

```bash
brew install graphviz
dot -V
bddstudio doctor
```

## Project YAML reminder

Quote Boolean expressions in YAML:

```yaml
outputs:
  y: "(a & b) | (~a & c)"
```

Do not write:

```yaml
outputs:
  y: (a & b) | (~a & c)
```

because YAML treats `&` specially.

## Output location

GUI runs are stored in:

```text
.bddstudio_gui/runs/<timestamp>/
```

Each run contains:

```text
project.yaml
report.md
report.html
summary.txt
truth_tables.txt
p0/
  dot/
  png/
  svg/
  pdf/
  final_node_table.txt
  reduction_log.json
```

