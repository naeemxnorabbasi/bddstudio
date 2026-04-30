
from __future__ import annotations
import argparse, sys, json, shutil
from pathlib import Path
from bddstudio.core.project import load_project
from bddstudio.core.expr import truth_rows
from bddstudio.bdd.manager import BDD, reduce_with_log
from bddstudio.render.dot import write_dot, render_tree, dot_available
from bddstudio.report.report import write_reports

def cmd_doctor(args):
    print("BDD Studio doctor")
    print(f"Python: OK")
    d=dot_available()
    print(f"Graphviz dot: OK ({d})" if d else "Graphviz dot: NOT FOUND. DOT files will still be created; install Graphviz for PNG/SVG/PDF.")
    return 0

def cmd_check(args):
    try:
        p=load_project(args.project)
        print(f"Project: {p.name}")
        print(f"Inputs: {', '.join(p.inputs)}")
        print(f"Outputs: {', '.join(p.outputs)}")
        print(f"Variable order: {' < '.join(p.order)}")
        print("Check: OK")
        return 0
    except Exception as e:
        print(f"Check failed: {e}", file=sys.stderr)
        return 1

def cmd_truth(args):
    p=load_project(args.project)
    for name,e in p.outputs.items():
        print(f"\n{name} = {e}")
        print(" ".join(p.order)+" | "+name)
        for env,val in truth_rows(e,p.order):
            print(" ".join(str(env[v]) for v in p.order)+" | "+str(val))
    return 0

def build_one(p, name, expr, formats, render):
    out=Path(p.output_dir)/name
    (out/"dot").mkdir(parents=True, exist_ok=True)
    full=BDD(p.order)
    root=full.build_full(expr)
    # Keep the full Shannon tree for the initial diagram. Do not compact or
    # reduce it here; otherwise simple examples like a&b&c appear already
    # reduced and hide the reduction process.
    write_dot(full,root,out/"dot"/"000_initial_full_ordered_bdd.dot",f"{name}: initial FULL ordered BDD")
    (out/"initial_full_node_table.txt").write_text(full.node_table(root)+"\n")
    red, rroot, events=reduce_with_log(full,root)
    write_dot(red,rroot,out/"dot"/"final_robdd.dot",f"{name}: final ROBDD")
    (out/"final_node_table.txt").write_text(red.node_table(rroot)+"\n")
    (out/"reduction_log.json").write_text(json.dumps(events,indent=2))
    # write after-step tables as text for determinism
    steps=out/"steps"; steps.mkdir(exist_ok=True)
    for ev in events:
        (steps/f"{ev['step']:03d}_{ev['title'].replace(' ','_')}.txt").write_text(ev["description"]+"\n\nAfter:\n"+ev["after"]+"\n")
    if render:
        render_tree(out/"dot", formats)
    return {"name":name,"final_table":red.node_table(rroot),"events":events}

def cmd_build(args):
    p=load_project(args.project)
    if args.output_dir:
        p.output_dir=args.output_dir
    formats=[x.strip() for x in args.formats.split(",") if x.strip()] if args.formats else ["dot"]
    render=not args.no_render
    summaries=[]
    print(f"Building {p.name}")
    print(f"Variable order: {' < '.join(p.order)}")
    for name,expr in p.outputs.items():
        s=build_one(p,name,expr,formats,render)
        summaries.append(s)
        print(f"  {name}: final nodes={len([ln for ln in s['final_table'].splitlines() if ln.startswith('N')])}, reductions={len(s['events'])}")
    write_reports(p,summaries)
    print(f"Wrote: {p.output_dir}")
    if render and any(f in ("png","svg","pdf") for f in formats) and not dot_available():
        print("Note: Graphviz dot was not found, so only DOT files were generated.")
    return 0

def cmd_render_dot(args):
    fmts=[x.strip() for x in args.formats.split(",") if x.strip()]
    made=render_tree(args.directory,fmts)
    if not dot_available():
        print("Graphviz dot not found.")
        return 1
    print(f"Rendered {len(made)} files.")
    return 0

def cmd_serve(args):
    from bddstudio.gui.server import serve
    serve(host=args.host, port=args.port, workspace=args.workspace, open_browser=not args.no_browser)
    return 0

def main(argv=None):
    ap=argparse.ArgumentParser(prog="bddstudio")
    sub=ap.add_subparsers(dest="cmd", required=True)
    p=sub.add_parser("doctor"); p.set_defaults(func=cmd_doctor)
    p=sub.add_parser("check"); p.add_argument("project"); p.set_defaults(func=cmd_check)
    p=sub.add_parser("truth"); p.add_argument("project"); p.set_defaults(func=cmd_truth)
    p=sub.add_parser("build"); p.add_argument("project"); p.add_argument("--formats",default="dot",help="comma-separated: dot,png,svg,pdf"); p.add_argument("--no-render",action="store_true"); p.add_argument("--output-dir"); p.set_defaults(func=cmd_build)
    p=sub.add_parser("render-dot"); p.add_argument("directory"); p.add_argument("--formats",default="png,svg"); p.set_defaults(func=cmd_render_dot)
    p=sub.add_parser("serve", help="launch the professional local CAD-style GUI")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--workspace", default=None)
    p.add_argument("--no-browser", action="store_true")
    p.set_defaults(func=cmd_serve)
    args=ap.parse_args(argv)
    return args.func(args)
if __name__=="__main__":
    raise SystemExit(main())
