import { fireEvent, render, screen, waitFor } from "@testing-library/react";

import { DescriptionResult } from "@/components/DescriptionResult";

describe("DescriptionResult", () => {
  it("announces the result and copies the description", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, "clipboard", {
      configurable: true,
      value: { writeText },
    });

    render(
      <DescriptionResult
        result={{
          description: "海辺を犬が走っています。",
          detail: "brief",
          model: "gpt-4.1-mini",
          request_id: "request-3",
        }}
      />,
    );

    expect(screen.getByText("海辺を犬が走っています。")).toBeInTheDocument();
    fireEvent.click(screen.getByTestId("description-result-copy-button"));

    await waitFor(() => {
      expect(writeText).toHaveBeenCalledWith("海辺を犬が走っています。");
      expect(screen.getByRole("status")).toHaveTextContent("コピーしました");
    });
  });
});
