"use client";

import { ShieldCheck, BookOpen, Users, TrendingUp, ArrowRight, GitBranch as Github } from "lucide-react";

export default function Trust() {
  return (
    <section className="py-32 border-y border-border bg-black">
      <div className="max-w-7xl mx-auto px-6 flex flex-col items-center text-center">
        
        <div className="flex items-center gap-2 px-4 py-1.5 rounded-full border border-border bg-white/5 text-xs text-gray-300 tracking-[0.2em] uppercase mb-8">
          <span className="text-accent text-[14px]">✦</span> OUR MISSION
        </div>

        <h2 className="text-5xl md:text-7xl font-bold tracking-tight text-white mb-6 leading-[1.1]">
          Explainable AI <br /> for Clinical Decision Making.
        </h2>

        <p className="text-gray-400 max-w-2xl text-[17px] leading-relaxed mb-24">
          Synaura combines deep learning, explainability, and evidence-backed reasoning to build more trustworthy medical AI systems.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-x-8 gap-y-12 text-left w-full mb-24">
          <div className="flex flex-col gap-4 border-l border-border/50 pl-6">
            <div className="w-10 h-10 rounded-full border border-border flex items-center justify-center bg-card">
              <ShieldCheck className="w-4 h-4 text-white" />
            </div>
            <h3 className="text-white font-medium text-[15px]">Built for Trust</h3>
            <p className="text-gray-500 text-[13px] leading-relaxed">Explainable predictions with GradCAM and uncertainty quantification.</p>
          </div>

          <div className="flex flex-col gap-4 border-l border-border/50 pl-6">
            <div className="w-10 h-10 rounded-full border border-border flex items-center justify-center bg-card">
              <BookOpen className="w-4 h-4 text-white" />
            </div>
            <h3 className="text-white font-medium text-[15px]">Backed by Research</h3>
            <p className="text-gray-500 text-[13px] leading-relaxed">State-of-the-art models validated on real-world clinical datasets.</p>
          </div>

          <div className="flex flex-col gap-4 border-l border-border/50 pl-6">
            <div className="w-10 h-10 rounded-full border border-border flex items-center justify-center bg-card">
              <Users className="w-4 h-4 text-white" />
            </div>
            <h3 className="text-white font-medium text-[15px]">Designed for Impact</h3>
            <p className="text-gray-500 text-[13px] leading-relaxed">Helping clinicians make faster, more confident, evidence-based decisions.</p>
          </div>

          <div className="flex flex-col gap-4 border-l border-border/50 pl-6">
            <div className="w-10 h-10 rounded-full border border-border flex items-center justify-center bg-card">
              <TrendingUp className="w-4 h-4 text-white" />
            </div>
            <h3 className="text-white font-medium text-[15px]">Future-Ready</h3>
            <p className="text-gray-500 text-[13px] leading-relaxed">Continuously improving through open research, community, and real-world feedback.</p>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row items-center gap-4 mb-24">
          <a href="#demo" className="flex items-center gap-2 bg-white text-black px-6 py-3 rounded-lg text-sm font-medium hover:bg-gray-200 transition-colors">
            Try Live Demo <ArrowRight className="w-4 h-4" />
          </a>
          <a href="#research" className="flex items-center gap-2 bg-transparent border border-border text-white px-6 py-3 rounded-lg text-sm font-medium hover:bg-white/5 transition-colors">
             View Research <ArrowRight className="w-4 h-4" />
          </a>
          <a href="#github" className="flex items-center gap-2 bg-transparent border border-border text-white px-6 py-3 rounded-lg text-sm font-medium hover:bg-white/5 transition-colors">
            <Github className="w-4 h-4" /> Explore GitHub <ArrowRight className="w-4 h-4" />
          </a>
        </div>

        <div className="w-full bg-card border border-border rounded-2xl py-12 px-6 flex flex-col md:flex-row items-center justify-center gap-12 md:gap-24">
           <div className="flex items-center gap-4 text-lg md:text-xl font-mono tracking-widest text-white">
             <span className="text-accent text-2xl">✦</span> Transparent AI.
           </div>
           <div className="flex items-center gap-4 text-lg md:text-xl font-mono tracking-widest text-white">
             <span className="text-accent text-2xl">✦</span> Reliable Decisions.
           </div>
           <div className="flex items-center gap-4 text-lg md:text-xl font-mono tracking-widest text-white">
             <span className="text-accent text-2xl">✦</span> Clinical Impact.
           </div>
        </div>

      </div>
    </section>
  );
}
