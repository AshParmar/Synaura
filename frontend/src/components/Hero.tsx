"use client";

import { motion } from "framer-motion";
import { ArrowRight, Upload, Cpu, ScanLine } from "lucide-react";
import Link from "next/link";
import Image from "next/image";

export default function Hero() {
  return (
    <section className="py-24 bg-black">
      <div className="max-w-[1400px] mx-auto px-6">
        
        <div className="grid lg:grid-cols-12 gap-12 items-start">
          {/* Left: Text */}
          <div className="lg:col-span-4 flex flex-col items-start text-left pt-4">
            <div className="flex items-center gap-2 mb-4">
              <span className="text-[10px] text-gray-500 font-mono tracking-[0.2em] uppercase">LIVE DEMO PREVIEW</span>
            </div>

            <h1 className="text-4xl md:text-5xl font-semibold tracking-tight text-white mb-6 leading-[1.1]">
              See Synaura in Action
            </h1>

            <p className="text-gray-400 text-sm leading-relaxed mb-12">
              Upload a chest X-ray and get instant AI analysis with GradCAM visualization, confidence scores, and a detailed clinical report.
            </p>

            <div className="flex flex-col gap-6 w-full mb-12 relative">
               <div className="absolute left-6 top-8 bottom-8 w-[1px] border-l border-dashed border-border z-0" />
               
                <div className="bg-card border border-border rounded-xl p-4 flex gap-4 relative z-10">
                  <div className="w-12 h-12 rounded-lg border border-border bg-black flex items-center justify-center shrink-0">
                     <Upload className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h3 className="text-white text-sm font-medium mb-1">1. Upload X-Ray</h3>
                    <p className="text-xs text-gray-500">Provide a chest X-ray image for instant analysis</p>
                  </div>
               </div>
               
               <div className="p-4 flex gap-4 relative z-10 opacity-70 hover:opacity-100 transition-opacity">
                  <div className="w-12 h-12 rounded-lg border border-border bg-black flex items-center justify-center shrink-0">
                     <Cpu className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h3 className="text-white text-sm font-medium mb-1">2. CNN & Fuzzy Inference</h3>
                    <p className="text-xs text-gray-500">DenseNet-121 outputs predictions with fuzzy uncertainty bounds</p>
                  </div>
               </div>
               
               <div className="p-4 flex gap-4 relative z-10 opacity-70 hover:opacity-100 transition-opacity">
                  <div className="w-12 h-12 rounded-lg border border-border bg-black flex items-center justify-center shrink-0">
                     <ScanLine className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h3 className="text-white text-sm font-medium mb-1">3. GradCAM & Groq RAG</h3>
                    <p className="text-xs text-gray-500">Visual localization and LLM-generated clinical context</p>
                  </div>
               </div>
            </div>

            <Link href="/demo" className="bg-white text-black px-6 py-3 rounded-lg text-sm font-medium hover:bg-gray-200 transition-colors flex items-center gap-2">
               Try Demo Now <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          {/* Right: Mockup Interface */}
          <div className="lg:col-span-8 bg-[#0D0D0D] border border-border rounded-2xl p-6 shadow-2xl flex flex-col md:flex-row gap-6">
             {/* Upload Box */}
             <div className="w-full md:w-[260px] shrink-0 border border-border bg-card rounded-xl flex flex-col">
                <div className="p-4 border-b border-border">
                  <h3 className="text-white text-sm font-medium">Upload Chest X-Ray</h3>
                </div>
                <div className="p-4 flex-1 flex flex-col">
                  <div className="flex-1 border border-dashed border-border rounded-lg flex flex-col items-center justify-center p-6 text-center mb-4">
                     <Upload className="w-6 h-6 text-gray-400 mb-4" />
                     <p className="text-xs text-white font-medium mb-1">Drag & drop your image</p>
                     <p className="text-[10px] text-gray-500">or click to browse</p>
                  </div>
                  <div className="text-[10px] text-center text-gray-500 mb-4">Supports: PNG, JPG, DICOM</div>
                  <button className="w-full flex items-center justify-center gap-2 py-2.5 rounded-lg border border-border text-xs text-white hover:bg-white/5 transition-colors">
                     Use Sample X-Ray
                  </button>
                </div>
             </div>

             {/* Viewer Box */}
             <div className="flex-1 flex flex-col gap-6">
               <div className="flex-1 flex flex-col gap-4">
                  <div className="flex justify-center gap-8 text-xs">
                     <span className="text-white font-medium border-b-2 border-accent pb-1">Original</span>
                     <span className="text-gray-500">GradCAM</span>
                     <span className="text-gray-500">Overlay</span>
                  </div>
                  <div className="flex-1 bg-black border border-border rounded-xl relative overflow-hidden flex items-center justify-center min-h-[300px]">
                     <div className="absolute inset-4 rounded-lg bg-[url('https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Chest_Xray_PA_3-8-2010.png/640px-Chest_Xray_PA_3-8-2010.png')] bg-cover bg-center opacity-80 mix-blend-screen" />
                  </div>
                  <div className="flex items-center justify-between text-gray-500">
                     <div className="flex gap-4">
                       <span className="text-lg">⊕</span>
                       <span className="text-lg">⊖</span>
                       <span className="text-lg">↻</span>
                     </div>
                     <div className="flex items-center gap-2 flex-1 max-w-[200px] px-4">
                       <div className="h-1 flex-1 bg-gray-800 rounded-full"><div className="w-1/2 h-full bg-white rounded-full"></div></div>
                       <span className="text-xs">100%</span>
                     </div>
                     <span className="text-lg">⛶</span>
                  </div>
               </div>
             </div>

             {/* Analysis Box */}
             <div className="w-full md:w-[280px] shrink-0">
               <div className="flex justify-between items-center mb-6">
                 <h3 className="text-white text-sm font-medium">AI Analysis</h3>
                 <span className="px-2 py-0.5 rounded-full bg-green-500/10 text-green-500 text-[10px] border border-green-500/20">Pipeline Complete</span>
               </div>
               
               <h2 className="text-lg font-medium text-white mb-6">Cardiomegaly Detected</h2>
               
               <div className="mb-6">
                 <div className="text-xs text-gray-400 mb-4">Fuzzy Interval (Diagnostic Confidence)</div>
                 <div className="flex flex-col items-center">
                    <span className="text-xl font-mono font-medium text-accent mb-2">[89.5% - 94.2%]</span>
                    <div className="w-full h-1.5 bg-gray-800 rounded-full overflow-hidden relative">
                       <div className="absolute top-0 bottom-0 left-[89%] right-[5%] bg-accent rounded-full shadow-[0_0_8px_rgba(37,99,235,0.8)]" />
                    </div>
                 </div>
               </div>

               <div className="mb-6">
                 <div className="text-xs text-gray-400 mb-2">GradCAM Region Extract</div>
                 <div className="text-sm text-white flex items-center gap-2">
                   <ScanLine className="w-4 h-4 text-accent" /> Cardiac Region (Enlarged)
                 </div>
               </div>

               <div className="mb-8">
                 <div className="text-xs text-gray-400 mb-2">LLM Context Engine</div>
                 <div className="text-sm text-yellow-500 flex items-center gap-2">
                   <span className="w-1.5 h-1.5 rounded-full bg-yellow-500" /> Llama-3.1-8b Active
                 </div>
               </div>

               <button className="w-full flex items-center justify-center gap-2 py-3 rounded-lg border border-border text-xs text-white hover:bg-white/5 transition-colors">
                  View Full Report →
               </button>
             </div>
          </div>
        </div>

        {/* Stats Bar */}
        <div className="mt-24 border border-border rounded-2xl bg-[#0D0D0D] px-10 py-12 flex flex-col xl:flex-row items-center justify-between gap-12 relative">
          <div className="absolute top-8 left-10 text-[10px] text-gray-500 tracking-[0.2em] uppercase font-medium">POWERED BY ADVANCED AI</div>
          
          <div className="grid grid-cols-2 md:grid-cols-5 gap-12 w-full pt-6">
            <div className="flex items-center gap-4">
              <svg className="w-8 h-8 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>
              <div>
                <div className="text-2xl md:text-3xl font-semibold text-white mb-1">95%+</div>
                <div className="text-xs text-gray-500">Pipeline Accuracy</div>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <svg className="w-8 h-8 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M4 7V4h16v3M4 12h16M4 17v3h16v-3"/></svg>
              <div>
                <div className="text-2xl md:text-3xl font-semibold text-white mb-1">224²</div>
                <div className="text-xs text-gray-500">Tensor Normalization</div>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <svg className="w-8 h-8 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
              <div>
                <div className="text-2xl md:text-3xl font-semibold text-white mb-1">5</div>
                <div className="text-xs text-gray-500">Pathologies Classified</div>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <svg className="w-8 h-8 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M12 4c-4.4 0-8 3.6-8 8s3.6 8 8 8 8-3.6 8-8-3.6-8-8-8z"/><path d="M12 12c-2.2 0-4-1.8-4-4s1.8-4 4-4 4 1.8 4 4-1.8 4-4 4z"/></svg>
              <div>
                <div className="text-2xl md:text-3xl font-semibold text-white mb-1">2</div>
                <div className="text-xs text-gray-500">Unified Architectures</div>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <svg className="w-8 h-8 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
              <div>
                <div className="text-2xl md:text-3xl font-semibold text-white mb-1">&lt; 3s</div>
                <div className="text-xs text-gray-500">Groq LLM Response</div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </section>
  );
}
