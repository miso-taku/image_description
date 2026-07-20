# コンポーネントメソッド

詳細な業務ルールはFunctional Designで定義する。ここではシグネチャと目的を示す。

## C-B1 API層

- `create_description(image: UploadFile, detail: str) -> DescriptionResponse`
  - 目的: 検証後にAI説明サービスを呼び出し結果を返す。
- `health() -> HealthResponse`
  - 目的: アプリ状態とバージョンを返す（課金呼び出しなし）。

## C-B3 画像検証

- `validate_image(filename: str | None, content_type: str | None, data: bytes, max_bytes: int) -> ValidatedImage`
  - 目的: MIME、シグネチャ、サイズ、空チェックを行い、無効時は `InvalidImageError` を送出。
- `detect_media_type(data: bytes) -> str | None`
  - 目的: 先頭バイトから実MIMEタイプを判定。

## C-B4 AI説明サービス

- `build_prompt(detail: DetailLevel) -> str`
  - 目的: 詳細度と安全指針を含む日本語システムプロンプトを構築。
- `describe_image(image: ValidatedImage, detail: DetailLevel, request_id: str) -> ImageDescription`
  - 目的: PydanticAI Agentを実行し構造化結果を得る。外部失敗は `DescriptionServiceError` へ変換。

## C-B5 スキーマ

- `DetailLevel(str, Enum)`: `brief` / `standard` / `detailed`。
- `DescriptionResponse`: `description`, `detail`, `model`, `request_id`。
- `HealthResponse`: `status`, `version`。
- `ErrorResponse`: `error.code`, `error.message`, `error.request_id`。
- `ImageDescription`: PydanticAIの出力型 `description: str`。

## C-F4 APIクライアント

- `requestDescription(file: File, detail: DetailLevel): Promise<DescriptionResult>`
  - 目的: multipart送信、成功・失敗を型付きで返す。

## C-F5 クライアント検証

- `validateFile(file: File): ValidationResult`
  - 目的: MIMEとサイズを検証しユーザー向けメッセージを返す。
