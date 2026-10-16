"use client";

import { useState } from "react";
import { Sparkles } from "lucide-react";
import {
  PropertyCreateRequest,
  PropertyCreateRequestSchema,
} from "@/lib/schemas/property.schema";

interface PropertyFormProps {
  defaultEquityIls: number;
  isSubmitting: boolean;
  onSubmitWizard: (
    propertyData: PropertyCreateRequest,
    financing: {
      equity_ils: number;
      annual_interest_rate_pct: number;
      loan_years: number;
    }
  ) => Promise<void>;
}

export function PropertyForm({
  defaultEquityIls,
  isSubmitting,
  onSubmitWizard,
}: PropertyFormProps) {
  const [address, setAddress] = useState("שדרות הנשיא 45");
  const [city, setCity] = useState("חיפה");
  const [neighborhood, setNeighborhood] = useState("מרכז הכרמל");
  const [askingPrice, setAskingPrice] = useState(1900000);
  const [areaSqm, setAreaSqm] = useState(105);
  const [rooms, setRooms] = useState(4);
  const [floor, setFloor] = useState(3);
  const [estimatedRent, setEstimatedRent] = useState(6800);
  const [isSingleHome, setIsSingleHome] = useState(true);

  const [equityIls, setEquityIls] = useState(defaultEquityIls || 1100000);
  const [interestRate, setInterestRate] = useState(4.75);
  const [loanYears, setLoanYears] = useState(25);
  const [validationError, setValidationError] = useState<string | null>(null);

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);

    const parsed = PropertyCreateRequestSchema.safeParse({
      address,
      city,
      neighborhood,
      asking_price_ils: Number(askingPrice),
      area_sqm: Number(areaSqm),
      rooms: Number(rooms),
      floor: Number(floor),
      estimated_monthly_rent_ils: Number(estimatedRent),
      is_single_home: isSingleHome,
    });

    if (!parsed.success) {
      setValidationError(
        parsed.error.issues.map((i) => i.message).join(" | ")
      );
      return;
    }

    await onSubmitWizard(parsed.data, {
      equity_ils: Number(equityIls),
      annual_interest_rate_pct: Number(interestRate),
      loan_years: Number(loanYears),
    });
  };

  return (
    <form
      onSubmit={handleFormSubmit}
      className="liquid-glass rounded-2xl p-6 space-y-6"
    >
      <h3 className="text-base font-bold text-white">
        פרטי הנכס ותנאי המימון לבדיקה
      </h3>

      {validationError && (
        <div className="p-3.5 rounded-xl bg-rose-500/15 border border-rose-500/40 text-rose-200 text-xs">
          {validationError}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-xs text-slate-300 mb-1">עיר</label>
          <input
            type="text"
            value={city}
            onChange={(e) => setCity(e.target.value)}
            className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950/80 border border-white/10 text-white text-sm"
          />
        </div>
        <div>
          <label className="block text-xs text-slate-300 mb-1">כתובת הנכס</label>
          <input
            type="text"
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950/80 border border-white/10 text-white text-sm"
          />
        </div>
        <div>
          <label className="block text-xs text-slate-300 mb-1">שכונה</label>
          <input
            type="text"
            value={neighborhood}
            onChange={(e) => setNeighborhood(e.target.value)}
            className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950/80 border border-white/10 text-white text-sm"
          />
        </div>

        <div>
          <label className="block text-xs text-slate-300 mb-1">
            מחיר מבוקש (₪)
          </label>
          <input
            type="number"
            value={askingPrice}
            onChange={(e) => setAskingPrice(Number(e.target.value))}
            className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950/80 border border-white/10 text-white text-sm"
          />
        </div>
        <div>
          <label className="block text-xs text-slate-300 mb-1">
            שטח במודעה (מ״ר)
          </label>
          <input
            type="number"
            value={areaSqm}
            onChange={(e) => setAreaSqm(Number(e.target.value))}
            className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950/80 border border-white/10 text-white text-sm"
          />
        </div>
        <div>
          <label className="block text-xs text-slate-300 mb-1">
            שכירות חודשית משוערת (₪)
          </label>
          <input
            type="number"
            value={estimatedRent}
            onChange={(e) => setEstimatedRent(Number(e.target.value))}
            className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950/80 border border-white/10 text-white text-sm"
          />
        </div>

        <div>
          <label className="block text-xs text-slate-300 mb-1">חדרים</label>
          <input
            type="number"
            step="0.5"
            value={rooms}
            onChange={(e) => setRooms(Number(e.target.value))}
            className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950/80 border border-white/10 text-white text-sm"
          />
        </div>
        <div>
          <label className="block text-xs text-slate-300 mb-1">קומה</label>
          <input
            type="number"
            value={floor}
            onChange={(e) => setFloor(Number(e.target.value))}
            className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950/80 border border-white/10 text-white text-sm"
          />
        </div>
        <div>
          <label className="block text-xs text-slate-300 mb-1">
            הון עצמי לעסקה (₪)
          </label>
          <input
            type="number"
            value={equityIls}
            onChange={(e) => setEquityIls(Number(e.target.value))}
            className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950/80 border border-white/10 text-white text-sm"
          />
        </div>

        <div>
          <label className="block text-xs text-slate-300 mb-1">
            ריבית משכנתא שנתית (%)
          </label>
          <input
            type="number"
            step="0.05"
            value={interestRate}
            onChange={(e) => setInterestRate(Number(e.target.value))}
            className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950/80 border border-white/10 text-white text-sm"
          />
        </div>
        <div>
          <label className="block text-xs text-slate-300 mb-1">
            תקופת משכנתא (שנים)
          </label>
          <input
            type="number"
            value={loanYears}
            onChange={(e) => setLoanYears(Number(e.target.value))}
            className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950/80 border border-white/10 text-white text-sm"
          />
        </div>
        <div className="flex items-end pb-2">
          <label className="flex items-center gap-2 cursor-pointer text-xs text-slate-200">
            <input
              type="checkbox"
              checked={isSingleHome}
              onChange={(e) => setIsSingleHome(e.target.checked)}
              className="w-4 h-4 accent-cyan-400"
            />
            דירה יחידה (פטור/מדרגות מופחתות במס רכישה)
          </label>
        </div>
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full py-3.5 rounded-xl bg-gradient-to-l from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-bold shadow-lg shadow-cyan-500/20 flex items-center justify-center gap-2 transition disabled:opacity-50"
      >
        <Sparkles className="w-5 h-5" />
        {isSubmitting
          ? "מאנדקס מסמכים ב-RAG ומפעיל 5 סוכנים במקביל..."
          : "שמור נכס, אנדקס PDF והזנק צוות סוכנים"}
      </button>
    </form>
  );
}
