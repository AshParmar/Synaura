import { Terminal, Copy, Check, Star, Users, Shield, Download, Code, GitBranch } from "lucide-react";
import Image from "next/image";

export default function Github() {
  return (
    <section className="py-24 bg-black min-h-screen">
      <div className="max-w-[1400px] mx-auto px-6">
        
        <div className="grid lg:grid-cols-2 gap-16 items-center mb-16">
          <div>
            <div className="flex items-center gap-2 mb-6">
               <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
               <span className="text-[10px] text-gray-400 font-mono tracking-[0.2em] uppercase">OPEN SOURCE / BUILT IN PUBLIC</span>
            </div>
            <h1 className="text-5xl md:text-[64px] font-semibold tracking-tight text-white mb-6 leading-[1.1]">
              Open Source.<br /> Built for Impact.
            </h1>
            <p className="text-gray-400 text-[17px] leading-relaxed max-w-xl mb-8">
              Synaura is an open-source AI system for explainable chest X-ray analysis. We believe in transparency, reproducibility, and community-driven innovation in healthcare AI.
            </p>
            <div className="flex items-center gap-4 mb-16">
               <a href="https://github.com/ashparmar/synaura" className="flex items-center gap-2 bg-white text-black px-6 py-3 rounded-lg text-sm font-medium hover:bg-gray-200 transition-colors">
                  <GitBranch className="w-4 h-4" /> View on GitHub →
               </a>
               <a href="https://github.com/ashparmar/synaura" className="flex items-center gap-2 bg-transparent border border-border text-white px-6 py-3 rounded-lg text-sm font-medium hover:bg-white/5 transition-colors">
                  <Star className="w-4 h-4" /> Star the Repository
               </a>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
               <div className="flex flex-col gap-2">
                  <Code className="w-5 h-5 text-gray-400 mb-2" />
                  <span className="text-xs font-semibold text-white">100% Open Source</span>
                  <span className="text-[11px] text-gray-500 leading-tight">MIT Licensed and free for everyone.</span>
               </div>
               <div className="flex flex-col gap-2 border-l border-border/50 pl-6">
                  <Shield className="w-5 h-5 text-gray-400 mb-2" />
                  <span className="text-xs font-semibold text-white">Reproducible</span>
                  <span className="text-[11px] text-gray-500 leading-tight">End-to-end pipeline with documentation.</span>
               </div>
               <div className="flex flex-col gap-2 border-l border-border/50 pl-6">
                  <Users className="w-5 h-5 text-gray-400 mb-2" />
                  <span className="text-xs font-semibold text-white">Community Driven</span>
                  <span className="text-[11px] text-gray-500 leading-tight">Contributions, discussions & ideas welcome.</span>
               </div>
               <div className="flex flex-col gap-2 border-l border-border/50 pl-6">
                  <Download className="w-5 h-5 text-gray-400 mb-2" />
                  <span className="text-xs font-semibold text-white">Built for Developers</span>
                  <span className="text-[11px] text-gray-500 leading-tight">Modular, extensible and easy to integrate.</span>
               </div>
            </div>
          </div>

          <div className="bg-[#0A0A0A] border border-border rounded-xl p-4 overflow-hidden hidden lg:block shadow-2xl">
            {/* Github Mockup Box */}
            <div className="border border-border rounded-lg bg-[#0D1117] flex flex-col h-[500px]">
               <div className="flex items-center justify-between border-b border-border p-4">
                  <div className="flex items-center gap-3">
                     <GitBranch className="w-5 h-5 text-gray-400" />
                     <span className="text-blue-400 font-semibold text-sm">synaura-ai <span className="text-gray-400">/</span> synaura <span className="px-1.5 py-0.5 border border-border rounded-full text-[10px] text-gray-400 ml-2">Public</span></span>
                  </div>
                  <div className="flex items-center gap-2">
                     <div className="flex text-xs text-gray-400 border border-border rounded-md overflow-hidden bg-[#21262D]">
                        <div className="px-3 py-1 border-r border-border flex items-center gap-1"><span className="w-2 h-2 rounded-full border border-gray-400" /> Watch</div>
                        <div className="px-3 py-1 font-semibold text-gray-300">27</div>
                     </div>
                     <div className="flex text-xs text-gray-400 border border-border rounded-md overflow-hidden bg-[#21262D]">
                        <div className="px-3 py-1 border-r border-border flex items-center gap-1"><Star className="w-3 h-3" /> Star</div>
                        <div className="px-3 py-1 font-semibold text-gray-300">1.2k</div>
                     </div>
                     <div className="flex text-xs text-gray-400 border border-border rounded-md overflow-hidden bg-[#21262D]">
                        <div className="px-3 py-1 border-r border-border flex items-center gap-1"><GitBranch className="w-3 h-3" /> Fork</div>
                        <div className="px-3 py-1 font-semibold text-gray-300">231</div>
                     </div>
                  </div>
               </div>
               <div className="p-4 border-b border-border flex gap-6 text-[13px] text-gray-400">
                  <div className="flex items-center gap-2 text-white border-b-2 border-[#F78166] pb-2 font-medium"><Code className="w-4 h-4" /> Code</div>
                  <div className="flex items-center gap-2 pb-2">Issues <span className="px-1.5 py-0.5 bg-gray-800 rounded-full text-[10px]">12</span></div>
                  <div className="flex items-center gap-2 pb-2">Pull requests <span className="px-1.5 py-0.5 bg-gray-800 rounded-full text-[10px]">5</span></div>
                  <div className="flex items-center gap-2 pb-2">Discussions</div>
                  <div className="flex items-center gap-2 pb-2">Actions</div>
               </div>
               <div className="p-4 flex-1 overflow-hidden">
                  <div className="border border-border rounded-lg bg-[#0D1117]">
                     <div className="bg-[#161B22] border-b border-border p-3 flex justify-between text-xs text-gray-400">
                        <div className="flex items-center gap-2">
                           <div className="w-5 h-5 bg-gray-600 rounded-full" />
                           <span className="font-semibold text-gray-300">rushikesh-d</span> feat: add GradCAM visualization and update pipeline
                        </div>
                        <div className="flex gap-4">
                           <span>2 hours ago</span>
                           <span className="font-mono">1,234 Commits</span>
                        </div>
                     </div>
                     {[
                       {name: "models", msg: "add EfficientNet-B4 training pipeline", time: "2 hours ago"},
                       {name: "frontend", msg: "update UI components", time: "1 day ago"},
                       {name: "backend", msg: "refactor API routes", time: "1 day ago"},
                       {name: "rag", msg: "improve retrieval pipeline", time: "2 days ago"},
                       {name: "gradcam", msg: "add attention visualization utils", time: "2 days ago"},
                       {name: "datasets", msg: "update dataset cards", time: "4 days ago"}
                     ].map((item, i) => (
                       <div key={i} className="flex justify-between p-3 border-b border-border text-xs text-gray-400 hover:bg-[#161B22]">
                          <div className="flex items-center gap-2 w-1/4"><span className="text-gray-500 text-sm">📁</span> {item.name}</div>
                          <div className="w-1/2 truncate">{item.msg}</div>
                          <div className="w-1/4 text-right">{item.time}</div>
                       </div>
                     ))}
                  </div>
               </div>
            </div>
          </div>
        </div>

        {/* Installation */}
        <div className="grid lg:grid-cols-3 gap-6 mb-8">
           <div className="lg:col-span-2 border border-border rounded-2xl bg-[#0D0D0D] p-8 flex flex-col md:flex-row items-center gap-8">
              <div className="w-16 h-16 shrink-0 border border-border rounded-xl flex items-center justify-center bg-card">
                 <Code className="w-6 h-6 text-white" />
              </div>
              <div className="flex-1">
                 <div className="text-sm font-semibold text-white mb-1">Get Started in Seconds</div>
                 <div className="text-xs text-gray-500 mb-6">Everything you need to run Synaura locally.</div>
                 <div className="bg-black border border-border rounded-lg p-4 font-mono text-xs text-gray-300 leading-loose">
                    <span className="text-gray-600 mr-4">1</span> <span className="text-green-400">$</span> git clone <span className="text-green-400">https://github.com/ashparmar/synaura.git</span><br />
                    <span className="text-gray-600 mr-4">2</span> <span className="text-green-400">$</span> cd synaura<br />
                    <span className="text-gray-600 mr-4">3</span> <span className="text-green-400">$</span> pip install -r requirements.txt<br />
                    <span className="text-gray-600 mr-4">4</span> <span className="text-green-400">$</span> uvicorn backend.main:app --reload
                 </div>
              </div>
              <button className="hidden md:flex border border-border text-white text-xs px-4 py-2 rounded-lg hover:bg-white/5 whitespace-nowrap">
                 View Documentation →
              </button>
           </div>
           
           <div className="border border-border rounded-2xl bg-[#0D0D0D] p-8 flex flex-col justify-between">
              <div>
                 <div className="flex items-center gap-3 mb-4">
                    <Terminal className="w-6 h-6 text-white" />
                    <span className="text-sm font-semibold text-white">Docker Support</span>
                 </div>
                 <p className="text-xs text-gray-500 leading-relaxed mb-6">
                    Run the full stack with one command. Detailed setup guide and API docs included.
                 </p>
              </div>
              <button className="w-fit border border-border text-white text-xs px-4 py-2 rounded-lg hover:bg-white/5">
                 View Dockerfile →
              </button>
           </div>
        </div>

        {/* Stats */}
        <div className="w-full border border-border rounded-2xl bg-black px-10 py-12 flex items-center justify-between overflow-x-auto custom-scrollbar">
           <div className="flex min-w-max gap-16 px-4">
               <div className="flex items-center gap-4">
                 <svg className="w-8 h-8 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M4 7V4h16v3M4 12h16M4 17v3h16v-3"/></svg>
                 <div>
                   <div className="text-2xl font-semibold text-white mb-1">10K+</div>
                   <div className="text-xs text-gray-500">X-rays Analyzed</div>
                 </div>
               </div>
               
               <div className="flex items-center gap-4">
                 <svg className="w-8 h-8 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>
                 <div>
                   <div className="text-2xl font-semibold text-white mb-1">95%+</div>
                   <div className="text-xs text-gray-500">Test Set Accuracy</div>
                   <div className="text-[10px] text-gray-600 mt-1">(NIH + MIMIC-CXR)</div>
                 </div>
               </div>

               <div className="flex items-center gap-4">
                 <svg className="w-8 h-8 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                 <div>
                   <div className="text-2xl font-semibold text-white mb-1">20+</div>
                   <div className="text-xs text-gray-500">Abnormalities Detected</div>
                 </div>
               </div>

               <div className="flex items-center gap-4">
                 <svg className="w-8 h-8 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M12 4c-4.4 0-8 3.6-8 8s3.6 8 8 8 8-3.6 8-8-3.6-8-8-8z"/><path d="M12 12c-2.2 0-4-1.8-4-4s1.8-4 4-4 4 1.8 4 4-1.8 4-4 4z"/></svg>
                 <div>
                   <div className="text-2xl font-semibold text-white mb-1">5</div>
                   <div className="text-xs text-gray-500">AI Models</div>
                 </div>
               </div>

               <div className="flex items-center gap-4">
                 <Star className="w-8 h-8 text-gray-400" />
                 <div>
                   <div className="text-2xl font-semibold text-white mb-1">1.2k+</div>
                   <div className="text-xs text-gray-500">GitHub Stars</div>
                 </div>
               </div>
           </div>
        </div>

      </div>
    </section>
  );
}
