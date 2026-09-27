import { useEffect, useState } from "react";
import { useLocation, useParams, Link } from "react-router-dom";
import { fetchAssessment, downloadReport } from "../api/client";
import RiskRing from "../components/results/RiskRing";
import ShapImpactBars from "../components/results/ShapImpactBars";
import RecommendationCards from "../components/results/RecommendationCards";
import ClinicalDisclaimer from "../components/results/ClinicalDisclaimer";
import ResultsSkeleton from "../components/results/ResultsSkeleton";
import ColdStartNotice from "../components/ui/ColdStartNotice";
import Spinner from "../components/ui/Spinner";

export default function Results() {
  const { id } = useParams();
  const location = useLocation();
  // If we arrived right after submitting, the result is already in
  // navigation state -- skip the extra fetch. Otherwise (e.g. direct link,
  // page refresh) load it from history.
  const [data, setData] = useState(location.state || null);
  const [loading, setLoading] = useState(!location.state);
  const [error, setError] = useState("");
  const [downloading, setDownloading] = useState(false);
  const [downloadError, setDownloadError] = useState("");

  useEffect(() => {
    if (data) return;
    fetchAssessment(id)
      .then(setData)
      .catch(() => setError("Couldn't load this assessment."))
      .finally(() => setLoading(false));
  }, [id, data]);

  const handleDownload = () => {
    setDownloadError("");
    setDownloading(true);
    downloadReport(data.assessment_id)
      .catch(() => setDownloadError("Couldn't download the PDF. Please try again."))
      .finally(() => setDownloading(false));
  };

  if (loading) {
    return (
      <main className="mx-auto max-w-3xl px-5 py-10 sm:px-6" aria-busy="true">
        <h1 className="mb-6 text-3xl font-semibold text-ink">Your assessment</h1>
        <ColdStartNotice active={loading} className="mb-6" />
        <ResultsSkeleton />
      </main>
    );
  }

  if (error) {
    return (
      <main className="mx-auto max-w-3xl px-5 py-10 sm:px-6">
        <div className="glass p-8 text-center">
          <p className="text-[15px] font-medium text-risk-high">{error}</p>
          <p className="mt-1 text-sm text-ink/60">
            It may have been removed, or the link is incomplete.
          </p>
          <Link to="/dashboard" className="btn-secondary mt-5">
            Back to dashboard
          </Link>
        </div>
      </main>
    );
  }

  if (!data) return null;

  return (
    <main className="mx-auto max-w-3xl space-y-8 px-5 py-10 sm:px-6">
      <h1 className="text-3xl font-semibold text-ink">Your assessment</h1>

      <section className="glass p-6 sm:p-8" aria-label="Risk score">
        <RiskRing
          score={data.risk_score}
          label={data.risk_label}
          condition={data.condition}
          note={data.recommendations?.urgency_note}
        />
      </section>

      <section className="glass p-6 sm:p-8">
        <h2 className="mb-5 text-xl font-semibold text-ink">What&apos;s driving this</h2>
        <ShapImpactBars factors={data.top_factors} />
      </section>

      <section>
        <h2 className="mb-4 text-xl font-semibold text-ink">Recommendations</h2>
        <RecommendationCards recommendations={data.recommendations} />
      </section>

      <ClinicalDisclaimer text={data.disclaimer} />

      <div>
        <div className="flex flex-col gap-3 sm:flex-row">
          <button
            type="button"
            onClick={handleDownload}
            disabled={downloading}
            className="btn-secondary"
          >
            {downloading ? <Spinner /> : (
              <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor"
                   strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M12 4v11m0 0l-4.5-4.5M12 15l4.5-4.5M5 20h14" />
              </svg>
            )}
            {downloading ? "Preparing PDF…" : "Download PDF"}
          </button>
          <Link to="/dashboard" className="btn-primary">
            View dashboard
          </Link>
        </div>
        {downloadError && (
          <p role="alert" className="mt-3 text-sm text-risk-high">
            {downloadError}
          </p>
        )}
      </div>
    </main>
  );
}
