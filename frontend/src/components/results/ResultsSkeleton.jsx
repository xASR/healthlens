const Block = ({ className }) => <div className={`rounded-full bg-ink/[0.07] ${className}`} />;

export default function ResultsSkeleton() {
  return (
    <div className="space-y-6 motion-safe:animate-pulse" aria-hidden="true">
      <div className="glass flex flex-col items-center gap-6 p-8 sm:flex-row sm:gap-10">
        <div className="h-44 w-44 shrink-0 rounded-full border-[14px] border-ink/[0.07]" />
        <div className="w-full max-w-xs space-y-3">
          <Block className="h-6 w-48" />
          <Block className="h-7 w-28" />
          <Block className="h-3 w-full" />
          <Block className="h-3 w-4/5" />
        </div>
      </div>
      <div className="glass space-y-6 p-6">
        <Block className="h-5 w-40" />
        {[0, 1, 2, 3].map((i) => (
          <div key={i} className="space-y-2">
            <Block className="h-3 w-1/3" />
            <Block className="h-2.5 w-full" />
          </div>
        ))}
      </div>
    </div>
  );
}
