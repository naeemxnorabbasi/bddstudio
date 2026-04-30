# BDD Studio

**BDD Studio** is a local teaching tool for building, reducing, and visualizing Binary Decision Diagrams (BDDs) and Reduced Ordered Binary Decision Diagrams (ROBDDs).

It is designed for students learning:

- Boolean functions
- Shannon expansion
- Ordered BDD construction
- ROBDD reduction
- Variable ordering
- Truth tables
- Node tables
- SystemVerilog-style Boolean expressions
- BDD-based equivalence-checking concepts

BDD Studio runs locally on your computer. Your project files and diagrams stay on your machine.

---

## What BDD Studio Generates

For a Boolean function such as:

```yaml
outputs:
  y: "a & b & c"
```

BDD Studio can generate:

- Truth tables
- Initial full ordered BDD diagrams
- Step-by-step reduction logs
- Final ROBDD diagrams
- DOT files
- PNG diagrams
- SVG diagrams
- PDF diagrams
- Initial and final node tables
- HTML reports
- A local browser-based GUI

---

## BDD Studio GUI

BDD Studio includes a local browser-based CAD-style interface.

The GUI provides:

- Project YAML editor
- Built-in example loader
- File loader for your own YAML files
- Check button
- Build Diagrams button
- Output selector
- Diagram selector
- Initial BDD viewer
- Final ROBDD viewer
- Truth table inspector
- Initial node-table inspector
- Final node-table inspector
- Reduction-log inspector
- HTML report launcher

The GUI runs locally at:

```text
http://127.0.0.1:8765
```

or another port if you choose one.

---

## Quick Start for Students on macOS

### 1. Install Graphviz

BDD Studio uses Graphviz to render DOT files into PNG, SVG, and PDF diagrams.

Install Homebrew if needed:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Then install Graphviz:

```bash
brew install graphviz
dot -V
```

You should see a Graphviz version printed.

---

### 2. Download BDD Studio

Clone the repository:

```bash
git clone https://github.com/naeemxnorabbasi/bddstudio.git
cd bddstudio
```

Alternatively, download the latest release ZIP from:

```text
https://github.com/naeemxnorabbasi/bddstudio/releases
```

---

### 3. Create a Python Environment

From inside the `bddstudio` folder:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

---

### 4. Check the Installation

```bash
bddstudio doctor
```

Expected result:

```text
BDD Studio doctor
Python: OK
Graphviz dot: OK
```

---

### 5. Launch the GUI

```bash
bddstudio serve
```

Open this address in your browser:

```text
http://127.0.0.1:8765
```

If the port is already busy, use another port:

```bash
bddstudio serve --port 8766
```

Then open:

```text
http://127.0.0.1:8766
```

---

## Try the Built-In Examples

BDD Studio includes several example projects:

```text
examples/and3.yaml
examples/xor3.yaml
examples/xor4.yaml
examples/xnor3.yaml
examples/xnor4.yaml
examples/mux2.yaml
examples/mux4.yaml
examples/mult_3x2.yaml
```

From the command line:

```bash
bddstudio check examples/and3.yaml
bddstudio truth examples/and3.yaml
bddstudio build examples/and3.yaml --formats png,svg,pdf
```

Generated output will appear under:

```text
build/
```

For example:

```text
build/and3/
```

---

## Example 1: 3-Input AND Gate

Create a file called:

```text
examples/and3.yaml
```

with this content:

```yaml
project:
  name: "3 Input AND Gate"

signals:
  inputs:
    - a
    - b
    - c

  intermediates: {}

  outputs:
    y: "a & b & c"

bdd:
  variable_order:
    - a
    - b
    - c

render:
  output_dir: "build/and3"

  formats:
    dot: true
    png: true
    svg: true
    pdf: true
    markdown: true
    html: true
```

Run:

```bash
bddstudio build examples/and3.yaml --formats png,svg,pdf
```

For this function and variable order:

```text
a < b < c
```

the final ROBDD should be:

```text
N1 = Node(c, 0, 1)
N2 = Node(b, 0, N1)
N3 = Node(a, 0, N2)

Root(y) = N3
```

This represents:

```text
y = a & b & c
```

---

## Example 2: 3-Input XOR

```yaml
project:
  name: "3 Input XOR"

signals:
  inputs:
    - a
    - b
    - c

  intermediates: {}

  outputs:
    y: "a ^ b ^ c"

bdd:
  variable_order:
    - a
    - b
    - c

render:
  output_dir: "build/xor3"
```

Run:

```bash
bddstudio build examples/xor3.yaml --formats png,svg,pdf
```

---

## Example 3: 2-to-1 Mux

SystemVerilog-style conditional expressions are supported.

```yaml
project:
  name: "2 Input Mux"

signals:
  inputs:
    - sel
    - d0
    - d1

  intermediates: {}

  outputs:
    y: "sel ? d1 : d0"

bdd:
  variable_order:
    - sel
    - d0
    - d1

render:
  output_dir: "build/mux2"
```

The conditional expression:

```text
sel ? d1 : d0
```

means:

```text
if sel = 0, output d0
if sel = 1, output d1
```

So in BDD notation:

```text
Node(sel, low=d0, high=d1)
```

---

## YAML Expression Rule

Boolean expressions should be quoted.

Correct:

```yaml
y: "a & b"
```

Incorrect:

```yaml
y: a & b
```

YAML treats `&` specially unless the expression is inside quotes.

---

## Supported Boolean Operators

BDD Studio currently supports small Boolean expressions using:

