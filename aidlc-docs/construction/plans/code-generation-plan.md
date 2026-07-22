# コード生成計画 (image-description-app)

## Part 1 - 計画 / Part 2 - 生成（実装済み）

application/documentationの配置ルール: アプリコードはワークスペース直下、ドキュメントは aidlc-docs 配下。

## バックエンド (`backend/`)

- [x] `backend/pyproject.toml` — Python 3.12、依存、Ruff/mypy/pytest設定
- [x] `backend/.python-version` — 3.12.8
- [x] `backend/app/__init__.py`
- [x] `backend/app/main.py` — FastAPIアプリ生成、CORS、例外ハンドラー、ルーター登録
- [x] `backend/app/core/config.py` — Pydantic Settings
- [x] `backend/app/core/logging.py` — 構造化JSONロギング
- [x] `backend/app/core/errors.py` — AppError階層と例外ハンドラー
- [x] `backend/app/core/security.py` — レート制限、リクエストIDミドルウェア
- [x] `backend/app/schemas/description.py` — DetailLevel、レスポンス、AI出力
- [x] `backend/app/schemas/error.py` — ErrorResponse
- [x] `backend/app/services/image_validation.py` — 検証（純粋ロジック）
- [x] `backend/app/services/description_service.py` — PydanticAI連携
- [x] `backend/app/api/routes.py` — `/api/v1/descriptions`, `/health`
- [x] `backend/tests/` — 単体、API、PBTテスト（28件成功）
- [x] `backend/.env.example` — ダミー値
- [x] `backend/README.md`

## フロントエンド (`frontend/`)

- [x] `frontend/package.json` — Next.js/React/TS、テスト、lint
- [x] `frontend/tsconfig.json`, `next.config.mjs`(ヘッダー), `eslint.config.mjs`, `vitest.config.ts`
- [x] `frontend/app/layout.tsx`, `app/page.tsx`, `app/globals.css`
- [x] `frontend/components/ImageUploader.tsx`
- [x] `frontend/components/DescriptionResult.tsx`
- [x] `frontend/lib/apiClient.ts`, `lib/validation.ts`, `lib/types.ts`
- [x] `frontend/__tests__/` — validation、apiClient、コンポーネント、フロー（12件成功）
- [x] `frontend/.env.local.example`
- [x] `frontend/README.md`

## ルート

- [x] `README.md` — 全体概要と起動手順
- [x] `.gitignore`（ルート／backend はルートで集約／frontend 個別）

## テスト方針（実施結果）

- OpenAIはPydanticAIのモデル差し替え・Fakeサービスでスタブ化し課金なし。
- Hypothesisでスキーマ往復・列挙値・サイズ境界をPBT (PBT-02,03,07,08)。
- 例ベーステストで正常系と各エラー分類を固定。
- バックエンド: ruff・mypy(strict)・pytest 28件すべて成功。
- フロントエンド: eslint・tsc・vitest 12件・next build・npm audit(脆弱性0)すべて成功。

## ストーリートレーサビリティ

- US-01 画像選択 → `ImageUploader.tsx`（クリック/ドラッグ＆ドロップ、プレビュー、メタ表示）
- US-02 入力検証 → `lib/validation.ts` + backend `image_validation.py`（多層検証）
- US-03 詳細度選択 → `ImageUploader.tsx`（brief/standard/detailed、既定standard）
- US-04 説明生成 → `lib/apiClient.ts` + backend `description_service.py`
- US-05 結果表示/コピー → `DescriptionResult.tsx`（aria-live、コピー通知）
- US-06 エラー理解 → `apiClient.ts` の分類 + backend 例外ハンドラー
- US-07 プライバシー → 送信前の明示、非永続化（front/back 双方）
- US-08 アクセシビリティ → ラベル/フォーカス/色非依存/レスポンシブ（globals.css）
- US-09 ローカル起動 → ルート/各READMEの手順
