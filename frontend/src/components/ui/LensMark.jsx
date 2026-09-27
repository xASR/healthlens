// The HealthLens mark: a lens ring with a heartbeat trace crossing it.
// No external asset -- inline SVG so it matches the glass tokens exactly
// and never needs a separate favicon/logo file to stay in sync.
export default function LensMark({ className = "h-5 w-5" }) {
  return (
    <svg viewBox="0 0 24 24" className={className} aria-hidden="true">
      <circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" strokeWidth="1.5" opacity="0.35" />
      <path
        d="M4.5 12H8l2-4.5L13 17l2-5h4.5"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
