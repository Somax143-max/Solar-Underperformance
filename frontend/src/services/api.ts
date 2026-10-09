import { mockDashboardData } from "../data/mockData";
import type { DiagnosticDashboardData } from "../types/diagnostic";

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"
).replace(/\/+$/, "");

export interface DiagnosisRequest {
  plant_capacity_kw: number;
  irradiance_poa_wm2: number;
  module_temperature_c: number;
  actual_power_kw: number;
  inverter_temperature_c: number;
  sustained_decline?: boolean;
  stable_irradiance?: boolean;
  repeated_time_pattern?: boolean;
  sufficient_irradiance?: boolean;
  reference_irradiance_wm2?: number | null;
  reference_expected_power_kw?: number | null;
  target_string?: string | null;
  target_string_current_a?: number | null;
  peer_string_currents_a?: number[] | null;
}

export interface DiagnosisApiResponse {
  expected_power_kw: number;
  actual_power_kw: number;
  power_gap_kw: number;
  underperformance_percent: number;
  root_cause: string;
  confidence: number;
  evidence: string[];
  recommendation: string;
}

async function requestJson<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: {
        Accept: "application/json",
        ...options.headers,
      },
    });
  } catch {
    throw new Error(
      "Cannot reach the solar diagnostic backend. Start the FastAPI server and check its address.",
    );
  }

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(
      `Backend request failed (${response.status}): ${
        detail || response.statusText
      }`,
    );
  }

  return (await response.json()) as T;
}

export async function getDashboardData(): Promise<DiagnosticDashboardData> {
  const dashboardUrl = import.meta.env.VITE_DASHBOARD_URL as
    | string
    | undefined;

  // No dashboard endpoint has been confirmed yet, so use clearly labelled
  // sample data instead of pretending the diagnostic endpoint supplies it.
  if (!dashboardUrl) {
    return mockDashboardData;
  }

  const response = await requestJson<DiagnosticDashboardData>(
    dashboardUrl,
  );

  return { ...response, source: "api" };
}

export async function checkBackendHealth(): Promise<{
  status: string;
  service: string;
}> {
  return requestJson("/health");
}

export async function runDiagnosis(
  input: DiagnosisRequest,
): Promise<DiagnosisApiResponse> {
  return requestJson("/api/v1/diagnostics", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(input),
  });
}
