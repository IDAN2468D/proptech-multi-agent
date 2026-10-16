"use client";

import { useEffect, useState } from "react";
import { CheckCircle2, Save, ShieldAlert, Sliders } from "lucide-react";
import { useInvestorProfile } from "@/hooks/use-investor-profile";

export default function InvestorProfilePage() {
  const { profile, isLoading, updateProfile, isUpdating } =
    useInvestorProfile();

  const [equity, setEquity] = useState(800000);
  const [riskTolerance, setRiskTolerance] = useState<
    "CONSERVATIVE" | "MODERATE" | "AGGRESSIVE"
  >("MODERATE");
  const [maxRiskScore, setMaxRiskScore] = useState(70);
  const [minYield, setMinYield] = useState(3.2);
  const [citiesText, setCitiesText] = useState("תל אביב, חיפה, רמת גן");
  const [isSingleHome, setIsSingleHome] = useState(false);
  const [savedBanner, setSavedBanner] = useState(false);

  useEffect(() => {
    if (profile) {
      setEquity(profile.available_equity_ils);
      setRiskTolerance(profile.risk_tolerance);
      setMaxRiskScore(profile.max_risk_score_threshold);
      setMinYield(profile.min_target_net_yield_pct);
      setCitiesText(profile.preferred_cities.join(", "));
      setIsSingleHome(profile.is_single_home_buyer);
    }
  }, [profile]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavedBanner(false);
    await updateProfile({
      available_equity_ils: Number(equity),
      risk_tolerance: riskTolerance,
      max_risk_score_threshold: Number(maxRiskScore),
      min_target_net_yield_pct: Number(minYield),
      preferred_cities: citiesText
        .split(",")
        .map((c) => c.trim())
        .filter(Boolean),
      is_single_home_buyer: isSingleHome,
    });
    setSavedBanner(true);
  };

  if (isLoading) {
    return <div className="liquid-glass rounded-2xl p-8 animate-pulse h-96" />;
  }

  return (
    <div className="max-w-3xl space-y-6">
      <div className="flex items-center gap-3">
        <div className="p-3 rounded-xl bg-cyan-500/20 border border-cyan-400/30 text-cyan-300">
          <Sliders className="w-6 h-6" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-white">
            הגדרות פרופיל משקיע (Long-Term Memory ב-MongoDB)
          </h2>
          <p className="text-sm text-slate-400">
            האורקסטרטור וסוכן ה-Critic מתאימים את חישובי המס, המינוף וסף ה-HITL
            לפרופיל זה.
          </p>
        </div>
      </div>

      {savedBanner && (
        <div className="p-4 rounded-xl bg-emerald-500/15 border border-emerald-500/40 text-emerald-300 flex items-center gap-2 text-sm">
          <CheckCircle2 className="w-5 h-5" />
          פרופיל המשקיע נשמר בהצלחה בזיכרון ארוך-הטווח (MongoDB)!
        </div>
      )}

      <form
        onSubmit={handleSubmit}
        className="liquid-glass rounded-2xl p-8 space-y-6"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              הון עצמי זמין להשקעה (₪)
            </label>
            <input
              type="number"
              required
              min={50000}
              step={10000}
              value={equity}
              onChange={(e) => setEquity(Number(e.target.value))}
              className="w-full px-4 py-2.5 rounded-xl bg-slate-950/80 border border-white/10 text-white"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              מדיניות סיכון מועדפת
            </label>
            <select
              value={riskTolerance}
              onChange={(e) =>
                setRiskTolerance(
                  e.target.value as "CONSERVATIVE" | "MODERATE" | "AGGRESSIVE"
                )
              }
              className="w-full px-4 py-2.5 rounded-xl bg-slate-950/80 border border-white/10 text-white"
            >
              <option value="CONSERVATIVE">שמרני (Conservative)</option>
              <option value="MODERATE">מאוזן (Moderate)</option>
              <option value="AGGRESSIVE">אגרסיבי / השבחה (Aggressive)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              סף ציון סיכון לעצירת HITL ({maxRiskScore}/100)
            </label>
            <input
              type="range"
              min={25}
              max={90}
              value={maxRiskScore}
              onChange={(e) => setMaxRiskScore(Number(e.target.value))}
              className="w-full accent-cyan-400"
            />
            <span className="text-xs text-slate-400 flex items-center gap-1 mt-1">
              <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
              מעל ציון זה הריצה תיעצר ב-PAUSED_FOR_APPROVAL לאישור אנושי
            </span>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              יעד תשואת Cap Rate נטו מינימלית (%)
            </label>
            <input
              type="number"
              step="0.1"
              min={1}
              max={15}
              value={minYield}
              onChange={(e) => setMinYield(Number(e.target.value))}
              className="w-full px-4 py-2.5 rounded-xl bg-slate-950/80 border border-white/10 text-white"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            ערים מועדפות להשקעה (מופרדות בפסיק)
          </label>
          <input
            type="text"
            value={citiesText}
            onChange={(e) => setCitiesText(e.target.value)}
            className="w-full px-4 py-2.5 rounded-xl bg-slate-950/80 border border-white/10 text-white"
          />
        </div>

        <label className="flex items-center gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={isSingleHome}
            onChange={(e) => setIsSingleHome(e.target.checked)}
            className="w-4 h-4 accent-cyan-500 rounded"
          />
          <span className="text-sm text-slate-200">
            זוהי דירה יחידה (חישוב מדרגות מס רכישה מופחתות לדירה יחידה)
          </span>
        </label>

        <button
          type="submit"
          disabled={isUpdating}
          className="px-6 py-3 rounded-xl bg-gradient-to-l from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold flex items-center gap-2 shadow-lg shadow-cyan-500/20 transition"
        >
          <Save className="w-4 h-4" />
          {isUpdating ? "שומר ב-MongoDB..." : "שמירת העדפות משקיע"}
        </button>
      </form>
    </div>
  );
}
