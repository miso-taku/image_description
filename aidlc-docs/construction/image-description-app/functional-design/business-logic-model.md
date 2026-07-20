# 業務ロジックモデル

## 説明生成フロー

```text
receive(image, detail)
  -> generate request_id (server-side)
  -> validate detail (enum)
  -> read bytes (bounded by max size)
  -> validate_image(bytes): media type + signature + size + non-empty
  -> build_prompt(detail)
  -> agent.run([prompt, BinaryContent(bytes, media_type)]) with timeout
  -> map result -> DescriptionResponse
  -> on any external failure -> domain error -> ErrorResponse
```

## テスト可能プロパティ (PBT-01)

| コンポーネント | プロパティ | カテゴリ |
| -------------- | ---------- | -------- |
| 画像検証       | サイズ境界の受理/拒否 | Invariant |
| 画像検証       | シグネチャ→MIME判定    | Invariant |
| APIスキーマ    | JSONシリアライズ往復   | Round-trip |
| 詳細度         | 列挙の受理/拒否        | Invariant |

AIエージェント呼び出し自体は外部依存のためPBT対象外（N/A）とし、モックで例ベーステストする。
