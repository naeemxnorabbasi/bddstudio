
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple, List, Set
from bddstudio.core.expr import Expr, Const

@dataclass
class Node:
    id:int
    var:str|None
    low:int|None=None
    high:int|None=None
    terminal:int|None=None

class BDD:
    def __init__(self, order:list[str]):
        self.order=order
        self.nodes:Dict[int,Node]={0:Node(0,None,terminal=0),1:Node(1,None,terminal=1)}
        self.next_id=2
        self.events=[]
    def new_node(self,var,low,high)->int:
        nid=self.next_id; self.next_id+=1
        self.nodes[nid]=Node(nid,var,low,high,None)
        return nid
    def build_full(self, expr:Expr, idx=0)->int:
        """
        Build a true *unreduced full ordered BDD* for teaching.

        Important: do NOT stop early when a cofactor simplifies to a constant.
        For a variable order [a,b,c], the initial BDD should still contain
        a complete Shannon tree down to c. Constant cofactors become nodes such
        as Node(c, 0, 0) or Node(b, 0, 0), which are then removed explicitly by
        Rule 1 during reduction. This makes examples like y=a&b&c show a large
        initial BDD and a smaller final ROBDD, which is pedagogically correct.

        At the end of the order, the expression must evaluate to 0 or 1.
        """
        expr = expr.simplify()
        if idx >= len(self.order):
            try:
                return int(expr.eval({}))
            except Exception:
                if isinstance(expr, Const):
                    return int(expr.value)
                raise ValueError(f"expression did not reduce to constant at end of order: {expr}")
        var = self.order[idx]
        low_expr = expr.restrict(var, 0).simplify()
        high_expr = expr.restrict(var, 1).simplify()
        low = self.build_full(low_expr, idx + 1)
        high = self.build_full(high_expr, idx + 1)
        return self.new_node(var, low, high)
    def reachable(self, root:int)->Set[int]:
        seen=set()
        def dfs(n):
            if n in seen: return
            seen.add(n)
            node=self.nodes[n]
            if node.terminal is None:
                dfs(node.low); dfs(node.high)
        dfs(root); return seen
    def compact_copy(self, root:int):
        # remove unreachable only
        keep=self.reachable(root)
        self.nodes={k:v for k,v in self.nodes.items() if k in keep or k in (0,1)}
    def node_table(self, root:int)->str:
        ids=sorted(n for n in self.reachable(root) if n not in (0,1))
        lines=[]
        for n in ids:
            node=self.nodes[n]
            lines.append(f"N{n} = Node({node.var}, {self._ref(node.low)}, {self._ref(node.high)})")
        lines.append(f"Root = {self._ref(root)}")
        return "\n".join(lines)
    def _ref(self,n:int)->str:
        return str(n) if n in (0,1) else f"N{n}"

def reduce_with_log(full:BDD, root:int):
    b=BDD(full.order)
    # deep copy nodes
    b.nodes={k:Node(v.id,v.var,v.low,v.high,v.terminal) for k,v in full.nodes.items()}
    b.next_id=full.next_id
    events=[]
    root_cur=root

    def redirect(old,new):
        nonlocal root_cur
        if root_cur==old: root_cur=new
        for nd in b.nodes.values():
            if nd.terminal is None:
                if nd.low==old: nd.low=new
                if nd.high==old: nd.high=new

    # deterministic bottom-up passes
    changed=True; step=0
    while changed:
        changed=False
        # eliminate low == high, deepest variables first by node id stable
        for nid in sorted(list(b.nodes.keys())):
            if nid in (0,1) or nid not in b.nodes: continue
            nd=b.nodes[nid]
            if nd.low==nd.high:
                new=nd.low
                desc=f"Rule 1: eliminate N{nid} = Node({nd.var}, {b._ref(nd.low)}, {b._ref(nd.high)}). Both children are the same, so the variable test is redundant."
                before=b.node_table(root_cur)
                redirect(nid,new); del b.nodes[nid]
                b.compact_copy(root_cur)
                after=b.node_table(root_cur)
                step+=1; events.append({"step":step,"rule":"Rule 1","title":f"Eliminate redundant N{nid}","description":desc,"before":before,"after":after})
                changed=True
                break
        if changed: continue
        # merge same triple
        triples={}
        for nid in sorted(b.nodes.keys()):
            if nid in (0,1): continue
            nd=b.nodes[nid]
            key=(nd.var,nd.low,nd.high)
            if key in triples:
                keep=triples[key]; old=nid
                desc=f"Rule 2: merge N{old} into N{keep}. They have the same variable, low child, and high child."
                before=b.node_table(root_cur)
                redirect(old,keep); del b.nodes[old]
                b.compact_copy(root_cur)
                after=b.node_table(root_cur)
                step+=1; events.append({"step":step,"rule":"Rule 2","title":f"Merge N{old} into N{keep}","description":desc,"before":before,"after":after})
                changed=True
                break
            triples[key]=nid
    b.compact_copy(root_cur)
    return b, root_cur, events
