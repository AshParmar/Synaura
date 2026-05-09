import Github from "@/components/Github";
import Footer from "@/components/Footer";

export default function GithubPage() {
  return (
    <main className="bg-black text-white selection:bg-accent/30 selection:text-white">
      <Github />
      <Footer />
    </main>
  );
}
