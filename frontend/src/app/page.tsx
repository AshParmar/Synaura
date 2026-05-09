import Hero from "@/components/Hero";
import HowItWorks from "@/components/HowItWorks";
import Trust from "@/components/Trust";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <main className="bg-black text-white selection:bg-accent/30 selection:text-white">
      <Hero />
      <HowItWorks />
      <Trust />
      <Footer />
    </main>
  );
}
