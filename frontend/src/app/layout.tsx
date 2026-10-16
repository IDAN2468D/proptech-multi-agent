import type { Metadata } from "next";
import { Heebo } from "next/font/google";
import "./globals.css";
import { QueryProvider } from "@/components/ui/QueryProvider";

const heebo = Heebo({
  subsets: ["hebrew", "latin"],
  weight: ["400", "500", "600", "700", "800"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "PropTech AI | מערכת מולטי-סוכנים לניתוח עסקאות והשקעות נדל״ן",
  description:
    "מערכת Back End & Front End מבוססת 5 סוכני AI לניתוח עסקאות נדל״ן, משכנתא, מיסוי ונסחי טאבו",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="he" dir="rtl" className="dark">
      <body className={`${heebo.className} antialiased selection:bg-cyan-500/30`}>
        <QueryProvider>{children}</QueryProvider>
      </body>
    </html>
  );
}
