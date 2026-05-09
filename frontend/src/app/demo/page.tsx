import Demo from "@/components/Demo";
import Footer from "@/components/Footer";

export default function DemoPage() {
  return (
    <main className="bg-black text-white selection:bg-accent/30 selection:text-white">
      <Demo />
      <Footer />
    </main>
  );
}
