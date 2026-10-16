import { z } from "zod";
import {
  MacroStressTestResultSchema,
  NegotiationPlaybookResultSchema,
  UrbanRenewalGISResultSchema,
  VisionRenovationResultSchema,
} from "./agent-outputs-v2.schema";

export const MarketAnalysisResultSchema = z.object({
  avg_price_per_sqm_ils: z.number(),
  subject_price_per_sqm_ils: z.number(),
  market_deviation_pct: z.number(),
  estimated_monthly_rent_ils: z.number(),
  comparable_transactions_count: z.number().int(),
  neighborhood_highlights: z.array(z.string()),
});

export const FinancialMetricsResultSchema = z.object({
  purchase_tax_ils: z.number(),
  loan_amount_ils: z.number(),
  loan_to_value_pct: z.number(),
  monthly_mortgage_payment_ils: floatOrNum(),
  net_monthly_cashflow_ils: z.number(),
  gross_yield_pct: z.number(),
  net_cap_rate_pct: z.number(),
  cash_on_cash_return_pct: z.number(),
  projected_10yr_irr_pct: z.number(),
});

function floatOrNum() {
  return z.number();
}

export const LegalFindingSchema = z.object({
  category: z.string(),
  severity: z.enum(["LOW", "MEDIUM", "HIGH", "CRITICAL"]),
  description: z.string(),
  source_document: z.string(),
  page_number: z.number().int(),
  exact_quote: z.string(),
});

export const LegalDueDiligenceResultSchema = z.object({
  findings: z.array(LegalFindingSchema),
  registered_area_sqm: z.number().nullable().optional(),
  has_blocking_liens_or_warnings: z.boolean(),
});

export const CriticVerdictSchema = z.object({
  status: z.enum(["APPROVED", "NEEDS_HUMAN_REVIEW", "REJECTED"]),
  overall_risk_score: z.number().int().min(1).max(100),
  context_clashes_detected: z.array(z.string()),
  math_verification_passed: z.boolean(),
  hitl_reason: z.string().nullable().optional(),
});

export const InvestmentExecutiveReportSchema = z
  .object({
    run_id: z.string(),
    property_id: z.string().optional(),
    status: z
      .enum(["RUNNING", "PAUSED_FOR_APPROVAL", "COMPLETED", "REJECTED", "FAILED"])
      .optional(),
    run_status: z
      .enum(["RUNNING", "PAUSED_FOR_APPROVAL", "COMPLETED", "REJECTED", "FAILED"])
      .optional(),
    investment_recommendation: z
      .enum(["STRONG_BUY", "BUY_WITH_CAUTION", "HOLD_FOR_REVIEW", "AVOID"])
      .optional(),
    executive_summary: z.string().optional(),
    market: MarketAnalysisResultSchema.optional(),
    financials: FinancialMetricsResultSchema.optional(),
    legal: LegalDueDiligenceResultSchema.optional(),
    critic: CriticVerdictSchema.optional(),
    vision_renovation: VisionRenovationResultSchema.nullable().optional(),
    urban_renewal_gis: UrbanRenewalGISResultSchema.nullable().optional(),
    macro_stress_test: MacroStressTestResultSchema.nullable().optional(),
    negotiation_playbook: NegotiationPlaybookResultSchema.nullable().optional(),
  })
  .transform((data) => ({
    ...data,
    run_status: data.run_status ?? data.status ?? "COMPLETED",
  }));

export type MarketAnalysisResult = z.infer<typeof MarketAnalysisResultSchema>;
export type FinancialMetricsResult = z.infer<typeof FinancialMetricsResultSchema>;
export type LegalFinding = z.infer<typeof LegalFindingSchema>;
export type LegalDueDiligenceResult = z.infer<typeof LegalDueDiligenceResultSchema>;
export type CriticVerdict = z.infer<typeof CriticVerdictSchema>;
export type InvestmentExecutiveReport = z.infer<typeof InvestmentExecutiveReportSchema>;
