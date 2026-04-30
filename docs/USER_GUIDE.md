# BDD Studio v0.4

Deterministic local tool for generating teaching-oriented BDD/ROBDD artifacts from small Boolean functions.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .

bddstudio doctor
bddstudio check examples/mult_3x2.yaml
bddstudio build examples/mult_3x2.yaml --formats png,svg,pdf
```

If Graphviz is not installed, DOT files are still generated.

## macOS Graphviz

```bash
brew install graphviz
dot -V
bddstudio doctor
```

## Important YAML note

Quote Boolean expressions because YAML uses `&` for anchors:

```yaml
x0: "a0 & b0"   # correct
```

not:

```yaml
x0: a0 & b0     # YAML may misread this
```


## Commands

- `bddstudio doctor`
- `bddstudio check PROJECT.yaml`
- `bddstudio truth PROJECT.yaml`
- `bddstudio build PROJECT.yaml --formats dot,png,svg,pdf`
- `bddstudio build PROJECT.yaml --no-render`
- `bddstudio render-dot build/PROJECT --formats png,svg,pdf`

## Supported expression syntax

`~`, `&`, `|`, `^`, `~^`, `^~`, `?:`, parentheses, `0`, `1`, `1'b0`, `1'b1`.

All variables are treated as 1-bit Boolean signals.
