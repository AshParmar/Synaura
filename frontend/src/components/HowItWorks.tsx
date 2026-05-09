"use client";

import { motion } from "framer-motion";
import { Upload, Network, Activity, LineChart, FileText, Shield, Database, Target, UserCheck } from "lucide-react";

export default function HowItWorks() {
  return (
    <section className="py-24 bg-black">
      <div className="max-w-[1400px] mx-auto px-6">
        
        <div className="mb-16">
          <div className="text-[10px] text-gray-500 tracking-[0.2em] uppercase font-mono mb-4">HOW IT WORKS</div>
          <h2 className="text-4xl md:text-5xl font-semibold tracking-tight text-white mb-6 leading-[1.1]">
            From X-Ray to <br /> Explainable Insight
          </h2>
          <p className="text-gray-400 text-sm leading-relaxed max-w-md">
            Synaura combines advanced deep learning with GradCAM visualizations and confidence estimation to deliver accurate, interpretable, and clinically relevant results.
          </p>
        </div>

        {/* 5-Step Flow */}
        <div className="w-full flex flex-col xl:flex-row items-center gap-4 xl:gap-8 mb-16 overflow-x-auto custom-scrollbar pb-4">
          
          <div className="flex-1 min-w-[240px] bg-[#0A0A0A] border border-border rounded-xl p-6 relative flex flex-col h-[280px]">
             <div className="text-xs text-gray-500 mb-6 font-mono">01</div>
             <div className="flex-1 flex flex-col justify-center">
                <div className="w-16 h-16 border border-border border-dashed rounded-xl flex items-center justify-center mb-8 mx-auto">
                   <Upload className="w-6 h-6 text-gray-400" />
                </div>
                <h3 className="text-white text-[15px] font-medium mb-2">Input Processing</h3>
                <p className="text-xs text-gray-500 leading-relaxed">Chest X-ray images are uploaded, resized to 224x224, and tensor-normalized for the model.</p>
             </div>
             <div className="hidden xl:flex absolute -right-6 top-1/2 -translate-y-1/2 w-6 items-center justify-center z-10 text-gray-600">→</div>
          </div>

          <div className="flex-1 min-w-[240px] bg-[#0A0A0A] border border-border rounded-xl p-6 relative flex flex-col h-[280px]">
             <div className="text-xs text-gray-500 mb-6 font-mono">02</div>
             <div className="flex-1 flex flex-col justify-center">
                <div className="w-16 h-16 flex items-center justify-center mb-8 mx-auto">
                   <Network className="w-10 h-10 text-gray-300" strokeWidth={1} />
                </div>
                <h3 className="text-white text-[15px] font-medium mb-2">CNN Classification</h3>
                <p className="text-xs text-gray-500 leading-relaxed">A custom-trained DenseNet-121 architecture performs multi-class pathology classification.</p>
             </div>
             <div className="hidden xl:flex absolute -right-6 top-1/2 -translate-y-1/2 w-6 items-center justify-center z-10 text-gray-600">→</div>
          </div>

          <div className="flex-1 min-w-[240px] bg-[#0A0A0A] border border-border rounded-xl p-6 relative flex flex-col h-[280px]">
             <div className="text-xs text-gray-500 mb-6 font-mono">03</div>
             <div className="flex-1 flex flex-col justify-center">
                <div className="w-16 h-16 flex items-center justify-center mb-8 mx-auto">
                   <LineChart className="w-10 h-10 text-gray-300" strokeWidth={1} />
                </div>
                <h3 className="text-white text-[15px] font-medium mb-2">Fuzzy Intervals</h3>
                <p className="text-xs text-gray-500 leading-relaxed">Replaces exact softmax scores with fuzzy logic intervals [L, U] to quantify AI uncertainty.</p>
             </div>
             <div className="hidden xl:flex absolute -right-6 top-1/2 -translate-y-1/2 w-6 items-center justify-center z-10 text-gray-600">→</div>
          </div>

          <div className="flex-1 min-w-[240px] bg-[#0A0A0A] border border-border rounded-xl p-6 relative flex flex-col h-[280px]">
             <div className="text-xs text-gray-500 mb-6 font-mono">04</div>
             <div className="flex-1 flex flex-col justify-center">
                <div className="w-16 h-16 flex items-center justify-center mb-8 mx-auto relative">
                   <Activity className="w-10 h-10 text-gray-300" strokeWidth={1} />
                   <div className="absolute right-2 bottom-2 w-4 h-4 bg-orange-500/80 blur-md rounded-full" />
                </div>
                <h3 className="text-white text-[15px] font-medium mb-2">GradCAM Overlay</h3>
                <p className="text-xs text-gray-500 leading-relaxed">Generates a heatmap of model activations to extract the specific affected lung regions.</p>
             </div>
             <div className="hidden xl:flex absolute -right-6 top-1/2 -translate-y-1/2 w-6 items-center justify-center z-10 text-gray-600">→</div>
          </div>

          <div className="flex-1 min-w-[240px] bg-[#0A0A0A] border border-border rounded-xl p-6 relative flex flex-col h-[280px]">
             <div className="text-xs text-gray-500 mb-6 font-mono">05</div>
             <div className="flex-1 flex flex-col justify-center">
                <div className="w-16 h-16 flex items-center justify-center mb-8 mx-auto">
                   <FileText className="w-10 h-10 text-gray-300" strokeWidth={1} />
                </div>
                <h3 className="text-white text-[15px] font-medium mb-2">Groq RAG Report</h3>
                <p className="text-xs text-gray-500 leading-relaxed">Llama-3 LLM uses PubMed medical embeddings to instantly write a clinical context report.</p>
             </div>
          </div>

        </div>

        {/* 4 Feature Boxes */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 bg-[#050505] border border-border rounded-2xl p-6 md:p-8">
           <div className="flex flex-col md:flex-row items-start gap-4 pr-6 lg:border-r border-border/50">
              <div className="w-12 h-12 rounded-xl border border-border bg-black flex items-center justify-center shrink-0">
                 <Shield className="w-5 h-5 text-gray-400" />
              </div>
              <div>
                 <h4 className="text-[13px] font-medium text-white mb-1">Privacy First</h4>
                 <p className="text-[11px] text-gray-500 leading-relaxed">All data is encrypted and processed with strict privacy standards.</p>
              </div>
           </div>
           
           <div className="flex flex-col md:flex-row items-start gap-4 pr-6 lg:border-r border-border/50 lg:pl-6">
              <div className="w-12 h-12 rounded-xl border border-border bg-black flex items-center justify-center shrink-0">
                 <Database className="w-5 h-5 text-gray-400" />
              </div>
              <div>
                 <h4 className="text-[13px] font-medium text-white mb-1">RAG Evidence</h4>
                 <p className="text-[11px] text-gray-500 leading-relaxed">Reports are backed by medical literature using retrieval-augmented generation.</p>
              </div>
           </div>

           <div className="flex flex-col md:flex-row items-start gap-4 pr-6 lg:border-r border-border/50 lg:pl-6">
              <div className="w-12 h-12 rounded-xl border border-border bg-black flex items-center justify-center shrink-0">
                 <Target className="w-5 h-5 text-gray-400" />
              </div>
              <div>
                 <h4 className="text-[13px] font-medium text-white mb-1">High Accuracy</h4>
                 <p className="text-[11px] text-gray-500 leading-relaxed">Trained on diverse datasets and validated for reliable performance.</p>
              </div>
           </div>

           <div className="flex flex-col md:flex-row items-start gap-4 lg:pl-6">
              <div className="w-12 h-12 rounded-xl border border-border bg-black flex items-center justify-center shrink-0">
                 <UserCheck className="w-5 h-5 text-gray-400" />
              </div>
              <div>
                 <h4 className="text-[13px] font-medium text-white mb-1">Clinician Focused</h4>
                 <p className="text-[11px] text-gray-500 leading-relaxed">Built for radiologists and healthcare professionals.</p>
              </div>
           </div>
        </div>

        <div className="mt-16 text-center text-[10px] text-gray-600 tracking-[0.2em] uppercase flex flex-col items-center gap-2">
           SCROLL TO EXPLORE
           <span>↓</span>
        </div>

      </div>
    </section>
  );
}
