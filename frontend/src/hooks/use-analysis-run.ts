"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { proptechApi } from "@/lib/api-client";
import {
  AnalysisRunRequest,
  HITLApproveRequest,
} from "@/lib/schemas/property.schema";

export function useAnalysisRun(runId?: string) {
  const queryClient = useQueryClient();

  const runQuery = useQuery({
    queryKey: ["analysis-run", runId],
    queryFn: () => proptechApi.getAnalysisRun(runId as string),
    enabled: Boolean(runId),
    refetchInterval: (query) => {
      const status = query.state.data?.run_status;
      return status === "RUNNING" ? 2000 : false;
    },
  });

  const startRunMutation = useMutation({
    mutationFn: (payload: AnalysisRunRequest) =>
      proptechApi.runAnalysis(payload),
    onSuccess: (report) => {
      queryClient.setQueryData(["analysis-run", report.run_id], report);
      queryClient.invalidateQueries({ queryKey: ["investor-profile"] });
    },
  });

  const approveHitlMutation = useMutation({
    mutationFn: (payload: HITLApproveRequest) =>
      proptechApi.approveHitlRun(runId as string, payload),
    onSuccess: (updatedReport) => {
      queryClient.setQueryData(["analysis-run", runId], updatedReport);
      queryClient.invalidateQueries({ queryKey: ["investor-profile"] });
    },
  });

  return {
    report: runQuery.data,
    isLoading: runQuery.isLoading,
    error: runQuery.error,
    startAnalysis: startRunMutation.mutateAsync,
    isStarting: startRunMutation.isPending,
    approveHitl: approveHitlMutation.mutateAsync,
    isApprovingHitl: approveHitlMutation.isPending,
  };
}
