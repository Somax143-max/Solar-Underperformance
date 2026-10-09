import { useEffect, useState } from "react";
import {
  Activity,
  AlertTriangle,
  ArrowDownRight,
  ArrowUpRight,
  BatteryCharging,
  CheckCircle2,
  Clock3,
  Sun,
  Zap,
} from "lucide-react";
import type { ReactNode } from "react";
import { getDashboardData } from "../../services/api";
import type {
  DiagnosticDashboardData,
  InverterStatus,
} from "../../types/diagnostic";

function formatNumber(value: number): string {
  return new Intl.NumberFormat("en-IN", {
    maximumFractionDigits: 1,
  }).format(value);
}

function MetricCard({
  label,
  value,
  unit,
  detail,
  icon,
  warning = false,
}: {
  label: string;
  value: string;
  unit?: string;
  detail: string;
  icon: ReactNode;
  warning?: boolean;
}) {
  return (
    <section className="metric-card">
      <div className="metric-top">
        <span className="metric-label">{label}</span>
        <span className={`metric-icon ${warning ? "metric-icon-warning" : ""}`}>
          {icon}
        </span>
      </div>
      <div className="metric-value">
        {value}<span>{unit}</span>
      </div>
      <div className={`metric-detail ${warning ? "warning-text" : ""}`}>
        {warning ? <ArrowDownRight size={15} /> : <ArrowUpRight size={15} />}
        {detail}
      </div>
    </section>
  );
}

function InverterRow({ inverter }: { inverter: InverterStatus }) {
  const healthy = inverter.status === "healthy";

  return (
    <div className="inverter-row">
      <div className={`inverter-icon ${healthy ? "" : "inverter-icon-alert"}`}>
        {healthy ? <CheckCircle2 size={18} /> : <AlertTriangle size={18} />}
      </div>
      <div className="inverter-name">
        <strong>{inverter.id}</strong>
        <span>
          {formatNumber(inverter.actualPowerKw)} /{" "}
          {formatNumber(inverter.expectedPowerKw)} kW
        </span>
      </div>
      <span className="inverter-temp">{inverter.temperatureC}°C</span>
      <span className={`inverter-status ${healthy ? "healthy" : "review"}`}>
        {healthy ? "Healthy" : inverter.status === "offline" ? "Offline" : "Review"}
      </span>
    </div>
  );
}

function LoadingState() {
  return (
    <main className="dashboard">
      <section className="panel" style={{ marginTop: 40 }}>
        <h2>Loading solar diagnostics…</h2>
        <p>Please wait while dashboard data is retrieved.</p>
      </section>
    </main>
  );
}

function ErrorState({ message, retry }: { message: string; retry: () => void }) {
  return (
    <main className="dashboard">
      <section className="panel" style={{ marginTop: 40 }}>
        <h2>Dashboard data could not be loaded</h2>
        <p>{message}</p>
        <button
          type="button"
          onClick={retry}
          style={{
            background: "#0f766e",
            color: "white",
            border: 0,
            borderRadius: 8,
            padding: "10px 16px",
            marginTop: 12,
          }}
        >
          Try again
        </button>
      </section>
    </main>
  );
}

