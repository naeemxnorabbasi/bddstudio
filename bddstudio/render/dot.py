
from pathlib import Path
import subprocess, shutil
def write_dot(bdd, root, path, title="BDD"):
    path=Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    reach=bdd.reachable(root)
    lines=['digraph G {','  graph [rankdir=TB, labelloc="t", label="'+title.replace('"','\\"')+'"];','  node [fontname="Helvetica"];','  edge [fontname="Helvetica"];']
    if 0 in reach: lines.append('  T0 [label="0", shape=box, style="rounded"];')
    if 1 in reach: lines.append('  T1 [label="1", shape=box, style="rounded"];')
    for nid in sorted(n for n in reach if n not in (0,1)):
        nd=bdd.nodes[nid]
        lines.append(f'  N{nid} [label="N{nid}: {nd.var}", shape=circle];')
    def ref(n): return "T0" if n==0 else "T1" if n==1 else f"N{n}"
    for nid in sorted(n for n in reach if n not in (0,1)):
        nd=bdd.nodes[nid]
        lines.append(f'  N{nid} -> {ref(nd.low)} [label="0", style=dashed];')
        lines.append(f'  N{nid} -> {ref(nd.high)} [label="1", style=solid];')
    lines.append('}')
    path.write_text("\n".join(lines)+"\n")
def dot_available():
    return shutil.which("dot")
def render_dot(dot_path, fmt):
    dot_path=Path(dot_path)
    # Professional project layout: keep DOT files in dot/, rendered files in sibling png/svg/pdf folders.
    if dot_path.parent.name == "dot":
        out_dir = dot_path.parent.parent / fmt
        out_dir.mkdir(parents=True, exist_ok=True)
        out = out_dir / (dot_path.stem + "." + fmt)
    else:
        out = dot_path.with_suffix("." + fmt)
    subprocess.run(["dot", f"-T{fmt}", str(dot_path), "-o", str(out)], check=True)
    return out
def render_tree(root_dir, formats):
    root_dir=Path(root_dir)
    dots=list(root_dir.rglob("*.dot"))
    made=[]
    if not dot_available(): return made
    for d in dots:
        for fmt in formats:
            if fmt=="dot": continue
            made.append(render_dot(d,fmt))
    return made
