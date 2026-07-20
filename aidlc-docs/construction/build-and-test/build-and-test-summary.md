# ビルドとテスト手順

## 前提

- Python 3.12.8（uvが自動取得可能）
- Node.js 20以上、npm
- OpenAI APIキー（実呼び出し時のみ。テストは不要）

## バックエンド

```bash
cd backend
uv sync
# lint と型
uv run ruff check .
uv run mypy app
# テスト（外部APIはモック、課金なし）
uv run pytest
# 起動
uv run uvicorn app.main:app --reload --port 8000
```

環境変数は `backend/.env` に設定する（`.env.example` を複製）。

## フロントエンド

```bash
cd frontend
npm install
npm run lint
npm run typecheck
npm test
npm run dev   # http://localhost:3000
```

## 統合確認

1. バックエンドを8000で起動。
2. フロントエンドを3000で起動。
3. 画像を選択し詳細度を変えて説明を生成。
4. コピー機能とエラー表示を確認。

## セキュリティ確認 (SECURITY-10)

```bash
# 依存脆弱性（Docker利用可能時）
docker run --rm -v "$PWD:/workspace" anchore/grype:latest dir:/workspace
# SBOM
docker run --rm -v "$PWD:/workspace" anchore/syft:latest dir:/workspace -o spdx-json > sbom.spdx.json
```

## PBT再現性 (PBT-08)

- Hypothesisの縮小は既定で有効。
- 失敗時はseedと最小反例が出力される。
- seed固定は `HYPOTHESIS_SEED` もしくは `--hypothesis-seed` で可能。

## ビルド・テストサマリー

- 品質ゲート: ruff, mypy, pytest（BE）／ eslint, tsc, vitest（FE）。
- 生成コード後に各ゲートを実行し結果を記録する。
