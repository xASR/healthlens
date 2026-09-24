import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { submitAssessment } from "../api/client";

const initialForm = {
  condition: "diabetes",
  age: "",
  sex: "female",
  bmi: "",
  systolic_bp: "",
  diastolic_bp: "",
  glucose: "",
  cholesterol_total: "",
  smoker: false,
  physically_active: true,
  family_history: false,
};

// Mirrors the ge/le bounds in backend/app/schemas/questionnaire.py --
// client-side validation is a UX nicety, the backend is the real gate.
const numericFields = {
  age: { label: "Age (years)", min: 1, max: 120 },
  bmi: { label: "BMI", min: 10, max: 80, step: "0.1" },
  systolic_bp: { label: "Systolic blood pressure (mmHg)", min: 70, max: 250 },
  diastolic_bp: { label: "Diastolic blood pressure (mmHg)", min: 40, max: 150 },
  glucose: { label: "Fasting glucose (mg/dL)", min: 40, max: 500 },
  cholesterol_total: { label: "Total cholesterol (mg/dL)", min: 100, max: 400 },
};

export default function Questionnaire() {
  const [form, setForm] = useState(initialForm);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  const update = (field, value) => setForm((f) => ({ ...f, [field]: value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const payload = {
        ...form,
        age: Number(form.age),
        bmi: Number(form.bmi),
        systolic_bp: Number(form.systolic_bp),
        diastolic_bp: Number(form.diastolic_bp),
        glucose: Number(form.glucose),
        cholesterol_total: Number(form.cholesterol_total),
      };
      const result = await submitAssessment(payload);
      navigate(`/results/${result.assessment_id}`, { state: result });
    } catch (err) {
      if (err.response?.status === 503) {
        setError(
          "The prediction model isn't trained yet on the server. This is " +
            "expected until Week 3-4 model training is complete."
        );
      } else {
        setError("Something went wrong submitting your assessment. Please try again.");
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <h1 className="mb-1 text-3xl text-teal-900">Health questionnaire</h1>
      <p className="mb-8 text-sm text-teal-700">
        These are routine indicators from a basic checkup. Nothing here is
        stored anywhere except your private HealthLens history.
      </p>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="mb-1 block text-sm font-medium text-ink">
            Which condition would you like screened?
          </label>
          <select
            value={form.condition}
            onChange={(e) => update("condition", e.target.value)}
            className="w-full rounded-md border border-teal-100 bg-white px-3 py-2"
          >
            <option value="diabetes">Type 2 Diabetes</option>
            <option value="heart_disease">Cardiovascular Disease</option>
          </select>
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-ink">Sex</label>
          <select
            value={form.sex}
            onChange={(e) => update("sex", e.target.value)}
            className="w-full rounded-md border border-teal-100 bg-white px-3 py-2"
          >
            <option value="female">Female</option>
            <option value="male">Male</option>
          </select>
        </div>

        <div className="grid grid-cols-2 gap-4">
          {Object.entries(numericFields).map(([field, cfg]) => (
            <div key={field}>
              <label className="mb-1 block text-sm font-medium text-ink">
                {cfg.label}
              </label>
              <input
                type="number"
                required
                min={cfg.min}
                max={cfg.max}
                step={cfg.step || "1"}
                value={form[field]}
                onChange={(e) => update(field, e.target.value)}
                className="w-full rounded-md border border-teal-100 bg-white px-3 py-2 focus:border-teal-400"
              />
            </div>
          ))}
        </div>

        <fieldset className="space-y-3">
          <legend className="mb-1 text-sm font-medium text-ink">Lifestyle</legend>
          <label className="flex items-center gap-2 text-sm text-ink">
            <input
              type="checkbox"
              checked={form.smoker}
              onChange={(e) => update("smoker", e.target.checked)}
            />
            I currently smoke
          </label>
          <label className="flex items-center gap-2 text-sm text-ink">
            <input
              type="checkbox"
              checked={form.physically_active}
              onChange={(e) => update("physically_active", e.target.checked)}
            />
            I'm physically active most weeks
          </label>
          <label className="flex items-center gap-2 text-sm text-ink">
            <input
              type="checkbox"
              checked={form.family_history}
              onChange={(e) => update("family_history", e.target.checked)}
            />
            Family history of this condition
          </label>
        </fieldset>

        {error && (
          <p className="rounded-md bg-risk-high/10 px-3 py-2 text-sm text-risk-high">
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-md bg-teal-600 py-2.5 font-medium text-white hover:bg-teal-700 disabled:opacity-60"
        >
          {submitting ? "Analyzing..." : "Get my risk assessment"}
        </button>
      </form>
    </div>
  );
}
