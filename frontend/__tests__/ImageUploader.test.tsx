import { fireEvent, render, screen, waitFor } from "@testing-library/react";

import { ImageUploader } from "@/components/ImageUploader";
import { createDescription } from "@/lib/apiClient";

vi.mock("@/lib/apiClient", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@/lib/apiClient")>();
  return { ...actual, createDescription: vi.fn() };
});

const mockedCreateDescription = vi.mocked(createDescription);

describe("ImageUploader", () => {
  it("starts with standard detail and requires an image", () => {
    render(<ImageUploader onResult={vi.fn()} onError={vi.fn()} />);

    expect(screen.getByTestId("image-uploader-detail-standard")).toBeChecked();
    expect(screen.getByTestId("image-uploader-submit-button")).toBeDisabled();
  });

  it("rejects unsupported files before submission", () => {
    render(<ImageUploader onResult={vi.fn()} onError={vi.fn()} />);
    const file = new File(["text"], "notes.txt", { type: "text/plain" });

    fireEvent.change(screen.getByTestId("image-uploader-file-input"), {
      target: { files: [file] },
    });

    expect(screen.getByRole("alert")).toHaveTextContent("JPEG、PNG、WebP");
    expect(mockedCreateDescription).not.toHaveBeenCalled();
  });

  it("submits a valid image exactly once and returns the result", async () => {
    const result = {
      description: "小さな鳥が枝に止まっています。",
      detail: "standard" as const,
      model: "gpt-4.1-mini",
      request_id: "request-4",
    };
    mockedCreateDescription.mockResolvedValueOnce(result);
    const onResult = vi.fn();
    const file = new File(
      [new Uint8Array([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a])],
      "bird.png",
      { type: "image/png" },
    );

    render(<ImageUploader onResult={onResult} onError={vi.fn()} />);
    fireEvent.change(screen.getByTestId("image-uploader-file-input"), {
      target: { files: [file] },
    });
    fireEvent.click(screen.getByTestId("image-uploader-submit-button"));

    await waitFor(() => {
      expect(mockedCreateDescription).toHaveBeenCalledTimes(1);
      expect(onResult).toHaveBeenCalledWith(result);
    });
  });
});
