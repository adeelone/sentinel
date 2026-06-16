import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { App } from "./App";

describe("App", () => {
  it("renders dashboard sections", () => {
    render(<App />);
    expect(screen.getByText("Fraud operations dashboard")).toBeTruthy();
    expect(screen.getByText("Triage queue")).toBeTruthy();
  });
});

