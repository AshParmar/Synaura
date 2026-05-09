import { FileText, ExternalLink, Brain, Target, BookOpen, ActivitySquare } from "lucide-react";

export default function Research() {
  return (
    <section className="py-24 bg-black min-h-screen">
      <div className="max-w-[1400px] mx-auto px-6">
        
        {/* Header Section */}
        <div className="grid lg:grid-cols-2 gap-16 mb-16">
          <div>
            <div className="text-[10px] text-gray-500 tracking-[0.2em] uppercase mb-4">RESEARCH & SYSTEM ARCHITECTURE</div>
            <h1 className="text-4xl md:text-5xl font-semibold tracking-tight text-white mb-6 leading-[1.1]">
              Engineered for <br /> Clinical Intelligence.
            </h1>
            <p className="text-gray-400 text-[15px] leading-relaxed max-w-xl">
              Synaura integrates state-of-the-art deep learning with GradCAM explainability, uncertainty quantification, and RAG-powered evidence retrieval to deliver transparent, reliable, and clinically meaningful insights.
            </p>
          </div>

          <div className="grid grid-cols-3 gap-8">
             <div className="flex flex-col gap-1 border-l border-border/50 pl-6">
                <span className="text-2xl font-medium text-white">95.7%</span>
                <span className="text-xs text-gray-500">Accuracy</span>
             </div>
             <div className="flex flex-col gap-1 border-l border-border/50 pl-6">
                <span className="text-2xl font-medium text-white">0.948</span>
                <span className="text-xs text-gray-500">F1 Score</span>
             </div>
             <div className="flex flex-col gap-1 border-l border-border/50 pl-6">
                <span className="text-2xl font-medium text-white">0.977</span>
                <span className="text-xs text-gray-500">AUC-ROC</span>
             </div>
             <div className="flex flex-col gap-1 border-l border-border/50 pl-6">
                <span className="text-2xl font-medium text-white">3.12%</span>
                <span className="text-xs text-gray-500">ECE Score ↓</span>
                <span className="text-[10px] text-green-500 mt-1">Well Calibrated</span>
             </div>
             <div className="flex flex-col gap-1 border-l border-border/50 pl-6">
                <span className="text-2xl font-medium text-white">112K+</span>
                <span className="text-xs text-gray-500">X-Ray Images</span>
                <span className="text-[10px] text-gray-600 mt-1">NIH + MIMIC-CXR</span>
             </div>
             <div className="flex flex-col gap-1 border-l border-border/50 pl-6">
                <span className="text-2xl font-medium text-white">20+</span>
                <span className="text-xs text-gray-500">Abnormalities</span>
                <span className="text-[10px] text-gray-600 mt-1">Detected</span>
             </div>
          </div>
        </div>

        {/* Pipeline Diagram */}
        <div className="w-full border border-border rounded-2xl bg-card p-10 mb-8 overflow-x-auto custom-scrollbar">
           <div className="min-w-[1000px] flex items-start justify-between relative">
              <div className="absolute top-8 left-10 right-10 h-[1px] bg-border/50 -z-10" />
              
              {[
                { title: "Chest X-Ray\nInput", icon: "X-Ray" },
                { title: "Preprocessing", subtitle: "Normalization &\nEnhancement", icon: "Controls" },
                { title: "Vision Encoder", subtitle: "EfficientNet-B4\nBackbone", icon: "Box" },
                { title: "Abnormality\nDetection", subtitle: "Multi-label\nClassification", icon: "Target" },
                { title: "GradCAM\nExplainability", subtitle: "Attention Mapping\n& Localization", icon: "Lungs" },
                { title: "Confidence\nCalibration", subtitle: "Uncertainty\nEstimation", icon: "Chart" },
                { title: "RAG Evidence\nRetrieval", subtitle: "Medical Literature\nSearch", icon: "Search" },
                { title: "Clinical Report\nGeneration", subtitle: "Structured\nOutput", icon: "File" }
              ].map((step, i) => (
                <div key={i} className="flex flex-col items-center text-center gap-4 bg-card w-28">
                   <div className="w-16 h-16 rounded-xl border border-border bg-[#141414] flex items-center justify-center text-gray-400 relative z-10 shadow-lg">
                      <div className="w-6 h-6 bg-gray-600/20 rounded-md" />
                   </div>
                   <div>
                     <div className="text-[13px] font-medium text-white whitespace-pre-line leading-snug mb-1">{step.title}</div>
                     {step.subtitle && <div className="text-[11px] text-gray-500 whitespace-pre-line leading-tight">{step.subtitle}</div>}
                   </div>
                </div>
              ))}
           </div>
        </div>

        {/* Paper & Features */}
        <div className="grid lg:grid-cols-[1fr_400px] gap-8">
           <div className="border border-border rounded-2xl bg-card flex flex-col md:flex-row overflow-hidden">
              <div className="w-full md:w-1/3 bg-white p-4 shrink-0 flex items-center justify-center">
                 {/* Mock Paper PDF */}
                 <div className="w-full aspect-[1/1.4] border border-gray-200 shadow-sm relative p-4 flex flex-col">
                    <div className="w-full h-2 bg-gray-200 mb-2 rounded" />
                    <div className="w-3/4 h-2 bg-gray-200 mb-6 rounded" />
                    <div className="w-full h-1 bg-gray-100 mb-1 rounded" />
                    <div className="w-full h-1 bg-gray-100 mb-1 rounded" />
                    <div className="w-5/6 h-1 bg-gray-100 mb-4 rounded" />
                    <div className="flex gap-2 mt-auto">
                      <div className="w-1/2 aspect-video bg-blue-500/10 rounded" />
                      <div className="w-1/2 aspect-video bg-red-500/10 rounded" />
                    </div>
                    <div className="absolute bottom-2 right-2 bg-gray-800 text-white text-[8px] px-1.5 py-0.5 rounded font-mono">PDF</div>
                 </div>
              </div>
              <div className="p-8 flex flex-col justify-center">
                 <div className="text-[10px] text-[#2563EB] tracking-[0.2em] uppercase font-semibold mb-3">RESEARCH PAPER</div>
                 <h2 className="text-2xl font-medium text-white mb-4 leading-snug">Synaura: Explainable Chest X-Ray Analysis with GradCAM and RAG-powered Evidence Retrieval</h2>
                 <p className="text-xs text-gray-400 mb-4">Rushikesh D. • Atharva A. • Vinayak B. • Pranav B. • Prof. Rashmi Honrao</p>
                 <div className="text-xs text-gray-500 mb-6 flex items-center gap-2">
                    <BookOpen className="w-3 h-3" /> International Conference on Intelligent Systems & Applications (ICISA 2024)
                 </div>
                 <p className="text-sm text-gray-400 leading-relaxed mb-8">
                    We propose Synaura, an explainable AI framework for chest X-ray analysis that combines deep learning, GradCAM visualization, uncertainty quantification, and RAG-based evidence retrieval to generate transparent and clinically grounded reports.
                 </p>
                 <div className="flex items-center gap-4">
                    <button className="flex items-center gap-2 bg-transparent border border-border text-white px-5 py-2.5 rounded-lg text-sm font-medium hover:bg-white/5 transition-colors">
                       <FileText className="w-4 h-4" /> Read Paper →
                    </button>
                    <button className="flex items-center gap-2 bg-transparent border border-border text-white px-5 py-2.5 rounded-lg text-sm font-medium hover:bg-white/5 transition-colors">
                       <ExternalLink className="w-4 h-4" /> View on arXiv
                    </button>
                 </div>
              </div>
           </div>

           <div className="border border-border rounded-2xl bg-card p-8 flex flex-col gap-8 justify-center">
              <div className="flex items-start gap-4">
                 <Brain className="w-6 h-6 text-gray-400 shrink-0 mt-1" />
                 <div>
                   <h3 className="text-[14px] font-medium text-white mb-1">Deep Learning</h3>
                   <p className="text-[13px] text-gray-500 leading-relaxed">EfficientNet-B4 backbone fine-tuned on large-scale chest X-ray datasets for robust generalization.</p>
                 </div>
              </div>
              <div className="flex items-start gap-4">
                 <Target className="w-6 h-6 text-gray-400 shrink-0 mt-1" />
                 <div>
                   <h3 className="text-[14px] font-medium text-white mb-1">Explainability</h3>
                   <p className="text-[13px] text-gray-500 leading-relaxed">GradCAM heatmaps highlight regions influencing the model's predictions.</p>
                 </div>
              </div>
              <div className="flex items-start gap-4">
                 <BookOpen className="w-6 h-6 text-gray-400 shrink-0 mt-1" />
                 <div>
                   <h3 className="text-[14px] font-medium text-white mb-1">Evidence Grounding</h3>
                   <p className="text-[13px] text-gray-500 leading-relaxed">RAG pipeline retrieves and cites relevant medical literature for every finding.</p>
                 </div>
              </div>
              <div className="flex items-start gap-4">
                 <ActivitySquare className="w-6 h-6 text-gray-400 shrink-0 mt-1" />
                 <div>
                   <h3 className="text-[14px] font-medium text-white mb-1">Reliability</h3>
                   <p className="text-[13px] text-gray-500 leading-relaxed">Confidence calibration and uncertainty estimation ensure trustworthy clinical decisions.</p>
                 </div>
              </div>
           </div>
        </div>

      </div>
    </section>
  );
}
