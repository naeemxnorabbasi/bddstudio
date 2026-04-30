# Features, Limitations, and Future Work

## Features

- YAML project files
- Multiple outputs
- Intermediate signals
- Truth tables
- Initial ordered BDD
- Final ROBDD
- Reduction logs
- DOT output
- Optional PNG/SVG/PDF rendering through Graphviz
- Markdown/HTML report

## Limitations

- Intended for small pedagogical examples.
- No full SystemVerilog parser.
- No vectors, part-selects, concatenations, arithmetic, comparisons, loops, or always_comb parsing.
- Reduction diagrams are currently initial/final; step text logs are generated for each reduction.
- Large functions may create very large full BDDs.

## Future Work

- Web GUI with step slider
- Node inspector
- Variable order experiments
- Direct ROBDD construction using a unique table
- Equivalence checking
- Multi-output shared ROBDD manager
- Better per-step highlighted diagrams
- SystemVerilog subset parser
- Worksheet and solution-key generation
