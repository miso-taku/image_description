# コンポーネント定義

アプリケーションは単一ユニット `image-description-app` を構成する2モジュールから成る。

## バックエンド (FastAPI)

### C-B1 API層 (`app/api`)

- **責務**: HTTPエンドポイントの公開、リクエスト受付、レスポンス整形。
- **公開**: `POST /api/v1/descriptions`、`GET /health`。
- **依存**: 設定、画像検証、AI説明サービス、スキーマ、例外処理。

### C-B2 設定 (`app/core/config.py`)

- **責務**: 環境変数からの設定読み込みと検証。
- **項目**: OpenAI APIキー、モデル、タイムアウト、CORSオリジン、最大サイズ、レート制限、環境種別。
- **依存**: Pydantic Settings。

### C-B3 画像検証 (`app/services/image_validation.py`)

- **責務**: MIMEタイプ、ファイルシグネチャ、サイズ、空チェックの検証。
- **依存**: なし（純粋ロジック）。

### C-B4 AI説明サービス (`app/services/description_service.py`)

- **責務**: 詳細度に応じたプロンプト構築、PydanticAI Agent実行、結果整形。
- **依存**: PydanticAI、設定、スキーマ。

### C-B5 スキーマ (`app/schemas`)

- **責務**: リクエスト、レスポンス、エラー、AI出力のPydanticモデル定義。
- **依存**: Pydantic。

### C-B6 例外処理とロギング (`app/core`)

- **責務**: ドメイン例外、グローバル例外ハンドラー、構造化ロギング、リクエストID。
- **依存**: FastAPI、標準logging。

### C-B7 セキュリティミドルウェア (`app/core/security.py`)

- **責務**: 簡易レート制限、リクエストサイズ制限補助、リクエストIDの付与。

## フロントエンド (Next.js/React)

### C-F1 ページ (`app/page.tsx`)

- **責務**: 画面全体の構成と状態管理。

### C-F2 アップロードコンポーネント (`components/ImageUploader.tsx`)

- **責務**: クリックとドラッグ＆ドロップ、プレビュー、クライアント検証、詳細度選択、実行操作。

### C-F3 結果コンポーネント (`components/DescriptionResult.tsx`)

- **責務**: 説明表示、コピー操作、状態通知、ライブリージョン。

### C-F4 APIクライアント (`lib/apiClient.ts`)

- **責務**: バックエンドへの送信、レスポンスとエラーの型付き処理。

### C-F5 クライアント検証 (`lib/validation.ts`)

- **責務**: MIMEとサイズのクライアント側検証（サーバー検証の重複防御）。
