"use client";

import { useRef } from "react";
import { CheckCircle2, FileText, ShieldAlert, Trash2, UploadCloud } from "lucide-react";
import { DocumentUploadResponse } from "@/lib/schemas/property.schema";

interface PdfRagDropzoneProps {
  files: File[];
  onFilesChange: (files: File[]) => void;
  uploadProgress: number;
  indexedResults: DocumentUploadResponse[];
}

export function PdfRagDropzone({
  files,
  onFilesChange,
  uploadProgress,
  indexedResults,
}: PdfRagDropzoneProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);

  const handleSelectFiles = (fileList: FileList | null) => {
    if (!fileList) return;
    const added = Array.from(fileList);
    onFilesChange([...files, ...added]);
  };

  const removeFile = (index: number) => {
    onFilesChange(files.filter((_, i) => i !== index));
  };

  return (
    <div className="liquid-glass rounded-2xl p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-base font-bold text-white">
            העלאת מסמכי הנכס לתחקור RAG משפטי ושמאי
          </h3>
          <p className="text-xs text-slate-400">
            העלה נסח טאבו, חוזה מכר או דוח שמאות (PDF) לאינדוקס ב-MongoDB Vector
            Store
          </p>
        </div>
        <span className="px-2.5 py-1 rounded-lg bg-cyan-500/15 text-cyan-300 text-xs font-medium">
          Context Sanitized
        </span>
      </div>

      <div
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          handleSelectFiles(e.dataTransfer.files);
        }}
        className="border-2 border-dashed border-cyan-400/30 hover:border-cyan-400/70 rounded-2xl p-8 text-center cursor-pointer transition bg-slate-950/40"
      >
        <input
          ref={inputRef}
          type="file"
          multiple
          accept=".pdf,application/pdf"
          className="hidden"
          onChange={(e) => handleSelectFiles(e.target.files)}
        />
        <UploadCloud className="w-10 h-10 text-cyan-400 mx-auto mb-2" />
        <p className="text-sm font-semibold text-white">
          גרור לכאן קובצי PDF או לחץ לבחירת קבצים מהמחשב
        </p>
        <p className="text-xs text-slate-400 mt-1">
          תומך בפירוק עמודים סמנטי וציטוט מדויק (Page Number + Exact Quote)
        </p>
      </div>

      {files.length > 0 && (
        <div className="space-y-2">
          {files.map((file, idx) => (
            <div
              key={`${file.name}-${idx}`}
              className="flex items-center justify-between px-4 py-2.5 rounded-xl bg-slate-900/90 border border-white/10 text-sm"
            >
              <div className="flex items-center gap-2.5">
                <FileText className="w-4 h-4 text-cyan-400" />
                <span className="text-white font-medium">{file.name}</span>
                <span className="text-xs text-slate-400">
                  ({Math.max(1, Math.round(file.size / 1024))} KB)
                </span>
              </div>
              <button
                type="button"
                onClick={() => removeFile(idx)}
                className="text-rose-400 hover:text-rose-300 p-1"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}

      {uploadProgress > 0 && (
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs text-cyan-300">
            <span>סטטוס אינדוקס וקטורי ב-MongoDB...</span>
            <span>{uploadProgress}%</span>
          </div>
          <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
            <div
              className="h-full bg-gradient-to-l from-cyan-400 to-blue-500 transition-all duration-300"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
        </div>
      )}

      {indexedResults.length > 0 && (
        <div className="space-y-2 pt-2">
          {indexedResults.map((res, idx) => (
            <div
              key={idx}
              className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-xs space-y-1"
            >
              <div className="flex items-center gap-1.5 text-emerald-300 font-semibold">
                <CheckCircle2 className="w-4 h-4" />
                הקובץ {res.filename} אונדקס ({res.chunks_indexed} מקטעים מתוך{" "}
                {res.pages_extracted} עמודים)
              </div>
              {res.sanitized_warnings.length > 0 && (
                <div className="flex items-center gap-1 text-amber-300">
                  <ShieldAlert className="w-3.5 h-3.5" />
                  נוטרלו {res.sanitized_warnings.length} ניסיונות Context
                  Poisoning במסמך.
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
