import { useEffect, useState } from "react";
import { useLocation, useParams, Link } from "react-router-dom";
import { fetchAssessment, downloadReportUrl } from "../api/client";

const RISK_COLORS = {
  low: "text-risk-low border-risk-low",
  moderate: "text-risk-moderate border-risk-moderate",
  high: "text-risk-high border-risk-high",
};

export default function Results() {
  const { id } = useParams();
  const location = useLocation();
  // If we arrived right after submitting, the result is already in
  // navigation state -- skip the extra fetch. Otherwise (e.g. direct link,
  // page refresh) load it from history.
  const [data, setData] = useState(location.state || null);
  const [loading, setLoading] = useState(!location.state);
  const [error, setError] = useState("");

  useEffect(() => {
    if (data) return;
    fetchAssessment(id)
      .then(setData)
      .catch(() => setError("Couldn't load this assessment."))
      .finally(() => setLoading(false));
  }, [id, data]);

  if (loading) return <p className="p-10 text-teal-700">Loading results...</p>;
  if (error) return <p className="p-10 text-risk-high">{error}</p>;
  if (!data) return null;

  const riskClass = RISK_COLORS[data.risk_label] || RISK_COLORS.moderate;

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <h1 className="mb-6 text-3xl text-teal-900">Your assessment</h1>

      <div className={`mb-8 rounded-lg border-2 p-6 ${riskClass}`}>
        <p className="text-sm uppercase tracking-wide opacity-80">
          {data.condition.replace("_", " ")} risk
        </p>
        <p className="text-4xl font-semibold">
          {(data.risk_score * 100).toFixed(0)}%
        </p>
        <p className="text-lg capitalize">{data.risk_label} risk</p>
      </div>

      <section className="mb-8">
        <h2 className="mb-3 text-xl text-teal-900">What's driving this</h2>
        <ul className="space-y-2">
          {data.top_factors.map((f) => (
            <li
              key={f.feature}
              className="flex items-center justify-between rounded-md border border-teal-100 bg-white px-4 py-3"
            >
              <span className="capitalize">{f.feature.replace(/_/g, " ")}</span>
              <span className="text-sm text-teal-700">
                value: {f.value} &middot; impact {f.impact > 0 ? "+" : ""}
                {f.impact}
              </span>
            </li>
          ))}
        </ul>
      </section>

      <section className="mb-8">
        <h2 className="mb-3 text-xl text-teal-900">Recommendations</h2>
        <div className="space-y-4 rounded-md border border-teal-100 bg-white p-5">
          <div>
            <h3 className="text-sm font-semibold text-teal-800">Diet</h3>
            <ul className="ml-4 list-disc text-sm text-ink">
              {data.recommendations.diet.map((tip, i) => (
                <li key={i}>{tip}</li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-teal-800">Exercise</h3>
            <ul className="ml-4 list-disc text-sm text-ink">
              {data.recommendations.exercise.map((tip, i) => (
                <li key={i}>{tip}</li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-teal-800">
              Suggested specialist
            </h3>
            <p className="text-sm text-ink">{data.recommendations.specialist}</p>
          </div>
        </div>
      </section>

      <p className="mb-8 text-xs italic text-teal-700">
        {data.disclaimer ||
          "HealthLens is a preliminary screening tool, not a medical diagnosis."}
      </p>

      <div className="flex gap-3">
        <a
          href={downloadReportUrl(data.assessment_id)}
          className="rounded-md border border-teal-600 px-4 py-2 text-sm font-medium text-teal-700 hover:bg-teal-50"
        >
          Download PDF
        </a>
        <Link
          to="/dashboard"
          className="rounded-md bg-teal-600 px-4 py-2 text-sm font-medium text-white hover:bg-teal-700"
        >
          View dashboard
        </Link>
      </div>
    </div>
  );
}
