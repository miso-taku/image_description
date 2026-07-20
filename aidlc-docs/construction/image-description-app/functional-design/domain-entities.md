# ドメインエンティティ

## DetailLevel (列挙)

| 値         | 説明   |
| ---------- | ------ |
| `brief`    | 短い   |
| `standard` | 標準   |
| `detailed` | 詳細   |

## ValidatedImage

- `data: bytes` — 画像バイト列（メモリ保持のみ）
- `media_type: str` — 検証済みMIMEタイプ
- `size_bytes: int` — サイズ

## ImageDescription (AI出力)

- `description: str` — 日本語の画像説明

## DescriptionResult (API出力)

- `description: str`
- `detail: DetailLevel`
- `model: str`
- `request_id: str`
