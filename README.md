# Image Description（画像説明生成アプリ）

アップロードした画像の内容を**日本語の自然文**で説明する Web アプリケーションです。
画像を 1 枚選択し、説明の詳しさ（短い／標準／詳細）を指定すると、OpenAI の
Vision 対応モデルが画像を解析して日本語の説明文を生成します。

ローカル環境での利用を想定しており、画像や生成結果を永続保存しません。

## 主な機能

- 画像を 1 枚選択（クリック / ドラッグ＆ドロップ）してプレビュー表示
- 入力形式の検証（JPEG / PNG / WebP、最大 10 MB、MIME・シグネチャ・サイズを多層検証）
- 説明レベルの選択（`brief` 短い / `standard` 標準 / `detailed` 詳細）
- OpenAI API による日本語説明文の生成
- 生成結果の表示とクリップボードへのコピー
- 日本語での安全なエラー表示（認証・レート制限・タイムアウト・外部 API 障害を区別）
- 有料 API を呼び出さないヘルスチェック（`GET /health`）

## 技術スタック

| 領域 | 技術 |
|------|------|
| バックエンド | Python 3.12.8、uv、FastAPI、Pydantic、Pydantic Settings、PydanticAI |
| フロントエンド | Next.js、React、TypeScript |
| AI プロバイダー | OpenAI API（既定モデル `gpt-4.1-mini`、`OPENAI_MODEL` で変更可能） |

## リポジトリ構成

```text
image_description/
├── backend/          # FastAPI + PydanticAI バックエンド（実装済み）
│   ├── app/          # アプリケーション本体（API・設定・検証・AIサービス・スキーマ）
│   ├── tests/        # pytest による単体・API・Property-Based テスト
│   └── README.md     # バックエンドのセットアップと実行方法
├── frontend/         # Next.js フロントエンド（計画中）
├── aidlc-docs/       # AI-DLC 方法論による設計・要件ドキュメント
└── AGENTS.md         # AI コーディングエージェント向けの指針
```

> **注記**: 現時点では `backend/` が実装済みです。`frontend/`（Next.js）は
> [要件定義書](aidlc-docs/inception/requirements/requirements.md) に基づき今後実装予定です。

## クイックスタート（バックエンド）

```bash
cd backend
uv sync --extra dev
cp .env.example .env   # その後 .env を編集して OPENAI_API_KEY を設定
uv run uvicorn app.main:app --reload --port 8000
```

- API ドキュメント: http://localhost:8000/docs
- ヘルスチェック: http://localhost:8000/health

詳細なセットアップ・環境変数・API 仕様は [backend/README.md](backend/README.md) を参照してください。

## API 概要

### POST /api/v1/descriptions

`multipart/form-data`:

- `image`: JPEG / PNG / WebP（最大 10 MB）
- `detail`: `brief`（短い） | `standard`（標準） | `detailed`（詳細）

成功時は `{ description, detail, model, request_id }`、
エラー時は `{ error: { code, message, request_id } }` を返します。

## 設計思想・セキュリティ方針

- **プライバシー**: 画像・生成結果はメモリ上でのみ処理し、永続化しません。ログにも画像や説明本文を出力しません。
- **シークレット管理**: `OPENAI_API_KEY` は環境変数からのみ読み込み、ソース管理に含めません（`.env.example` はダミー・空値のみ）。
- **多層検証**: 拡張子だけでなく MIME タイプ・ファイルシグネチャ・サイズを OpenAI 呼び出し前に検証します。
- **CORS**: 既定で `http://localhost:3000` のみ許可します。
- **レート制限**: ローカル向けのレート制限を実装しています。
- **アクセシビリティ**: キーボード操作、フォーカス表示、色に依存しない状態伝達を要件としています。

## 開発について

本プロジェクトは AI-DLC（AI-Driven Development Life Cycle）方法論に沿って開発されています。
要件・設計・タスクなどのドキュメントは [aidlc-docs/](aidlc-docs/) 配下にまとまっています。

品質チェック（バックエンド）:

```bash
cd backend
uv run ruff check .
uv run mypy app
uv run pytest
```

## 対象外（初期リリース）

ユーザー登録・ログイン、データベースや履歴保存、複数画像の一括処理、画像 URL 入力、
画像編集・生成、OCR 精度保証、人物識別、クラウド配備用 IaC、本番 SLA 保証などは対象外です。
