# GUI file loading and diagram selection

BDD Studio v0.7 adds a more complete local GUI workflow.

## What changed

- The diagram drop-down now preserves the user's selected diagram.
- Final ROBDD diagrams can be selected reliably from the diagram menu.
- The default diagram after a build is the final ROBDD when available.
- The GUI can list and load any YAML example in the `examples/` folder.
- A local file picker can import any `.yaml` or `.yml` project from your Mac.
- A server-side path box can load files such as `examples/and3.yaml`.
- The inspector has separate tabs for the initial full node table and final node table.

## Loading built-in examples

Start the GUI:

```bash
bddstudio serve --port 8766
```

Use the example drop-down in the left panel and click **Load Example**.

Included examples:

- `and3.yaml`
- `mult_3x2.yaml`
- `xor3.yaml`
- `xor4.yaml`
- `xnor3.yaml`
- `xnor4.yaml`
- `mux2.yaml`
- `mux4.yaml`

## Loading your own file

Click **Open YAML File...** in the left panel. This uses the browser's normal file picker and reads the file into the editor.

The browser does not give the local server direct access to arbitrary files for security reasons, so imported files are loaded as text into the editor. Click **Build Diagrams** after loading.

## Loading by server path

Use the path box for files available relative to the BDD Studio project directory, for example:

```text
examples/and3.yaml
```

Then click **Load Path**.

## Selecting ROBDD diagrams

After building:

1. Choose the output from the **Output** drop-down.
2. Choose `final_robdd.dot` from the **Diagram** drop-down.
3. The preview shows the corresponding PNG when Graphviz rendered it.

If a PNG is not available, use **Open DOT** or **Open SVG**.
