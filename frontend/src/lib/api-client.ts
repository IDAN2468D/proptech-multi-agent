import { z } from "zod";
import {
  InvestmentExecutiveReport,
  InvestmentExecutiveReportSchema,
} from "./schemas/agent-outputs.schema";
import {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  TokenResponseSchema,
  UserResponse,
  UserResponseSchema,
} from "./schemas/auth.schema";
import {
  AnalysisRunRequest,
  DocumentUploadResponse,
  DocumentUploadResponseSchema,
  HITLApproveRequest,
  InvestorProfile,
  InvestorProfileSchema,
  PropertyCreateRequest,
  PropertyResponse,
  PropertyResponseSchema,
} from "./schemas/property.schema";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

const TOKEN_STORAGE_KEY = "proptech_jwt_token";

export function getStoredToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_STORAGE_KEY);
}

export function setStoredToken(token: string): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(TOKEN_STORAGE_KEY, token);
  document.cookie = `proptech_token=${token}; path=/; max-age=3600; SameSite=Lax`;
}

export function clearStoredToken(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(TOKEN_STORAGE_KEY);
  document.cookie =
    "proptech_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
}

export class ApiClientError extends Error {
  status: number;
  code: string;
  traceId?: string;

  constructor(message: string, status: number, code = "API_ERROR", traceId?: string) {
    super(message);
    this.status = status;
    this.code = code;
    this.traceId = traceId;
  }
}

async function requestWithSchema<T>(
  path: string,
  schema: z.ZodType<T, z.ZodTypeDef, unknown>,
  options: RequestInit = {}
): Promise<T> {
  const token = getStoredToken();
  const headers = new Headers(options.headers || {});

  if (token && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  if (!(options.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    clearStoredToken();
  }

  const rawJson = await response.json().catch(() => ({}));

  if (!response.ok) {
    const errMsg =
      rawJson?.error?.message ||
      rawJson?.detail ||
      `שגיאת שרת (${response.status})`;
    const errCode = rawJson?.error?.code || "HTTP_ERROR";
    const traceId = rawJson?.error?.trace_id;
    throw new ApiClientError(errMsg, response.status, errCode, traceId);
  }

  return schema.parse(rawJson);
}

export const proptechApi = {
  register(payload: RegisterRequest): Promise<UserResponse> {
    return requestWithSchema("/api/v1/auth/register", UserResponseSchema, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async login(payload: LoginRequest): Promise<TokenResponse> {
    const res = await requestWithSchema(
      "/api/v1/auth/login",
      TokenResponseSchema,
      {
        method: "POST",
        body: JSON.stringify(payload),
      }
    );
    setStoredToken(res.access_token);
    return res;
  },

  getInvestorProfile(): Promise<InvestorProfile> {
    return requestWithSchema("/api/v1/investor/profile", InvestorProfileSchema);
  },

  updateInvestorProfile(
    payload: Partial<InvestorProfile>
  ): Promise<InvestorProfile> {
    return requestWithSchema("/api/v1/investor/profile", InvestorProfileSchema, {
      method: "PUT",
      body: JSON.stringify(payload),
    });
  },

  listProperties(): Promise<PropertyResponse[]> {
    return requestWithSchema(
      "/api/v1/properties",
      z.array(PropertyResponseSchema)
    );
  },

  createProperty(payload: PropertyCreateRequest): Promise<PropertyResponse> {
    return requestWithSchema("/api/v1/properties", PropertyResponseSchema, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  uploadPropertyDocument(
    propertyId: string,
    file: File
  ): Promise<DocumentUploadResponse> {
    const formData = new FormData();
    formData.append("file", file);
    return requestWithSchema(
      `/api/v1/properties/${propertyId}/documents`,
      DocumentUploadResponseSchema,
      {
        method: "POST",
        body: formData,
      }
    );
  },

  runAnalysis(payload: AnalysisRunRequest): Promise<InvestmentExecutiveReport> {
    return requestWithSchema(
      "/api/v1/analysis/run",
      InvestmentExecutiveReportSchema,
      {
        method: "POST",
        body: JSON.stringify(payload),
      }
    );
  },

  getAnalysisRun(runId: string): Promise<InvestmentExecutiveReport> {
    return requestWithSchema(
      `/api/v1/analysis/${runId}`,
      InvestmentExecutiveReportSchema
    );
  },

  approveHitlRun(
    runId: string,
    payload: HITLApproveRequest
  ): Promise<InvestmentExecutiveReport> {
    return requestWithSchema(
      `/api/v1/analysis/${runId}/approve`,
      InvestmentExecutiveReportSchema,
      {
        method: "POST",
        body: JSON.stringify(payload),
      }
    );
  },
};


import {
  MacroStressTestResult,
  MacroStressTestResultSchema,
  ShareDealResponse,
  ShareDealResponseSchema,
  VisionRenovationResult,
  VisionRenovationResultSchema,
} from "./schemas/agent-outputs-v2.schema";

export const proptechApiV2 = {
  uploadVisionFloorplan(
    propertyId: string,
    conditionHint: string,
    hasDampness: boolean
  ): Promise<VisionRenovationResult> {
    const form = new FormData();
    form.append("property_condition_hint", conditionHint);
    form.append("has_dampness_hint", String(hasDampness));
    return requestWithSchema(
      `/api/v1/properties/${propertyId}/vision-upload`,
      VisionRenovationResultSchema,
      {
        method: "POST",
        body: form,
      }
    );
  },

  runInteractiveStressTest(
    runId: string,
    payload: {
      interest_rate_pct: number;
      monthly_rent_ils: number;
      renovation_overrun_ils: number;
      equity_override_ils?: number;
    }
  ): Promise<MacroStressTestResult> {
    return requestWithSchema(
      `/api/v1/analysis/${runId}/stress-test`,
      MacroStressTestResultSchema,
      {
        method: "POST",
        body: JSON.stringify(payload),
      }
    );
  },

  shareDealPackage(
    runId: string,
    webhookChannel = "#proptech-deals"
  ): Promise<ShareDealResponse> {
    return requestWithSchema(
      `/api/v1/analysis/${runId}/share-deal`,
      ShareDealResponseSchema,
      {
        method: "POST",
        body: JSON.stringify({ webhook_channel: webhookChannel }),
      }
    );
  },
};
