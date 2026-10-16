"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { proptechApi } from "@/lib/api-client";
import { InvestorProfile } from "@/lib/schemas/property.schema";

export function useInvestorProfile() {
  const queryClient = useQueryClient();

  const profileQuery = useQuery({
    queryKey: ["investor-profile"],
    queryFn: () => proptechApi.getInvestorProfile(),
    retry: 1,
  });

  const updateProfileMutation = useMutation({
    mutationFn: (payload: Partial<InvestorProfile>) =>
      proptechApi.updateInvestorProfile(payload),
    onSuccess: (updated) => {
      queryClient.setQueryData(["investor-profile"], updated);
    },
  });

  return {
    profile: profileQuery.data,
    isLoading: profileQuery.isLoading,
    error: profileQuery.error,
    updateProfile: updateProfileMutation.mutateAsync,
    isUpdating: updateProfileMutation.isPending,
  };
}
