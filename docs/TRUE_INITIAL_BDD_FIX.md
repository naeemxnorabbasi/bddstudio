# True Initial BDD Fix

Version 0.6 changes the teaching-mode BDD construction.

Previous behavior:
- The builder stopped early when a cofactor simplified to a constant.
- For `y = a & b & c`, the "initial" BDD could already look like the final ROBDD.

Correct teaching behavior:
- The initial ordered BDD is a full Shannon tree for the selected variable order.
- Constant cofactors are still expanded through the remaining variables.
- This creates nodes such as `Node(c, 0, 0)` and `Node(b, 0, 0)`.
- The reduction log then explicitly removes those redundant tests using Rule 1.

Example:

```yaml
project:
  name: "3 Input AND Gate"
signals:
  inputs: [a, b, c]
  intermediates: {}
  outputs:
    y: "a & b & c"
bdd:
  variable_order: [a, b, c]
render:
  output_dir: "build/and3"
```

Expected final ROBDD:

```text
N1 = Node(c, 0, 1)
N2 = Node(b, 0, N1)
N3 = Node(a, 0, N2)
Root = N3
```

Expected initial full BDD:
- 7 nonterminal nodes for a 3-variable full binary decision tree.
- Many nodes reduce away because both branches point to 0.
