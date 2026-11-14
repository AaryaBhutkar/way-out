import { Shell } from "@/components/Shell";

/** Plainly labeled drill page. It must never look like a real county site. */
export default function Page() {
  return (
    <Shell title="Way Out drill page" owner="Deep" task="D1-07">
      <p className="rounded border border-help/50 px-3 py-1 text-sm font-semibold text-help">
        WAY OUT DRILL PAGE · NOT AN OFFICIAL COUNTY SITE
      </p>
      <h1 className="text-2xl font-semibold">Test zone: Oak Creek 14</h1>
      <p className="text-muted">Ready / Set / Go toggle goes here (D1-07). TinyFish reads this page.</p>
    </Shell>
  );
}
