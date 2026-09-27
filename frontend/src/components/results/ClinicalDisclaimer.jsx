const FALLBACK =
  "HealthLens is a preliminary screening tool, not a medical diagnosis. " +
  "Please consult a qualified healthcare professional for evaluation.";

// GET /history/{id} doesn't return `disclaimer`, so the fallback matters on
// refresh and direct links.
export default function ClinicalDisclaimer({ text }) {
  return (
    <aside className="flex gap-3 rounded-2xl border border-ink/[0.08] bg-white/40 px-4 py-3.5 backdrop-blur-xl">
      <svg
        viewBox="0 0 24 24"
        className="mt-0.5 h-4 w-4 shrink-0 text-ink/45"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        aria-hidden="true"
      >
        <circle cx="12" cy="12" r="9.5" />
        <path d="M12 11v5.5M12 7.5v.01" />
      </svg>
      <p className="text-xs leading-relaxed text-ink/60">{text || FALLBACK}</p>
    </aside>
  );
}
