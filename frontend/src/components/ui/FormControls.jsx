// Glass form primitives for the questionnaire. All are controlled and
// stateless: the page keeps owning its single `form` object and `update()`.

const FIELD_BASE =
  "peer block h-14 w-full rounded-2xl border border-ink/10 bg-white/60 px-4 pb-2 pt-6 " +
  "text-[15px] text-ink shadow-[inset_0_1px_0_rgba(255,255,255,0.8)] backdrop-blur-xl " +
  "transition duration-200 ease-apple placeholder:text-transparent hover:border-ink/20 " +
  "focus:border-teal-400 focus:bg-white/85 focus:outline-none focus:ring-4 focus:ring-teal-400/15 " +
  "focus-visible:outline-none [&:not(:placeholder-shown):invalid]:border-risk-high/60 " +
  "motion-reduce:transition-none";

// Hides the browser's number spinners; values are typed, not nudged.
const NO_SPINNER =
  "[appearance:textfield] [&::-webkit-inner-spin-button]:appearance-none " +
  "[&::-webkit-outer-spin-button]:appearance-none";

export function FloatingInput({ id, label, unit, hint, className = "", ...inputProps }) {
  const hintId = hint ? `${id}-hint` : undefined;
  return (
    <div className={className}>
      <div className="relative">
        <input
          id={id}
          placeholder=" "
          aria-describedby={hintId}
          className={`${FIELD_BASE} ${NO_SPINNER} ${unit ? "pr-16" : ""}`}
          {...inputProps}
        />
        <label
          htmlFor={id}
          className="pointer-events-none absolute left-4 top-2 translate-y-0 text-xs text-ink/55 transition-all duration-200 ease-apple
                     peer-placeholder-shown:top-1/2 peer-placeholder-shown:-translate-y-1/2 peer-placeholder-shown:text-[15px]
                     peer-focus:top-2 peer-focus:translate-y-0 peer-focus:text-xs peer-focus:text-teal-600
                     motion-reduce:transition-none"
        >
          {label}
        </label>
        {unit && (
          <span className="pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 text-sm text-ink/40">
            {unit}
          </span>
        )}
      </div>
      {hint && (
        <p id={hintId} className="mt-1.5 px-1 text-xs leading-relaxed text-ink/55">
          {hint}
        </p>
      )}
    </div>
  );
}

export function SegmentedControl({ name, legend, options, value, onChange }) {
  return (
    <fieldset>
      <legend className="mb-2 px-1 text-sm font-medium text-ink/70">{legend}</legend>
      <div
        className="grid gap-1 rounded-2xl bg-ink/[0.06] p-1"
        style={{ gridTemplateColumns: `repeat(${options.length}, minmax(0, 1fr))` }}
      >
        {options.map((opt) => {
          const checked = value === opt.value;
          return (
            <label
              key={opt.value}
              className={`cursor-pointer rounded-xl px-3 py-2 text-center text-sm font-medium transition duration-200 ease-apple
                          has-[:focus-visible]:ring-2 has-[:focus-visible]:ring-teal-600 motion-reduce:transition-none
                          ${checked ? "bg-white text-ink shadow-segment" : "text-ink/60 hover:text-ink"}`}
            >
              <input
                type="radio"
                name={name}
                value={opt.value}
                checked={checked}
                onChange={() => onChange(opt.value)}
                className="sr-only"
              />
              {opt.label}
            </label>
          );
        })}
      </div>
    </fieldset>
  );
}

// Radio list for options whose labels need a line of explanation.
export function ChoiceList({ name, legend, options, value, onChange }) {
  return (
    <fieldset>
      <legend className="mb-2 px-1 text-sm font-medium text-ink/70">{legend}</legend>
      <div className="divide-y divide-ink/[0.06] overflow-hidden rounded-2xl border border-ink/10 bg-white/60">
        {options.map((opt) => {
          const checked = value === opt.value;
          return (
            <label
              key={opt.value}
              className="flex cursor-pointer items-center gap-3 px-4 py-3 transition-colors duration-150 hover:bg-white/70
                         has-[:focus-visible]:bg-teal-50"
            >
              <input
                type="radio"
                name={name}
                value={opt.value}
                checked={checked}
                onChange={() => onChange(opt.value)}
                className="sr-only"
              />
              <span className="min-w-0 flex-1">
                <span className="block text-[15px] text-ink">{opt.title}</span>
                <span className="block text-xs text-ink/55">{opt.detail}</span>
              </span>
              <svg
                viewBox="0 0 24 24"
                className={`h-5 w-5 shrink-0 text-teal-600 transition-opacity duration-150 ${checked ? "opacity-100" : "opacity-0"}`}
                fill="none"
                stroke="currentColor"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <path d="M5 12.5l4.5 4.5L19 7.5" />
              </svg>
            </label>
          );
        })}
      </div>
    </fieldset>
  );
}

// iOS-style switch. A real checkbox (role="switch") underneath, so keyboard,
// forms and screen readers behave normally.
export function ToggleRow({ id, label, description, checked, onChange }) {
  return (
    <label htmlFor={id} className="flex cursor-pointer items-center justify-between gap-4 px-4 py-3.5">
      <span className="min-w-0">
        <span className="block text-[15px] text-ink">{label}</span>
        {description && <span className="mt-0.5 block text-xs text-ink/55">{description}</span>}
      </span>
      <span className="relative inline-flex shrink-0">
        <input
          id={id}
          type="checkbox"
          role="switch"
          checked={checked}
          onChange={(e) => onChange(e.target.checked)}
          className="peer sr-only"
        />
        <span
          aria-hidden="true"
          className="h-[31px] w-[51px] rounded-full bg-ink/15 transition-colors duration-200 ease-apple
                     peer-checked:bg-teal-600 peer-focus-visible:ring-4 peer-focus-visible:ring-teal-400/30"
        />
        <span
          aria-hidden="true"
          className="absolute left-[2px] top-[2px] h-[27px] w-[27px] rounded-full bg-white shadow-thumb
                     transition-transform duration-300 ease-spring peer-checked:translate-x-5 motion-reduce:transition-none"
        />
      </span>
    </label>
  );
}
