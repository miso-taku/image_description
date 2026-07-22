# ビルドとテスト手順

## 前提

- Python 3.12.8（uvが自動取得可能）
- Node.js 20以上、npm
- OpenAI APIキー（実呼び出し時のみ。テストは不要）

## バックエンド

```bash
cd backend
uv sync --extra dev
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
Copy-Item .env.local.example .env.local   # 必要に応じ NEXT_PUBLIC_API_BASE_URL を編集
npm run lint
npm run typecheck
npm test
npm run build
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
# フロントエンド依存監査（Node標準）
cd frontend; npm audit --audit-level=moderate
```

## PBT再現性 (PBT-08)

- Hypothesisの縮小は既定で有効。
- 失敗時はseedと最小反例が出力される。
- seed固定は `HYPOTHESIS_SEED` もしくは `--hypothesis-seed` で可能。

## ビルド・テスト実行結果

### バックエンド（`backend/`）

- ruff check: 成功（0件）
- mypy app（strict）: 成功（15ファイル・0件）
- pytest: 28件すべて成功
  - test_api.py 9件 / test_description_service.py 8件 / test_image_validation.py 9件 / test_schemas_pbt.py 2件

### フロントエンド（`frontend/`）

- eslint: 成功（0件）
- tsc --noEmit: 成功（0件）
- vitest run: 12件すべて成功（4ファイル）
  - validation / apiClient / DescriptionResult / ImageUploader
- next build: 本番ビルド成功（静的プリレンダリング）
- npm audit: 脆弱性0件（PostCSSを8.5.10へoverride）

## セキュリティヘッダー検証（稼働確認）

`GET http://localhost:3000` の応答で以下を確認済み:

- `Content-Security-Policy`: `default-src 'self'` 起点の制限的ポリシー
- `Strict-Transport-Security`: `max-age=31536000; includeSubDomains`
- `X-Content-Type-Options`: `nosniff`
- `X-Frame-Options`: `DENY`
- `Referrer-Policy`: `strict-origin-when-cross-origin`

## ビルド・テストサマリー

- 品質ゲート: ruff, mypy, pytest（BE）／ eslint, tsc, vitest, next build, npm audit（FE）。
- すべての品質ゲートが成功。Operationsフェーズ（ローカル運用手順）へ進行可能。
