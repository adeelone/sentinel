import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { App } from "./App";

describe("App", () => {
  it("renders dashboard sections", () => {
    render(<App />);
    expect(screen.getByRole("heading", { name: "Score a transaction", level: 1 })).toBeTruthy();
    expect(screen.getByRole("heading", { name: "Review queue" })).toBeTruthy();
  });
});
