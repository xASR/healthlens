// Diverging bar chart of the SHAP top factors. Bars grow right from the
// center axis when a factor raised risk and left when it lowered it, scaled
// against the largest absolute impact in this result.
//
// Values arrive model-encoded (see predictor.py's _to_feature_frame), so
// they are decoded here for display.

const CHEST_PAIN = {
  1: "Typical angina",
  2: "Atypical angina",
  3: "Non-anginal pain",
  4: "No chest pain",
};

const yesNo = (v) => (Number(v) === 1 ? "Yes" : "No");

const FEATURES = {
  glucose: { label: "Fasting glucose", unit: "mg/dL" },
  bmi: { label: "BMI" },
  age: { label: "Age", unit: "years" },
  pregnancies: { label: "Pregnancies" },
  systolic_bp: { label: "Systolic BP", unit: "mmHg" },
  diastolic_bp: { label: "Diastolic BP", unit: "mmHg" },
  cholesterol_total: { label: "Total cholesterol", unit: "mg/dL" },
  sex: { label: "Sex", format: (v) => (Number(v) === 1 ? "Male" : "Female") },
  chest_pain_type: { label: "Chest pain", format: (v) => CHEST_PAIN[Number(v)] ?? String(v) },
  exercise_angina: { label: "Chest pain on exertion", format: yesNo },
  fbs: { label: "Fasting glucose over 120", format: yesNo },
};

function describe(feature, value) {
  const meta = FEATURES[feature] || {
    label: feature.replace(/_/g, " ").replace(/^./, (c) => c.toUpperCase()),
  };
  let shown;
  if (meta.format) {
    shown = meta.format(value);
  } else if (typeof value === "number") {
    shown = Number.isInteger(value) ? String(value) : value.toFixed(1);
  } else {
    shown = String(value);
  }
  return { label: meta.label, value: meta.unit ? `${shown} ${meta.unit}` : shown };
}

// Random Forest TreeExplainer output is in probability units, so an impact
// of 0.144 is a 14.4 percentage-point shift from the model's average.
const toPoints = (impact) => `${impact > 0 ? "+" : "−"}${(Math.abs(impact) * 100).toFixed(1)}`;

export default function ShapImpactBars({ factors }) {
  if (!factors?.length) return null;
  const maxAbs = Math.max(...factors.map((f) => Math.abs(f.impact)), 1e-9);

  return (
    <div>
      <div className="mb-4 grid grid-cols-2 text-xs text-ink/55" aria-hidden="true">
        <span className="flex items-center gap-1.5 justify-self-end pr-3">
          <span className="h-2 w-2 rounded-full bg-risk-low" />
          Lowers risk
        </span>
        <span className="flex items-center gap-1.5 pl-3">
          <span className="h-2 w-2 rounded-full bg-risk-high" />
          Raises risk
        </span>
      </div>

      <ul className="space-y-5">
        {factors.map((f) => {
          const { label, value } = describe(f.feature, f.value);
          const raises = f.impact > 0;
          const width = Math.max((Math.abs(f.impact) / maxAbs) * 50, 1.5);
          return (
            <li key={f.feature}>
              <div className="mb-2 flex items-baseline justify-between gap-4">
                <p className="min-w-0 text-[15px] text-ink">
                  <span className="font-medium">{label}</span>
                  <span className="ml-2 text-ink/50">{value}</span>
                </p>
                <p
                  className={`shrink-0 text-sm font-semibold tabular-nums ${raises ? "text-risk-high" : "text-risk-low"}`}
                >
                  {toPoints(f.impact)}
                  <span className="ml-0.5 text-xs font-medium opacity-70">pts</span>
                  <span className="sr-only">{raises ? ", raises risk" : ", lowers risk"}</span>
                </p>
              </div>
              <div className="relative h-2.5 rounded-full bg-ink/[0.06]" aria-hidden="true">
                <span className="absolute -inset-y-1 left-1/2 w-px bg-ink/25" />
                <span
                  className={`absolute inset-y-0 ${raises ? "left-1/2 rounded-r-full bg-risk-high" : "right-1/2 rounded-l-full bg-risk-low"}`}
                  style={{ width: `${width}%` }}
                />
              </div>
            </li>
          );
        })}
      </ul>

      <p className="mt-6 text-xs leading-relaxed text-ink/55">
        Each bar shows how much that answer moved your score, in percentage
        points, compared with the model&apos;s average prediction. These are the
        {` ${factors.length} `}largest factors.
      </p>
    </div>
  );
}
