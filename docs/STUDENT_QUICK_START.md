# BDD Studio Student Quick Start

BDD Studio is a local teaching workbench for building Binary Decision Diagrams
(BDDs) and Reduced Ordered Binary Decision Diagrams (ROBDDs) from small Boolean
functions.

## 1. Install Graphviz

BDD Studio always generates DOT files. To turn DOT files into PNG, SVG, and PDF
diagrams, install Graphviz.

### macOS

```bash
brew install graphviz
dot -V
```

### Windows

Install Graphviz from <https://graphviz.org/download/> and make sure `dot` is
on your PATH.

### Linux

```bash
sudo apt-get update
sudo apt-get install -y graphviz
dot -V
```

## 2. Install BDD Studio

```bash
git clone https://github.com/YOUR_USERNAME/bddstudio.git
cd bddstudio

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

python -m pip install -e .
```

## 3. Launch the GUI

```bash
bddstudio serve
```

Open:

```text
http://127.0.0.1:8765
```

If the port is already busy:

```bash
bddstudio serve --port 8766
```

## 4. Try Examples

In the GUI, load one of these files:

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

Click:

```text
Check
Build Diagrams
```

Then inspect:

```text
Initial full ordered BDD
Final ROBDD
Initial node table
Final node table
Reduction log
Truth table
```

## 5. Create Your Own Boolean Function

Create a YAML file:

```yaml
project:
  name: "My Example"

signals:
  inputs:
    - a
    - b
    - c

  intermediates: {}

  outputs:
    y: "(a & b) | (~a & c)"

bdd:
  variable_order:
    - a
    - b
    - c

render:
  output_dir: "build/my_example"
```

Important: quote expressions containing Boolean operators.

Correct:

```yaml
y: "a & b"
```

Incorrect:

```yaml
y: a & b
```

YAML treats `&` specially unless the expression is quoted.

## 6. CLI Commands

```bash
bddstudio doctor
bddstudio check examples/and3.yaml
bddstudio truth examples/and3.yaml
bddstudio build examples/and3.yaml --formats png,svg,pdf
```

## 7. BDD Convention

BDD Studio uses:

```text
Node(x, low, high) = (~x & low) | (x & high)
low edge  = x = 0
high edge = x = 1
```

ROBDDs are canonical only for a fixed variable order.
