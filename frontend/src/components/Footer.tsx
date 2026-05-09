import { Activity } from "lucide-react";

export default function Footer() {
  return (
    <footer className="bg-black py-12 border-t border-border">
      <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between">
        
        <div className="flex items-center gap-3 text-white mb-6 md:mb-0">
          <Activity className="w-6 h-6 text-white" />
          <div className="flex flex-col">
            <span className="font-medium tracking-wider text-[15px] leading-tight">SYNAURA</span>
            <span className="text-[9px] text-gray-500 tracking-[0.15em]">AI RADIOLOGY INTELLIGENCE</span>
          </div>
        </div>

        <div className="flex items-center gap-8 text-sm text-gray-400 mb-6 md:mb-0">
           <a href="#research" className="hover:text-white transition-colors">Research</a>
           <a href="#github" className="hover:text-white transition-colors">GitHub</a>
           <a href="#" className="hover:text-white transition-colors">Documentation</a>
           <a href="#about" className="hover:text-white transition-colors">About</a>
           <a href="#contact" className="hover:text-white transition-colors">Contact</a>
        </div>

        <div className="text-sm text-gray-500 text-right">
          <p>© 2026 Synaura</p>
          <p>All rights reserved.</p>
        </div>

      </div>
    </footer>
  );
}
