import json, sys, re
from pathlib import Path

SETUP_CELL = '\n# --- Ensure ipywidgets is available (JupyterLite/regular Jupyter) ---\ntry:\n    import ipywidgets as widgets\nexcept ModuleNotFoundError:\n    try:\n        import piplite\n        await piplite.install([\'ipywidgets\'])\n    except Exception as e:\n        print("piplite install failed or not JupyterLite:", e)\n    import ipywidgets as widgets\n'

def nb(cells, title="Notebook", fe_source=None):
    meta = {
      "kernelspec": {"display_name":"Python 3","language":"python","name":"python3"},
      "language_info": {"name":"python","version":"3.11"},
    }
    if fe_source is not None:
        meta["fe_source"] = fe_source
    return {
      "cells": cells,
      "metadata": meta,
      "nbformat":4,
      "nbformat_minor":5
    }

def md(text): return {"cell_type":"markdown","metadata":{},"source":[text]}
def code(src): return {"cell_type":"code","metadata":{},"execution_count":None,"outputs":[],"source":[src]}

def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:60] or "q"

def build(inp, outdir):
    data = json.loads(Path(inp).read_text(encoding="utf-8"))
    qs = data["questions"]
    out = Path(outdir); out.mkdir(parents=True, exist_ok=True)

    catalog = []

    index_header = md("# 過去問カタログ（フィルタ可）\n\n出典や年度で絞り込みできます。")
    index_code = code(SETUP_CELL + """
import json
from IPython.display import display, HTML, clear_output
import ipywidgets as w

CAT_PATH = "_catalog.json"
data = json.loads(open(CAT_PATH, "r", encoding="utf-8").read())

def rows(filtered):
    head = "<tr><th>年度</th><th>回/期</th><th>問番号</th><th>タイトル</th><th>リンク</th></tr>"
    body = "".join(
        f"<tr><td>{{d.get('year','')}}</td><td>{{d.get('session','')}}</td><td>{{d.get('q','')}}</td>"
        f"<td>{{d.get('title','')}}</td>"
        f"<td><a href='{{d['filename']}}' target='_blank'>{{d['filename']}}</a></td></tr>"
        for d in filtered
    )
    return f"<table>{{head}}{{body}}</table>"

years = sorted(sorted({d.get("year","") for d in data if d.get("year")}), reverse=True)
sessions = sorted(sorted({d.get("session","") for d in data if d.get("session")}), reverse=True)
topics = sorted(sorted({t for d in data for t in d.get("tags", [])}))

year_dd = w.Dropdown(options=["(all)"] + years, description="年度")
sess_dd = w.Dropdown(options=["(all)"] + sessions, description="回")
topic_dd = w.Dropdown(options=["(all)"] + topics, description="タグ")
kw = w.Text(value="", description="キーワード")
out = w.Output()

def render(*_):
    with out:
        clear_output()
        ds = data
        if year_dd.value != "(all)":
            ds = [d for d in ds if d.get("year") == year_dd.value]
        if sess_dd.value != "(all)":
            ds = [d for d in ds if d.get("session") == sess_dd.value]
        if topic_dd.value != "(all)":
            ds = [d for d in ds if topic_dd.value in d.get("tags", [])]
        if kw.value.strip():
            key = kw.value.lower()
            ds = [d for d in ds if key in d.get("title","").lower() or key in d.get("stem","").lower()]
        html = rows(ds)
        display(HTML(html))

for wdg in (year_dd, sess_dd, topic_dd, kw):
    wdg.observe(render, names="value")

display(w.VBox([w.HBox([year_dd, sess_dd, topic_dd]), kw, out]))
render()
""")

    for q in qs:
        year = q.get("source_year")
        session = q.get("source_session")
        qno = q.get("source_qid")
        url = q.get("source_url")
        tags = q.get("tags", [])
        title = q["title"]
        stem = q["stem"]
        opts = q["options"]
        ans = q["answer"]
        exp = q.get("explain", "")

        badge_lines = []
        if year:    badge_lines.append(f"- 年度: **{year}**")
        if session: badge_lines.append(f"- 回/期: **{session}**")
        if qno:     badge_lines.append(f"- 問番号: **{qno}**")
        if url:     badge_lines.append(f"- 出典URL: [リンク]({url})")
        badge_md = "### 出典\n" + ("\n".join(badge_lines) if badge_lines else "（自作／出典未指定）")

        header = f"# {title}\n\n{badge_md}\n\n---\n\n**問題**\n\n{stem}\n\n**選択肢**\n" + "\n".join(f"{i+1}) {o}" for i,o in enumerate(opts))
        ui = (
            "from IPython.display import display, Markdown, clear_output\n\n"
            f"opts = {opts!r}\n"
            f"correct = {ans}\n"
            "radio = widgets.RadioButtons(options=[(f\"{i+1}) \" + o, i) for i,o in enumerate(opts)], description=\"選択\")\n"
            "btn = widgets.Button(description=\"判定\")\n"
            "out = widgets.Output()\n\n"
            "def on_click(_):\n"
            "    with out:\n"
            "        clear_output()\n"
            "        if radio.value == correct:\n"
            "            display(Markdown(\"**✅ 正解！**\"))\n"
            "        else:\n"
            "            display(Markdown(\"**❌ 不正解**\"))\n"
            f"        display(Markdown(\"**解説**: {exp}\"))\n\n"
            "btn.on_click(on_click)\n"
            "display(radio, btn, out)\n"
        )

        fe_source = {"year": year, "session": session, "q": qno, "url": url, "title": title, "tags": tags}
        cells = [md(header), code(SETUP_CELL), code(ui)]
        if q.get("code"):
            cells.append(md("---\n### 動作確認コード"))
            cells.append(code(q["code"]))

        parts = ["feB"]
        if year: parts.append(str(year))
        if session: parts.append(slugify(session))
        if qno: parts.append(slugify(qno))
        parts.append(slugify(title))
        fname = "-".join(parts) + ".ipynb"

        (out / fname).write_text(json.dumps(nb(cells, title, fe_source), ensure_ascii=False, indent=2), encoding="utf-8")
        catalog.append({"filename": fname, "year": year, "session": session, "q": qno, "url": url, "title": title, "tags": tags, "stem": stem[:200]})

    (out / "_catalog.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "index.ipynb").write_text(json.dumps(nb([index_header, index_code], "kakomon index"), ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    inp = sys.argv[1] if len(sys.argv) > 1 else "tools/kakomon_builder/data/questions.json"
    out = sys.argv[2] if len(sys.argv) > 2 else "content/kakomon"
    build(inp, out)
