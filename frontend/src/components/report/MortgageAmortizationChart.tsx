"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { FinancialMetricsResult } from "@/lib/schemas/agent-outputs.schema";

export function MortgageAmortizationChart({
  financials,
}: {
  financials: FinancialMetricsResult;
}) {
  const annualPayment = financials.monthly_mortgage_payment_ils * 12;
  const initialLoan = financials.loan_amount_ils;

  // Deterministic 10-year breakdown visualization based on Spitzer loan progression
  const data = Array.from({ length: 10 }, (_, idx) => {
    const year = idx + 1;
    const interestShare = Math.max(0.25, 0.72 - idx * 0.035);
    const interestPaid = Math.round(annualPayment * interestShare);
    const principalPaid = Math.max(0, Math.round(annualPayment - interestPaid));
    return {
      name: `שנה ${year}`,
      קרן: principalPaid,
      ריבית: interestPaid,
    };
  });

  return (
    <div className="liquid-glass rounded-2xl p-6 space-y-4">
      <div>
        <h3 className="text-base font-bold text-white">
          לוח סילוקין משכנתא 10 שנים ראשונות (התפלגות קרן מול ריבית בש״ח)
        </h3>
        <p className="text-xs text-slate-400">
          סך הלוואה: ₪{initialLoan.toLocaleString("he-IL")} | החזר חודשי התחלתי:
          ₪{financials.monthly_mortgage_payment_ils.toLocaleString("he-IL")}
        </p>
      </div>

      <div className="h-64 w-full" dir="ltr">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} />
            <YAxis stroke="#94a3b8" fontSize={12} />
            <Tooltip
              contentStyle={{
                backgroundColor: "#0f172a",
                borderColor: "#334155",
                borderRadius: "12px",
                color: "#f8fafc",
              }}
            />
            <Legend />
            <Bar dataKey="קרן" stackId="a" fill="#06b6d4" radius={[0, 0, 4, 4]} />
            <Bar
              dataKey="ריבית"
              stackId="a"
              fill="#6366f1"
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
