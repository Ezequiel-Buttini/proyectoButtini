// RED: definimos el contrato de fetchHealth antes de implementarlo.
import { describe, it, expect, vi, afterEach } from "vitest";
import { fetchHealth } from "./healthService";

describe("fetchHealth", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("returns the parsed health payload when the request succeeds", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ status: "ok", database: "connected" }),
      }),
    );

    const result = await fetchHealth();

    expect(result).toEqual({ status: "ok", database: "connected" });
    expect(fetch).toHaveBeenCalledWith("/health");
  });

  it("throws when the backend responds with a non-ok status", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: false, status: 500 }),
    );

    await expect(fetchHealth()).rejects.toThrow("Health check failed");
  });
});
