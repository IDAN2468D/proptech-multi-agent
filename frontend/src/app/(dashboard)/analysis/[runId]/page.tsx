"use client";

import { use, useEffect } from "react";
import { AgentPipelineVisualizer } from "@/components/agents/AgentPipelineVisualizer";
import { HitlApprovalModal } from "@/components/agents/HitlApprovalModal";
import { spatialAudio } from "@/components/audio/SpatialAudioFeedback";
import { NegotiationPlaybookCard } from "@/components/negotiation/NegotiationPlaybookCard";
import { ExecutiveSummaryHero } from "@/components/report/ExecutiveSummaryHero";
import { FinancialMetricsGrid } from "@/components/report/FinancialMetricsGrid";
import { LegalRagFindingsList } from "@/components/report/LegalRagFindingsList";
import { MarketCompsSection } from "@/components/report/MarketCompsSection";
import { MortgageAmortizationChart } from "@/components/report/MortgageAmortizationChart";
import { InteractiveWhatIfSandbox } from "@/components/stress-test/InteractiveWhatIfSandbox";
import { UrbanRenewalGisCard } from "@/components/urban/UrbanRenewalGisCard";
import { FloorplanVisionAnalyzer } from "@/components/vision/FloorplanVisionAnalyzer";
import { useAnalysisRun } from "@/hooks/use-analysis-run";

export default function AnalysisRunPage({
  params,
}: {
  params: Promise<{ runId: string }>;
}) {
  const { runId } = use(params);
  const { report, isLoading, error, approveHitl, isApprovingHitl } =
    useAnalysisRun(runId);

  useEffect(() => {
    if (!report) return;
    if (report.status === "PAUSED_FOR_APPROVAL") {
      spatialAudio.playSpatialCue("HITL_WARNING", 0.5);
    } else if (report.status === "COMPLETED") {
      spatialAudio.playSpatialCue("AGENT_DONE", 0);
    }
  }, [report?.status]);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-44 rounded-2xl liquid-glass animate-pulse" />
        <div className="h-64 rounded-2xl liquid-glass animate-pulse" />
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="liquid-glass rounded-2xl p-8 text-center space-y-2 border border-rose-500/30">
        <h3 className="text-lg font-bold text-rose-300">
          שגיאה בטעינת דוח הניתוח
        </h3>
        <p className="text-sm text-slate-400">
          {error instanceof Error ? error.message : "הריצה המבוקשת לא נמצאה"}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Live 9-Agent Pipeline Visualizer (v2.0) */}
      <AgentPipelineVisualizer report={report} />

      {/* Human-In-The-Loop Approval Modal (shown when PAUSED_FOR_APPROVAL) */}
      <HitlApprovalModal
        report={report}
        isSubmitting={isApprovingHitl}
        onSubmitDecision={async (payload) => {
          await approveHitl(payload);
        }}
      />

      {/* Executive Summary + Risk Gauge */}
      <ExecutiveSummaryHero report={report} />

      {/* Financial Metrics Cards */}
      {report.financials && (
        <FinancialMetricsGrid financials={report.financials} />
      )}

      {/* v2.0 Agent 9: AI Negotiation & Counter-Offer Playbook + WhatsApp/Telegram Share */}
      {report.negotiation_playbook && (
        <NegotiationPlaybookCard
          runId={report.run_id}
          playbook={report.negotiation_playbook}
        />
      )}

      {/* v2.0 Agent 8: Interactive What-If Sandbox & Monte Carlo Stress-Test */}
      {report.macro_stress_test && (
        <InteractiveWhatIfSandbox
          runId={report.run_id}
          initialStress={report.macro_stress_test}
          defaultRentIls={
            report.financials
              ? Math.round(
                  report.financials.monthly_mortgage_payment_ils +
                    report.financials.net_monthly_cashflow_ils
                )
              : 5200
          }
        />
      )}

      {/* v2.0 Agent 6 & Agent 7: Vision CAPEX & Urban Renewal GIS */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {report.vision_renovation && (
          <FloorplanVisionAnalyzer
            propertyId={report.property_id}
            initialVision={report.vision_renovation}
          />
        )}
        {report.urban_renewal_gis && (
          <UrbanRenewalGisCard gis={report.urban_renewal_gis} />
        )}
      </div>

      {/* Charts: Mortgage Amortization & Market Comps */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {report.financials && (
          <MortgageAmortizationChart financials={report.financials} />
        )}
        {report.market && <MarketCompsSection market={report.market} />}
      </div>

      {/* Legal RAG Findings with Exact Citations */}
      {report.legal && <LegalRagFindingsList legal={report.legal} />}
    </div>
  );
}
