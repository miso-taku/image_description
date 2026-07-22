"use client";

import Image from "next/image";
import {
  type ChangeEvent,
  type DragEvent,
  type FormEvent,
  useEffect,
  useId,
  useRef,
  useState,
} from "react";

import { ApiClientError, createDescription } from "@/lib/apiClient";
import type { DescriptionResponse, DetailLevel } from "@/lib/types";
import {
  formatFileSize,
  validateImageMetadata,
  validateImageSignature,
} from "@/lib/validation";

interface ImageUploaderProps {
  onResult: (result: DescriptionResponse) => void;
  onError: (message: string | null) => void;
  disabled?: boolean;
}

interface SelectedImage {
  file: File;
  previewUrl: string;
}

const DETAIL_OPTIONS: Array<{
  value: DetailLevel;
  label: string;
  description: string;
}> = [
  { value: "brief", label: "短い", description: "主要な内容を1〜2文で説明" },
  { value: "standard", label: "標準", description: "被写体や背景を簡潔な段落で説明" },
  { value: "detailed", label: "詳細", description: "位置関係や雰囲気まで詳しく説明" },
];

export function ImageUploader({
  onResult,
  onError,
  disabled = false,
}: ImageUploaderProps) {
  const inputId = useId();
  const [selected, setSelected] = useState<SelectedImage | null>(null);
  const [detail, setDetail] = useState<DetailLevel>("standard");
  const [localError, setLocalError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const previewUrlRef = useRef<string | null>(null);

  useEffect(() => {
    return () => {
      if (previewUrlRef.current) {
        URL.revokeObjectURL(previewUrlRef.current);
      }
    };
  }, []);

  function clearSelection() {
    if (previewUrlRef.current) {
      URL.revokeObjectURL(previewUrlRef.current);
      previewUrlRef.current = null;
    }
    setSelected(null);
  }

  function selectFile(nextFile: File | null) {
    if (!nextFile) {
      return;
    }
    const error = validateImageMetadata(nextFile);
    setLocalError(error);
    onError(error);
    if (error) {
      clearSelection();
      return;
    }
    if (previewUrlRef.current) {
      URL.revokeObjectURL(previewUrlRef.current);
    }
    const previewUrl = URL.createObjectURL(nextFile);
    previewUrlRef.current = previewUrl;
    setSelected({ file: nextFile, previewUrl });
  }

  function handleChange(event: ChangeEvent<HTMLInputElement>) {
    selectFile(event.target.files?.[0] ?? null);
    event.target.value = "";
  }

  function handleDragOver(event: DragEvent<HTMLLabelElement>) {
    event.preventDefault();
    if (!disabled && !isSubmitting) {
      setIsDragging(true);
    }
  }

  function handleDrop(event: DragEvent<HTMLLabelElement>) {
    event.preventDefault();
    setIsDragging(false);
    if (!disabled && !isSubmitting) {
      selectFile(event.dataTransfer.files?.[0] ?? null);
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selected || disabled || isSubmitting) {
      const message = selected ? null : "説明する画像を選択してください。";
      setLocalError(message);
      onError(message);
      return;
    }

    setIsSubmitting(true);
    setLocalError(null);
    onError(null);

    try {
      const signatureError = await validateImageSignature(selected.file);
      if (signatureError) {
        setLocalError(signatureError);
        onError(signatureError);
        return;
      }
      const result = await createDescription(selected.file, detail);
      onResult(result);
    } catch (error) {
      const message =
        error instanceof ApiClientError
          ? `${error.message}${error.retryable ? " 再試行できます。" : ""}`
          : "予期しないエラーが発生しました。再試行してください。";
      setLocalError(message);
      onError(message);
    } finally {
      setIsSubmitting(false);
    }
  }

  const controlsDisabled = disabled || isSubmitting;

  return (
    <form className="upload-card" onSubmit={handleSubmit}>
      <div className="section-heading">
        <span className="step-number" aria-hidden="true">1</span>
        <div>
          <h2>画像を選択</h2>
          <p>JPEG、PNG、WebP形式・10 MB以下</p>
        </div>
      </div>

      <label
        className={`drop-zone${isDragging ? " is-dragging" : ""}`}
        htmlFor={inputId}
        onDragEnter={handleDragOver}
        onDragOver={handleDragOver}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        data-testid="image-uploader-drop-zone"
      >
        <input
          id={inputId}
          className="visually-hidden"
          type="file"
          accept="image/jpeg,image/png,image/webp"
          onChange={handleChange}
          disabled={controlsDisabled}
          data-testid="image-uploader-file-input"
        />
        <span className="upload-icon" aria-hidden="true">↑</span>
        <strong>画像をドラッグ＆ドロップ</strong>
        <span>またはクリックしてファイルを選択</span>
      </label>

      {selected ? (
        <div className="selected-image" data-testid="image-uploader-preview">
          <div className="preview-frame">
            <Image
              src={selected.previewUrl}
              alt={`選択した画像: ${selected.file.name}`}
              fill
              sizes="(max-width: 720px) 90vw, 560px"
              unoptimized
            />
          </div>
          <div className="file-meta">
            <strong>{selected.file.name}</strong>
            <span>{formatFileSize(selected.file.size)}</span>
          </div>
        </div>
      ) : null}

      {localError ? (
        <p className="inline-error" role="alert">{localError}</p>
      ) : null}

      <fieldset className="detail-fieldset" disabled={controlsDisabled}>
        <legend>
          <span className="step-number" aria-hidden="true">2</span>
          説明の詳しさ
        </legend>
        <div className="detail-options">
          {DETAIL_OPTIONS.map((option) => (
            <label className="detail-option" key={option.value}>
              <input
                type="radio"
                name="detail"
                value={option.value}
                checked={detail === option.value}
                onChange={() => setDetail(option.value)}
                data-testid={`image-uploader-detail-${option.value}`}
              />
              <span>
                <strong>{option.label}</strong>
                <small>{option.description}</small>
              </span>
            </label>
          ))}
        </div>
      </fieldset>

      <div className="privacy-note">
        <span aria-hidden="true">ⓘ</span>
        <p>
          生成を実行すると、選択した画像は説明作成のためOpenAI APIへ送信されます。
          アプリケーション自身は画像や説明を保存しません。
        </p>
      </div>

      <button
        className="primary-button"
        type="submit"
        disabled={controlsDisabled || !selected}
        data-testid="image-uploader-submit-button"
      >
        {isSubmitting ? "説明を生成中…" : "画像の説明を生成"}
      </button>

      <p className="submit-status" role="status" aria-live="polite">
        {isSubmitting ? "画像を安全に送信し、説明を生成しています。" : ""}
      </p>
    </form>
  );
}
