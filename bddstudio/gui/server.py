
from __future__ import annotations
import json, os, time, tempfile, webbrowser, threading, traceback
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, unquote, parse_qs
from bddstudio.core.project import load_project
from bddstudio.core.expr import truth_rows
from bddstudio.cli.main import build_one
from bddstudio.report.report import write_reports
from bddstudio.render.dot import dot_available

APP_HTML = r"""<!doctype html>
<html>
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>BDD Studio CAD</title>
<style>
:root{
  --bg:#0e1117;--panel:#151a23;--panel2:#1b2230;--line:#2d3748;--text:#e6edf3;--muted:#9aa4b2;
  --accent:#68a0ff;--accent2:#7ee787;--warn:#ffcc66;--bad:#ff7b72;--chip:#243048;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font:14px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
.app{display:grid;grid-template-rows:54px 1fr;height:100vh}
.top{display:flex;align-items:center;gap:14px;padding:0 18px;background:#0b0f16;border-bottom:1px solid var(--line)}
.logo{display:flex;align-items:center;gap:10px;font-weight:800;letter-spacing:.2px}
.logo-mark{width:28px;height:28px;border-radius:8px;background:linear-gradient(135deg,var(--accent),#b88cff);box-shadow:0 0 30px #68a0ff44}
.badge{font-size:12px;color:var(--muted);border:1px solid var(--line);padding:3px 8px;border-radius:999px}
.spacer{flex:1}
button,select,input{background:var(--panel2);color:var(--text);border:1px solid var(--line);border-radius:8px;padding:8px 10px}
button{cursor:pointer;font-weight:650}
button.primary{background:linear-gradient(180deg,#3973e6,#295bc2);border-color:#497de1}
button.good{background:#1f6f43;border-color:#2f8756}
button:hover{filter:brightness(1.08)}
.main{display:grid;grid-template-columns:420px 1fr 390px;min-height:0}
.pane{min-height:0;border-right:1px solid var(--line);background:var(--panel)}
.pane.right{border-right:0;border-left:1px solid var(--line)}
.pane-head{height:42px;display:flex;align-items:center;gap:8px;padding:0 12px;border-bottom:1px solid var(--line);background:#111722;font-weight:750}
.pane-body{height:calc(100% - 42px);overflow:auto;padding:12px}
textarea{width:100%;height:calc(100vh - 245px);resize:none;background:#0c1017;color:#e6edf3;border:1px solid var(--line);border-radius:10px;padding:12px;font:13px/1.45 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
.row{display:flex;gap:8px;align-items:center;margin-bottom:10px;flex-wrap:wrap}
.status{white-space:pre-wrap;background:#0c1017;border:1px solid var(--line);border-radius:10px;padding:10px;color:var(--muted);font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;max-height:180px;overflow:auto}
.stage{display:grid;grid-template-rows:auto 1fr;height:100%;min-height:0}
.toolbar{display:flex;gap:8px;align-items:center;padding:12px;border-bottom:1px solid var(--line);background:#111722;flex-wrap:wrap}
.viewer{min-height:0;overflow:auto;padding:18px;background:
 radial-gradient(circle at 1px 1px,#263140 1px,transparent 0) 0 0/22px 22px,#0e1117}
.card{background:var(--panel);border:1px solid var(--line);border-radius:14px;box-shadow:0 12px 50px #0005;padding:14px;margin:auto;max-width:100%}
.preview{display:block;max-width:100%;height:auto;background:white;border-radius:8px}
.tabs{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px}
.tab{padding:6px 10px;border-radius:999px;background:var(--chip);color:var(--muted);cursor:pointer;border:1px solid transparent}
.tab.active{color:#fff;border-color:var(--accent);background:#1f3155}
pre{white-space:pre-wrap;background:#0c1017;border:1px solid var(--line);border-radius:10px;padding:10px;overflow:auto;color:#c9d1d9;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
.kv{display:grid;grid-template-columns:115px 1fr;gap:6px 10px;margin-bottom:12px}
.k{color:var(--muted)}
a{color:var(--accent)}
.small{font-size:12px;color:var(--muted)}
input[type=file]{display:none}
.filelabel{display:inline-block;background:var(--panel2);color:var(--text);border:1px solid var(--line);border-radius:8px;padding:8px 10px;cursor:pointer;font-weight:650}
.pathbox{flex:1;min-width:160px}
</style>
</head>
<body>
<div class="app">
  <div class="top">
    <div class="logo"><div class="logo-mark"></div><div>BDD Studio CAD</div></div>
    <div class="badge">local deterministic BDD/ROBDD workbench</div>
    <div class="spacer"></div>
    <button onclick="checkProject()">Check</button>
    <button class="primary" onclick="buildProject()">Build Diagrams</button>
  </div>
  <div class="main">
    <div class="pane">
      <div class="pane-head">Project YAML</div>
      <div class="pane-body">
        <div class="row">
          <select id="exampleSel"></select>
          <button onclick="loadSelectedExample()">Load Example</button>
        </div>
        <div class="row">
          <label class="filelabel" for="fileOpen">Open YAML File…</label>
          <input id="fileOpen" type="file" accept=".yaml,.yml,.txt" onchange="openLocalFile(event)">
          <button onclick="downloadYaml()">Download YAML</button>
        </div>
        <div class="row">
          <input class="pathbox" id="serverPath" placeholder="server path, e.g. examples/and3.yaml">
          <button onclick="loadServerPath()">Load Path</button>
        </div>
        <div class="row">
          <label><input id="fmt_png" type="checkbox" checked> PNG</label>
          <label><input id="fmt_svg" type="checkbox" checked> SVG</label>
          <label><input id="fmt_pdf" type="checkbox"> PDF</label>
        </div>
        <textarea id="yaml"></textarea>
        <div style="height:10px"></div>
        <div id="status" class="status">Ready.</div>
      </div>
    </div>
    <div class="stage">
      <div class="toolbar">
        <span class="small">Output</span><select id="outputSel" onchange="onOutputChange()"></select>
        <span class="small">Diagram</span><select id="diagramSel" onchange="onDiagramChange()"></select>
        <button onclick="openCurrentDot()">Open DOT</button>
        <button onclick="openCurrentSvg()">Open SVG</button>
        <button onclick="openReport()">Open HTML Report</button>
        <button onclick="downloadRun()">Open Build Folder</button>
      </div>
      <div class="viewer">
        <div class="card">
          <div id="previewMsg" class="small">Build a project to see diagrams.</div>
          <img id="preview" class="preview" style="display:none"/>
        </div>
      </div>
    </div>
    <div class="pane right">
      <div class="pane-head">Inspector</div>
      <div class="pane-body">
        <div class="tabs">
          <div class="tab active" onclick="setTab('summary',this)">Summary</div>
          <div class="tab" onclick="setTab('initial',this)">Initial Table</div>
          <div class="tab" onclick="setTab('nodes',this)">Final Table</div>
          <div class="tab" onclick="setTab('log',this)">Reduction Log</div>
          <div class="tab" onclick="setTab('truth',this)">Truth</div>
        </div>
        <div id="inspector"><pre>No build yet.</pre></div>
      </div>
    </div>
  </div>
</div>
<script>
let state={run:null, tab:'summary', diagrams:[]};

async function api(path, body=null){
  let opt=body?{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}:{};
  let r=await fetch(path,opt);
  let t=await r.text();
  try{return JSON.parse(t)}catch(e){return {ok:false,error:t}}
}
function setStatus(s){document.getElementById('status').textContent=s}

async function init(){
  let r=await api('/api/examples');
  let sel=document.getElementById('exampleSel'); sel.innerHTML='';
  for(let item of (r.examples||[])){
    let opt=document.createElement('option'); opt.value=item.path; opt.textContent=item.name; sel.appendChild(opt);
  }
  await loadSelectedExample();
}

async function loadSelectedExample(){
  let path=document.getElementById('exampleSel').value || 'examples/mult_3x2.yaml';
  let r=await api('/api/load-path?path='+encodeURIComponent(path));
  if(r.ok){document.getElementById('yaml').value=r.yaml; document.getElementById('serverPath').value=path; setStatus('Loaded '+path+'. Click Check or Build Diagrams.');}
  else setStatus('ERROR: '+r.error);
}
async function loadServerPath(){
  let path=document.getElementById('serverPath').value.trim();
  if(!path){setStatus('Enter a server-side path such as examples/and3.yaml'); return}
  let r=await api('/api/load-path?path='+encodeURIComponent(path));
  if(r.ok){document.getElementById('yaml').value=r.yaml; setStatus('Loaded '+path);}
  else setStatus('ERROR: '+r.error);
}
function openLocalFile(ev){
  let f=ev.target.files[0]; if(!f)return;
  let reader=new FileReader();
  reader.onload=()=>{document.getElementById('yaml').value=reader.result; setStatus('Loaded local file: '+f.name+'. Click Check or Build Diagrams.');};
  reader.readAsText(f);
}
function downloadYaml(){
  let blob=new Blob([document.getElementById('yaml').value],{type:'text/yaml'});
  let a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download='bddstudio_project.yaml'; a.click();
  setTimeout(()=>URL.revokeObjectURL(a.href),1000);
}

async function checkProject(){
  setStatus('Checking...');
  let r=await api('/api/check',{yaml:document.getElementById('yaml').value});
  setStatus(r.ok ? r.message : ('ERROR: '+r.error+'\n'+(r.trace||'')));
}
function formats(){
  let f=['dot'];
  if(document.getElementById('fmt_png').checked)f.push('png');
  if(document.getElementById('fmt_svg').checked)f.push('svg');
  if(document.getElementById('fmt_pdf').checked)f.push('pdf');
  return f.join(',');
}
async function buildProject(){
  setStatus('Building BDDs/ROBDDs and rendering diagrams...');
  let r=await api('/api/build',{yaml:document.getElementById('yaml').value,formats:formats()});
  if(!r.ok){setStatus('ERROR: '+r.error+'\n'+(r.trace||'')); return}
  state.run=r;
  setStatus(r.message);
  populateOutputs();
  await loadDiagramsForOutput();
  refreshInspector();
}
function populateOutputs(){
  let o=document.getElementById('outputSel'); o.innerHTML='';
  for(let name of state.run.outputs){let opt=document.createElement('option');opt.value=name;opt.textContent=name;o.appendChild(opt)}
}
async function onOutputChange(){
  await loadDiagramsForOutput();
  refreshInspector();
}
async function loadDiagramsForOutput(preferred=null){
  if(!state.run)return;
  let out=document.getElementById('outputSel').value;
  let d=await api('/api/diagrams?run='+encodeURIComponent(state.run.run_id)+'&output='+encodeURIComponent(out));
  state.diagrams=d.diagrams||[];
  let sel=document.getElementById('diagramSel'); sel.innerHTML='';
  for(let item of state.diagrams){let opt=document.createElement('option');opt.value=item;opt.textContent=item;sel.appendChild(opt)}
  let final=state.diagrams.find(x=>x.toLowerCase().includes('final')) || state.diagrams[state.diagrams.length-1] || '';
  sel.value=preferred && state.diagrams.includes(preferred) ? preferred : final;
  onDiagramChange();
}
function onDiagramChange(){
  if(!state.run)return;
  let out=document.getElementById('outputSel').value;
  let chosen=document.getElementById('diagramSel').value;
  let img=document.getElementById('preview');
  if(chosen){
    img.src='/artifact/'+encodeURIComponent(state.run.run_id)+'/'+encodeURIComponent(out)+'/png/'+chosen.replace('.dot','.png')+'?t='+Date.now();
    img.onerror=()=>{ img.style.display='none'; document.getElementById('previewMsg').innerHTML=chosen+'<br>No PNG preview found. Try SVG/DOT buttons, or install Graphviz.'; };
    img.onload=()=>{ img.style.display='block'; document.getElementById('previewMsg').textContent=chosen; };
  } else {
    img.style.display='none';
    document.getElementById('previewMsg').textContent='No diagrams found.';
  }
}
function setTab(t,el){
  state.tab=t;
  for(let x of document.querySelectorAll('.tab'))x.classList.remove('active');
  el.classList.add('active');
  refreshInspector();
}
async function refreshInspector(){
  if(!state.run)return;
  let out=document.getElementById('outputSel').value;
  let r=await api('/api/inspect?run='+encodeURIComponent(state.run.run_id)+'&output='+encodeURIComponent(out)+'&tab='+encodeURIComponent(state.tab));
  document.getElementById('inspector').innerHTML='<pre>'+escapeHtml(r.text||'')+'</pre>';
}
function escapeHtml(s){return String(s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]))}
function openReport(){ if(state.run) window.open('/artifact/'+encodeURIComponent(state.run.run_id)+'/report.html','_blank'); }
function downloadRun(){ if(state.run) window.open('/artifact/'+encodeURIComponent(state.run.run_id)+'/','_blank'); }
function currentDiagram(){return document.getElementById('diagramSel').value}
function currentOutput(){return document.getElementById('outputSel').value}
function openCurrentDot(){ if(state.run && currentDiagram()) window.open('/artifact/'+encodeURIComponent(state.run.run_id)+'/'+encodeURIComponent(currentOutput())+'/dot/'+encodeURIComponent(currentDiagram()),'_blank'); }
function openCurrentSvg(){ if(state.run && currentDiagram()) window.open('/artifact/'+encodeURIComponent(state.run.run_id)+'/'+encodeURIComponent(currentOutput())+'/svg/'+encodeURIComponent(currentDiagram().replace('.dot','.svg')),'_blank'); }

init();
</script>
</body>
</html>"""

