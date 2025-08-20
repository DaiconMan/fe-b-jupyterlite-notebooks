
# 過去問 → Jupyterノート 自動生成キット（ローカル/CI両対応）

- 編集するのは **`tools/kakomon_builder/data/questions.json`** だけ。
- 生成物は **`content/kakomon/`** に出力され、JupyterLiteで配信されます。

## 使い方（ローカル）
```bash
python tools/kakomon_builder/build_notebooks.py tools/kakomon_builder/data/questions.json content/kakomon
git add content/kakomon
git commit -m "chore(kakomon): regenerate notebooks from data/questions.json"
```

## よくある質問
- **ipywidgetsが無い** → 生成ノート先頭に**自動導入セル**を同梱済み（JupyterLite/通常Jupyter両対応）。
- **公開に出ない** → `content/` 以下に出力されていますか？コミット済みですか？

このキット作成: 2025-08-20
