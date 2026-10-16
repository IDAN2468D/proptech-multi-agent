import { z } from "zod";

export const RenovationItemSchema = z.object({
  work_category: z.string(),
  area_or_units: z.number(),
  unit_cost_ils: z.number(),
  total_cost_ils: z.number(),
});

export const VisionRenovationResultSchema = z.object({
  property_condition: z.enum([
    "NEW",
    "GOOD",
    "NEEDS_COSMETIC_RENOVATION",
    "NEEDS_FULL_RENOVATION",
  ]),
  can_add_room_or_split: z.boolean(),
  structural_notes: z.array(z.string()),
  boq_items: z.array(RenovationItemSchema),
  total_estimated_renovation_ils: z.number(),
  estimated_post_renovation_value_ils: z.number(),
});

export const UrbanRenewalGISResultSchema = z.object({
  tama38_or_pinui_binui_likelihood: z.enum([
    "LOW",
    "MEDIUM",
    "HIGH",
    "ACTIVE_PLAN",
  ]),
  distance_to_light_rail_meters: z.number().int(),
  walkability_score: z.number().int().min(1).max(100),
  expected_additional_sqm: z.number(),
  projected_renewal_upside_pct: z.number(),
});

export const MacroStressTestResultSchema = z.object({
  base_case_monthly_cashflow_ils: z.number(),
  rate_hike_plus_1_5_pct_cashflow_ils: z.number(),
  vacancy_2_months_annual_cashflow_ils: z.number(),
  combined_worst_case_monthly_cashflow_ils: z.number(),
  probability_of_positive_cashflow_pct: z.number(),
  max_safe_interest_rate_pct: z.number(),
});

export const PriceReductionJustificationSchema = z.object({
  reason: z.string(),
  deduction_amount_ils: z.number(),
  evidence_source: z.string(),
});

export const NegotiationPlaybookResultSchema = z.object({
  asking_price_ils: z.number(),
  recommended_opening_offer_ils: z.number(),
  target_closing_price_ils: z.number(),
  walk_away_max_price_ils: z.number(),
  price_reduction_justifications: z.array(PriceReductionJustificationSchema),
  ready_to_send_hebrew_message: z.string(),
});

export const ShareDealResponseSchema = z.object({
  dispatched: z.boolean(),
  run_id: z.string(),
  webhook_channel: z.string(),
  slack_message_preview: z.string(),
  calendar_ics: z.string(),
});

export type RenovationItem = z.infer<typeof RenovationItemSchema>;
export type VisionRenovationResult = z.infer<typeof VisionRenovationResultSchema>;
export type UrbanRenewalGISResult = z.infer<typeof UrbanRenewalGISResultSchema>;
export type MacroStressTestResult = z.infer<typeof MacroStressTestResultSchema>;
export type NegotiationPlaybookResult = z.infer<
  typeof NegotiationPlaybookResultSchema
>;
export type ShareDealResponse = z.infer<typeof ShareDealResponseSchema>;
