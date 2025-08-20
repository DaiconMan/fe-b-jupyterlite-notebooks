
import json, sys
from pathlib import Path

SETUP_CELL = '\n# --- Ensure ipywidgets is available (JupyterLite/regular Jupyter) ---\ntry:\n    import ipywidgets as widgets\nexcept ModuleNotFoundError:\n    try:\n        import piplite\n        await piplite.install([\'ipywidgets\'])\n    except Exception as e:\n        print("piplite install failed or not JupyterLite:", e)\n    import ipywidgets as widgets\n'

def nb(cells, title="Notebook"):
    return {
      "cells": cells,
      "metadata": {
        "kernelspec": {"display_name":"Python 3","language":"python","name":"python3"},
        "language_info": {"name":"python","version":"3.11"}
      },
      "nbformat":4,
      "nbformat_minor":5
    }

def md(text): return {"cell_type":"markdown","metadata":{},"source":[text]}
def code(src): return {"cell_type":"code","metadata":{},"execution_count":None,"outputs":[],"source":[src]}

def mcq_cells(q):
    stem = q["stem"]
    opts = q["options"]
    ans  = q["answer"]
    exp  = q.get("explain","")
    header = f"# {q['id']}: {q['title']}\n\n{stem}\n\n**選択肢**\n" + "\n".join(f"{i+1}) {o}" for i,o in enumerate(opts))
    ui = f"""
from IPython.display import display, Markdown, clear_output

opts = {opts!r}
correct = {ans}
radio = widgets.RadioButtons(options=[(f"{{i+1}}) " + o, i) for i,o in enumerate(opts)], description="選択")
btn = widgets.Button(description="判定")
out = widgets.Output()

def on_click(_):
    with out:
        clear_output()
        if radio.value == correct:
            display(Markdown("**✅ 正解！**"))
        else:
            display(Markdown("**❌ 不正解**"))
        display(Markdown("**解説**: {exp}"))

btn.on_click(on_click)
display(radio, btn, out)
"""
    cells = [md(header), code(SETUP_CELL), code(ui)]
    if q.get("code"):
        cells.append(md("---\n### 動作確認コード"))
        cells.append(code(q["code"]))
    return cells

def build(inp, outdir):
    data = json.loads(Path(inp).read_text(encoding="utf-8"))
    out = Path(outdir); out.mkdir(parents=True, exist_ok=True)

    # index
    links = "\n".join(f"- [{q['id']}: {q['title']}]({q['id']}.ipynb)" for q in data["questions"])
    (out / "index.ipynb").write_text(json.dumps(nb([md(f"# 過去問スタイル MCQ\n\n{links}")]), ensure_ascii=False, indent=2), encoding="utf-8")

    # each question
    for q in data["questions"]:
        notebook = nb(mcq_cells(q), q["title"])
        (out / f"{q['id']}.ipynb").write_text(json.dumps(notebook, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    inp = sys.argv[1] if len(sys.argv) > 1 else "tools/kakomon_builder/data/questions.json"
    out = sys.argv[2] if len(sys.argv) > 2 else "content/kakomon"
    build(inp, out)
