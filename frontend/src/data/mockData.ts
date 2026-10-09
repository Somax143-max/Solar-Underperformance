import type { DiagnosticDashboardData } from "../types/diagnostic";

export const mockDashboardData: DiagnosticDashboardData = {
  source: "demo",
  plant: {
    id: "PLANT-DEMO-01",
    name: "Solar Plant Alpha",
    location: "Demo Site, India",
    status: "warning",
    capacityKw: 1000,
    lastUpdated: "Demo data",
  },
  metrics: {
    expectedPowerKw: 918,
    actualPowerKw: 742,
    underperformancePercent: 19.2,
    energyLossKwh: 176,
    revenueLoss: 1232,
    currency: "INR",
  },
  powerHistory: [
    { timestamp: "08:00", expectedPowerKw: 280, actualPowerKw: 265 },
    { timestamp: "09:00", expectedPowerKw: 450, actualPowerKw: 421 },
    { timestamp: "10:00", expectedPowerKw: 640, actualPowerKw: 574 },
    { timestamp: "11:00", expectedPowerKw: 790, actualPowerKw: 681 },
    { timestamp: "12:00", expectedPowerKw: 918, actualPowerKw: 742 },
    { timestamp: "13:00", expectedPowerKw: 880, actualPowerKw: 730 },
    { timestamp: "14:00", expectedPowerKw: 760, actualPowerKw: 665 },
    { timestamp: "15:00", expectedPowerKw: 590, actualPowerKw: 535 },
  ],
  diagnosis: {
    id: "DIAG-DEMO-01",
    rootCause: "Possible inverter thermal derating",
    confidencePercent: 91,
    severity: "high",
    affectedAssetId: "INV-02",
    explanation:
      "Illustrative demo diagnosis only. Lower sample output coincides with elevated sample inverter temperature. This is not a verified fault.",
  },
  evidence: [
    {
      id: "EVD-01",
      title: "Elevated inverter temperature",
      description: "Sample INV-02 temperature: 78°C.",
      severity: "high",
      source: "Demo data",
    },
    {
      id: "EVD-02",
      title: "Generation below expected",
      description: "Sample actual power: 742 kW; expected power: 918 kW.",
      severity: "high",
      source: "Demo data",
    },
    {
      id: "EVD-03",
      title: "Inverter output deviation",
      description: "Sample INV-02 output is below peer demo units.",
      severity: "medium",
      source: "Demo data",
    },
  ],
  recommendations: [
    {
      id: "REC-01",
      title: "Inspect INV-02 cooling system",
      description:
        "Review cooling airflow, fan operation, operating conditions, and sensor readings before confirming any hardware fault.",
      priority: "high",
      affectedAssetId: "INV-02",
    },
  ],
  inverters: [
    {
      id: "INV-01",
      expectedPowerKw: 240,
      actualPowerKw: 232,
      temperatureC: 54,
      status: "healthy",
    },
    {
      id: "INV-02",
      expectedPowerKw: 240,
      actualPowerKw: 146,
      temperatureC: 78,
      status: "warning",
    },
    {
      id: "INV-03",
      expectedPowerKw: 240,
      actualPowerKw: 224,
      temperatureC: 57,
      status: "healthy",
    },
    {
      id: "INV-04",
      expectedPowerKw: 198,
      actualPowerKw: 140,
      temperatureC: 69,
      status: "warning",
    },
  ],
};
