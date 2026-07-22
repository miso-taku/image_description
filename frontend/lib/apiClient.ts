import type {
  ApiErrorBody,
  DescriptionResponse,
  DetailLevel,
} from "./types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ??
  "http://localhost:8000";

const RETRYABLE_CODES = new Set([
  "rate_limited",
  "rate_limited_local",
  "upstream_timeout",
  "upstream_unavailable",
  "internal_error",
]);

export class ApiClientError extends Error {
  readonly code: string;
  readonly requestId?: string | null;
  readonly retryable: boolean;

  constructor(
    message: string,
    code = "network_error",
    requestId?: string | null,
  ) {
    super(message);
    this.name = "ApiClientError";
    this.code = code;
    this.requestId = requestId;
    this.retryable = RETRYABLE_CODES.has(code) || code === "network_error";
  }
}

function isApiErrorBody(value: unknown): value is ApiErrorBody {
  if (!value || typeof value !== "object" || !("error" in value)) {
    return false;
  }
  const error = (value as { error?: unknown }).error;
  return Boolean(
    error &&
      typeof error === "object" &&
      "code" in error &&
      "message" in error &&
      typeof (error as { code: unknown }).code === "string" &&
      typeof (error as { message: unknown }).message === "string",
  );
}

function isDescriptionResponse(value: unknown): value is DescriptionResponse {
  if (!value || typeof value !== "object") {
    return false;
  }
  const candidate = value as Record<string, unknown>;
  return (
    typeof candidate.description === "string" &&
    typeof candidate.detail === "string" &&
    typeof candidate.model === "string" &&
    typeof candidate.request_id === "string"
  );
}

export async function createDescription(
  image: File,
  detail: DetailLevel,
  signal?: AbortSignal,
): Promise<DescriptionResponse> {
  const formData = new FormData();
  formData.append("image", image, image.name);
  formData.append("detail", detail);

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/api/v1/descriptions`, {
      method: "POST",
      body: formData,
      signal,
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ApiClientError("処理を中止しました。", "aborted");
    }
    throw new ApiClientError(
      "バックエンドへ接続できません。起動状態を確認して再試行してください。",
    );
  }

  let payload: unknown;
  try {
    payload = await response.json();
  } catch {
    throw new ApiClientError(
      "サーバーから解釈できない応答を受信しました。",
      "invalid_response",
    );
  }

  if (!response.ok) {
    if (isApiErrorBody(payload)) {
      throw new ApiClientError(
        payload.error.message,
        payload.error.code,
        payload.error.request_id,
      );
    }
    throw new ApiClientError(
      "画像説明の生成に失敗しました。時間をおいて再試行してください。",
      "unknown_error",
    );
  }

  if (!isDescriptionResponse(payload)) {
    throw new ApiClientError(
      "サーバー応答の形式が正しくありません。",
      "invalid_response",
    );
  }

  return payload;
}