| Operator | Meaning |
|---|---|
| `~a` | NOT |
| `a & b` | AND |
| `a \| b` | OR |
| `a ^ b` | XOR |
| `a ~^ b` | XNOR |
| `a ^~ b` | XNOR |
| `sel ? d1 : d0` | Conditional / mux |
| `0`, `1` | Constants |
| Parentheses | Grouping |

---

## BDD Convention Used by This Tool

BDD Studio uses this convention:

```text
Node(x, low, high)
```

where:

```text
low  = child followed when x = 0
high = child followed when x = 1
```

Each BDD node is equivalent to a 2-to-1 mux:

```text
Node(x, low, high) = MUX(x, low, high)
                   = (~x & low) | (x & high)
```

In diagrams:

```text
dashed edge = 0 branch
solid edge  = 1 branch
```

---

## Shannon Expansion

BDD construction is based on Shannon expansion:

```text
f = MUX(x, f[x=0], f[x=1])
```

or equivalently:

```text
f = (~x & f[x=0]) | (x & f[x=1])
```

For example, for:

```text
f = a & b & c
```

using variable order:

```text
a < b < c
```

the root node tests `a`.

```text
if a = 0, f = 0
if a = 1, f = b & c
```

So:

```text
f = Node(a, 0, b & c)
```

---

## ROBDD Reduction Rules

BDD Studio reduces ordered BDDs into ROBDDs using:

```text
Rule 0: Merge terminal nodes.
Rule 1: Eliminate redundant nodes where low child = high child.
Rule 2: Merge isomorphic nodes with the same variable, same low child, and same high child.
Rule 3: Preserve the selected variable order.
```

The final ROBDD is canonical only for a fixed variable order.

That means two Boolean functions are equivalent if their final ROBDDs are structurally identical under the same variable order.

---

## Command-Line Usage

Check a project:

```bash
bddstudio check examples/and3.yaml
```

Generate a truth table:

```bash
bddstudio truth examples/and3.yaml
```

Build diagrams and reports:

```bash
bddstudio build examples/and3.yaml --formats png,svg,pdf
```

Generate DOT only:

```bash
bddstudio build examples/and3.yaml --no-render
```

Render existing DOT files later:

```bash
bddstudio render-dot build/and3 --formats png,svg,pdf
```

Launch the GUI:

```bash
bddstudio serve
```

Launch the GUI on a different port:

```bash
bddstudio serve --port 8766
```

---

## Output Files

After running a build, BDD Studio creates files such as:

```text
build/and3/
  report.md
  report.html

  y/
    dot/
      000_initial_full_ordered_bdd.dot
      final_robdd.dot

    png/
      000_initial_full_ordered_bdd.png
      final_robdd.png

    svg/
      000_initial_full_ordered_bdd.svg
      final_robdd.svg

    initial_full_node_table.txt
    final_node_table.txt
    reduction_log.json
```

---

## Current Limitations

BDD Studio is a teaching tool, not a full industrial formal-verification engine.

Currently supported:

- Small Boolean functions
- 1-bit Boolean variables
- Multiple outputs
- Temporary intermediate signals
- Fixed variable order
- Full ordered BDD construction
- ROBDD reduction
- Truth-table generation
- DOT/PNG/SVG/PDF diagram generation
- Local browser GUI

Currently not supported:

- Full SystemVerilog parsing
- Multi-bit vectors such as `logic [3:0] a`
- Arithmetic operators such as `+`, `-`, `*`
- Comparisons such as `==`, `<`, `>`
- Concatenation such as `{a,b}`
- Part-selects such as `bus[3]`
- Loops or procedural RTL
- Dynamic variable reordering
- Industrial-scale BDD optimization

For arithmetic circuits such as multipliers, write the bit-level Boolean equations explicitly.

---

## Suggested Student Exercises

1. Build the ROBDD for a 3-input AND gate.
2. Compare the BDD and ROBDD for `a | (a & b)`.
3. Build the ROBDD for `a ^ b ^ c`.
4. Build the ROBDD for a 3-input XNOR.
5. Change the variable order and compare node counts.
6. Build a mux using `sel ? d1 : d0`.
7. Build a 4-to-1 mux.
8. Try the 3-bit by 2-bit multiplier example.
9. Explain every reduction step from the reduction log.
10. Use final ROBDDs to check whether two functions are equivalent.

---

## Troubleshooting

### `bddstudio: command not found`

Make sure your virtual environment is active:

```bash
source .venv/bin/activate
```

Then reinstall:

```bash
python -m pip install -e .
```

---

### `Graphviz dot: NOT FOUND`

Install Graphviz:

```bash
brew install graphviz
```

Then check:

```bash
dot -V
bddstudio doctor
```

---

### `OSError: Address already in use`

Another GUI server is already using the default port.

Use a different port:

```bash
bddstudio serve --port 8766
```

Or find and stop the old process:

```bash
lsof -i :8765
kill <PID>
```

---

### YAML parse errors

Quote Boolean expressions:

```yaml
y: "a & b"
```

not:

```yaml
y: a & b
```

---

## Future Work

Possible future improvements include:

- Equivalence-checking mode
- More polished node-inspector GUI
- Variable-order comparison dashboard
- Dynamic variable-order demonstrations
- Export to LaTeX worksheets
- Auto-generated homework problems
- Auto-grading for student BDD submissions
- More SystemVerilog input support
- Bit-vector expansion for small buses
- Packaged one-click macOS application
- Better diagram layout controls for large BDDs

---

## License

This project is released for educational use.

See `LICENSE` for details.
