"use client";

import { AlertTriangle, CheckCircle2, Loader2, XCircle } from "lucide-react";

export type AgentVisualState =
  | "RUNNING"
  | "COMPLETED"
  | "PAUSED_FOR_APPROVAL"
  | "REJECTED";

export function AgentStatusBadge({ state }: { state: AgentVisualState }) {
  if (state === "RUNNING") {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-cyan-500/20 border border-cyan-400/40 text-cyan-300 text-xs font-semibold">
        <Loader2 className="w-3.5 h-3.5 animate-spin" />
        פעיל במקביל
      </span>
    );
  }

  if (state === "PAUSED_FOR_APPROVAL") {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-amber-500/20 border border-amber-400/40 text-amber-300 text-xs font-semibold">
        <AlertTriangle className="w-3.5 h-3.5" />
        ממתין לאישור HITL
      </span>
    );
  }

  if (state === "REJECTED") {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-rose-500/20 border border-rose-400/40 text-rose-300 text-xs font-semibold">
        <XCircle className="w-3.5 h-3.5" />
        נבלם / נדחה
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/20 border border-emerald-400/40 text-emerald-300 text-xs font-semibold">
      <CheckCircle2 className="w-3.5 h-3.5" />
      הושלם ואומת
    </span>
  );
}
