"use client";

import { useState } from "react";
import { BookOpen, FileWarning, Quote, Scale } from "lucide-react";
import { formatSqm } from "@/lib/formatters";
import { LegalDueDiligenceResult } from "@/lib/schemas/agent-outputs.schema";

const SEVERITY_BADGE: Record<string, string> = {
  CRITICAL: "bg-rose-500/20 border-rose-500/40 text-rose-300",
  HIGH: "bg-amber-500/20 border-amber-500/40 text-amber-300",
  MEDIUM: "bg-cyan-500/20 border-cyan-500/40 text-cyan-300",
  LOW: "bg-emerald-500/20 border-emerald-500/40 text-emerald-300",
};

export function LegalRagFindingsList({
  legal,
}: {
  legal: LegalDueDiligenceResult;
}) {
  const [selectedSeverity, setSelectedSeverity] = useState<string>("ALL");

  const filtered = legal.findings.filter((f) =>
    selectedSeverity === "ALL" ? true : f.severity === selectedSeverity
  );

  return (
    <div className="liquid-glass rounded-2xl p-6 space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <Scale className="w-4 h-4 text-cyan-400" />
            ממצאי תחקור RAG משפטי ושמאי (נסח טאבו, חוזה מכר ושמאות)
          </h3>
          <p className="text-xs text-slate-400">
            כל ממצא מחויב בציטוט מדויק (Exact Quote) ומספר עמוד מתוך המסמך
          </p>
        </div>

        <div className="flex items-center gap-2">
          {legal.registered_area_sqm && (
            <span className="px-3 py-1 rounded-xl bg-slate-900 border border-white/10 text-xs text-cyan-300 font-semibold">
              שטח רשום בטאבו: {formatSqm(legal.registered_area_sqm)}
            </span>
          )}
          <select
            value={selectedSeverity}
            onChange={(e) => setSelectedSeverity(e.target.value)}
            className="px-3 py-1.5 rounded-xl bg-slate-950 border border-white/15 text-xs text-white"
          >
            <option value="ALL">כל רמות החומרה ({legal.findings.length})</option>
            <option value="CRITICAL">CRITICAL</option>
            <option value="HIGH">HIGH</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="LOW">LOW</option>
          </select>
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="p-6 rounded-xl bg-slate-900/60 text-center text-xs text-slate-400">
          לא נמצאו ממצאים ברמת החומרה שנבחרה.
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((finding, idx) => (
            <div
              key={idx}
              className="p-4 rounded-xl bg-slate-950/75 border border-white/10 space-y-2.5"
            >
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span
                    className={`px-2.5 py-0.5 rounded-lg border text-[11px] font-bold ${
                      SEVERITY_BADGE[finding.severity] || SEVERITY_BADGE.LOW
                    }`}
                  >
                    {finding.severity}
                  </span>
                  <span className="text-xs font-bold text-white">
                    {finding.category}
                  </span>
                </div>

                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-cyan-500/10 border border-cyan-400/20 text-cyan-300 text-xs font-medium">
                  <BookOpen className="w-3.5 h-3.5" />
                  {finding.source_document} • עמוד {finding.page_number}
                </span>
              </div>

              <p className="text-sm text-slate-200 flex items-start gap-2">
                <FileWarning className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                <span>{finding.description}</span>
              </p>

              <blockquote className="p-3 rounded-lg bg-slate-900/90 border-s-4 border-cyan-400 text-xs text-slate-300 font-mono flex items-start gap-2">
                <Quote className="w-4 h-4 text-cyan-400 shrink-0" />
                <span>&ldquo;{finding.exact_quote}&rdquo;</span>
              </blockquote>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
