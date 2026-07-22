"use client";

import { useState } from "react";

import type { DescriptionResponse } from "@/lib/types";

interface DescriptionResultProps {
  result: DescriptionResponse;
}

const DETAIL_LABELS = {
  brief: "短い",
  standard: "標準",
  detailed: "詳細",
} as const;

export function DescriptionResult({ result }: DescriptionResultProps) {
  const [copyStatus, setCopyStatus] = useState<string>("");

  async function copyDescription() {
    try {
      if (!navigator.clipboard) {
        throw new Error("Clipboard API unavailable");
      }
      await navigator.clipboard.writeText(result.description);
      setCopyStatus("説明をクリップボードへコピーしました。 ");
    } catch {
      setCopyStatus("コピーできませんでした。テキストを選択してコピーしてください。");
    }
  }

  return (
    <section className="result-card" aria-labelledby="result-heading">
      <div className="result-heading-row">
        <div>
          <span className="eyebrow">生成結果</span>
          <h2 id="result-heading">画像の説明</h2>
        </div>
        <button
          className="secondary-button"
          type="button"
          onClick={copyDescription}
          data-testid="description-result-copy-button"
        >
          コピー
        </button>
      </div>

      <div className="description-text" aria-live="polite">
        {result.description}
      </div>

      <dl className="result-meta">
        <div>
          <dt>詳しさ</dt>
          <dd>{DETAIL_LABELS[result.detail]}</dd>
        </div>
        <div>
          <dt>モデル</dt>
          <dd>{result.model}</dd>
        </div>
        <div>
          <dt>リクエストID</dt>
          <dd>{result.request_id}</dd>
        </div>
      </dl>

      <p className="copy-status" role="status" aria-live="polite">
        {copyStatus}
      </p>
    </section>
  );
}
