"use client";

import {
  Banknote,
  Calculator,
  Coins,
  Percent,
  PiggyBank,
  TrendingUp,
} from "lucide-react";
import { formatILS, formatPct } from "@/lib/formatters";
import { FinancialMetricsResult } from "@/lib/schemas/agent-outputs.schema";

export function FinancialMetricsGrid({
  financials,
}: {
  financials: FinancialMetricsResult;
}) {
  const cards = [
    {
      label: "תשואת Cap Rate נטו",
      value: formatPct(financials.net_cap_rate_pct),
      sub: `תשואה ברוטו: ${formatPct(financials.gross_yield_pct)}`,
      icon: Percent,
      highlight: "text-cyan-300",
    },
    {
      label: "תשואה על ההון (Cash-on-Cash)",
      value: formatPct(financials.cash_on_cash_return_pct),
      sub: "כולל שקלול מס רכישה והוצאות",
      icon: PiggyBank,
      highlight:
        financials.cash_on_cash_return_pct >= 0
          ? "text-emerald-300"
          : "text-rose-300",
    },
    {
      label: "IRR חזוי ל-10 שנים",
      value: formatPct(financials.projected_10yr_irr_pct),
      sub: "כולל עליית ערך וסילוק קרן משכנתא",
      icon: TrendingUp,
      highlight: "text-indigo-300",
    },
    {
      label: "תזרים מזומנים חודשי נטו",
      value: formatILS(financials.net_monthly_cashflow_ils),
      sub: `החזר משכנתא: ${formatILS(financials.monthly_mortgage_payment_ils)}/חודש`,
      icon: Banknote,
      highlight:
        financials.net_monthly_cashflow_ils >= 0
          ? "text-emerald-300"
          : "text-rose-400",
    },
    {
      label: "היקף משכנתא ושיעור מימון (LTV)",
      value: formatILS(financials.loan_amount_ils),
      sub: `שיעור מימון: ${formatPct(financials.loan_to_value_pct)}`,
      icon: Calculator,
      highlight: "text-white",
    },
    {
      label: "מס רכישה מחושב (מדרגות מס)",
      value: formatILS(financials.purchase_tax_ils),
      sub: "חושב דטרמיניסטית בפייתון",
      icon: Coins,
      highlight: "text-amber-300",
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {cards.map((card, i) => {
        const Icon = card.icon;
        return (
          <div
            key={i}
            className="liquid-glass rounded-2xl p-5 space-y-2 border border-white/10"
          >
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>{card.label}</span>
              <Icon className="w-4 h-4 text-cyan-400" />
            </div>
            <div className={`text-2xl font-extrabold ${card.highlight}`}>
              {card.value}
            </div>
            <p className="text-xs text-slate-400">{card.sub}</p>
          </div>
        );
      })}
    </div>
  );
}
