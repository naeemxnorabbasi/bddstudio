
from pathlib import Path
import html, json
def write_reports(project, summaries):
    out=Path(project.output_dir); out.mkdir(parents=True, exist_ok=True)
    md=["# "+project.name,"","## Assumptions","","All variables are 1-bit Boolean signals.","Low edge = 0, high edge = 1.","","## Variable order","","`"+" < ".join(project.order)+"`",""]
    for s in summaries:
        md += [f"## Output `{s['name']}`","", "### Final ROBDD node table","", "```text", s["final_table"], "```","", f"Reduction steps: {len(s['events'])}",""]
    (out/"report.md").write_text("\n".join(md))
    body="<h1>"+html.escape(project.name)+"</h1><p>Variable order: <code>"+html.escape(" < ".join(project.order))+"</code></p>"
    for s in summaries:
        body+=f"<h2>Output <code>{html.escape(s['name'])}</code></h2><pre>{html.escape(s['final_table'])}</pre><p>Reduction steps: {len(s['events'])}</p>"
    (out/"report.html").write_text("<!doctype html><meta charset='utf-8'><title>BDD Studio Report</title><style>body{font-family:Arial;margin:40px;max-width:1000px}pre{background:#f5f5f5;padding:12px;border-radius:8px}</style>"+body)
