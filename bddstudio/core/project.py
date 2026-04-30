
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List
import yaml
from .expr import Expr, parse_expr

@dataclass
class Project:
    name:str
    inputs:List[str]
    intermediates:Dict[str,Expr]
    outputs:Dict[str,Expr]
    order:List[str]
    output_dir:str
    raw:dict

def _expand(e:Expr, defs:Dict[str,Expr])->Expr:
    prev=None
    cur=e
    # repeated substitution until stable
    for _ in range(100):
        nxt=cur.subst(defs).simplify()
        if nxt==cur: return nxt
        cur=nxt
    raise ValueError("possible cyclic intermediate definitions")

def load_project(path:str|Path)->Project:
    path=Path(path)
    data=yaml.safe_load(path.read_text()) or {}
    sig=data.get("signals",{})
    inputs=list(sig.get("inputs",[]))
    inter=sig.get("intermediates",{}) or {}
    outs=sig.get("outputs",{}) or {}
    defs={}
    expanded_inter={}
    for k,v in inter.items():
        expr=_expand(parse_expr(str(v)), defs)
        defs[k]=expr
        expanded_inter[k]=expr
    expanded_out={}
    for k,v in outs.items():
        expanded_out[k]=_expand(parse_expr(str(v)), defs)
    bdd=data.get("bdd",{}) or {}
    order=list(bdd.get("variable_order", inputs))
    missing=sorted(set().union(*(e.vars() for e in expanded_out.values()))-set(order))
    if missing:
        raise ValueError(f"variable_order is missing variables used by outputs: {missing}")
    render=data.get("render",{}) or {}
    outdir=render.get("output_dir") or f"build/{data.get('project',{}).get('name','bdd_project').lower().replace(' ','_')}"
    return Project(data.get("project",{}).get("name", path.stem), inputs, expanded_inter, expanded_out, order, outdir, data)
