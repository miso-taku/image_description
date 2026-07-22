"use client";

import { useState } from "react";

import { DescriptionResult } from "@/components/DescriptionResult";
import { ImageUploader } from "@/components/ImageUploader";
import type { DescriptionResponse } from "@/lib/types";

export default function Home() {
  const [result, setResult] = useState<DescriptionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  function handleResult(nextResult: DescriptionResponse) {
    setResult(nextResult);
    setError(null);
  }

  return (
    <main>
      <header className="hero">
        <div className="brand-mark" aria-hidden="true">視</div>
        <p className="eyebrow">AI IMAGE DESCRIPTION</p>
        <h1>画像を、ことばに。</h1>
        <p className="hero-copy">
          画像を1枚選ぶだけで、内容を分かりやすい日本語で説明します。
        </p>
      </header>

      <div className="content-grid">
        <ImageUploader onResult={handleResult} onError={setError} />

        {error ? (
          <aside className="page-error" role="alert" aria-live="assertive">
            <strong>説明を生成できませんでした</strong>
            <span>{error}</span>
          </aside>
        ) : null}

        {result ? <DescriptionResult result={result} /> : (
          <section className="empty-result" aria-label="生成結果">
            <div aria-hidden="true">✦</div>
            <p>画像の説明はここに表示されます。</p>
          </section>
        )}
      </div>

      <footer>
        <p>画像と生成結果はこのアプリケーションに保存されません。</p>
      </footer>
    </main>
  );
}
