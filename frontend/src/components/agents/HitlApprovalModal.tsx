"use client";

import { useState } from "react";
import { AlertOctagon, Check, ShieldAlert, X } from "lucide-react";
import { InvestmentExecutiveReport } from "@/lib/schemas/agent-outputs.schema";
import { HITLApproveRequest } from "@/lib/schemas/property.schema";

interface HitlApprovalModalProps {
  report: InvestmentExecutiveReport;
  isSubmitting: boolean;
  onSubmitDecision: (payload: HITLApproveRequest) => Promise<void>;
}

export function HitlApprovalModal({
  report,
  isSubmitting,
  onSubmitDecision,
}: HitlApprovalModalProps) {
  const [updatedPrice, setUpdatedPrice] = useState<string>("1650000");
  const [updatedEquity, setUpdatedEquity] = useState<string>("1100000");
  const [notes, setNotes] = useState<string>(
    "המוכר המציא מכתב החרגה והוריד את המחיר לאחר מו״מ בגין פער השטח בטאבו."
  );

  if (report.run_status !== "PAUSED_FOR_APPROVAL" || !report.critic) {
    return null;
  }

  const handleDecision = async (approved: boolean) => {
    await onSubmitDecision({
      approved,
      updated_asking_price_ils: updatedPrice ? Number(updatedPrice) : undefined,
      updated_equity_ils: updatedEquity ? Number(updatedEquity) : undefined,
      investor_notes: notes,
    });
  };

  return (
    <div className="liquid-glass-glow rounded-2xl p-6 border-2 border-amber-400/50 bg-amber-950/20 space-y-5">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-amber-500/20 border border-amber-400/40 text-amber-300">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-amber-400">
              HTTP 202 Accepted • PAUSED_FOR_APPROVAL
            </span>
            <h3 className="text-lg font-bold text-white">
              עצירה לאישור אנושי (Human-In-The-Loop Guardrail)
            </h3>
            <p className="text-xs text-slate-300">{report.critic.hitl_reason}</p>
          </div>
        </div>
        <div className="px-3.5 py-1.5 rounded-xl bg-amber-500/20 border border-amber-400/40 text-amber-200 text-sm font-bold">
          סיכון: {report.critic.overall_risk_score}/100
        </div>
      </div>

      {report.critic.context_clashes_detected.length > 0 && (
        <div className="p-4 rounded-xl bg-slate-950/80 border border-rose-500/30 space-y-2">
          <div className="flex items-center gap-2 text-rose-300 text-xs font-bold">
            <AlertOctagon className="w-4 h-4" />
            סתירות מידע שזוהו בהצלבה בין הסוכנים (Context Clashes):
          </div>
          <ul className="list-disc list-inside text-xs text-slate-200 space-y-1">
            {report.critic.context_clashes_detected.map((clash, i) => (
              <li key={i}>{clash}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-xs text-slate-300 mb-1">
            עדכון מחיר רכישה לאחר משא ומתן (₪)
          </label>
          <input
            type="number"
            value={updatedPrice}
            onChange={(e) => setUpdatedPrice(e.target.value)}
            className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950/90 border border-white/15 text-white text-sm"
          />
        </div>
        <div>
          <label className="block text-xs text-slate-300 mb-1">
            עדכון הון עצמי לעסקה (₪)
          </label>
          <input
            type="number"
            value={updatedEquity}
            onChange={(e) => setUpdatedEquity(e.target.value)}
            className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950/90 border border-white/15 text-white text-sm"
          />
        </div>
      </div>

      <div>
        <label className="block text-xs text-slate-300 mb-1">
          הערות משקיע / תנאי מתלה לאישור
        </label>
        <input
          type="text"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950/90 border border-white/15 text-white text-sm"
        />
      </div>

      <div className="flex flex-wrap items-center gap-3 pt-1">
        <button
          type="button"
          disabled={isSubmitting}
          onClick={() => handleDecision(true)}
          className="px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-sm flex items-center gap-2 transition disabled:opacity-50"
        >
          <Check className="w-4 h-4" />
          {isSubmitting
            ? "מחשב מחדש ומפיק דוח סופי..."
            : "אשר סיכון והפק דוח השקעה סופי"}
        </button>

        <button
          type="button"
          disabled={isSubmitting}
          onClick={() => handleDecision(false)}
          className="px-5 py-2.5 rounded-xl bg-rose-500/20 hover:bg-rose-500/30 border border-rose-500/40 text-rose-200 font-semibold text-sm flex items-center gap-2 transition disabled:opacity-50"
        >
          <X className="w-4 h-4" />
          דחה עסקה (AVOID)
        </button>
      </div>
    </div>
  );
}
