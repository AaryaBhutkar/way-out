"use client";

import { useEffect, useRef } from "react";
import { SimBadge } from "@/components/Shell";
import type { CallSummary, CallTurn, HouseholdRecord } from "@/lib/api";
import { ESCALATION_LABEL, STAGE_LABEL, STATUS_LABEL, clock, latencyTone, recordRows } from "./format";

type Correction = { field: string; from: unknown; to: unknown; at: string };

export function CallDetail({
  call,
  turns,
  record,
  corrections,
  requestStatus,
}: {
  call: CallSummary;
  turns: CallTurn[];
  record: HouseholdRecord | undefined;
  corrections: Correction[];
  requestStatus: string | null;
}) {
  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <header className="flex flex-wrap items-center gap-2 border-b border-line px-4 py-3">
        <h2 className="text-base font-semibold">{call.household?.address ?? call.householdId}</h2>
        {call.household?.simulated && <SimBadge />}
        <span className="text-sm text-muted">
          {call.direction} · {call.language.toUpperCase()} ·{" "}
          {call.done ? "ended" : (STAGE_LABEL[call.stage ?? ""] ?? call.stage)}
        </span>
        <div className="ml-auto flex items-center gap-2">
          {call.escalations.map((e) => (
            <span
              key={e}
              className={`rounded px-2 py-0.5 text-xs font-semibold ${
                e === "medical" || e === "flames" ? "bg-fire/15 text-fire" : "border border-help/40 text-help"
              }`}
            >
              {ESCALATION_LABEL[e] ?? e}
            </span>
          ))}
          <StatusChip status={requestStatus} />
        </div>
      </header>
      <div className="grid min-h-0 flex-1 grid-cols-1 lg:grid-cols-[1fr_18rem]">
        <Transcript turns={turns} live={!call.done} />
        <RecordPanel record={record} corrections={corrections} />
      </div>
    </div>
  );
}

function StatusChip({ status }: { status: string | null }) {
  if (!status) return <span className="rounded border border-line px-2 py-0.5 text-xs text-muted">No request</span>;
  const tone =
    status === "received" || status === "reassigning"
      ? "border-fire/50 text-fire"
      : status === "approved"
        ? "border-line text-muted"
        : "border-out/50 text-out";
  return (
    <span key={status} className={`animate-flash rounded border px-2 py-0.5 text-xs font-medium ${tone}`}>
      {STATUS_LABEL[status] ?? status}
    </span>
  );
}

function Transcript({ turns, live }: { turns: CallTurn[]; live: boolean }) {
  const end = useRef<HTMLDivElement>(null);
  useEffect(() => end.current?.scrollIntoView({ block: "end", behavior: "smooth" }), [turns.length]);
  return (
    <div className="min-h-0 overflow-y-auto px-4 py-3">
      <ol className="flex flex-col gap-2.5">
        {turns.map((t, i) => (
          <li
            key={`${t.speaker}|${t.at}|${i}`}
            className={`flex flex-col ${t.speaker === "agent" ? "items-start" : "items-end"}`}
          >
            <div
              className={`max-w-[85%] rounded-lg px-3 py-2 text-sm leading-relaxed ${
                t.speaker === "agent" ? "bg-panel" : "bg-vehicle/15"
              }`}
            >
              {t.text || <span className="italic text-muted">(silent, waiting)</span>}
            </div>
            <div className="mt-1 flex items-center gap-1.5 text-[11px] text-muted">
              <span className="tabular-nums">{clock(t.at)}</span>
              {t.speaker === "agent" && typeof t.latencyMs === "number" && (
                <span
                  title={t.interpreterMs != null ? `interpreter ${Math.round(t.interpreterMs)} ms` : undefined}
                  className={`rounded border px-1.5 tabular-nums ${latencyTone(t.latencyMs)}`}
                >
                  {Math.round(t.latencyMs)} ms
                </span>
              )}
              {t.speaker === "agent" && t.interpreter && t.interpreter !== "gemini" && (
                <span className="rounded border border-line px-1.5">{t.interpreter}</span>
              )}
              {t.fallback && <span className="rounded border border-help/40 px-1.5 text-help">fallback</span>}
              {t.guardBlocked && (
                <span title="The honesty guard dropped the AI's acknowledgment" className="rounded border border-sim/40 px-1.5 text-sim">
                  ack blocked
                </span>
              )}
            </div>
          </li>
        ))}
        {live && (
          <li className="flex items-center gap-1.5 text-xs text-muted">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-vehicle" /> live
          </li>
        )}
      </ol>
      <div ref={end} />
    </div>
  );
}

function RecordPanel({ record, corrections }: { record: HouseholdRecord | undefined; corrections: Correction[] }) {
  return (
    <aside className="min-h-0 overflow-y-auto border-t border-line px-4 py-3 lg:border-t-0 lg:border-l">
      <h3 className="mb-2 text-xs font-semibold tracking-wider text-muted uppercase">Record</h3>
      <dl className="flex flex-col">
        {recordRows(record).map((row) => (
          <div key={row.key} className="flex items-baseline justify-between gap-3 border-b border-line/60 py-1.5">
            <dt className="text-sm text-muted">{row.label}</dt>
            {/* Remount on change so a newly heard value flashes once. */}
            <dd key={row.value ?? "—"} className={`animate-flash rounded px-1 text-sm ${row.value ? "" : "text-muted/50"}`}>
              {row.value ?? "—"}
            </dd>
          </div>
        ))}
      </dl>
      {corrections.length > 0 && (
        <>
          <h3 className="mt-4 mb-2 text-xs font-semibold tracking-wider text-muted uppercase">Corrections</h3>
          <ul className="flex flex-col gap-1 text-xs text-muted">
            {corrections.map((c, i) => (
              <li key={`${c.field}|${c.at}|${i}`}>
                <span className="text-ink">{c.field}</span>: {String(c.from)} → {String(c.to)}
              </li>
            ))}
          </ul>
        </>
      )}
    </aside>
  );
}
