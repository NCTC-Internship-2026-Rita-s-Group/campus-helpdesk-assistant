export function SkeletonCard() {
  return (
    <div className="w-full rounded-2xl border border-white/5 bg-[#001433]/20 p-5 space-y-4 relative overflow-hidden shadow-md">
      {/* 🔮 Highly Reflective Shimmer Ambient Animation Cover overlay */}
      <div
        className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/[0.04] to-transparent animate-shimmer"
        style={{ animationDuration: "1.5s" }}
      />

      <div className="flex items-center justify-between gap-4">
        <div className="h-4 w-1/3 rounded-lg bg-white/10" />
        <div className="h-3 w-16 rounded bg-white/5" />
      </div>

      <div className="space-y-2.5">
        <div className="h-3 w-full rounded bg-white/5" />
        <div className="h-3 w-5/6 rounded bg-white/5" />
        <div className="h-3 w-2/3 rounded bg-white/5" />
      </div>
    </div>
  );
}

export function SkeletonGridGroup({ count = 3 }: { count?: number }) {
  return (
    <div className="space-y-3.5 w-full">
      {Array.from({ length: count }).map((_, idx) => (
        <SkeletonCard key={idx} />
      ))}
    </div>
  );
}
