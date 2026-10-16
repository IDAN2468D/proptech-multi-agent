"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { PdfRagDropzone } from "@/components/properties/PdfRagDropzone";
import { PropertyForm } from "@/components/properties/PropertyForm";
import { useAnalysisRun } from "@/hooks/use-analysis-run";
import { useInvestorProfile } from "@/hooks/use-investor-profile";
import { usePropertyDocuments } from "@/hooks/use-property-documents";
import { PropertyCreateRequest } from "@/lib/schemas/property.schema";

export default function NewPropertyWizardPage() {
  const router = useRouter();
  const { profile } = useInvestorProfile();
  const {
    createProperty,
    uploadDocumentsBatch,
    uploadProgress,
    indexedResults,
  } = usePropertyDocuments();
  const { startAnalysis } = useAnalysisRun();

  const [files, setFiles] = useState<File[]>([]);
  const [isBusy, setIsBusy] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleWizardSubmit = async (
    propertyData: PropertyCreateRequest,
    financing: {
      equity_ils: number;
      annual_interest_rate_pct: number;
      loan_years: number;
    }
  ) => {
    setErrorMsg(null);
    setIsBusy(true);
    try {
      const createdProp = await createProperty(propertyData);
      if (files.length > 0) {
        await uploadDocumentsBatch(createdProp.id, files);
      }
      const report = await startAnalysis({
        property_id: createdProp.id,
        equity_ils: financing.equity_ils,
        annual_interest_rate_pct: financing.annual_interest_rate_pct,
        loan_years: financing.loan_years,
        annual_expenses_ils: 6000,
        appreciation_rate_pct: 3.0,
      });
      router.push(`/analysis/${report.run_id}`);
    } catch (err: unknown) {
      setErrorMsg(
        err instanceof Error ? err.message : "שגיאה בהרצת אשף בדיקת הנכס"
      );
      setIsBusy(false);
    }
  };

  return (
    <div className="max-w-4xl space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white">
          אשף הקמת נכס, אינדוקס מסמכי PDF והזנקת צוות הסוכנים
        </h2>
        <p className="text-sm text-slate-400">
          העלה נסח טאבו וחוזה מכר כדי שסוכן ה-RAG וסוכן ה-Critic יצליבו את השטח
          הרשום מול שטח המודעה ויאתרו הערות אזהרה.
        </p>
      </div>

      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-500/15 border border-rose-500/40 text-rose-200 text-sm">
          {errorMsg}
        </div>
      )}

      <PdfRagDropzone
        files={files}
        onFilesChange={setFiles}
        uploadProgress={uploadProgress}
        indexedResults={indexedResults}
      />

      <PropertyForm
        defaultEquityIls={profile?.available_equity_ils || 1100000}
        isSubmitting={isBusy}
        onSubmitWizard={handleWizardSubmit}
      />
    </div>
  );
}
