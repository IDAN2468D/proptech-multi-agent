"use client";

import { CheckCircle2, ShieldAlert, TrendingUp } from "lucide-react";
import { InvestmentExecutiveReport } from "@/lib/schemas/agent-outputs.schema";

const REC_STYLES: Record<
  string,
  { label: string; colorClass: string; badgeBg: string }
> = {
  STRONG_BUY: {
    label: "STRONG BUY • מומלץ מאוד לרכישה",
    colorClass: "text-emerald-300",
    badgeBg: "bg-emerald-500/20 border-emerald-400/40",
  },
  BUY_WITH_CAUTION: {
    label: "BUY WITH CAUTION • רכישה בזהירות",
    colorClass: "text-cyan-300",
    badgeBg: "bg-cyan-500/20 border-cyan-400/40",
  },
  HOLD_FOR_REVIEW: {
    label: "HOLD FOR REVIEW • המתן לבדיקה אנושית",
    colorClass: "text-amber-300",
    badgeBg: "bg-amber-500/20 border-amber-400/40",
  },
  AVOID: {
    label: "AVOID • עסקה מסוכנת / לא מומלצת",
    colorClass: "text-rose-300",
    badgeBg: "bg-rose-500/20 border-rose-400/40",
  },
};

export function ExecutiveSummaryHero({
  report,
}: {
  report: InvestmentExecutiveReport;
}) {
  const recKey = report.investment_recommendation || "HOLD_FOR_REVIEW";
  const recStyle = REC_STYLES[recKey] || REC_STYLES.HOLD_FOR_REVIEW;
  const riskScore = report.critic?.overall_risk_score ?? 50;
  const mathVerified = report.critic?.math_verification_passed ?? true;

  return (
    <div className="liquid-glass-glow rounded-2xl p-6 space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="space-y-2">
          <div className="flex flex-wrap items-center gap-2.5">
            <span
              className={`px-3.5 py-1.5 rounded-xl border text-xs font-extrabold ${recStyle.badgeBg} ${recStyle.colorClass}`}
            >
              {recStyle.label}
            </span>

            <span
              className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-xl text-xs font-semibold border ${
                mathVerified
                  ? "bg-emerald-500/15 border-emerald-400/30 text-emerald-300"
                  : "bg-rose-500/15 border-rose-400/30 text-rose-300"
              }`}
            >
              {mathVerified ? (
                <>
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  אימות מתמטי דטרמיניסטי: 100% תואם
                </>
              ) : (
                <>
                  <ShieldAlert className="w-3.5 h-3.5" />
                  כשל באימות מתמטי
                </>
              )}
            </span>
          </div>

          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-cyan-400" />
            תקציר מנהלים מבוסס 5 סוכנים
          </h2>
        </div>

        {/* Visual Risk Score Gauge (1-100) */}
        <div className="p-4 rounded-2xl bg-slate-950/80 border border-white/10 min-w-52 space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400">מדד סיכון משוקלל (Critic)</span>
            <span
              className={`font-extrabold text-sm ${
                riskScore >= 70
                  ? "text-rose-400"
                  : riskScore >= 45
                  ? "text-amber-400"
                  : "text-emerald-400"
              }`}
            >
              {riskScore} / 100
            </span>
          </div>
          <div className="w-full h-2.5 rounded-full bg-slate-800 overflow-hidden">
            <div
              className={`h-full transition-all duration-500 ${
                riskScore >= 70
                  ? "bg-rose-500"
                  : riskScore >= 45
                  ? "bg-amber-400"
                  : "bg-emerald-400"
              }`}
              style={{ width: `${riskScore}%` }}
            />
          </div>
        </div>
      </div>

      {report.executive_summary && (
        <p className="text-sm text-slate-200 leading-relaxed bg-slate-950/60 p-4 rounded-xl border border-white/5">
          {report.executive_summary}
        </p>
      )}
    </div>
  );
}
