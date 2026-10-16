"use client";

import { useState } from "react";
import { CheckCircle2, Hammer, Layers, RefreshCw } from "lucide-react";
import { proptechApiV2 } from "@/lib/api-client";
import { formatILS } from "@/lib/formatters";
import { VisionRenovationResult } from "@/lib/schemas/agent-outputs-v2.schema";
import { spatialAudio } from "@/components/audio/SpatialAudioFeedback";

interface FloorplanVisionAnalyzerProps {
  propertyId?: string;
  initialVision: VisionRenovationResult;
}

export function FloorplanVisionAnalyzer({
  propertyId,
  initialVision,
}: FloorplanVisionAnalyzerProps) {
  const [vision, setVision] = useState<VisionRenovationResult>(initialVision);
  const [conditionHint, setConditionHint] = useState<string>(
    initialVision.property_condition
  );
  const [hasDampness, setHasDampness] = useState<boolean>(false);
  const [showOverlay, setShowOverlay] = useState<boolean>(true);
  const [isRecalculating, setIsRecalculating] = useState<boolean>(false);

  const handleRecalculate = async () => {
    if (!propertyId) return;
    setIsRecalculating(true);
    try {
      const updated = await proptechApiV2.uploadVisionFloorplan(
        propertyId,
        conditionHint,
        hasDampness
      );
      setVision(updated);
      spatialAudio.playSpatialCue("AGENT_DONE", -0.35);
    } finally {
      setIsRecalculating(false);
    }
  };

  return (
    <div className="liquid-glass rounded-2xl p-6 space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <Hammer className="w-4 h-4 text-cyan-400" />
            סוכן 6: ניתוח תשריט, פוטנציאל השבחה וכתב כמויות שיפוץ (Vision & BOQ)
          </h3>
          <p className="text-xs text-slate-400">
            חישוב עלויות שיפוץ דטרמיניסטי (renovation_calculator.py) ושווי נכס
            לאחר השבחה
          </p>
        </div>

        <button
          type="button"
          onClick={() => setShowOverlay(!showOverlay)}
          className="px-3 py-1.5 rounded-xl bg-cyan-500/15 border border-cyan-400/30 text-cyan-300 text-xs font-semibold flex items-center gap-1.5"
        >
          <Layers className="w-3.5 h-3.5" />
          {showOverlay ? "הסתר שכבת Vision Overlay" : "הצג שכבת Vision Overlay"}
        </button>
      </div>

      {/* Interactive Vision Floorplan Overlay Blueprint */}
      {showOverlay && (
        <div className="p-4 rounded-xl bg-slate-950/90 border border-cyan-500/30 space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
            <span className="text-cyan-300 font-bold">
              שכבת ניתוח הנדסי בתשריט (Floorplan Structural Overlay)
            </span>
            <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 font-semibold">
              {vision.can_add_room_or_split
                ? "אפשרות להוספת חדר / פיצול: כן"
                : "חלל תקני"}
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-xs">
            {vision.structural_notes.map((note, idx) => (
              <div
                key={idx}
                className="p-2.5 rounded-lg bg-slate-900 border border-white/10 text-slate-200 flex items-start gap-2"
              >
                <CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                <span>{note}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Condition Controls */}
      {propertyId && (
        <div className="flex flex-wrap items-center gap-3 bg-slate-900/60 p-3.5 rounded-xl border border-white/5 text-xs">
          <select
            value={conditionHint}
            onChange={(e) => setConditionHint(e.target.value)}
            className="px-3 py-2 rounded-lg bg-slate-950 border border-white/15 text-white"
          >
            <option value="NEW">דירה חדשה מקבלן (NEW)</option>
            <option value="GOOD">מצב שמור (GOOD)</option>
            <option value="NEEDS_COSMETIC_RENOVATION">
              דרוש שיפוץ קוסמטי (COSMETIC)
            </option>
            <option value="NEEDS_FULL_RENOVATION">
              דרוש שיפוץ יסודי מלא (FULL)
            </option>
          </select>

          <label className="flex items-center gap-2 text-slate-200 cursor-pointer">
            <input
              type="checkbox"
              checked={hasDampness}
              onChange={(e) => setHasDampness(e.target.checked)}
              className="accent-cyan-400"
            />
            זוהו מוקדי רטיבות/איטום
          </label>

          <button
            type="button"
            disabled={isRecalculating}
            onClick={handleRecalculate}
            className="px-3.5 py-2 rounded-lg bg-cyan-500/20 hover:bg-cyan-500/30 border border-cyan-400/30 text-cyan-200 font-semibold flex items-center gap-1.5"
          >
            <RefreshCw
              className={`w-3.5 h-3.5 ${isRecalculating ? "animate-spin" : ""}`}
            />
            חשב כתב כמויות מחדש
          </button>
        </div>
      )}

      {/* BOQ Table */}
      <div className="overflow-x-auto rounded-xl border border-white/10">
        <table className="w-full text-xs text-start">
          <thead className="bg-slate-900/90 text-slate-400 border-b border-white/10">
            <tr>
              <th className="py-2.5 px-4 text-start">סעיף עבודה (BOQ)</th>
              <th className="py-2.5 px-4 text-start">כמות / מ״ר</th>
              <th className="py-2.5 px-4 text-start">עלות ליחידה</th>
              <th className="py-2.5 px-4 text-start">סה״כ סעיף</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {vision.boq_items.map((item, idx) => (
              <tr key={idx} className="hover:bg-white/5">
                <td className="py-2.5 px-4 text-white font-medium">
                  {item.work_category}
                </td>
                <td className="py-2.5 px-4 text-slate-300">
                  {item.area_or_units}
                </td>
                <td className="py-2.5 px-4 text-slate-300">
                  {formatILS(item.unit_cost_ils)}
                </td>
                <td className="py-2.5 px-4 text-cyan-300 font-bold">
                  {formatILS(item.total_cost_ils)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-4 rounded-xl bg-slate-900/90 border border-white/10 flex items-center justify-between">
          <span className="text-xs text-slate-400">
            סה״כ אומדן שיפוץ דטרמיניסטי:
          </span>
          <span className="text-lg font-extrabold text-amber-300">
            {formatILS(vision.total_estimated_renovation_ils)}
          </span>
        </div>
        <div className="p-4 rounded-xl bg-slate-900/90 border border-emerald-500/30 flex items-center justify-between">
          <span className="text-xs text-slate-400">
            שווי נכס מוערך לאחר השבחה:
          </span>
          <span className="text-lg font-extrabold text-emerald-300">
            {formatILS(vision.estimated_post_renovation_value_ils)}
          </span>
        </div>
      </div>
    </div>
  );
}
