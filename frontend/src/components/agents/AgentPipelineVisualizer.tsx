"use client";

import { motion } from "framer-motion";
import {
  Activity,
  BarChart3,
  Building2,
  Calculator,
  Cpu,
  Hammer,
  Handshake,
  Scale,
  ShieldAlert,
} from "lucide-react";
import { InvestmentExecutiveReport } from "@/lib/schemas/agent-outputs.schema";
import { AgentStatusBadge, AgentVisualState } from "./AgentStatusBadge";

export function AgentPipelineVisualizer({
  report,
}: {
  report: InvestmentExecutiveReport;
}) {
  const isRunning = report.run_status === "RUNNING";
  const isPaused = report.run_status === "PAUSED_FOR_APPROVAL";
  const isRejected = report.run_status === "REJECTED";

  const subAgentState: AgentVisualState = isRunning ? "RUNNING" : "COMPLETED";
  const criticState: AgentVisualState = isRunning
    ? "RUNNING"
    : isPaused
    ? "PAUSED_FOR_APPROVAL"
    : isRejected
    ? "REJECTED"
    : "COMPLETED";

  const agents = [
    {
      id: "orchestrator",
      title: "1. Orchestrator",
      subtitle: "Supervisor & Memory",
      icon: Cpu,
      state: subAgentState,
      detail: "תזמור מקבילי של 9 סוכנים וזיכרון משקיע ב-MongoDB",
    },
    {
      id: "market",
      title: "2. Market & Comps",
      subtitle: "עסקאות השוואה",
      icon: BarChart3,
      state: subAgentState,
      detail: report.market
        ? `${report.market.comparable_transactions_count} עסקאות | סטייה: ${report.market.market_deviation_pct}%`
        : "שולף נתוני שוק...",
    },
    {
      id: "financial",
      title: "3. Financial & ROI",
      subtitle: "Zero-Math Python",
      icon: Calculator,
      state: subAgentState,
      detail: report.financials
        ? `Cap: ${report.financials.net_cap_rate_pct}% | IRR: ${report.financials.projected_10yr_irr_pct}%`
        : "מחשב משכנתא ומס...",
    },
    {
      id: "legal",
      title: "4. Legal Tabu RAG",
      subtitle: "Vector Citations",
      icon: Scale,
      state: subAgentState,
      detail: report.legal
        ? `${report.legal.findings.length} ממצאים משפטיים מנסח הטאבו`
        : "סורק מקטעי PDF...",
    },
    {
      id: "critic",
      title: "5. Critic Guardrail",
      subtitle: "Fact-Check & HITL",
      icon: ShieldAlert,
      state: criticState,
      detail: report.critic
        ? `סיכון: ${report.critic.overall_risk_score}/100 | מתמטיקה: 100%`
        : "מצליב נתונים...",
    },
    {
      id: "vision",
      title: "6. Vision & BOQ",
      subtitle: "Floorplan & Renovation",
      icon: Hammer,
      state: subAgentState,
      detail: report.vision_renovation
        ? `כתב כמויות (BOQ): ₪${report.vision_renovation.total_estimated_renovation_ils.toLocaleString("he-IL")}`
        : "מנתח תשריט ושיפוץ...",
    },
    {
      id: "gis",
      title: "7. Urban Renewal GIS",
      subtitle: "תמ״א 38 / פינוי-בינוי",
      icon: Building2,
      state: subAgentState,
      detail: report.urban_renewal_gis
        ? `סבירות: ${report.urban_renewal_gis.tama38_or_pinui_binui_likelihood} | +${report.urban_renewal_gis.expected_additional_sqm} מ״ר`
        : "בודק תב״ע ורכבת קלה...",
    },
    {
      id: "stress",
      title: "8. Macro Stress-Test",
      subtitle: "1,000 Monte Carlo",
      icon: Activity,
      state: subAgentState,
      detail: report.macro_stress_test
        ? `הסתברות תזרים חיובי: ${report.macro_stress_test.probability_of_positive_cashflow_pct}%`
        : "מריץ מונטה-קרלו...",
    },
    {
      id: "negotiation",
      title: "9. AI Negotiation",
      subtitle: "Counter-Offer Playbook",
      icon: Handshake,
      state: subAgentState,
      detail: report.negotiation_playbook
        ? `מחיר יעד לסגירה: ₪${report.negotiation_playbook.target_closing_price_ils.toLocaleString("he-IL")}`
        : "מגבש הצעה נגדית...",
    },
  ];

  return (
    <div className="liquid-glass rounded-2xl p-6 space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h3 className="text-base font-bold text-white">
            טופולוגיית צוות 9 הסוכנים (v2.0 Multi-Agent & 5-MCP Pipeline)
          </h3>
          <p className="text-xs text-slate-400">
            ריצה מקבילית מבודדת-הקשר של סוכני השוק, הפיננסים, ה-RAG, ה-Vision,
            ה-GIS, ה-Stress-Test והמשא ומתן
          </p>
        </div>
        <AgentStatusBadge state={criticState} />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {agents.map((ag, idx) => {
          const Icon = ag.icon;
          return (
            <motion.div
              key={ag.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, delay: idx * 0.04 }}
              className={`transform-gpu rounded-xl p-3.5 border space-y-2 ${
                ag.state === "PAUSED_FOR_APPROVAL"
                  ? "bg-amber-950/30 border-amber-400/40"
                  : ag.state === "REJECTED"
                  ? "bg-rose-950/30 border-rose-400/40"
                  : "bg-slate-900/80 border-white/10"
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="p-2 rounded-lg bg-cyan-500/15 text-cyan-300">
                    <Icon className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-white">{ag.title}</h4>
                    <p className="text-[11px] text-cyan-400">{ag.subtitle}</p>
                  </div>
                </div>
                <AgentStatusBadge state={ag.state} />
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                {ag.detail}
              </p>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
