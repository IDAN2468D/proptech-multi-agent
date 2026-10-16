"use client";

import { useState } from "react";
import { Calendar, Check, Copy, Handshake, Share2 } from "lucide-react";
import { proptechApiV2 } from "@/lib/api-client";
import { formatILS } from "@/lib/formatters";
import {
  NegotiationPlaybookResult,
  ShareDealResponse,
} from "@/lib/schemas/agent-outputs-v2.schema";
import { spatialAudio } from "@/components/audio/SpatialAudioFeedback";

export function NegotiationPlaybookCard({
  runId,
  playbook,
}: {
  runId: string;
  playbook: NegotiationPlaybookResult;
}) {
  const [copied, setCopied] = useState(false);
  const [shareResult, setShareResult] = useState<ShareDealResponse | null>(
    null
  );
  const [isSharing, setIsSharing] = useState(false);

  const handleCopyMessage = async () => {
    await navigator.clipboard.writeText(playbook.ready_to_send_hebrew_message);
    setCopied(true);
    spatialAudio.playSpatialCue("AGENT_DONE", 0.0);
    setTimeout(() => setCopied(false), 2500);
  };

  const handleShareDeal = async () => {
    setIsSharing(true);
    try {
      const res = await proptechApiV2.shareDealPackage(runId);
      setShareResult(res);
      spatialAudio.playSpatialCue("DEAL_SHARED", 0.25);
    } finally {
      setIsSharing(false);
    }
  };

  const downloadIcsCalendar = () => {
    if (!shareResult?.calendar_ics) return;
    const blob = new Blob([shareResult.calendar_ics], {
      type: "text/calendar;charset=utf-8",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `proptech-tour-${runId.slice(0, 8)}.ics`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="liquid-glass-glow rounded-2xl p-6 space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <Handshake className="w-5 h-5 text-cyan-400" />
            סוכן 9: אסטרטגיית משא ומתן והצעה נגדית מבוססת ממצאים (AI Negotiation
            Playbook)
          </h3>
          <p className="text-xs text-slate-400">
            תרגום ליקויי ה-RAG מנסח הטאבו וכתב הכמויות (BOQ) להפחתת מחיר מנומקת
          </p>
        </div>

        <button
          type="button"
          disabled={isSharing}
          onClick={handleShareDeal}
          className="px-4 py-2 rounded-xl bg-indigo-500/20 hover:bg-indigo-500/30 border border-indigo-400/40 text-indigo-200 text-xs font-bold flex items-center gap-1.5 transition"
        >
          <Share2 className="w-3.5 h-3.5" />
          {isSharing ? "משדר ל-Deal-Room MCP..." : "שתף עסקה ל-Slack וייצא יומן"}
        </button>
      </div>

      {/* Price Targets Row */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
        <div className="p-3.5 rounded-xl bg-slate-900/90 border border-white/10">
          <span className="text-xs text-slate-400 block">מחיר מבוקש</span>
          <span className="text-lg font-bold text-slate-200">
            {formatILS(playbook.asking_price_ils)}
          </span>
        </div>
        <div className="p-3.5 rounded-xl bg-cyan-950/40 border border-cyan-400/30">
          <span className="text-xs text-cyan-300 block">הצעת פתיחה מומלצת</span>
          <span className="text-lg font-extrabold text-cyan-300">
            {formatILS(playbook.recommended_opening_offer_ils)}
          </span>
        </div>
        <div className="p-3.5 rounded-xl bg-emerald-950/40 border border-emerald-400/40">
          <span className="text-xs text-emerald-300 block">
            מחיר יעד לסגירה (Target)
          </span>
          <span className="text-lg font-extrabold text-emerald-300">
            {formatILS(playbook.target_closing_price_ils)}
          </span>
        </div>
        <div className="p-3.5 rounded-xl bg-rose-950/30 border border-rose-400/30">
          <span className="text-xs text-rose-300 block">
            מחיר גג לעצירה (Walk-Away)
          </span>
          <span className="text-lg font-bold text-rose-300">
            {formatILS(playbook.walk_away_max_price_ils)}
          </span>
        </div>
      </div>

      {/* Justifications Table */}
      <div className="space-y-2">
        <h4 className="text-xs font-bold text-slate-300">
          פירוט נימוקי הפחתת המחיר מול המוכר:
        </h4>
        <div className="space-y-2">
          {playbook.price_reduction_justifications.map((item, idx) => (
            <div
              key={idx}
              className="p-3 rounded-xl bg-slate-950/80 border border-white/10 flex flex-wrap items-center justify-between gap-2 text-xs"
            >
              <div>
                <p className="text-white font-semibold">{item.reason}</p>
                <span className="text-[11px] text-cyan-400">
                  מקור הוכחה: {item.evidence_source}
                </span>
              </div>
              <span className="px-3 py-1 rounded-lg bg-rose-500/15 border border-rose-500/30 text-rose-300 font-bold">
                -{formatILS(item.deduction_amount_ils)}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Ready-to-Send Hebrew Counter-Offer Message */}
      <div className="p-4 rounded-xl bg-slate-950/90 border border-cyan-500/30 space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold text-cyan-300">
            נוסח הודעה מוכן לשליחה למוכר / מתווך (WhatsApp / Email):
          </span>
          <button
            type="button"
            onClick={handleCopyMessage}
            className="px-3 py-1.5 rounded-lg bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-200 text-xs font-semibold flex items-center gap-1.5"
          >
            {copied ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-400" />
                הועתק ללוח!
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5" />
                העתק הודעה למוכר/מתווך
              </>
            )}
          </button>
        </div>
        <pre className="whitespace-pre-wrap text-xs text-slate-200 font-sans leading-relaxed">
          {playbook.ready_to_send_hebrew_message}
        </pre>
      </div>

      {shareResult && (
        <div className="p-4 rounded-xl bg-indigo-950/40 border border-indigo-400/40 flex flex-wrap items-center justify-between gap-3 text-xs">
          <div className="space-y-1">
            <span className="text-indigo-300 font-bold block">
              ✓ נשלח לערוץ {shareResult.webhook_channel} דרך Deal-Room MCP
            </span>
            <p className="text-slate-300">{shareResult.slack_message_preview}</p>
          </div>
          <button
            type="button"
            onClick={downloadIcsCalendar}
            className="px-3.5 py-2 rounded-lg bg-emerald-500/20 border border-emerald-400/40 text-emerald-200 font-bold flex items-center gap-1.5"
          >
            <Calendar className="w-3.5 h-3.5" />
            הורד זימון לסיור בנכס (.ics)
          </button>
        </div>
      )}
    </div>
  );
}
