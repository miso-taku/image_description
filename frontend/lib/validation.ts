const TEN_MEGABYTES = 10 * 1024 * 1024;

export const MAX_IMAGE_BYTES = TEN_MEGABYTES;
export const ACCEPTED_IMAGE_TYPES = [
  "image/jpeg",
  "image/png",
  "image/webp",
] as const;

export function validateImageMetadata(
  file: Pick<File, "size" | "type">,
): string | null {
  if (file.size === 0) {
    return "空の画像ファイルは選択できません。";
  }
  if (file.size > MAX_IMAGE_BYTES) {
    return "画像サイズは10 MB以下にしてください。";
  }
  if (!ACCEPTED_IMAGE_TYPES.includes(file.type as (typeof ACCEPTED_IMAGE_TYPES)[number])) {
    return "JPEG、PNG、WebP形式の画像を選択してください。";
  }
  return null;
}

function startsWith(bytes: Uint8Array, signature: number[]): boolean {
  return signature.every((value, index) => bytes[index] === value);
}

function isWebP(bytes: Uint8Array): boolean {
  return (
    startsWith(bytes, [0x52, 0x49, 0x46, 0x46]) &&
    bytes[8] === 0x57 &&
    bytes[9] === 0x45 &&
    bytes[10] === 0x42 &&
    bytes[11] === 0x50
  );
}

export async function validateImageSignature(file: File): Promise<string | null> {
  const bytes = new Uint8Array(await file.slice(0, 12).arrayBuffer());
  const matchesDeclaredType =
    (file.type === "image/jpeg" && startsWith(bytes, [0xff, 0xd8, 0xff])) ||
    (file.type === "image/png" &&
      startsWith(bytes, [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a])) ||
    (file.type === "image/webp" && isWebP(bytes));

  return matchesDeclaredType
    ? null
    : "画像の内容とファイル形式が一致しません。別の画像を選択してください。";
}

export function formatFileSize(bytes: number): string {
  if (bytes < 1024) {
    return `${bytes} B`;
  }
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
