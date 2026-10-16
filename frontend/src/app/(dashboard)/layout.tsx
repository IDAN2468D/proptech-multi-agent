"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  BrainCircuit,
  Building2,
  FolderPlus,
  LayoutDashboard,
  LogOut,
  ShieldCheck,
  UserCog,
  Volume2,
  VolumeX,
  Wallet,
} from "lucide-react";
import { spatialAudio } from "@/components/audio/SpatialAudioFeedback";
import { clearStoredToken } from "@/lib/api-client";
import { formatILS, formatPct } from "@/lib/formatters";
import { useInvestorProfile } from "@/hooks/use-investor-profile";

const NAV_ITEMS = [
  {
    href: "/dashboard",
    label: "חדר בקרה ונכסים",
    icon: LayoutDashboard,
  },
  {
    href: "/properties/new",
    label: "בדיקת נכס חדש + RAG",
    icon: FolderPlus,
  },
  {
    href: "/investor-profile",
    label: "פרופיל משקיע (Memory)",
    icon: UserCog,
  },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const { profile } = useInvestorProfile();
  const [isAudioMuted, setIsAudioMuted] = useState(false);

  const handleToggleAudio = () => {
    const muted = spatialAudio.toggleMute();
    setIsAudioMuted(muted);
    if (!muted) {
      spatialAudio.playSpatialCue("AGENT_DONE", 0);
    }
  };

  const handleLogout = async () => {
    clearStoredToken();
    await fetch("/api/auth", { method: "DELETE" });
    router.push("/login");
  };

  return (
    <div className="min-h-screen flex bg-slate-950 text-slate-100">
      {/* RTL Sidebar */}
      <aside className="w-72 liquid-glass border-e border-white/10 p-6 flex flex-col justify-between shrink-0">
        <div className="space-y-8">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-cyan-500/20 border border-cyan-400/30 text-cyan-300">
              <Building2 className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white tracking-tight">
                PropTech AI v2.0
              </h2>
              <span className="text-xs text-cyan-400 flex items-center gap-1">
                <BrainCircuit className="w-3.5 h-3.5" />9 סוכנים פעילים
              </span>
            </div>
          </div>

          <nav className="space-y-2">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const active = pathname.startsWith(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition ${
                    active
                      ? "bg-cyan-500/20 text-cyan-300 border border-cyan-400/30 shadow-md shadow-cyan-950/50"
                      : "text-slate-300 hover:bg-white/5 hover:text-white"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-slate-900/80 border border-white/10 space-y-2 text-xs">
            <div className="flex items-center gap-1.5 text-emerald-400 font-semibold">
              <ShieldCheck className="w-4 h-4" />
              Zero-Math Hallucination
            </div>
            <p className="text-slate-400 leading-relaxed">
              כל חישובי המס, המשכנתא, ה-IRR והשיפוץ מאומתים דטרמיניסטית בפייתון
              מול סוכן ה-Critic.
            </p>
          </div>

          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/20 text-sm transition"
          >
            <LogOut className="w-4 h-4" />
            התנתקות מהמערכת
          </button>
        </div>
      </aside>

      {/* Main Content + Topbar */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-20 liquid-glass border-b border-white/10 px-8 flex items-center justify-between">
          <div>
            <h1 className="text-lg font-bold text-white">
              חדר בקרה להשקעות נדל״ן (Investment Command Center v2.0)
            </h1>
            <p className="text-xs text-slate-400">
              9 סוכנים: שוק, מיסוי, משכנתא, RAG משפטי, ראייה ממוחשבת, GIS תמ״א,
              מונטה-קרלו ומו״מ
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleToggleAudio}
              title="Spatial Audio Feedback (Web Audio API)"
              className="px-3 py-2 rounded-xl bg-slate-900/90 border border-white/10 hover:border-cyan-500/40 text-xs text-slate-300 flex items-center gap-1.5 transition"
            >
              {isAudioMuted ? (
                <>
                  <VolumeX className="w-4 h-4 text-rose-400" />
                  <span>סאונד מושתק</span>
                </>
              ) : (
                <>
                  <Volume2 className="w-4 h-4 text-cyan-400" />
                  <span>Spatial Audio</span>
                </>
              )}
            </button>

            {profile && (
              <>
                <div className="px-4 py-2 rounded-xl bg-slate-900/90 border border-cyan-500/30 flex items-center gap-3">
                  <Wallet className="w-4 h-4 text-cyan-400" />
                  <div className="text-xs">
                    <span className="text-slate-400 block">הון עצמי זמין</span>
                    <span className="text-white font-bold">
                      {formatILS(profile.available_equity_ils)}
                    </span>
                  </div>
                </div>
                <div className="px-4 py-2 rounded-xl bg-slate-900/90 border border-white/10 text-xs">
                  <span className="text-slate-400 block">
                    יעד תשואה / סף סיכון
                  </span>
                  <span className="text-emerald-400 font-bold">
                    {formatPct(profile.min_target_net_yield_pct)} | עד{" "}
                    {profile.max_risk_score_threshold}/100
                  </span>
                </div>
              </>
            )}
          </div>
        </header>

        <main className="flex-1 p-8 overflow-y-auto">{children}</main>
      </div>
    </div>
  );
}
