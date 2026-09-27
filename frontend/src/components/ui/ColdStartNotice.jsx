import useDelayedFlag from "../../hooks/useDelayedFlag";

// Stays silent for normal-latency requests; appears only when a request has
// been pending long enough that a cold start is the likely cause.
// The role="status" wrapper is always mounted so screen readers announce the
// message when it appears.
export default function ColdStartNotice({ active, delayMs = 4000, className = "" }) {
  const show = useDelayedFlag(active, delayMs);

  return (
    <div role="status" aria-live="polite" className={className}>
      {show && (
        <div className="glass flex items-start gap-3 rounded-2xl px-4 py-3.5">
          <span className="relative mt-1.5 flex h-2.5 w-2.5 shrink-0" aria-hidden="true">
            <span className="absolute inline-flex h-full w-full rounded-full bg-teal-400 opacity-60 motion-safe:animate-ping" />
            <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-teal-600" />
          </span>
          <div>
            <p className="text-sm font-medium text-ink">
              Waking up server &amp; initializing ML model…
            </p>
            <p className="mt-0.5 text-xs leading-relaxed text-ink/60">
              The server sleeps when idle, so the first request after a pause
              can take up to a minute. Keep this page open.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
