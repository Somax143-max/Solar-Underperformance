export type Severity = "low" | "medium" | "high" | "critical";

export type PlantStatus = "operational" | "warning" | "offline";

export type DataSource = "demo" | "api";

export interface PlantInfo {
  id: string;
  name: string;
  location: string;
  status: PlantStatus;
  capacityKw: number;
  lastUpdated: string;
}

export interface PerformanceMetrics {
  expectedPowerKw: number;
  actualPowerKw: number;
  underperformancePercent: number;
  energyLossKwh: number;
  revenueLoss: number;
  currency: string;
}

export interface PowerHistoryPoint {
  timestamp: string;
  expectedPowerKw: number;
  actualPowerKw: number;
}

export interface Diagnosis {
  id: string;
  rootCause: string;
  confidencePercent: number;
  severity: Severity;
  affectedAssetId: string;
  explanation: string;
}

export interface DiagnosticEvidence {
  id: string;
  title: string;
  description: string;
  severity: Severity;
  source?: string;
}

export interface Recommendation {
  id: string;
  title: string;
  description: string;
  priority: Severity;
  affectedAssetId: string;
}

export interface InverterStatus {
  id: string;
  expectedPowerKw: number;
  actualPowerKw: number;
  temperatureC: number;
  status: "healthy" | "warning" | "offline";
}

export interface DiagnosticDashboardData {
  source: DataSource;
  plant: PlantInfo;
  metrics: PerformanceMetrics;
  powerHistory: PowerHistoryPoint[];
  diagnosis: Diagnosis | null;
  evidence: DiagnosticEvidence[];
  recommendations: Recommendation[];
  inverters: InverterStatus[];
}
