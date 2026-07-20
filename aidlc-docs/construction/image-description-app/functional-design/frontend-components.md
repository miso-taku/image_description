# フロントエンドコンポーネント

## ImageUploader

- **Props**: `onResult`, `onError`, `disabled`
- **State**: 選択ファイル、プレビューURL、詳細度、送信中フラグ、クライアント検証エラー
- **操作**: クリック選択、ドラッグ＆ドロップ、詳細度選択、生成実行
- **アクセシビリティ**: ラベル付きinput、キーボード操作、フォーカス可視、状態のテキスト表示

## DescriptionResult

- **Props**: `description`, `model`, `detail`, `requestId`
- **操作**: クリップボードコピー、コピー結果通知
- **アクセシビリティ**: `aria-live="polite"` による更新通知

## page

- 上記2コンポーネントとAPIクライアントを統合し、送信前に「画像はOpenAIへ送信される」旨を表示する。
