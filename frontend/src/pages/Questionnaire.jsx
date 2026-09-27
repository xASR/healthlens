import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { submitAssessment } from "../api/client";
import {
  FloatingInput,
  SegmentedControl,
  ChoiceList,
  ToggleRow,
} from "../components/ui/FormControls";
import ColdStartNotice from "../components/ui/ColdStartNotice";
import Spinner from "../components/ui/Spinner";

const initialForm = {
  condition: "diabetes",
  age: "",
  sex: "female",
  bmi: "",
  systolic_bp: "",
  diastolic_bp: "",
  glucose: "",
  cholesterol_total: "",
  pregnancies: "0",
  chest_pain_type: "typical_angina",
  exercise_angina: false,
  smoker: false,
  physically_active: true,
  family_history: false,
};

const conditionOptions = [
  { value: "diabetes", label: "Type 2 diabetes" },
  { value: "heart_disease", label: "Heart disease" },
];

const sexOptions = [
  { value: "female", label: "Female" },
  { value: "male", label: "Male" },
];

// Mirrors the "cp" categories in the UCI Heart Disease dataset the heart
// disease model is trained on (see predictor.py's CHEST_PAIN_TYPE_MAP).
const chestPainOptions = [
  { value: "typical_angina", title: "Typical angina", detail: "Classic chest pain that comes on with exertion" },
  { value: "atypical_angina", title: "Atypical angina", detail: "Chest discomfort that doesn't follow the classic pattern" },
  { value: "non_anginal_pain", title: "Non-anginal pain", detail: "Chest pain unrelated to the heart" },
  { value: "asymptomatic", title: "No chest pain", detail: "I don't get chest pain" },
];

// Mirrors the ge/le bounds in backend/app/schemas/questionnaire.py --
// client-side validation is a UX nicety, the backend is the real gate.
const numericFields = {
  age: { label: "Age", unit: "years", min: 1, max: 120, inputMode: "numeric" },
  bmi: { label: "BMI", min: 10, max: 80, step: "0.1", inputMode: "decimal" },
  systolic_bp: { label: "Systolic BP", unit: "mmHg", min: 70, max: 250, inputMode: "numeric" },
  diastolic_bp: { label: "Diastolic BP", unit: "mmHg", min: 40, max: 150, inputMode: "numeric" },
  glucose: { label: "Fasting glucose", unit: "mg/dL", min: 40, max: 500, inputMode: "numeric" },
  cholesterol_total: { label: "Total cholesterol", unit: "mg/dL", min: 100, max: 400, inputMode: "numeric" },
};

// FastAPI returns `detail` as a string for errors raised in route code, but
// as an array of objects for Pydantic validation errors. Rendering the array
// directly would crash React, so flatten it to text.
function formatDetail(detail) {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((d) => {
        const field = d?.loc?.[d.loc.length - 1];
        return field ? `${String(field).replace(/_/g, " ")}: ${d.msg}` : d?.msg;
      })
      .filter(Boolean)
      .join(" ");
  }
  return "";
}

function Section({ title, description, children }) {
  return (
    <section className="glass space-y-5 p-5 sm:p-6">
      <div>
        <h2 className="text-lg font-semibold text-ink">{title}</h2>
        {description && <p className="mt-1 text-sm text-ink/60">{description}</p>}
      </div>
      {children}
    </section>
  );
}

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
        pregnancies: form.sex === "female" ? Number(form.pregnancies || 0) : 0,
      };
      const result = await submitAssessment(payload);
      navigate(`/results/${result.assessment_id}`, { state: result });
    } catch (err) {
      if (err.response?.status === 503) {
        setError("Screening for this condition is unavailable right now. Try again in a few minutes.");
      } else if (err.response?.status === 422) {
        setError(formatDetail(err.response.data?.detail) || "Please check your answers and try again.");
      } else {
        setError("Something went wrong submitting your assessment. Please try again.");
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="mx-auto max-w-2xl px-5 py-10 sm:px-6">
      <h1 className="text-3xl font-semibold text-ink">Health questionnaire</h1>
      <p className="mb-8 mt-2 text-[15px] text-ink/60">
        These are routine indicators from a basic checkup. Nothing here is
        stored anywhere except your private HealthLens history.
      </p>

      <form onSubmit={handleSubmit} className="space-y-5" aria-busy={submitting}>
        <Section title="Screening">
          <SegmentedControl
            name="condition"
            legend="Condition to screen for"
            options={conditionOptions}
            value={form.condition}
            onChange={(v) => update("condition", v)}
          />
          <SegmentedControl
            name="sex"
            legend="Sex"
            options={sexOptions}
            value={form.sex}
            onChange={(v) => update("sex", v)}
          />

          {form.condition === "diabetes" && form.sex === "female" && (
            <FloatingInput
              id="pregnancies"
              label="Number of pregnancies"
              type="number"
              inputMode="numeric"
              min={0}
              max={20}
              value={form.pregnancies}
              onChange={(e) => update("pregnancies", e.target.value)}
              hint="The diabetes model was trained on female patients, where this is a known predictive factor. Enter 0 if not applicable."
            />
          )}

          {form.condition === "heart_disease" && (
            <>
              <ChoiceList
                name="chest_pain_type"
                legend="Chest pain"
                options={chestPainOptions}
                value={form.chest_pain_type}
                onChange={(v) => update("chest_pain_type", v)}
              />
              <div className="overflow-hidden rounded-2xl border border-ink/10 bg-white/60">
                <ToggleRow
                  id="exercise_angina"
                  label="Chest pain during exertion"
                  description="Pain, pressure, or tightness when physically active"
                  checked={form.exercise_angina}
                  onChange={(v) => update("exercise_angina", v)}
                />
              </div>
            </>
          )}
        </Section>

        <Section
          title="Checkup numbers"
          description="Use the most recent values from a checkup or lab report."
        >
          <div className="grid gap-4 sm:grid-cols-2">
            {Object.entries(numericFields).map(([field, cfg]) => (
              <FloatingInput
                key={field}
                id={field}
                label={cfg.label}
                unit={cfg.unit}
                type="number"
                required
                inputMode={cfg.inputMode}
                min={cfg.min}
                max={cfg.max}
                step={cfg.step || "1"}
                value={form[field]}
                onChange={(e) => update(field, e.target.value)}
              />
            ))}
          </div>
        </Section>

        <section>
          <h2 className="mb-2 px-1 text-lg font-semibold text-ink">Lifestyle</h2>
          <div className="glass-group">
            <ToggleRow
              id="smoker"
              label="I currently smoke"
              checked={form.smoker}
              onChange={(v) => update("smoker", v)}
            />
            <ToggleRow
              id="physically_active"
              label="Physically active most weeks"
              checked={form.physically_active}
              onChange={(v) => update("physically_active", v)}
            />
            <ToggleRow
              id="family_history"
              label="Family history of this condition"
              checked={form.family_history}
              onChange={(v) => update("family_history", v)}
            />
          </div>
        </section>

        {error && (
          <p role="alert" className="rounded-2xl border border-risk-high/20 bg-risk-high/10 px-4 py-3 text-sm text-risk-high">
            {error}
          </p>
        )}

        <button type="submit" disabled={submitting} className="btn-primary h-12 w-full text-[15px]">
          {submitting && <Spinner />}
          {submitting ? "Analyzing…" : "Get my risk assessment"}
        </button>

        <ColdStartNotice active={submitting} />
      </form>
    </main>
  );
}
