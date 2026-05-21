import History from "@/components/History";

export const metadata = {
  title: "Synaura | My Scans",
  description: "View your past radiology AI analysis reports.",
};

export default function HistoryPage() {
  return (
    <main className="min-h-screen bg-black text-white selection:bg-white selection:text-black">
      <History />
    </main>
  );
}
