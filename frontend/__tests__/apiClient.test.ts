import { ApiClientError, createDescription } from "@/lib/apiClient";

const image = new File([new Uint8Array([0xff, 0xd8, 0xff])], "photo.jpg", {
  type: "image/jpeg",
});

describe("createDescription", () => {
  it("returns a validated successful response", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            description: "猫が窓辺に座っています。",
            detail: "standard",
            model: "gpt-4.1-mini",
            request_id: "request-1",
          }),
          { status: 200, headers: { "Content-Type": "application/json" } },
        ),
      ),
    );

    await expect(createDescription(image, "standard")).resolves.toMatchObject({
      description: "猫が窓辺に座っています。",
      request_id: "request-1",
    });
  });

  it("maps the backend error envelope to ApiClientError", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            error: {
              code: "upstream_timeout",
              message: "OpenAI APIがタイムアウトしました。",
              request_id: "request-2",
            },
          }),
          { status: 504, headers: { "Content-Type": "application/json" } },
        ),
      ),
    );

    const promise = createDescription(image, "brief");
    await expect(promise).rejects.toBeInstanceOf(ApiClientError);
    await expect(promise).rejects.toMatchObject({
      code: "upstream_timeout",
      retryable: true,
      requestId: "request-2",
    });
  });

  it("returns a safe error when the backend is unavailable", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("network")));

    await expect(createDescription(image, "detailed")).rejects.toMatchObject({
      code: "network_error",
      retryable: true,
    });
  });
});
