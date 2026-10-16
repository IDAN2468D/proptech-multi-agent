import { z } from "zod";

export const InvestorProfileSchema = z.object({
  user_id: z.string().nullable().optional(),
  available_equity_ils: z.number().positive("הון עצמי חייב להיות חיובי"),
  risk_tolerance: z.enum(["CONSERVATIVE", "MODERATE", "AGGRESSIVE"]),
  max_risk_score_threshold: z.number().int().min(1).max(100),
  min_target_net_yield_pct: z.number().min(0),
  preferred_cities: z.array(z.string()),
  is_single_home_buyer: z.boolean(),
  analysis_history: z.array(z.record(z.any())).optional().default([]),
});

export const PropertyCreateRequestSchema = z.object({
  address: z.string().min(3, "כתובת חייבת להכיל לפחות 3 תווים"),
  city: z.string().min(2, "יש להזין שם עיר"),
  neighborhood: z.string().default(""),
  asking_price_ils: z.number().positive("מחיר מבוקש חייב להיות גדול מ-0"),
  area_sqm: z.number().min(11, 'שטח במ"ר חייב להיות גדול מ-10'),
  rooms: z.number().min(1, "מספר חדרים לא תקין"),
  floor: z.number().int(),
  estimated_monthly_rent_ils: z.number().positive().nullable().optional(),
  is_single_home: z.boolean().default(false),
});

export const PropertyResponseSchema = z.object({
  id: z.string(),
  owner_user_id: z.string(),
  address: z.string(),
  city: z.string(),
  neighborhood: z.string(),
  asking_price_ils: z.number(),
  area_sqm: z.number(),
  rooms: z.number(),
  floor: z.number().int(),
  estimated_monthly_rent_ils: z.number().nullable().optional(),
  is_single_home: z.boolean(),
});

export const DocumentUploadResponseSchema = z.object({
  property_id: z.string(),
  filename: z.string(),
  chunks_indexed: z.number().int(),
  pages_extracted: z.number().int(),
  sanitized_warnings: z.array(z.string()).default([]),
});

export const AnalysisRunRequestSchema = z.object({
  property_id: z.string(),
  equity_ils: z.number().positive().optional(),
  annual_interest_rate_pct: z.number().min(0.1).max(20).default(4.85),
  loan_years: z.number().int().min(4).max(35).default(25),
  annual_expenses_ils: z.number().min(0).default(6000),
  appreciation_rate_pct: z.number().min(-10).max(25).default(3.0),
});

export const HITLApproveRequestSchema = z.object({
  approved: z.boolean().default(true),
  updated_asking_price_ils: z.number().positive().nullable().optional(),
  updated_equity_ils: z.number().positive().nullable().optional(),
  investor_notes: z.string().default(""),
});

export type InvestorProfile = z.infer<typeof InvestorProfileSchema>;
export type PropertyCreateRequest = z.infer<typeof PropertyCreateRequestSchema>;
export type PropertyResponse = z.infer<typeof PropertyResponseSchema>;
export type DocumentUploadResponse = z.infer<typeof DocumentUploadResponseSchema>;
export type AnalysisRunRequest = z.infer<typeof AnalysisRunRequestSchema>;
export type HITLApproveRequest = z.infer<typeof HITLApproveRequestSchema>;
