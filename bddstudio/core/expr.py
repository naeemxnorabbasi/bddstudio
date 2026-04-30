
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Set, Iterator
import itertools, re

class Expr:
    def eval(self, env: Dict[str,int]) -> int: raise NotImplementedError
    def vars(self) -> Set[str]: raise NotImplementedError
    def restrict(self, var: str, val: int) -> "Expr": raise NotImplementedError
    def subst(self, defs: Dict[str,"Expr"]) -> "Expr": return self
    def simplify(self) -> "Expr": return self

@dataclass(frozen=True)
class Const(Expr):
    value:int
    def eval(self, env): return int(self.value)
    def vars(self): return set()
    def restrict(self,var,val): return self
    def __str__(self): return str(int(self.value))

@dataclass(frozen=True)
class Var(Expr):
    name:str
    def eval(self, env): return int(env[self.name])
    def vars(self): return {self.name}
    def restrict(self,var,val): return Const(val) if self.name==var else self
    def subst(self, defs): return defs.get(self.name, self)
    def __str__(self): return self.name

@dataclass(frozen=True)
class Not(Expr):
    a:Expr
    def eval(self, env): return 1-self.a.eval(env)
    def vars(self): return self.a.vars()
    def restrict(self,var,val): return Not(self.a.restrict(var,val)).simplify()
    def subst(self,defs): return Not(self.a.subst(defs)).simplify()
    def simplify(self):
        a=self.a.simplify()
        if isinstance(a,Const): return Const(1-a.value)
        if isinstance(a,Not): return a.a.simplify()
        return Not(a)
    def __str__(self): return f"~({self.a})"

@dataclass(frozen=True)
class Bin(Expr):
    op:str; l:Expr; r:Expr
    def eval(self, env):
        a,b=self.l.eval(env),self.r.eval(env)
        if self.op=="&": return a & b
        if self.op=="|": return a | b
        if self.op=="^": return a ^ b
        if self.op=="~^": return 1-(a ^ b)
        raise ValueError(self.op)
    def vars(self): return self.l.vars()|self.r.vars()
    def restrict(self,var,val): return Bin(self.op,self.l.restrict(var,val),self.r.restrict(var,val)).simplify()
    def subst(self,defs): return Bin(self.op,self.l.subst(defs),self.r.subst(defs)).simplify()
    def simplify(self):
        l,r=self.l.simplify(),self.r.simplify()
        if isinstance(l,Const) and isinstance(r,Const): return Const(Bin(self.op,l,r).eval({}))
        if self.op=="&":
            if isinstance(l,Const): return r if l.value else Const(0)
            if isinstance(r,Const): return l if r.value else Const(0)
            if l==r: return l
        if self.op=="|":
            if isinstance(l,Const): return Const(1) if l.value else r
            if isinstance(r,Const): return Const(1) if r.value else l
            if l==r: return l
        if self.op=="^":
            if isinstance(l,Const): return Not(r).simplify() if l.value else r
            if isinstance(r,Const): return Not(l).simplify() if r.value else l
            if l==r: return Const(0)
        if self.op=="~^":
            return Not(Bin("^",l,r)).simplify()
        return Bin(self.op,l,r)
    def __str__(self): return f"({self.l} {self.op} {self.r})"

@dataclass(frozen=True)
class Mux(Expr):
    sel:Expr; low:Expr; high:Expr
    def eval(self, env): return self.high.eval(env) if self.sel.eval(env) else self.low.eval(env)
    def vars(self): return self.sel.vars()|self.low.vars()|self.high.vars()
    def restrict(self,var,val): return Mux(self.sel.restrict(var,val),self.low.restrict(var,val),self.high.restrict(var,val)).simplify()
    def subst(self,defs): return Mux(self.sel.subst(defs),self.low.subst(defs),self.high.subst(defs)).simplify()
    def simplify(self):
        s,l,h=self.sel.simplify(),self.low.simplify(),self.high.simplify()
        if isinstance(s,Const): return h if s.value else l
        if l==h: return l
        return Mux(s,l,h)
    def __str__(self): return f"({self.sel} ? {self.high} : {self.low})"

TOKEN_RE=re.compile(r"\s*(1'b0|1'b1|~\^|\^~|&&|\|\||[A-Za-z_][A-Za-z0-9_]*|[01]|[~!&|^?:()]|\S)")
class Parser:
    def __init__(self,s):
        self.toks=[t for t in TOKEN_RE.findall(s) if t.strip()]
        self.i=0
    def peek(self): return self.toks[self.i] if self.i<len(self.toks) else None
    def eat(self,t=None):
        p=self.peek()
        if t is not None and p!=t: raise SyntaxError(f"expected {t}, got {p}")
        self.i+=1; return p
    def parse(self):
        if not self.toks: raise SyntaxError("empty expression")
        e=self.cond()
        if self.peek() is not None: raise SyntaxError(f"unexpected token {self.peek()} in expression near: {' '.join(self.toks[self.i:])}")
        return e.simplify()
    def cond(self):
        e=self.or_()
        if self.peek()=="?":
            self.eat("?"); high=self.cond(); self.eat(":"); low=self.cond()
            e=Mux(e,low,high)
        return e
    def or_(self):
        e=self.xor()
        while self.peek() in ("|","||"):
            op=self.eat(); e=Bin("|",e,self.xor())
        return e
    def xor(self):
        e=self.and_()
        while self.peek() in ("^","~^","^~"):
            op=self.eat(); e=Bin("~^" if op in ("~^","^~") else "^",e,self.and_())
        return e
    def and_(self):
        e=self.unary()
        while self.peek() in ("&","&&"):
            self.eat(); e=Bin("&",e,self.unary())
        return e
    def unary(self):
        p=self.peek()
        if p in ("~","!"):
            self.eat(); return Not(self.unary())
        if p=="(":
            self.eat("("); e=self.cond(); self.eat(")"); return e
        if p in ("0","1","1'b0","1'b1"):
            self.eat(); return Const(1 if p in ("1","1'b1") else 0)
        if p and re.match(r"[A-Za-z_]",p):
            self.eat(); return Var(p)
        raise SyntaxError(f"unexpected token {p}")

def parse_expr(s:str)->Expr:
    return Parser(s).parse()

def truth_rows(expr:Expr, order:list[str]):
    for vals in itertools.product([0,1], repeat=len(order)):
        env=dict(zip(order,vals))
        yield env, expr.eval(env)
