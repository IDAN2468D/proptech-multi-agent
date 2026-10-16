"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { proptechApi } from "@/lib/api-client";
import {
  DocumentUploadResponse,
  PropertyCreateRequest,
} from "@/lib/schemas/property.schema";

export function usePropertiesList() {
  return useQuery({
    queryKey: ["properties-list"],
    queryFn: () => proptechApi.listProperties(),
  });
}

export function usePropertyDocuments() {
  const queryClient = useQueryClient();
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [indexedResults, setIndexedResults] = useState<
    DocumentUploadResponse[]
  >([]);

  const createPropertyMutation = useMutation({
    mutationFn: (payload: PropertyCreateRequest) =>
      proptechApi.createProperty(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["properties-list"] });
    },
  });

  const uploadDocumentsBatch = async (
    propertyId: string,
    files: File[]
  ): Promise<DocumentUploadResponse[]> => {
    if (!files.length) return [];
    setUploadProgress(10);
    const results: DocumentUploadResponse[] = [];
    for (let i = 0; i < files.length; i++) {
      const res = await proptechApi.uploadPropertyDocument(
        propertyId,
        files[i]
      );
      results.push(res);
      setUploadProgress(Math.round(((i + 1) / files.length) * 100));
    }
    setIndexedResults(results);
    return results;
  };

  return {
    createProperty: createPropertyMutation.mutateAsync,
    isCreatingProperty: createPropertyMutation.isPending,
    uploadDocumentsBatch,
    uploadProgress,
    indexedResults,
  };
}
