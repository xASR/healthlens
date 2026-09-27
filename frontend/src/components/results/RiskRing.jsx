import { useEffect, useState } from "react";

const RISK_STYLES = {
  low: { stroke: "#2F9E6E", chip: "bg-risk-low/10 text-risk-low" },
  moderate: { stroke: "#D98E2F", chip: "bg-risk-moderate/10 text-risk-moderate" },
  high: { stroke: "#C4472C", chip: "bg-risk-high/10 text-risk-high" },
};

const CONDITION_NAMES = {
  diabetes: "Type 2 diabetes",
  heart_disease: "Heart disease",
};

const SIZE = 176;
const STROKE = 14;
const RADIUS = (SIZE - STROKE) / 2;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

export default function RiskRing({ score, label, condition, note }) {
  const pct = Math.round(score * 100);
  const style = RISK_STYLES[label] || RISK_STYLES.moderate;
  const conditionName = CONDITION_NAMES[condition] || condition.replace(/_/g, " ");

  // Start empty, then fill on the next frame so the CSS transition runs.
  // This is the page's one load animation.
  const [drawn, setDrawn] = useState(0);
  useEffect(() => {
    const frame = requestAnimationFrame(() => setDrawn(Math.min(Math.max(score, 0), 1)));
    return () => cancelAnimationFrame(frame);
  }, [score]);

  return (
    <div className="flex flex-col items-center gap-6 text-center sm:flex-row sm:gap-10 sm:text-left">
      <div className="relative shrink-0" style={{ width: SIZE, height: SIZE }}>
        <svg
          viewBox={`0 0 ${SIZE} ${SIZE}`}
          className="h-full w-full -rotate-90"
          role="img"
          aria-label={`Estimated ${conditionName.toLowerCase()} risk: ${pct} percent, ${label}`}
        >
          <circle
            cx={SIZE / 2}
            cy={SIZE / 2}
            r={RADIUS}
            fill="none"
            stroke="currentColor"
            strokeWidth={STROKE}
            className="text-ink/[0.07]"
          />
          <circle
            cx={SIZE / 2}
            cy={SIZE / 2}
            r={RADIUS}
            fill="none"
            stroke={style.stroke}
            strokeWidth={STROKE}
            strokeLinecap="round"
            strokeDasharray={CIRCUMFERENCE}
            strokeDashoffset={CIRCUMFERENCE * (1 - drawn)}
            opacity={drawn > 0 ? 1 : 0}
            className="transition-[stroke-dashoffset] duration-[1100ms] ease-spring motion-reduce:transition-none"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center" aria-hidden="true">
          <span className="font-display text-5xl font-semibold tabular-nums tracking-tight text-ink">
            {pct}
            <span className="ml-0.5 text-2xl font-medium text-ink/40">%</span>
          </span>
        </div>
      </div>

      <div className="max-w-sm">
        <h2 className="text-2xl font-semibold text-ink">{conditionName}</h2>
        <span
          className={`mt-2 inline-flex items-center rounded-full px-3 py-1 text-sm font-medium ${style.chip}`}
        >
          {label.charAt(0).toUpperCase() + label.slice(1)} risk
        </span>
        {note && <p className="mt-4 text-[15px] leading-relaxed text-ink/70">{note}</p>}
      </div>
    </div>
  );
}
