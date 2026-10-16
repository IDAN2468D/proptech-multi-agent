"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { CheckCircle, MapPin } from "lucide-react";
import { formatILS, formatPct } from "@/lib/formatters";
import { MarketAnalysisResult } from "@/lib/schemas/agent-outputs.schema";

export function MarketCompsSection({
  market,
}: {
  market: MarketAnalysisResult;
}) {
  const chartData = [
    {
      name: "ממוצע עסקאות באזור",
      מחיר_למר: Math.round(market.avg_price_per_sqm_ils),
    },
    {
      name: "הנכס הנבדק",
      מחיר_למר: Math.round(market.subject_price_per_sqm_ils),
    },
  ];

  return (
    <div className="liquid-glass rounded-2xl p-6 space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <MapPin className="w-4 h-4 text-cyan-400" />
            ניתוח שוק ועסקאות השוואה (Market & Comps Agent)
          </h3>
          <p className="text-xs text-slate-400">
            מבוסס על {market.comparable_transactions_count} עסקאות השוואה באזור |
            שכירות משוערת: {formatILS(market.estimated_monthly_rent_ils)}/חודש
          </p>
        </div>

        <span
          className={`px-3 py-1 rounded-xl text-xs font-bold border ${
            market.market_deviation_pct > 10
              ? "bg-rose-500/15 border-rose-400/30 text-rose-300"
              : market.market_deviation_pct < 0
              ? "bg-emerald-500/15 border-emerald-400/30 text-emerald-300"
              : "bg-cyan-500/15 border-cyan-400/30 text-cyan-300"
          }`}
        >
          סטייה ממחיר השוק: {formatPct(market.market_deviation_pct, true)}
        </span>
      </div>

      <div className="h-52 w-full" dir="ltr">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} />
            <YAxis stroke="#94a3b8" fontSize={12} />
            <Tooltip
              contentStyle={{
                backgroundColor: "#0f172a",
                borderColor: "#334155",
                borderRadius: "12px",
                color: "#f8fafc",
              }}
            />
            <Bar dataKey="מחיר_למר" fill="#38bdf8" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="space-y-2">
        <h4 className="text-xs font-semibold text-slate-300">
          מאפייני השכונה ומגמות ביקוש:
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {market.neighborhood_highlights.map((item, idx) => (
            <div
              key={idx}
              className="flex items-center gap-2 text-xs text-slate-200 bg-slate-900/70 p-2.5 rounded-xl border border-white/5"
            >
              <CheckCircle className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
              <span>{item}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
