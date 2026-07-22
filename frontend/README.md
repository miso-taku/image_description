# Image Description Frontend

Next.js、React、TypeScriptで構築した画像説明生成アプリのフロントエンドです。

## セットアップ

```bash
npm install
Copy-Item .env.local.example .env.local
npm run dev
```

ブラウザで `http://localhost:3000` を開きます。バックエンドは既定で
`http://localhost:8000` を使用します。

## 品質チェック

```bash
npm run lint
npm run typecheck
npm test
npm run build
```

画像はブラウザからFastAPIバックエンドを経由してOpenAI APIへ送信されます。
このフロントエンドは画像や生成結果を永続保存しません。
