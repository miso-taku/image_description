# NFR要件と技術選定

## 技術スタック決定

| 項目             | 選定                          | 理由                                   |
| ---------------- | ----------------------------- | -------------------------------------- |
| 言語(BE)         | Python 3.12.8                 | 要求指定                               |
| パッケージ管理   | uv + uv.lock                  | 要求指定、依存固定 (SECURITY-10)       |
| Webフレームワーク | FastAPI                       | 要求指定、検証と型に強い               |
| データ検証       | Pydantic v2 / Pydantic Settings | 要求指定、設定と入力検証             |
| AI連携           | PydanticAI                    | 要求指定、構造化出力とマルチモーダル   |
| AIプロバイダー   | OpenAI Responses API          | 要求指定、画像入力対応                 |
| 既定モデル       | gpt-4.1-mini（設定可能）      | 画像対応かつ品質とコストのバランス     |
| 言語(FE)         | TypeScript                    | 型安全                                 |
| FEフレームワーク | Next.js (App Router) + React  | 要求指定                               |
| BEテスト         | pytest + httpx + pytest-asyncio | API/単体テスト                       |
| PBT              | Hypothesis                    | Python向けPBT (PBT-09)                 |
| FEテスト         | Vitest + Testing Library      | コンポーネント/フローテスト            |
| Lint/型(BE)      | Ruff + mypy                   | 品質                                   |
| Lint/型(FE)      | ESLint + tsc                  | 品質                                   |

## 性能

- 最大リクエストサイズをASGIレベルおよびアプリ検証で制限。
- OpenAI呼び出しに構成可能タイムアウト（既定60秒）。
- ローカル向けレート制限（既定 60 req/分/IP）。

## セキュリティ (該当ルール)

- SECURITY-03 構造化ログ、機密情報除外。
- SECURITY-04 フロントのセキュリティヘッダー。
- SECURITY-05 入力検証（型、サイズ、シグネチャ、列挙）。
- SECURITY-08 CORSを単一オリジンへ制限、ローカル公開の明示。
- SECURITY-09 安全なエラー、不要な永続化なし。
- SECURITY-10 lockfile、脆弱性スキャン、SBOM手順。
- SECURITY-11 検証多層化、レート制限、悪用ケース。
- SECURITY-13 スキーマ・ファイル検証後に処理。
- SECURITY-15 例外処理とグローバルハンドラー、フェイルクローズ。

## テスト (PBT-09)

- HypothesisをPython依存に追加。
- 縮小を無効化しない (PBT-08)。
- CIまたはテスト手順でseedを記録可能にする (PBT-08)。
