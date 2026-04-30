# BDD Studio

BDD Studio is a local, deterministic, CAD-style teaching workbench for Boolean
functions, BDD construction, ROBDD reduction, and equivalence-oriented learning.

It generates:

- initial full ordered BDD diagrams,
- step-by-step reduction artifacts,
- final ROBDD diagrams,
- DOT, PNG, SVG, and PDF outputs,
- truth tables,
- node tables,
- reduction logs,
- Markdown/HTML reports,
- a local browser-based GUI.

## Quick Start for Students

```bash
git clone https://github.com/YOUR_USERNAME/bddstudio.git
cd bddstudio

python -m venv .venv
source .venv/bin/activate

python -m pip install -e .
bddstudio doctor
bddstudio serve
```

Open:

```text
http://127.0.0.1:8765
```

On macOS, install Graphviz first:

```bash
brew install graphviz
```

## Try an Example

```bash
bddstudio check examples/and3.yaml
bddstudio build examples/and3.yaml --formats png,svg,pdf
```

More examples are in `examples/`.

## Documentation

- `docs/STUDENT_QUICK_START.md`
- `docs/USER_GUIDE.md`
- `docs/DESIGN_DOCUMENT.md`
- `docs/FEATURES_LIMITATIONS_FUTURE.md`
- `docs/PUBLISHING_GUIDE.md`

---

# BDD Studio v0.7 GUI File Loader

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


## Professional GUI

BDD Studio v0.5 includes a local CAD-style GUI:

```bash
bddstudio serve
```

Then open:

```text
http://127.0.0.1:8765
```

The GUI provides a project editor, build controls, diagram viewer, node-table inspector, reduction-log inspector, truth-table viewer, and report launcher.

See:

```text
docs/GUI_USER_GUIDE.md
docs/GUI_DESIGN_DOCUMENT.md
docs/GUI_FEATURES_LIMITATIONS_FUTURE.md
```


## Version 0.6 note: true initial BDDs

Teaching-mode initial diagrams are now true full ordered Shannon BDDs. The
builder no longer stops early when a cofactor becomes constant. This means a
3-input AND gate now shows the full initial tree first and a smaller final ROBDD
after the reduction steps.


## v0.7 GUI improvements

- Fixed diagram selection so `final_robdd.dot` can be selected reliably.
- Added built-in example dropdown.
- Added browser-based YAML file import.
- Added server-side path loader.
- Added initial/final node-table tabs in the inspector.
