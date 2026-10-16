"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  ArrowUpLeft,
  Building,
  FileSearch,
  FolderPlus,
  History,
  MapPin,
  Play,
} from "lucide-react";
import { formatILS, formatSqm } from "@/lib/formatters";
import { useAnalysisRun } from "@/hooks/use-analysis-run";
import { useInvestorProfile } from "@/hooks/use-investor-profile";
import { usePropertiesList } from "@/hooks/use-property-documents";

export default function DashboardPage() {
  const router = useRouter();
  const { data: properties, isLoading } = usePropertiesList();
  const { profile } = useInvestorProfile();
  const { startAnalysis, isStarting } = useAnalysisRun();

  const handleQuickRun = async (propertyId: string) => {
    const report = await startAnalysis({
      property_id: propertyId,
      equity_ils: profile?.available_equity_ils || 900000,
      annual_interest_rate_pct: 4.85,
      loan_years: 25,
      annual_expenses_ils: 6000,
      appreciation_rate_pct: 3.0,
    });
    router.push(`/analysis/${report.run_id}`);
  };

  return (
    <div className="space-y-8">
      {/* Top Call to Action Banner */}
      <div className="liquid-glass-glow rounded-2xl p-6 flex flex-wrap items-center justify-between gap-4">
        <div className="space-y-1">
          <h2 className="text-xl font-bold text-white">
            ניתוח עסקת נדל״ן באמצעות צוות סוכנים אוטונומי
          </h2>
          <p className="text-sm text-slate-300">
            הזן פרטי נכס והעלה נסח טאבו/חוזה מכר כדי להפעיל במקביל את סוכן השוק,
            הסוכן הפיננסי, סוכן ה-RAG המשפטי וסוכן ה-Critic.
          </p>
        </div>
        <Link
          href="/properties/new"
          className="px-5 py-3 rounded-xl bg-gradient-to-l from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold flex items-center gap-2 shadow-lg shadow-cyan-500/20 transition"
        >
          <FolderPlus className="w-4 h-4" />
          הוספת נכס והעלאת מסמכי PDF
        </Link>
      </div>

      {/* Properties Grid */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <Building className="w-5 h-5 text-cyan-400" />
            הנכסים השמורים בתיק המשקיע
          </h3>
          <span className="text-xs text-slate-400">
            {properties?.length || 0} נכסים רשומים
          </span>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="h-48 rounded-2xl liquid-glass animate-pulse p-6"
              />
            ))}
          </div>
        ) : !properties?.length ? (
          <div className="liquid-glass rounded-2xl p-10 text-center space-y-3">
            <FileSearch className="w-10 h-10 text-cyan-400 mx-auto" />
            <h4 className="text-base font-semibold text-white">
              עדיין לא הוזנו נכסים לבדיקה
            </h4>
            <p className="text-sm text-slate-400 max-w-md mx-auto">
              התחל על ידי הקמת נכס חדש והעלאת קובץ ה-PDF של נסח הטאבו או החוזה.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {properties.map((prop) => (
              <div
                key={prop.id}
                className="liquid-glass rounded-2xl p-6 flex flex-col justify-between space-y-5 hover:border-cyan-400/40 transition"
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="px-2.5 py-1 rounded-lg bg-cyan-500/15 text-cyan-300 text-xs font-medium flex items-center gap-1">
                      <MapPin className="w-3.5 h-3.5" />
                      {prop.city}
                    </span>
                    <span className="text-xs text-slate-400">
                      {prop.rooms} חד׳ | קומה {prop.floor}
                    </span>
                  </div>
                  <h4 className="text-lg font-bold text-white">
                    {prop.address}
                  </h4>
                  <div className="grid grid-cols-2 gap-2 pt-2 text-xs">
                    <div className="p-2.5 rounded-xl bg-slate-900/80 border border-white/5">
                      <span className="text-slate-400 block">מחיר מבוקש</span>
                      <span className="text-white font-bold text-sm">
                        {formatILS(prop.asking_price_ils)}
                      </span>
                    </div>
                    <div className="p-2.5 rounded-xl bg-slate-900/80 border border-white/5">
                      <span className="text-slate-400 block">שטח במודעה</span>
                      <span className="text-white font-bold text-sm">
                        {formatSqm(prop.area_sqm)}
                      </span>
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => handleQuickRun(prop.id)}
                  disabled={isStarting}
                  className="w-full py-2.5 px-4 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 border border-cyan-400/30 text-cyan-200 text-sm font-semibold flex items-center justify-center gap-2 transition disabled:opacity-50"
                >
                  <Play className="w-4 h-4" />
                  הפעל ניתוח מולטי-סוכנים
                </button>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Investor Long-Term Memory History */}
      {profile?.analysis_history && profile.analysis_history.length > 0 && (
        <section className="space-y-4">
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <History className="w-5 h-5 text-cyan-400" />
            היסטוריית בדיקות אחרונות (Long-Term Memory)
          </h3>
          <div className="liquid-glass rounded-2xl overflow-hidden">
            <table className="w-full text-sm text-start">
              <thead className="bg-slate-900/90 text-slate-400 text-xs border-b border-white/10">
                <tr>
                  <th className="py-3.5 px-5 text-start">מזהה ריצה</th>
                  <th className="py-3.5 px-5 text-start">עיר</th>
                  <th className="py-3.5 px-5 text-start">המלצת המערכת</th>
                  <th className="py-3.5 px-5 text-start">ציון סיכון</th>
                  <th className="py-3.5 px-5 text-start">פעולה</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {profile.analysis_history.map((item, idx) => (
                  <tr key={idx} className="hover:bg-white/5">
                    <td className="py-3.5 px-5 font-mono text-xs text-slate-300">
                      {String(item.run_id).slice(0, 12)}...
                    </td>
                    <td className="py-3.5 px-5 text-white">{item.city}</td>
                    <td className="py-3.5 px-5 font-semibold text-cyan-300">
                      {item.recommendation}
                    </td>
                    <td className="py-3.5 px-5">{item.risk_score}/100</td>
                    <td className="py-3.5 px-5">
                      <Link
                        href={`/analysis/${item.run_id}`}
                        className="text-cyan-400 hover:text-cyan-300 inline-flex items-center gap-1 text-xs font-semibold"
                      >
                        צפה בדוח המלא
                        <ArrowUpLeft className="w-3.5 h-3.5" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
}
