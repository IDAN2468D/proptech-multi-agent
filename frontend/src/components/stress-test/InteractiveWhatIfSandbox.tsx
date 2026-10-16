"use client";

import { useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Activity, Play } from "lucide-react";
import { proptechApiV2 } from "@/lib/api-client";
import { formatILS, formatPct } from "@/lib/formatters";
import { MacroStressTestResult } from "@/lib/schemas/agent-outputs-v2.schema";
import { spatialAudio } from "@/components/audio/SpatialAudioFeedback";

interface InteractiveWhatIfSandboxProps {
  runId: string;
  initialStress: MacroStressTestResult;
  defaultRentIls: number;
}

export function InteractiveWhatIfSandbox({
  runId,
  initialStress,
  defaultRentIls,
}: InteractiveWhatIfSandboxProps) {
  const [stress, setStress] = useState<MacroStressTestResult>(initialStress);
  const [interestRate, setInterestRate] = useState<number>(4.85);
  const [monthlyRent, setMonthlyRent] = useState<number>(defaultRentIls || 6800);
  const [renoOverrun, setRenoOverrun] = useState<number>(0);
  const [isSimulating, setIsSimulating] = useState<boolean>(false);

  const handleRunSimulation = async () => {
    setIsSimulating(true);
    try {
      const updated = await proptechApiV2.runInteractiveStressTest(runId, {
        interest_rate_pct: interestRate,
        monthly_rent_ils: monthlyRent,
        renovation_overrun_ils: renoOverrun,
      });
      setStress(updated);
      spatialAudio.playSpatialCue("AGENT_DONE", 0.35);
    } finally {
      setIsSimulating(false);
    }
  };

  const chartData = [
    {
      name: "תרחיש בסיס",
      תזרים_חודשי: Math.round(stress.base_case_monthly_cashflow_ils),
    },
    {
      name: "זעזוע ריבית (+1.5%)",
      תזרים_חודשי: Math.round(stress.rate_hike_plus_1_5_pct_cashflow_ils),
    },
    {
      name: "תרחיש קיצון משולב",
      תזרים_חודשי: Math.round(stress.combined_worst_case_monthly_cashflow_ils),
    },
  ];

  return (
    <div className="liquid-glass rounded-2xl p-6 space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <Activity className="w-4 h-4 text-cyan-400" />
            סוכן 8: סימולטור What-If חי ומבחן קיצון מונטה-קרלו (1,000 הרצות)
          </h3>
          <p className="text-xs text-slate-400">
            הזז את הסליידרים כדי לבדוק עמידות תזרימית מול עליית ריבית בנק ישראל,
            ירידת שכירות או חריגת שיפוץ
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-3 py-1 rounded-xl bg-cyan-500/15 border border-cyan-400/30 text-cyan-300 text-xs font-bold">
            הסתברות לתזרים חיובי:{" "}
            {formatPct(stress.probability_of_positive_cashflow_pct)}
          </span>
          <span className="px-3 py-1 rounded-xl bg-slate-900 border border-white/10 text-slate-200 text-xs font-semibold">
            ריבית איזון מקסימלית: {formatPct(stress.max_safe_interest_rate_pct)}
          </span>
        </div>
      </div>

      {/* 120Hz GPU Sliders */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 bg-slate-900/75 p-4 rounded-xl border border-white/10 text-xs">
        <div className="space-y-1.5">
          <div className="flex justify-between">
            <span className="text-slate-300">ריבית משכנתא שנתית:</span>
            <span className="text-cyan-300 font-bold">{interestRate}%</span>
          </div>
          <input
            type="range"
            min={2.5}
            max={9.5}
            step={0.1}
            value={interestRate}
            onChange={(e) => setInterestRate(Number(e.target.value))}
            className="w-full accent-cyan-400"
          />
        </div>

        <div className="space-y-1.5">
          <div className="flex justify-between">
            <span className="text-slate-300">שכר דירה חודשי:</span>
            <span className="text-emerald-300 font-bold">
              {formatILS(monthlyRent)}
            </span>
          </div>
          <input
            type="range"
            min={3000}
            max={16000}
            step={200}
            value={monthlyRent}
            onChange={(e) => setMonthlyRent(Number(e.target.value))}
            className="w-full accent-emerald-400"
          />
        </div>

        <div className="space-y-1.5">
          <div className="flex justify-between">
            <span className="text-slate-300">חריגת תקציב שיפוץ:</span>
            <span className="text-amber-300 font-bold">
              {formatILS(renoOverrun)}
            </span>
          </div>
          <input
            type="range"
            min={0}
            max={250000}
            step={10000}
            value={renoOverrun}
            onChange={(e) => setRenoOverrun(Number(e.target.value))}
            className="w-full accent-amber-400"
          />
        </div>
      </div>

      <button
        type="button"
        disabled={isSimulating}
        onClick={handleRunSimulation}
        className="px-5 py-2.5 rounded-xl bg-gradient-to-l from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white text-xs font-bold flex items-center gap-2 transition"
      >
        <Play className="w-3.5 h-3.5" />
        {isSimulating
          ? "מריץ 1,000 סימולציות מונטה-קרלו..."
          : "הרץ סימולציית What-If בזמן אמת"}
      </button>

      <div className="h-56 w-full" dir="ltr">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} />
            <YAxis stroke="#94a3b8" fontSize={12} />
            <ReferenceLine y={0} stroke="#f43f5e" strokeDasharray="3 3" />
            <Tooltip
              contentStyle={{
                backgroundColor: "#0f172a",
                borderColor: "#334155",
                borderRadius: "12px",
                color: "#f8fafc",
              }}
            />
            <Bar dataKey="תזרים_חודשי" fill="#22d3ee" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
