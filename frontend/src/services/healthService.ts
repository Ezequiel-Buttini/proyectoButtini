export interface HealthStatus {
  status: "ok" | "degraded";
  database: "connected" | "disconnected";
}

export async function fetchHealth(): Promise<HealthStatus> {
  const response = await fetch("/health");

  if (!response.ok) {
    throw new Error("Health check failed");
  }

  return response.json();
}
