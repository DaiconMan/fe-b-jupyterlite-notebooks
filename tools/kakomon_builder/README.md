
# 過去問 → Jupyter ノート自動生成（出典ひも付け対応版）

- ノートごとに **出典メタデータ**（年度 / 回・期 / 問番号 / 出典URL / タグ）を埋め込み、
  ファイル名とノート冒頭のバッジにも反映します。
- さらに `content/kakomon/_catalog.json` と **検索フィルタ付き index.ipynb** を生成します（ipywidgets）。

## 使い方
```bash
python tools/kakomon_builder/build_notebooks.py tools/kakomon_builder/data/questions.json content/kakomon
git add content/kakomon
git commit -m "chore(kakomon): regenerate notebooks with source metadata"
```

## questions.json の書式（例）
```json
{
  "questions": [{
    "title": "素数判定のループ境界",
    "stem": "…",
    "options": ["…"],
    "answer": 2,
    "explain": "…",
    "source_year": "2024",
    "source_session": "公開問題(科目B)",
    "source_qid": "Q-A01",
    "source_url": "https://example.com/ipa/…",
    "tags": ["アルゴリズム","…"]
  }]
}
```

※ 実運用では IPA 公開ページの実URLを入れてください。出典の明記と注意事項の遵守をお忘れなく。
