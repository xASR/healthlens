// Health-app style category cards: tinted icon + category name as the
// header, content in plain rows separated by hairlines.

const ICON_PROPS = {
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  className: "h-4 w-4",
  "aria-hidden": true,
};

const LeafIcon = () => (
  <svg {...ICON_PROPS}>
    <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z" />
    <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12" />
  </svg>
);

const ActivityIcon = () => (
  <svg {...ICON_PROPS}>
    <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
  </svg>
);

const DoctorIcon = () => (
  <svg {...ICON_PROPS}>
    <path d="M6 3v6a6 6 0 0 0 12 0V3" />
    <path d="M12 15v2a4 4 0 0 0 8 0v-3" />
    <circle cx="20" cy="12" r="2" />
  </svg>
);

function CategoryCard({ icon, title, tint, children, className = "" }) {
  return (
    <section className={`glass p-5 ${className}`}>
      <header className={`mb-3 flex items-center gap-2 ${tint.text}`}>
        <span className={`flex h-7 w-7 items-center justify-center rounded-lg ${tint.bg}`}>{icon}</span>
        <h3 className="text-sm font-semibold">{title}</h3>
      </header>
      {children}
    </section>
  );
}

function TipList({ items }) {
  return (
    <ul className="divide-y divide-ink/[0.06]">
      {items.map((tip, i) => (
        <li key={i} className="py-2.5 text-[15px] leading-relaxed text-ink/85 first:pt-0 last:pb-0">
          {tip}
        </li>
      ))}
    </ul>
  );
}

export default function RecommendationCards({ recommendations }) {
  if (!recommendations) return null;
  const { diet = [], exercise = [], specialist } = recommendations;

  return (
    <div className="grid gap-4 sm:grid-cols-2">
      <CategoryCard
        icon={<LeafIcon />}
        title="Diet"
        tint={{ text: "text-risk-low", bg: "bg-risk-low/10" }}
      >
        <TipList items={diet} />
      </CategoryCard>

      <CategoryCard
        icon={<ActivityIcon />}
        title="Exercise"
        tint={{ text: "text-risk-moderate", bg: "bg-risk-moderate/10" }}
      >
        <TipList items={exercise} />
      </CategoryCard>

      {specialist && (
        <CategoryCard
          icon={<DoctorIcon />}
          title="Suggested specialist"
          tint={{ text: "text-teal-600", bg: "bg-teal-600/10" }}
          className="sm:col-span-2"
        >
          <p className="text-[15px] leading-relaxed text-ink/85">{specialist}</p>
        </CategoryCard>
      )}
    </div>
  );
}