def _json(handler, obj, status=200):
    b=json.dumps(obj).encode()
    handler.send_response(status)
    handler.send_header("Content-Type","application/json")
    handler.send_header("Content-Length",str(len(b)))
    handler.end_headers()
    handler.wfile.write(b)

def _read_json(handler):
    n=int(handler.headers.get("Content-Length","0"))
    return json.loads(handler.rfile.read(n).decode() or "{}")

def _safe_join(root: Path, rel: str) -> Path:
    p=(root/rel).resolve()
    if not str(p).startswith(str(root.resolve())):
        raise ValueError("bad path")
    return p

class GuiHandler(BaseHTTPRequestHandler):
    server_version="BDDStudioGUI/0.5"
    def do_GET(self):
        try:
            u=urlparse(self.path)
            if u.path=="/":
                b=APP_HTML.encode()
                self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.send_header("Content-Length",str(len(b))); self.end_headers(); self.wfile.write(b); return
            if u.path=="/api/example":
                ex=Path(self.server.project_root)/"examples"/"mult_3x2.yaml"
                _json(self, {"ok":True,"yaml":ex.read_text()}); return
            if u.path=="/api/examples":
                examples_dir=Path(self.server.project_root)/"examples"
                items=[]
                for pth in sorted(list(examples_dir.glob("*.yaml"))+list(examples_dir.glob("*.yml"))):
                    items.append({"name":pth.stem, "path":"examples/"+pth.name})
                _json(self, {"ok":True,"examples":items}); return
            if u.path=="/api/load-path":
                q=parse_qs(u.query)
                rel=unquote(q.get("path",[""])[0])
                root=Path(self.server.project_root)
                try:
                    pth=_safe_join(root, rel)
                except Exception:
                    pth=_safe_join(Path.cwd(), rel)
                if not pth.exists() or not pth.is_file():
                    _json(self, {"ok":False,"error":f"file not found: {rel}"}, 404); return
                _json(self, {"ok":True,"yaml":pth.read_text()}); return
            if u.path=="/api/diagrams":
                q=parse_qs(u.query)
                run=unquote(q.get("run",[""])[0]); out=unquote(q.get("output",[""])[0])
                d=_safe_join(Path(self.server.workspace), f"runs/{run}/{out}/dot")
                diagrams=sorted([p.name for p in d.glob("*.dot")]) if d.exists() else []
                _json(self, {"ok":True,"diagrams":diagrams}); return
            if u.path=="/api/inspect":
                q=parse_qs(u.query)
                run=unquote(q.get("run",[""])[0]); out=unquote(q.get("output",[""])[0]); tab=unquote(q.get("tab",["summary"])[0])
                base=_safe_join(Path(self.server.workspace), f"runs/{run}")
                text=""
                if tab=="initial":
                    p=base/out/"initial_full_node_table.txt"; text=p.read_text() if p.exists() else "No initial node table."
                elif tab=="nodes":
                    p=base/out/"final_node_table.txt"; text=p.read_text() if p.exists() else "No final node table."
                elif tab=="log":
                    p=base/out/"reduction_log.json"; text=p.read_text() if p.exists() else "No reduction log."
                elif tab=="truth":
                    p=base/"truth_tables.txt"; text=p.read_text() if p.exists() else "No truth table."
                else:
                    p=base/"summary.txt"; text=p.read_text() if p.exists() else "No summary."
                _json(self, {"ok":True,"text":text}); return
            if u.path.startswith("/artifact/"):
                rel=unquote(u.path[len("/artifact/"):])
                p=_safe_join(Path(self.server.workspace)/"runs", rel)
                if p.is_dir():
                    items=sorted(p.iterdir())
                    html="<h2>BDD Studio Build Folder</h2><ul>"+"".join(f'<li><a href="{i.name}{"/" if i.is_dir() else ""}">{i.name}</a></li>' for i in items)+"</ul>"
                    b=html.encode(); self.send_response(200); self.send_header("Content-Type","text/html"); self.end_headers(); self.wfile.write(b); return
                if p.exists():
                    ctype="text/plain"
                    if p.suffix==".html": ctype="text/html"
                    elif p.suffix==".png": ctype="image/png"
                    elif p.suffix==".svg": ctype="image/svg+xml"
                    elif p.suffix==".pdf": ctype="application/pdf"
                    b=p.read_bytes(); self.send_response(200); self.send_header("Content-Type",ctype); self.send_header("Content-Length",str(len(b))); self.end_headers(); self.wfile.write(b); return
                self.send_error(404); return
            self.send_error(404)
        except Exception as e:
            _json(self, {"ok":False,"error":str(e),"trace":traceback.format_exc()}, 500)
    def do_POST(self):
        try:
            if self.path=="/api/check":
                data=_read_json(self); proj=Path(self.server.workspace)/"last_check.yaml"; proj.write_text(data.get("yaml",""))
                p=load_project(proj)
                _json(self, {"ok":True,"message":f"Project: {p.name}\nInputs: {', '.join(p.inputs)}\nOutputs: {', '.join(p.outputs)}\nVariable order: {' < '.join(p.order)}\nGraphviz: {'OK' if dot_available() else 'not found'}\nCheck: OK"})
                return
            if self.path=="/api/build":
                data=_read_json(self)
                run_id=time.strftime("%Y%m%d_%H%M%S")
                run_dir=Path(self.server.workspace)/"runs"/run_id; run_dir.mkdir(parents=True, exist_ok=True)
                proj=run_dir/"project.yaml"; proj.write_text(data.get("yaml",""))
                p=load_project(proj); p.output_dir=str(run_dir)
                fmts=[x.strip() for x in data.get("formats","dot,png,svg").split(",") if x.strip()]
                summaries=[]
                for name,expr in p.outputs.items():
                    summaries.append(build_one(p,name,expr,fmts,True))
                write_reports(p,summaries)
                summary=f"Project: {p.name}\nRun: {run_id}\nVariable order: {' < '.join(p.order)}\n"
                summary+="\n".join(f"{s['name']}: final nodes={len([ln for ln in s['final_table'].splitlines() if ln.startswith('N')])}, reductions={len(s['events'])}" for s in summaries)
                summary+=f"\nGraphviz: {'OK' if dot_available() else 'not found - DOT generated only'}"
                (run_dir/"summary.txt").write_text(summary)
                tt=[]
                for name,e in p.outputs.items():
                    tt.append(f"\n{name} = {e}\n"+" ".join(p.order)+" | "+name)
                    for env,val in truth_rows(e,p.order):
                        tt.append(" ".join(str(env[v]) for v in p.order)+" | "+str(val))
                (run_dir/"truth_tables.txt").write_text("\n".join(tt))
                _json(self, {"ok":True,"run_id":run_id,"outputs":list(p.outputs.keys()),"message":summary})
                return
            self.send_error(404)
        except Exception as e:
            _json(self, {"ok":False,"error":str(e),"trace":traceback.format_exc()}, 500)
    def log_message(self, fmt, *args):
        return

def serve(host="127.0.0.1", port=8765, workspace=None, open_browser=True):
    root=Path(__file__).resolve().parents[2]
    if workspace is None:
        workspace=Path.cwd()/".bddstudio_gui"
    workspace=Path(workspace); workspace.mkdir(parents=True, exist_ok=True)
    httpd=ThreadingHTTPServer((host,port), GuiHandler)
    httpd.project_root=str(root); httpd.workspace=str(workspace)
    url=f"http://{host}:{port}/"
    print(f"BDD Studio CAD GUI running at {url}")
    print(f"Workspace: {workspace}")
    if open_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping BDD Studio CAD GUI.")
