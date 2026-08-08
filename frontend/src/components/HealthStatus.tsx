import { useEffect, useState } from "react";
import { fetchHealth, type HealthStatus as HealthStatusData } from "../services/healthService";

export function HealthStatus() {
  const [health, setHealth] = useState<HealthStatusData | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    fetchHealth()
      .then(setHealth)
      .catch(() => setError(true));
  }, []);

  if (error) {
    return <p>No se pudo conectar con el backend.</p>;
  }

  if (!health) {
    return <p>Verificando estado del backend...</p>;
  }

  return (
    <p>
      Status: {health.status} (database: {health.database})
    </p>
  );
}
