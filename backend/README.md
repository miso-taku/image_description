# 画像説明生成バックエンド (Image Description Backend)

アップロードされた画像の日本語説明文を OpenAI API で生成する、FastAPI + PydanticAI 製のバックエンドです。

## 必要要件

- Python 3.12.8（uv が自動でインストール可能）
- uv
- OpenAI API キー（実際に説明文を生成する場合のみ必要。テストスイートは API を呼び出しません）

## セットアップ

```bash
cd backend
uv sync --extra dev
cp .env.example .env   # その後 .env を編集して OPENAI_API_KEY を設定
```

Windows PowerShell では `Copy-Item .env.example .env` を使用してください。

## 起動方法

```bash
uv run uvicorn app.main:app --reload --port 8000
```

- API ドキュメント: http://localhost:8000/docs
- ヘルスチェック: http://localhost:8000/health

## 品質チェック

```bash
uv run ruff check .
uv run mypy app
uv run pytest
```

## API

### POST /api/v1/descriptions

`multipart/form-data`:

- `image`: JPEG、PNG、WebP のいずれか（最大 10 MB）
- `detail`: `brief`（簡潔） | `standard`（標準） | `detailed`（詳細）

レスポンスは JSON `{ description, detail, model, request_id }`、
エラー時はエラーエンベロープ `{ error: { code, message, request_id } }` を返します。

## 環境変数

`.env.example` を `.env` にコピーして設定します（`.env` はコミットしないでください）。

| 変数名 | デフォルト値 | 説明 |
|--------|--------------|------|
| `OPENAI_API_KEY` | （空） | OpenAI API キー。実際の説明文生成に必須 |
| `OPENAI_MODEL` | `gpt-4.1-mini` | 使用する Vision 対応 OpenAI モデル |
| `OPENAI_TIMEOUT_SECONDS` | `60` | OpenAI リクエストのタイムアウト秒数 |
| `MAX_IMAGE_BYTES` | `10485760` | 受け付ける画像の最大サイズ（バイト、既定 10 MB） |
| `CORS_ALLOW_ORIGINS` | `http://localhost:3000` | 許可する CORS オリジン（カンマ区切り） |
| `RATE_LIMIT_REQUESTS` | `60` | レートリミットのリクエスト数上限 |
| `RATE_LIMIT_WINDOW_SECONDS` | `60` | レートリミットの時間窓（秒） |
| `ENVIRONMENT` | `development` | 実行環境名 |
| `APP_VERSION` | `0.1.0` | アプリケーションのバージョン |

## 補足事項

- OpenAI API キーは環境変数からのみ読み込まれ、ログには一切出力されません。
- 画像および生成された説明文はメモリ上でのみ処理され、永続化されません。
- デフォルトのモデルは `gpt-4.1-mini` です（`OPENAI_MODEL` で変更可能）。
