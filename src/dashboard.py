"""
CSV Data Dashboard - Portfolio Project
Author: Oscar J. Villa García
Description: Reads any CSV, performs statistical analysis and generates a self-contained HTML dashboard.
"""

import pandas as pd, json, logging, argparse
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

def analyze(df):
    report = {"shape": list(df.shape), "columns": {}}
    for col in df.columns:
        info = {"dtype": str(df[col].dtype), "nulls": int(df[col].isnull().sum())}
        if pd.api.types.is_numeric_dtype(df[col]):
            info.update({"min": round(float(df[col].min()),4), "max": round(float(df[col].max()),4),
                "mean": round(float(df[col].mean()),4), "median": round(float(df[col].median()),4),
                "std": round(float(df[col].std()),4), "type": "numeric", "values": df[col].dropna().tolist()[:200]})
        else:
            vc = df[col].value_counts().head(10)
            info.update({"unique": int(df[col].nunique()), "top_values": vc.index.tolist(), "top_counts": vc.values.tolist(), "type": "categorical"})
        report["columns"][col] = info
    return report

HTML = """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Dashboard — {filename}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>*{{box-sizing:border-box;margin:0;padding:0}}body{{font-family:'Segoe UI',sans-serif;background:#0f172a;color:#e2e8f0}}
header{{background:linear-gradient(135deg,#1e3a5f,#1e40af);padding:2rem;text-align:center}}header h1{{font-size:2rem}}
main{{max-width:1400px;margin:2rem auto;padding:0 1rem}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(400px,1fr));gap:1.5rem}}
.card{{background:#1e293b;border-radius:1rem;padding:1.5rem;border:1px solid #334155}}.card h2{{font-size:.9rem;color:#7dd3fc;margin-bottom:1rem;text-transform:uppercase}}
.stats{{display:grid;grid-template-columns:repeat(3,1fr);gap:.5rem;margin-bottom:1rem}}.stat{{background:#0f172a;border-radius:.5rem;padding:.6rem;text-align:center}}
.stat .val{{font-size:1rem;font-weight:700;color:#38bdf8}}.stat .lbl{{font-size:.7rem;color:#64748b}}.chart-wrap{{position:relative;height:160px}}
footer{{text-align:center;padding:2rem;color:#475569;font-size:.85rem}}</style></head><body>
<header><h1>📊 CSV Dashboard — {filename}</h1><p>{rows} rows · {cols} columns · {timestamp}</p></header>
<main><div class="grid" id="cards"></div></main>
<footer>Built by Oscar J. Villa García · ojviga@gmail.com</footer>
<script>
const DATA={data_json};const COLORS=["#38bdf8","#818cf8","#34d399","#fb923c","#f472b6","#a78bfa"];
function card(col,info,i){{
  const id="c_"+col.replace(/\W/g,"_");
  const stats=info.type==="numeric"?
    `<div class="stat"><div class="val">${{info.min}}</div><div class="lbl">Min</div></div><div class="stat"><div class="val">${{info.mean}}</div><div class="lbl">Mean</div></div><div class="stat"><div class="val">${{info.max}}</div><div class="lbl">Max</div></div>`:
    `<div class="stat"><div class="val">${{info.unique}}</div><div class="lbl">Unique</div></div><div class="stat"><div class="val">${{info.nulls}}</div><div class="lbl">Nulls</div></div><div class="stat"><div class="val">-</div><div class="lbl">-</div></div>`;
  return `<div class="card"><h2>${{col}}</h2><div class="stats">${{stats}}</div><div class="chart-wrap"><canvas id="${{id}}"></canvas></div></div>`;
}}
window.addEventListener("DOMContentLoaded",()=>{{
  const c=document.getElementById("cards");
  Object.entries(DATA.columns).forEach(([col,info],i)=>{{c.innerHTML+=card(col,info,i);}});
  Object.entries(DATA.columns).forEach(([col,info],i)=>{{
    const ctx=document.getElementById("c_"+col.replace(/\W/g,"_"))?.getContext("2d");
    if(!ctx)return;const color=COLORS[i%COLORS.length];
    if(info.type==="numeric")new Chart(ctx,{{type:"line",data:{{labels:info.values.map((_,j)=>j),datasets:[{{data:info.values,borderColor:color,borderWidth:1.5,pointRadius:0,fill:true,backgroundColor:color+"22"}}]}},options:{{plugins:{{legend:{{display:false}}}},scales:{{x:{{display:false}},y:{{ticks:{{color:"#94a3b8"}},grid:{{color:"#1e293b"}}}}}}}}}});
    else new Chart(ctx,{{type:"bar",data:{{labels:info.top_values.map(v=>String(v).slice(0,15)),datasets:[{{data:info.top_counts,backgroundColor:COLORS.map(c=>c+"cc")}}]}},options:{{indexAxis:"y",plugins:{{legend:{{display:false}}}},scales:{{x:{{ticks:{{color:"#94a3b8"}}}},y:{{ticks:{{color:"#94a3b8"}},grid:{{display:false}}}}}}}}}}});
  }});
}});
</script></body></html>"""

def generate_dashboard(csv_path, output_dir=None):
    csv_path = Path(csv_path).resolve()
    df = pd.read_csv(csv_path)
    report = analyze(df)
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "output"
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = Path(output_dir) / f"dashboard_{csv_path.stem}_{ts}.html"
    html = HTML.format(filename=csv_path.name, rows=df.shape[0], cols=df.shape[1],
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"), data_json=json.dumps(report))
    out_path.write_text(html, encoding="utf-8")
    log.info(f"Dashboard saved -> {out_path}")
    return out_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate HTML dashboard from CSV")
    parser.add_argument("csv", help="Path to CSV file")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    path = generate_dashboard(args.csv, args.output)
    print(f"\n✅ Dashboard ready -> {path}")