export default function Dashboard() {
  const [data, setData] = useState<DiagnosticDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let active = true;

    async function loadDashboard() {
      setLoading(true);
      setError(null);

      try {
        const result = await getDashboardData();
        if (active) setData(result);
      } catch (err) {
        if (active) {
          setError(
            err instanceof Error ? err.message : "An unexpected error occurred.",
          );
        }
      } finally {
        if (active) setLoading(false);
      }
    }

    void loadDashboard();

    return () => {
      active = false;
    };
  }, [reloadKey]);

  if (loading && !data) return <LoadingState />;

  if (error && !data) {
    return (
      <ErrorState
        message={error}
        retry={() => setReloadKey((current) => current + 1)}
      />
    );
  }

  if (!data) return null;

  const { plant, metrics, powerHistory, diagnosis, evidence, recommendations, inverters } = data;
  const isDemo = data.source === "demo";
  const currency = metrics.currency || "INR";
  const topRecommendation = recommendations[0];

  return (
    <main className="dashboard">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark"><Sun size={23} /></div>
          <div>
            <h1>Solar Diagnostic</h1>
            <p>PERFORMANCE COMMAND CENTER</p>
          </div>
        </div>
        <div className="topbar-right">
          <span className="demo-pill"><span /> {isDemo ? "DEMO DATA" : "API DATA"}</span>
          <span className="date-label"><Clock3 size={15} /> {plant.lastUpdated}</span>
        </div>
      </header>

      <section className="page-heading">
        <div>
          <p className="eyebrow">PLANT OVERVIEW / MONITORING</p>
          <h2>Solar plant performance</h2>
          <p className="page-description">
            Monitor generation, investigate possible losses, and review diagnostic evidence.
          </p>
        </div>
        <div className="plant-selector">
          <span className="plant-dot" />
          <div>
            <small>SELECTED PLANT</small>
            <strong>{plant.name}</strong>
          </div>
          <span className="capacity-tag">
            {formatNumber(plant.capacityKw / 1000)} MW
          </span>
        </div>
      </section>

      <section className="status-banner">
        <div className="status-symbol">
          {plant.status === "operational" ? (
            <CheckCircle2 size={21} />
          ) : (
            <AlertTriangle size={21} />
          )}
        </div>
        <div className="status-copy">
          <strong>
            {isDemo
              ? "Performance readings are illustrative demo data"
              : error
                ? "Latest refresh failed; showing previously loaded data"
                : plant.status === "operational"
                  ? "Plant status: operational"
                  : plant.status === "offline"
                    ? "Plant status: offline"
                    : "Plant status requires review"}
          </strong>
          <span>
            {isDemo
              ? "Do not interpret this sample as a verified plant fault or a live measurement."
              : `${plant.location} · Confirm important findings against plant telemetry.`}
          </span>
        </div>
        <span className="status-label">
          {isDemo ? "DEMO MODE" : plant.status.toUpperCase()}
        </span>
      </section>

      {error && data && (
        <section className="recommendation-note" style={{ marginBottom: 16 }}>
          <AlertTriangle size={16} />
          <span>Refresh error: {error}. Showing the last successfully loaded data.</span>
          <button
            type="button"
            onClick={() => setReloadKey((current) => current + 1)}
          >
            Retry
          </button>
        </section>
      )}

      <section className="metric-grid">
        <MetricCard
          label="Actual power"
          value={formatNumber(metrics.actualPowerKw)}
          unit=" kW"
          detail={`${formatNumber(metrics.underperformancePercent)}% below expected`}
          icon={<Zap size={20} />}
          warning={metrics.underperformancePercent > 0}
        />
        <MetricCard
          label="Expected power"
          value={formatNumber(metrics.expectedPowerKw)}
          unit=" kW"
          detail="Reference generation"
          icon={<Sun size={20} />}
        />
        <MetricCard
          label="Estimated energy loss"
          value={formatNumber(metrics.energyLossKwh)}
          unit=" kWh"
          detail={`Estimated value: ${currency} ${formatNumber(metrics.revenueLoss)}`}
          icon={<BatteryCharging size={20} />}
          warning={metrics.energyLossKwh > 0}
        />
        <MetricCard
          label="Plant capacity"
          value={formatNumber(plant.capacityKw)}
          unit=" kW"
          detail={plant.location}
          icon={<Activity size={20} />}
        />
      </section>

      <section className="content-grid">
        <article className="panel power-panel">
          <div className="panel-heading">
            <div>
              <h3>Power performance</h3>
              <p>Expected versus actual generation</p>
            </div>
            <span className="demo-tag">{isDemo ? "SAMPLE SERIES" : "API SERIES"}</span>
          </div>

          <div className="chart-legend">
            <span><i className="legend-expected" /> Expected power</span>
            <span><i className="legend-actual" /> Actual power</span>
          </div>

          <div
            className="bar-chart"
            role="img"
            aria-label="Expected and actual power comparison"
          >
            {powerHistory.map((point) => {
              const maxPower = Math.max(
                1,
                ...powerHistory.map((item) =>
                  Math.max(item.expectedPowerKw, item.actualPowerKw),
                ),
              );

              return (
                <div className="bar-group" key={point.timestamp}>
                  <div className="bars">
                    <div
                      className="bar expected-bar"
                      style={{ height: `${(point.expectedPowerKw / maxPower) * 100}%` }}
                      title={`Expected: ${point.expectedPowerKw} kW`}
                    />
                    <div
                      className="bar actual-bar"
                      style={{ height: `${(point.actualPowerKw / maxPower) * 100}%` }}
                      title={`Actual: ${point.actualPowerKw} kW`}
                    />
                  </div>
                  <span>{point.timestamp}</span>
                </div>
              );
            })}
          </div>
          <div className="chart-footnote">
            <span>{isDemo ? "Illustrative data only" : "Data received from API"}</span>
            <span>Power (kW)</span>
          </div>
        </article>

        <article className="panel diagnosis-panel">
          <div className="panel-heading">
            <div>
              <h3>Diagnostic insight</h3>
              <p>{isDemo ? "Example result — not a verified diagnosis" : "Backend diagnostic result"}</p>
            </div>
            {diagnosis && (
              <span className="severity-pill">{diagnosis.severity.toUpperCase()}</span>
            )}
          </div>

          {diagnosis ? (
            <>
              <div className="diagnosis-icon"><Activity size={23} /></div>
              <h4>{diagnosis.rootCause}</h4>
              <p className="diagnosis-description">{diagnosis.explanation}</p>
              <div className="confidence-row">
                <span>{isDemo ? "Demo confidence score" : "Diagnostic confidence"}</span>
                <strong>{formatNumber(diagnosis.confidencePercent)}%</strong>
              </div>
              <div className="confidence-track">
                <div style={{ width: `${Math.max(0, Math.min(100, diagnosis.confidencePercent))}%` }} />
              </div>
              <div className="asset-row">
                <span>Affected asset</span><strong>{diagnosis.affectedAssetId}</strong>
              </div>
            </>
          ) : (
            <p className="diagnosis-description">
              No diagnosis is available for the current data.
            </p>
          )}
        </article>
      </section>

      <section className="content-grid lower-grid">
        <article className="panel">
          <div className="panel-heading">
            <div>
              <h3>Inverter health</h3>
              <p>{isDemo ? "Illustrative equipment telemetry" : "Equipment telemetry from API"}</p>
            </div>
            <span className="subtle-count">{inverters.length} assets</span>
          </div>
          <div className="inverter-list">
            {inverters.map((inverter) => (
              <InverterRow key={inverter.id} inverter={inverter} />
            ))}
            {inverters.length === 0 && (
              <p className="diagnosis-description">No inverter data available.</p>
            )}
          </div>
        </article>

        <article className="panel recommendations-panel">
          <div className="panel-heading">
            <div>
              <h3>Recommended next step</h3>
              <p>{isDemo ? "Illustrative recommendation" : "Backend recommendation"}</p>
            </div>
          </div>

          {topRecommendation ? (
            <>
              <div className="recommendation-icon"><CheckCircle2 size={22} /></div>
              <h4>{topRecommendation.title}</h4>
              <p className="recommendation-description">{topRecommendation.description}</p>
              <div className="recommendation-note">
                <AlertTriangle size={16} />
                <span>
                  Priority: {topRecommendation.priority.toUpperCase()} · Asset: {topRecommendation.affectedAssetId}
                  . Verify against actual plant conditions before acting.
                </span>
              </div>
            </>
          ) : (
            <p className="diagnosis-description">No recommendation is available.</p>
          )}
        </article>
      </section>

      <article className="panel evidence-panel" style={{ marginBottom: 19 }}>
        <div className="panel-heading">
          <div>
            <h3>Diagnostic evidence</h3>
            <p>Signals associated with the returned diagnosis</p>
          </div>
          <span className="subtle-count">{evidence.length} items</span>
        </div>
        <div className="inverter-list">
          {evidence.map((item) => (
            <div className="inverter-row" key={item.id}>
              <div className="inverter-icon inverter-icon-alert">
                <AlertTriangle size={18} />
              </div>
              <div className="inverter-name">
                <strong>{item.title}</strong>
                <span>{item.description}</span>
              </div>
              <span className={`inverter-status ${item.severity === "low" ? "healthy" : "review"}`}>
                {item.severity.toUpperCase()}
              </span>
            </div>
          ))}
          {evidence.length === 0 && (
            <p className="diagnosis-description">No evidence items returned.</p>
          )}
        </div>
      </article>

      <footer className="dashboard-footer">
        <span>
          <span className="footer-dot" />
          Frontend connected · {isDemo ? "Demo mode" : "API mode"}
        </span>
        <span>Solar Diagnostic Command Center · Prototype</span>
      </footer>
    </main>
  );
}
