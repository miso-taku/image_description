import {
  MAX_IMAGE_BYTES,
  formatFileSize,
  validateImageMetadata,
  validateImageSignature,
} from "@/lib/validation";

describe("validateImageMetadata", () => {
  it("accepts a supported image within the size limit", () => {
    expect(validateImageMetadata({ size: 1024, type: "image/png" })).toBeNull();
  });

  it("rejects empty, oversized, and unsupported files", () => {
    expect(validateImageMetadata({ size: 0, type: "image/png" })).toContain("空");
    expect(
      validateImageMetadata({ size: MAX_IMAGE_BYTES + 1, type: "image/jpeg" }),
    ).toContain("10 MB");
    expect(validateImageMetadata({ size: 10, type: "image/gif" })).toContain(
      "JPEG、PNG、WebP",
    );
  });
});

describe("validateImageSignature", () => {
  it("accepts a PNG whose signature matches its declared MIME type", async () => {
    const file = new File(
      [new Uint8Array([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a])],
      "sample.png",
      { type: "image/png" },
    );
    await expect(validateImageSignature(file)).resolves.toBeNull();
  });

  it("rejects mismatched content", async () => {
    const file = new File([new Uint8Array([1, 2, 3, 4])], "fake.png", {
      type: "image/png",
    });
    await expect(validateImageSignature(file)).resolves.toContain("一致しません");
  });
});

describe("formatFileSize", () => {
  it("formats byte, KB, and MB values", () => {
    expect(formatFileSize(12)).toBe("12 B");
    expect(formatFileSize(1536)).toBe("1.5 KB");
    expect(formatFileSize(2 * 1024 * 1024)).toBe("2.0 MB");
  });
});
