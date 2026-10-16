const ilsFormatter = new Intl.NumberFormat("he-IL", {
  style: "currency",
  currency: "ILS",
  maximumFractionDigits: 0,
});

const numberFormatter = new Intl.NumberFormat("he-IL", {
  maximumFractionDigits: 1,
});

export function formatILS(amount: number | undefined | null): string {
  if (amount === undefined || amount === null || Number.isNaN(amount)) {
    return "₪0";
  }
  return ilsFormatter.format(amount);
}

export function formatPct(pct: number | undefined | null, showSign = false): string {
  if (pct === undefined || pct === null || Number.isNaN(pct)) {
    return "0.0%";
  }
  const formatted = `${pct.toFixed(2)}%`;
  if (showSign && pct > 0) {
    return `+${formatted}`;
  }
  return formatted;
}

export function formatSqm(sqm: number | undefined | null): string {
  if (sqm === undefined || sqm === null || Number.isNaN(sqm)) {
    return '0 מ"ר';
  }
  return `${numberFormatter.format(sqm)} מ"ר`;
}

export function formatDateIL(isoOrDate: string | Date | undefined | null): string {
  if (!isoOrDate) return "";
  const date = typeof isoOrDate === "string" ? new Date(isoOrDate) : isoOrDate;
  if (Number.isNaN(date.getTime())) return String(isoOrDate);
  const dd = String(date.getDate()).padStart(2, "0");
  const mm = String(date.getMonth() + 1).padStart(2, "0");
  const yyyy = date.getFullYear();
  return `${dd}/${mm}/${yyyy}`;
}
