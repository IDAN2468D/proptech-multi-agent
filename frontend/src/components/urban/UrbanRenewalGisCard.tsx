"use client";

import { Building2, Compass, Footprints, TrainFront } from "lucide-react";
import { formatPct, formatSqm } from "@/lib/formatters";
import { UrbanRenewalGISResult } from "@/lib/schemas/agent-outputs-v2.schema";

export function UrbanRenewalGisCard({
  gis,
}: {
  gis: UrbanRenewalGISResult;
}) {
  return (
    <div className="liquid-glass rounded-2xl p-6 space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <Building2 className="w-4 h-4 text-cyan-400" />
            סוכן 7: פוטנציאל התחדשות עירונית (תמ״א 38 / פינוי-בינוי) ו-GIS
          </h3>
          <p className="text-xs text-slate-400">
            ניתוח גיאו-מרחבי של תב״ע, מרחק לרכבת הקלה ואפסייד תמורות בעלים
          </p>
        </div>

        <span className="px-3 py-1 rounded-xl bg-emerald-500/20 border border-emerald-400/40 text-emerald-300 text-xs font-extrabold">
          סבירות תמ״א / פינוי-בינוי: {gis.tama38_or_pinui_binui_likelihood}
        </span>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="p-4 rounded-xl bg-slate-900/85 border border-white/10 space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>מרחק לרכבת קלה</span>
            <TrainFront className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-xl font-extrabold text-white">
            {gis.distance_to_light_rail_meters} מ׳
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/85 border border-white/10 space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>מדד הליכתיות (Walkability)</span>
            <Footprints className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-xl font-extrabold text-emerald-300">
            {gis.walkability_score} / 100
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/85 border border-white/10 space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>תוספת שטח צפויה (ממ״ד/מרפסת)</span>
            <Compass className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-xl font-extrabold text-cyan-300">
            +{formatSqm(gis.expected_additional_sqm)}
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/85 border border-white/10 space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>אפסייד שווי לאחר התחדשות</span>
            <Building2 className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-xl font-extrabold text-indigo-300">
            {formatPct(gis.projected_renewal_upside_pct, true)}
          </div>
        </div>
      </div>
    </div>
  );
}
