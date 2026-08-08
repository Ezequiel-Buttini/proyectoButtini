// RED: comportamiento esperado del componente antes de implementarlo.
import { describe, it, expect, vi, afterEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { HealthStatus } from "./HealthStatus";
import * as healthService from "../services/healthService";

describe("HealthStatus", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("shows the backend status once it loads", async () => {
    vi.spyOn(healthService, "fetchHealth").mockResolvedValue({
      status: "ok",
      database: "connected",
    });

    render(<HealthStatus />);

    await waitFor(() =>
      expect(screen.getByText(/status: ok/i)).toBeInTheDocument(),
    );
  });

  it("shows an error message when the check fails", async () => {
    vi.spyOn(healthService, "fetchHealth").mockRejectedValue(
      new Error("Health check failed"),
    );

    render(<HealthStatus />);

    await waitFor(() =>
      expect(screen.getByText(/no se pudo conectar/i)).toBeInTheDocument(),
    );
  });
});
