import { useState } from "react";
import { runDiagnosis } from "../../services/api";
import type {
  DiagnosisApiResponse,
  DiagnosisRequest,
} from "../../services/api";
import {
  Activity,
  AlertCircle,
  CheckCircle2,
  LoaderCircle,
  Send,
  Zap,
} from "lucide-react";

const initialValues = {
  plant_capacity_kw: "",
  irradiance_poa_wm2: "",
  module_temperature_c: "",
  actual_power_kw: "",
  inverter_temperature_c: "",
};

type FormValues = typeof initialValues;

export default function DiagnosticWorkbench() {
  const [values, setValues] = useState<FormValues>(initialValues);
  const [result, setResult] = useState<DiagnosisApiResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function updateField(field: keyof FormValues, value: string) {
    setValues((current) => ({ ...current, [field]: value }));
    setError("");
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setResult(null);

    const capacity = Number(values.plant_capacity_kw);
    const irradiance = Number(values.irradiance_poa_wm2);
    const moduleTemperature = Number(values.module_temperature_c);
    const actualPower = Number(values.actual_power_kw);
    const inverterTemperature = Number(values.inverter_temperature_c);

    if (
      !Number.isFinite(capacity) ||
      capacity <= 0 ||
      !Number.isFinite(irradiance) ||
      irradiance < 0 ||
      !Number.isFinite(moduleTemperature) ||
      !Number.isFinite(actualPower) ||
      actualPower < 0 ||
      !Number.isFinite(inverterTemperature)
    ) {
      setError("Check the measurements. Capacity must be above zero; irradiance and actual power cannot be negative.");
      return;
    }

    const payload: DiagnosisRequest = {
      plant_capacity_kw: capacity,
      irradiance_poa_wm2: irradiance,
      module_temperature_c: moduleTemperature,
      actual_power_kw: actualPower,
      inverter_temperature_c: inverterTemperature,
    };

    setLoading(true);
    try {
      const response = await runDiagnosis(payload);
      setResult(response);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "The diagnosis request failed. Check the backend and try again."
      );
    } finally {
      setLoading(false);
    }
  }

  const fields: {
    key: keyof FormValues;
    label: string;
    unit: string;
    min?: number;
    step: string;
    placeholder: string;
  }[] = [
    {
      key: "plant_capacity_kw",
      label: "Plant capacity",
      unit: "kW",
      min: 0.01,
      step: "any",
      placeholder: "e.g. 100",
    },
    {
      key: "irradiance_poa_wm2",
      label: "Plane-of-array irradiance",
      unit: "W/m²",
      min: 0,
      step: "any",
      placeholder: "e.g. 750",
    },
    {
      key: "module_temperature_c",
      label: "Module temperature",
      unit: "°C",
      step: "any",
      placeholder: "e.g. 45",
    },
    {
      key: "actual_power_kw",
      label: "Measured actual power",
      unit: "kW",
      min: 0,
      step: "any",
      placeholder: "e.g. 62",
    },
    {
      key: "inverter_temperature_c",
      label: "Inverter temperature",
      unit: "°C",
      step: "any",
      placeholder: "e.g. 52",
    },
  ];

  return (
    <section className="diagnostic-workbench">
      <div className="diagnostic-workbench-heading">
        <div className="diagnostic-heading-icon">
          <Activity size={21} />
        </div>
        <div>
          <p className="diagnostic-eyebrow">LIVE BACKEND INTEGRATION</p>
          <h2>Run a Solar Diagnosis</h2>
          <p className="diagnostic-subtitle">
            Submit plant measurements to the existing diagnostic engine.
          </p>
        </div>
      </div>

      <div className="diagnostic-workbench-grid">
        <form className="diagnostic-form" onSubmit={handleSubmit}>
          <div className="diagnostic-form-grid">
            {fields.map((field) => (
              <label className="diagnostic-field" key={field.key}>
                <span>{field.label}</span>
                <div className="diagnostic-input-wrap">
                  <input
                    type="number"
                    required
                    min={field.min}
                    step={field.step}
                    value={values[field.key]}
                    placeholder={field.placeholder}
                    onChange={(event) =>
                      updateField(field.key, event.target.value)
                    }
                  />
                  <span className="diagnostic-unit">{field.unit}</span>
                </div>
              </label>
            ))}
          </div>

          <button
            className="diagnostic-submit"
            type="submit"
            disabled={loading}
          >
            {loading ? (
              <LoaderCircle className="diagnostic-spinner" size={18} />
            ) : (
              <Send size={17} />
            )}
            {loading ? "Analyzing measurements..." : "Run Diagnosis"}
          </button>

          <p className="diagnostic-form-note">
            Use measurements from the same plant and time period. Results depend
            on the data submitted.
          </p>

          {error && (
            <div className="diagnostic-error" role="alert">
              <AlertCircle size={19} />
              <span>{error}</span>
            </div>
          )}
        </form>

        <div className="diagnostic-result-panel" aria-live="polite">
          {!result && !loading && !error && (
            <div className="diagnostic-empty-state">
              <div className="diagnostic-empty-icon">
                <Zap size={27} />
              </div>
              <h3>Diagnosis results will appear here</h3>
              <p>
                Enter your plant measurements and run the diagnosis to see the
                backend response.
              </p>
            </div>
          )}

          {loading && (
            <div className="diagnostic-empty-state">
              <LoaderCircle
                className="diagnostic-spinner diagnostic-large-spinner"
                size={32}
              />
              <h3>Analyzing plant performance</h3>
              <p>Waiting for the FastAPI diagnostic engine.</p>
            </div>
          )}

          {result && (
            <div className="diagnostic-result">
              <div className="diagnostic-result-topline">
                <span className="diagnostic-result-label">
                  <CheckCircle2 size={16} />
                  BACKEND RESPONSE
                </span>
                <span className="diagnostic-confidence">
                  {Number.isFinite(result.confidence)
                    ? `${Math.round(result.confidence * 100)}% confidence`
                    : "Confidence unavailable"}
                </span>
              </div>

              <h3 className="diagnostic-root-cause">{result.root_cause}</h3>

              <div className="diagnostic-result-metrics">
                <div>
                  <span>Expected power</span>
                  <strong>{result.expected_power_kw.toFixed(2)} kW</strong>
                </div>
                <div>
                  <span>Actual power</span>
                  <strong>{result.actual_power_kw.toFixed(2)} kW</strong>
                </div>
                <div>
                  <span>Power gap</span>
                  <strong>{result.power_gap_kw.toFixed(2)} kW</strong>
                </div>
                <div>
                  <span>Underperformance</span>
                  <strong>
                    {result.underperformance_percent.toFixed(1)}%
                  </strong>
                </div>
              </div>

              <div className="diagnostic-result-section">
                <h4>Recommendation</h4>
                <p>{result.recommendation}</p>
              </div>

              <div className="diagnostic-result-section">
                <h4>Supporting evidence</h4>
                {result.evidence.length > 0 ? (
                  <ul>
                    {result.evidence.map((item, index) => (
                      <li key={`${index}-${item}`}>{item}</li>
                    ))}
                  </ul>
                ) : (
                  <p>No supporting evidence was returned.</p>
                )}
              </div>

              <p className="diagnostic-result-disclaimer">
                This is an engineering diagnostic result, not a guarantee that
                the identified cause has been physically verified.
              </p>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
