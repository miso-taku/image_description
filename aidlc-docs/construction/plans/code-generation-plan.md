# コード生成計画 (image-description-app)

## Part 1 - 計画（本書） / Part 2 - 生成（実装）

application/documentationの配置ルール: アプリコードはワークスペース直下、ドキュメントは aidlc-docs 配下。

## バックエンド (`backend/`)

- [ ] `backend/pyproject.toml` — Python 3.12、依存、Ruff/mypy/pytest設定
- [ ] `backend/.python-version` — 3.12.8
- [ ] `backend/app/__init__.py`
- [ ] `backend/app/main.py` — FastAPIアプリ生成、CORS、例外ハンドラー、ルーター登録
- [ ] `backend/app/core/config.py` — Pydantic Settings
- [ ] `backend/app/core/logging.py` — 構造化JSONロギング
- [ ] `backend/app/core/errors.py` — AppError階層と例外ハンドラー
- [ ] `backend/app/core/security.py` — レート制限、リクエストIDミドルウェア
- [ ] `backend/app/schemas/description.py` — DetailLevel、レスポンス、AI出力
- [ ] `backend/app/schemas/error.py` — ErrorResponse
- [ ] `backend/app/services/image_validation.py` — 検証（純粋ロジック）
- [ ] `backend/app/services/description_service.py` — PydanticAI連携
- [ ] `backend/app/api/routes.py` — `/api/v1/descriptions`, `/health`
- [ ] `backend/tests/` — 単体、API、PBTテスト
- [ ] `backend/.env.example` — ダミー値
- [ ] `backend/README.md`

## フロントエンド (`frontend/`)

- [ ] `frontend/package.json` — Next.js/React/TS、テスト、lint
- [ ] `frontend/tsconfig.json`, `next.config.mjs`(ヘッダー), `.eslintrc`, `vitest.config.ts`
- [ ] `frontend/app/layout.tsx`, `app/page.tsx`, `app/globals.css`
- [ ] `frontend/components/ImageUploader.tsx`
- [ ] `frontend/components/DescriptionResult.tsx`
- [ ] `frontend/lib/apiClient.ts`, `lib/validation.ts`, `lib/types.ts`
- [ ] `frontend/__tests__/` — validation、コンポーネント、フロー
- [ ] `frontend/.env.local.example`
- [ ] `frontend/README.md`

## ルート

- [ ] `README.md` — 全体概要と起動手順
- [ ] `.gitignore`

## テスト方針

- OpenAIはPydanticAIの `TestModel`/`FunctionModel` またはモデル差し替えでスタブ化し課金しない。
- Hypothesisで BR-01/02/03 とスキーマ往復をPBT (PBT-02,03,07,08)。
- 例ベーステストで正常系と各エラー分類を固定。
