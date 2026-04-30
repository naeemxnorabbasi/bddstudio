# BDD Studio CAD GUI Design Document

## Goal

The GUI makes BDD Studio feel like a professional CAD-style workbench while preserving the deterministic command-line engine.

The LLM or user supplies a structured YAML project. The local engine performs parsing, BDD construction, reduction, rendering, and reporting.

## Design principles

1. **Deterministic core**  
   Same YAML input and variable order produce the same BDD/ROBDD outputs.

2. **Local-first**  
   The GUI runs on localhost. No data is sent to a server.

3. **CAD-like layout**  
   Three-pane workbench:
   - source/project editor
   - central diagram canvas
   - inspector/details panel

4. **Separation of concerns**
   - `core/`: expression parsing and project loading
   - `bdd/`: BDD construction and ROBDD reduction
   - `render/`: DOT/Graphviz output
   - `report/`: Markdown/HTML reports
   - `gui/`: local browser GUI

5. **Graceful degradation**
   DOT files are generated even when Graphviz is not installed. PNG/SVG/PDF previews require Graphviz.

## Current implementation

The GUI uses Python's standard-library `http.server`, HTML, CSS, and vanilla JavaScript. This keeps installation simple and avoids a heavy web framework dependency.

The GUI exposes these local API endpoints:

```text
GET  /
GET  /api/example
POST /api/check
POST /api/build
GET  /api/diagrams
GET  /api/inspect
GET  /artifact/<run-path>
```

## Why a browser GUI?

A browser GUI gives:
- high-quality layout,
- modern styling,
- easy SVG/PNG viewing,
- no native UI toolkit dependency,
- cross-platform behavior on macOS, Windows, and Linux.

## Future GUI architecture

For a more advanced product, the standard-library server can be replaced with:

```text
Backend: FastAPI
Frontend: React or Svelte
Diagram viewer: SVG pan/zoom
Packaging: PyInstaller or Tauri
```

