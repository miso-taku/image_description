# NFR設計パターン

## セキュリティヘッダー (SECURITY-04)

Next.jsの `next.config` で全HTML応答に付与する。

- `Content-Security-Policy`: `default-src 'self'; img-src 'self' data: blob:; connect-src 'self' http://localhost:8000; style-src 'self' 'unsafe-inline'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'`
- `Strict-Transport-Security`: `max-age=31536000; includeSubDomains`
- `X-Content-Type-Options`: `nosniff`
- `X-Frame-Options`: `DENY`
- `Referrer-Policy`: `strict-origin-when-cross-origin`

CSPで `unsafe-eval` は使用しない。`style-src` の `unsafe-inline` はNext.jsの制約に対する限定的許容として記録する。

## 例外処理とフェイルクローズ (SECURITY-15)

- ドメイン例外階層 `AppError` を定義。
- FastAPIの例外ハンドラーで `AppError` と未処理例外を `ErrorResponse` へ変換。
- 未処理例外は500かつ汎用メッセージ、詳細はサーバーログのみ。
- 外部呼び出しは必ずtry/exceptで捕捉し、フェイルクローズ。

## レート制限 (SECURITY-11)

- IP単位のインメモリ・スライディングウィンドウ制限。
- 超過時は429 `rate_limited_local`。
- ローカル用途向けの軽量実装であることを明記。

## ロギング (SECURITY-03)

- JSON構造化ログ（timestamp, level, message, request_id）。
- 画像バイト列、説明本文、APIキー、Authorizationを出力しない。
- OpenAI呼び出しの結果種別と所要時間のみ記録。

## 論理コンポーネント

- 追加のキューやキャッシュは不要（ローカル同期処理）。
