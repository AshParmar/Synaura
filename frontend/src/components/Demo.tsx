"use client";

import { useState, useCallback, useRef } from "react";
import { useAuth } from "@clerk/nextjs";
import { useDropzone } from "react-dropzone";
import { useReactToPrint } from "react-to-print";
import { motion, AnimatePresence } from "framer-motion";
import { UploadCloud, FileImage, Download, ScanLine, Brain, BookOpen, AlertCircle, X, ChevronRight, Activity, Shield } from "lucide-react";
import Image from "next/image";
import ReactMarkdown from "react-markdown";

type AnalysisResult = {
  disease: string;
  confidence: number;
  interval: [number, number];
  region: any;
  report: string;
  heatmap_base64?: string;
};

export default function Demo() {
  const { userId } = useAuth(); // Clerk user ID — null if not signed in
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [activeTab, setActiveTab] = useState<"original" | "overlay">("original");
  const [error, setError] = useState<string | null>(null);
  const [isGeneratingPdf, setIsGeneratingPdf] = useState(false);

  const reportRef = useRef<HTMLDivElement>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles[0]) {
      const f = acceptedFiles[0];
      setFile(f);
      setPreview(URL.createObjectURL(f));
      setResult(null);
      setError(null);
      setActiveTab("original");
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "image/*": [] },
    maxFiles: 1,
  });

  const clearFile = (e: React.MouseEvent) => {
    e.stopPropagation();
    setFile(null);
    setPreview(null);
    setResult(null);
    setError(null);
  };

  const runAnalysis = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch("/api/analyze_xray", {
        method: "POST",
        body: formData,
        // Pass Clerk user ID to backend so the report gets saved to MongoDB
        headers: userId ? { "x-user-id": userId } : {},
      });

      if (!res.ok) {
         const errData = await res.json().catch(() => ({}));
         throw new Error(errData.detail || `Server error: ${res.status}`);
      }
      
      const data = await res.json();
      setResult(data);
      setActiveTab("overlay");
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Failed to analyze X-ray. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = async () => {
    if (!result) return;
    setIsGeneratingPdf(true);
    try {
      const { jsPDF } = await import("jspdf");
      const doc = new jsPDF("p", "mm", "a4");
      
      const pageWidth = doc.internal.pageSize.getWidth();
      
      // Header
      doc.setFontSize(24);
      doc.setFont("helvetica", "bold");
      doc.text("SYNAURA", 20, 30);
      
      doc.setFontSize(10);
      doc.setFont("helvetica", "normal");
      doc.setTextColor(100, 100, 100);
      doc.text("ADVANCED RADIOLOGY INTELLIGENCE REPORT", 20, 38);
      
      doc.setDrawColor(200, 200, 200);
      doc.line(20, 45, pageWidth - 20, 45);
      
      // Patient Info
      doc.setFontSize(10);
      doc.setTextColor(50, 50, 50);
      doc.text(`Date: ${new Date().toLocaleDateString()}`, 140, 30);
      doc.text(`Time: ${new Date().toLocaleTimeString()}`, 140, 35);
      doc.text(`ID: SYN-${Math.floor(Math.random() * 1000000)}`, 140, 40);
      
      doc.text("Patient Name: Jane Doe (Anonymized)", 20, 55);
      doc.text("DOB: 01/01/1980", 20, 62);
      doc.text("Gender: Female", 20, 69);
      
      doc.text(`Study Date: ${new Date().toLocaleDateString()}`, 120, 55);
      doc.text("Modality: Radiography (DX)", 120, 62);
      doc.text("Body Part: Chest (PA/AP)", 120, 69);
      
      doc.line(20, 78, pageWidth - 20, 78);
      
      // Findings
      doc.setFontSize(14);
      doc.setFont("helvetica", "bold");
      doc.setTextColor(0, 0, 0);
      doc.text("AI Diagnostic Findings", 20, 90);
      
      doc.setFontSize(11);
      doc.setFont("helvetica", "normal");
      doc.setTextColor(100, 100, 100);
      doc.text("Primary Detection:", 20, 100);
      
      doc.setFontSize(14);
      doc.setFont("helvetica", "bold");
      doc.setTextColor(0, 0, 0);
      doc.text(result.disease, 60, 100);
      
      doc.setFontSize(11);
      doc.setFont("helvetica", "normal");
      doc.setTextColor(100, 100, 100);
      doc.text("Fuzzy Interval:", 20, 110);
      
      doc.setFontSize(12);
      doc.setFont("courier", "bold");
      doc.setTextColor(37, 99, 235); // accent color
      doc.text(`[${(result.interval[0] * 100).toFixed(1)}% - ${(result.interval[1] * 100).toFixed(1)}%]`, 60, 110);
      
      // Heatmap
      let yOffset = 130;
      if (result.heatmap_base64) {
        doc.setFontSize(12);
        doc.setFont("helvetica", "bold");
        doc.setTextColor(50, 50, 50);
        doc.text("GradCAM Localization Heatmap", 20, yOffset);
        
        try {
          doc.addImage(`data:image/png;base64,${result.heatmap_base64}`, "PNG", 20, yOffset + 5, 120, 120);
          yOffset += 135;
        } catch (e) {
          console.error("Failed to add image to PDF", e);
        }
      }
      
      // Report Text
      // Split report by newlines and handle basic markdown
      doc.addPage();
      let textY = 20;
      
      doc.setFontSize(14);
      doc.setFont("helvetica", "bold");
      doc.setTextColor(0, 0, 0);
      doc.text("Clinical Report", 20, textY);
      textY += 15;
      
      const lines = result.report.split('\n');
      for (const line of lines) {
        if (textY > 280) {
          doc.addPage();
          textY = 20;
        }
        
        if (line.startsWith('## ') || line.startsWith('### ') || line.startsWith('# ')) {
          doc.setFontSize(12);
          doc.setFont("helvetica", "bold");
          doc.setTextColor(37, 99, 235);
          const text = line.replace(/#/g, '').trim();
          doc.text(text, 20, textY);
          textY += 10;
        } else if (line.trim().length > 0) {
          doc.setFontSize(10);
          doc.setFont("helvetica", "normal");
          doc.setTextColor(50, 50, 50);
          
          // Remove bold markdown for simple printing
          const cleanText = line.replace(/\*\*/g, '').replace(/\*/g, '').replace(/- /g, '• ');
          
          const splitText = doc.splitTextToSize(cleanText, pageWidth - 40);
          doc.text(splitText, 20, textY);
          textY += (splitText.length * 6) + 4;
        }
      }
      
      doc.save(`Synaura_Report_${result.disease.replace(/\s+/g, '_')}.pdf`);
    } catch (err) {
      console.error("Failed to generate PDF", err);
    } finally {
      setIsGeneratingPdf(false);
    }
  };

  const fadeUpVariant = {
    hidden: { opacity: 0, y: 15 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: "easeOut" as const } }
  };

  return (
    <section id="demo" className="py-32 bg-black min-h-screen relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-accent/5 blur-[120px] rounded-full pointer-events-none" />

      <div className="max-w-[1400px] mx-auto px-6 relative z-10">
        <div className="mb-12 flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
          <motion.div initial="hidden" animate="visible" variants={fadeUpVariant}>
            <div className="flex items-center gap-2 mb-3">
              <span className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse" />
              <span className="text-[11px] text-gray-400 font-mono tracking-[0.2em] uppercase">LIVE DEMO</span>
            </div>
            <h2 className="text-3xl md:text-[40px] font-semibold tracking-tight text-white mb-4">
              Intelligence Workspace
            </h2>
            <p className="text-gray-400 max-w-xl text-[15px] leading-relaxed">
              Upload a chest X-Ray and get AI-powered insights with GradCAM visualization, confidence scores, and a comprehensive clinical report.
            </p>
          </motion.div>
          
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }} className="flex items-center gap-3 px-4 py-2 rounded-full border border-white/10 bg-white/5 backdrop-blur-md text-xs text-gray-400 shadow-xl">
            <Shield className="w-3.5 h-3.5 text-accent" />
            HIPAA Compliant <span className="text-gray-600">•</span> Encrypted <span className="text-gray-600">•</span> Research Use Only
          </motion.div>
        </div>

        {/* 3-Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:h-[650px]">
          
          {/* LEFT: Upload */}
          <motion.div 
            initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.5, delay: 0.1 }}
            className="lg:col-span-3 bg-[#0A0A0A] border border-white/10 rounded-2xl p-6 flex flex-col h-full shadow-2xl relative overflow-hidden group"
          >
            <div className="absolute top-0 inset-x-0 h-[1px] bg-gradient-to-r from-transparent via-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            
            <h3 className="text-white text-sm font-medium mb-6 flex items-center gap-2">
              <UploadCloud className="w-4 h-4 text-gray-400" /> Input Source
            </h3>
            
            <div
              {...getRootProps()}
              className={`flex-1 border-2 border-dashed rounded-xl flex flex-col items-center justify-center p-6 text-center cursor-pointer transition-all duration-300 relative overflow-hidden ${
                isDragActive ? "border-accent bg-accent/10 scale-[0.98]" : "border-white/10 hover:border-white/20 hover:bg-white/5"
              }`}
            >
              <input {...getInputProps()} />
              
              <AnimatePresence mode="wait">
                {preview ? (
                  <motion.div 
                    key="preview"
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    className="absolute inset-2 rounded-lg overflow-hidden"
                  >
                    <div className="absolute inset-0 bg-black/40 z-10 opacity-0 hover:opacity-100 transition-opacity flex items-center justify-center backdrop-blur-sm">
                       <span className="text-xs font-medium text-white px-3 py-1.5 bg-black/60 rounded-full border border-white/20">Change Image</span>
                    </div>
                    <img src={preview} alt="Upload preview" className="w-full h-full object-cover opacity-60" />
                  </motion.div>
                ) : (
                  <motion.div 
                    key="upload-prompt"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="flex flex-col items-center z-10"
                  >
                    <div className="w-12 h-12 rounded-full bg-white/5 flex items-center justify-center mb-4 border border-white/5 shadow-inner">
                      <UploadCloud className={`w-5 h-5 transition-colors duration-300 ${isDragActive ? "text-accent" : "text-gray-400"}`} />
                    </div>
                    <p className="text-sm text-white font-medium mb-1 tracking-wide">
                      {isDragActive ? "Drop image here" : "Drag & Drop X-Ray"}
                    </p>
                    <p className="text-xs text-gray-500 mt-2 font-mono">DICOM, PNG, JPEG</p>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {file && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="mt-4 p-4 rounded-xl bg-white/5 border border-white/10 backdrop-blur-md">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3 overflow-hidden">
                    <div className="w-8 h-8 rounded bg-black flex items-center justify-center shrink-0 border border-white/10">
                       <FileImage className="w-4 h-4 text-accent" />
                    </div>
                    <span className="text-xs text-gray-300 truncate font-medium">{file.name}</span>
                  </div>
                  <button onClick={clearFile} className="p-1 hover:bg-white/10 rounded-full text-gray-500 hover:text-white transition-colors">
                    <X className="w-3.5 h-3.5" />
                  </button>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    runAnalysis();
                  }}
                  disabled={loading}
                  className="w-full relative overflow-hidden bg-white text-black text-sm font-semibold py-3 rounded-lg hover:bg-gray-200 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 group"
                >
                  {loading ? (
                    <>
                      <ScanLine className="w-4 h-4 animate-[spin_3s_linear_infinite]" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      Run Intelligence <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                    </>
                  )}
                </button>
              </motion.div>
            )}
          </motion.div>

          {/* CENTER: Viewer */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: 0.2 }}
            className="lg:col-span-6 bg-[#0A0A0A] border border-white/10 rounded-2xl overflow-hidden relative flex flex-col h-full min-h-[400px] shadow-2xl"
          >
            <div className="h-14 border-b border-white/5 flex items-center justify-between px-6 bg-[#050505] shrink-0 z-20">
              <div className="flex gap-6">
                <button
                  onClick={() => setActiveTab("original")}
                  className={`text-[11px] font-semibold uppercase tracking-[0.15em] transition-all relative py-4 ${
                    activeTab === "original" ? "text-white" : "text-gray-500 hover:text-gray-300"
                  }`}
                >
                  Original
                  {activeTab === "original" && <motion.div layoutId="activeTab" className="absolute bottom-0 left-0 right-0 h-0.5 bg-accent" />}
                </button>
                <button
                  onClick={() => setActiveTab("overlay")}
                  disabled={!result}
                  className={`text-[11px] font-semibold uppercase tracking-[0.15em] transition-all relative py-4 ${
                    activeTab === "overlay" ? "text-accent" : "text-gray-500 hover:text-gray-300 disabled:opacity-30 disabled:hover:text-gray-500"
                  }`}
                >
                  GradCAM Overlay
                  {activeTab === "overlay" && <motion.div layoutId="activeTab" className="absolute bottom-0 left-0 right-0 h-0.5 bg-accent" />}
                </button>
              </div>
            </div>

            <div className="flex-1 relative bg-black flex items-center justify-center overflow-hidden">
              <div className="absolute inset-0 opacity-[0.03] bg-[radial-gradient(#fff_1px,transparent_1px)] [background-size:20px_20px] pointer-events-none" />
              
              {!preview ? (
                <div className="text-gray-600 flex flex-col items-center justify-center h-full">
                  <div className="relative">
                    <div className="absolute inset-0 bg-white/5 blur-xl rounded-full" />
                    <ScanLine className="w-10 h-10 mb-4 opacity-30 relative z-10" />
                  </div>
                  <p className="text-xs font-mono tracking-widest uppercase opacity-50">Viewer Idle</p>
                </div>
              ) : (
                <div className="relative w-full h-full flex items-center justify-center p-4">
                  <AnimatePresence mode="wait">
                    {!(activeTab === "overlay" && result && result.heatmap_base64) && (
                      <motion.img 
                        key="original"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.3 }}
                        src={preview} 
                        alt="X-Ray Preview" 
                        className="max-w-full max-h-full object-contain rounded-lg shadow-2xl" 
                      />
                    )}
                    
                    {activeTab === "overlay" && result && result.heatmap_base64 && (
                      <motion.img
                        key="heatmap"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.3 }}
                        src={`data:image/png;base64,${result.heatmap_base64}`} 
                        alt="GradCAM Heatmap Overlay" 
                        className="max-w-full max-h-full object-contain rounded-lg shadow-2xl absolute"
                      />
                    )}
                  </AnimatePresence>
                  
                  <AnimatePresence>
                    {loading && (
                      <motion.div 
                        initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                        className="absolute inset-0 bg-black/60 backdrop-blur-md flex flex-col items-center justify-center z-30"
                      >
                        <div className="w-full max-w-[240px] flex flex-col items-center">
                           <div className="relative w-16 h-16 mb-8">
                              <div className="absolute inset-0 border-2 border-white/10 rounded-full" />
                              <div className="absolute inset-0 border-2 border-accent border-t-transparent rounded-full animate-spin" />
                              <div className="absolute inset-0 flex items-center justify-center">
                                 <Activity className="w-5 h-5 text-accent animate-pulse" />
                              </div>
                           </div>
                           <div className="h-1 w-full bg-white/10 rounded-full overflow-hidden">
                             <motion.div
                               className="h-full bg-accent"
                               initial={{ x: "-100%" }}
                               animate={{ x: "100%" }}
                               transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                             />
                           </div>
                           <p className="text-[10px] text-accent mt-4 text-center font-mono uppercase tracking-[0.2em] animate-pulse">Running Multi-Modal Pipeline...</p>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              )}
            </div>
          </motion.div>

          {/* RIGHT: Output */}
          <motion.div 
            initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.5, delay: 0.3 }}
            className="lg:col-span-3 bg-[#0A0A0A] border border-white/10 rounded-2xl p-6 flex flex-col h-full overflow-hidden min-h-[400px] shadow-2xl"
          >
             <h3 className="text-white text-sm font-medium mb-6 flex items-center gap-2 pb-4 border-b border-white/5">
              <Brain className="w-4 h-4 text-accent" /> Intelligence Output
            </h3>

            {error && (
              <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="flex-1 flex flex-col items-center justify-center text-center px-4">
                 <div className="w-12 h-12 rounded-full bg-red-500/10 flex items-center justify-center mb-4 border border-red-500/20">
                    <AlertCircle className="w-6 h-6 text-red-500" />
                 </div>
                 <p className="text-sm font-medium text-red-400 mb-2">{error}</p>
                 <p className="text-xs text-gray-500 leading-relaxed">Ensure the FastAPI backend is running on port 8000.</p>
              </motion.div>
            )}

            {!result && !loading && !error && (
              <div className="flex-1 flex flex-col items-center justify-center text-center opacity-50">
                 <BookOpen className="w-8 h-8 text-gray-600 mb-4" />
                 <p className="text-xs font-mono uppercase tracking-widest text-gray-500">Awaiting Input</p>
              </div>
            )}

            {loading && !result && !error && (
              <div className="flex-1 flex flex-col gap-4 p-2">
                <div className="h-20 bg-white/5 rounded-xl animate-pulse" />
                <div className="h-32 bg-white/5 rounded-xl animate-pulse" />
                <div className="h-4 bg-white/5 rounded-full w-3/4 animate-pulse mt-4" />
                <div className="h-4 bg-white/5 rounded-full w-1/2 animate-pulse" />
              </div>
            )}

            {result && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex-1 flex flex-col overflow-hidden">
                <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar pb-4">
                  
                  {/* Primary Finding Box */}
                  <div className="mb-6 p-5 rounded-xl border border-white/10 bg-white/5 relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-1 h-full bg-accent" />
                    <p className="text-[10px] text-gray-400 font-mono uppercase tracking-widest mb-2">Primary Finding</p>
                    <p className="text-xl text-white font-medium mb-5">{result.disease}</p>
                    
                    {/* Fuzzy Interval UI */}
                    <div className="bg-black/50 rounded-lg p-3 border border-white/5">
                       <div className="flex justify-between items-end mb-2">
                          <span className="text-[11px] text-gray-400 uppercase tracking-wider">Fuzzy Interval</span>
                          <span className="text-xs text-accent font-mono font-medium">
                            [{(result.interval[0] * 100).toFixed(1)}% - {(result.interval[1] * 100).toFixed(1)}%]
                          </span>
                       </div>
                       
                       {/* Fuzzy Bar Visualization */}
                       <div className="h-2 w-full bg-white/10 rounded-full overflow-hidden relative">
                         <motion.div 
                           initial={{ left: 0, right: "100%" }}
                           animate={{ 
                             left: `${result.interval[0] * 100}%`,
                             right: `${100 - (result.interval[1] * 100)}%` 
                           }}
                           transition={{ duration: 1.2, ease: "easeOut" }}
                           className="absolute top-0 bottom-0 bg-gradient-to-r from-accent/50 via-accent to-accent/50 shadow-[0_0_10px_rgba(37,99,235,0.5)]"
                         />
                         {/* Optional: exact confidence marker within the interval */}
                         <motion.div
                           initial={{ left: 0 }}
                           animate={{ left: `${result.confidence * 100}%` }}
                           transition={{ duration: 1.2, ease: "easeOut" }}
                           className="absolute top-0 bottom-0 w-0.5 bg-white z-10 shadow-[0_0_5px_white]"
                         />
                       </div>
                       <div className="mt-2 text-[10px] text-gray-500 leading-tight">
                         The model predicts the presence of <span className="text-gray-300">{result.disease.toLowerCase()}</span> within the fuzzy probability interval shown above.
                       </div>
                    </div>
                  </div>

                  {/* Report Section */}
                  <div className="mb-6">
                     <p className="text-[10px] text-gray-400 font-mono uppercase tracking-widest mb-4 flex items-center gap-2">
                       <BookOpen className="w-3.5 h-3.5" /> Clinical Report
                     </p>
                     <div className="text-gray-300/90 leading-relaxed text-[13px] bg-white/[0.02] p-5 rounded-xl border border-white/5">
                       <ReactMarkdown
                         components={{
                           h1: ({node, ...props}) => <h1 className="text-xl font-bold text-accent mt-6 mb-4" {...props} />,
                           h2: ({node, ...props}) => <h2 className="text-lg font-bold text-accent mt-5 mb-3 border-b border-accent/20 pb-2" {...props} />,
                           h3: ({node, ...props}) => <h3 className="text-base font-bold text-white mt-4 mb-2" {...props} />,
                           p: ({node, ...props}) => <p className="mb-3 leading-relaxed" {...props} />,
                           ul: ({node, ...props}) => <ul className="list-disc pl-5 mb-3 space-y-1.5" {...props} />,
                           ol: ({node, ...props}) => <ol className="list-decimal pl-5 mb-3 space-y-1.5" {...props} />,
                           li: ({node, ...props}) => <li className="pl-1" {...props} />,
                           strong: ({node, ...props}) => <strong className="font-semibold text-white" {...props} />,
                         }}
                       >
                         {result.report}
                       </ReactMarkdown>
                     </div>
                  </div>
                </div>

                <div className="pt-4 border-t border-white/10 mt-auto shrink-0 bg-[#0A0A0A]">
                  <button 
                    onClick={handleDownloadPDF}
                    disabled={isGeneratingPdf}
                    className="w-full relative overflow-hidden flex items-center justify-center gap-2 py-3 rounded-xl border border-white/10 text-xs font-medium text-white hover:bg-white/10 transition-colors disabled:opacity-50 group"
                  >
                    {isGeneratingPdf ? (
                      <><ScanLine className="w-4 h-4 animate-spin" /> Generating PDF...</>
                    ) : (
                      <>
                        <Download className="w-4 h-4 group-hover:-translate-y-0.5 transition-transform" /> 
                        Download PDF Report
                      </>
                    )}
                  </button>
                </div>
              </motion.div>
            )}

            {/* Hidden Print Container for PDF Generation */}
            {result && (
              <div id="print-container" className="absolute top-[-9999px] left-[-9999px] w-[850px] bg-white p-16 text-black z-0 font-sans" ref={reportRef}>
                 
                 {/* Hospital/Clinic Header */}
                 <div className="flex items-start justify-between border-b-2 border-gray-800 pb-6 mb-8">
                    <div className="flex items-center gap-4">
                      <Activity className="w-10 h-10 text-black" />
                      <div>
                        <h1 className="text-3xl font-bold tracking-tight text-black">SYNAURA</h1>
                        <p className="text-xs text-gray-500 tracking-[0.1em] font-medium mt-1">ADVANCED RADIOLOGY INTELLIGENCE</p>
                      </div>
                    </div>
                    <div className="text-right text-xs text-gray-500 flex flex-col gap-1">
                      <p><span className="font-semibold text-gray-700">Date:</span> {new Date().toLocaleDateString()}</p>
                      <p><span className="font-semibold text-gray-700">Time:</span> {new Date().toLocaleTimeString()}</p>
                      <p><span className="font-semibold text-gray-700">ID:</span> SYN-{Math.floor(Math.random() * 1000000)}</p>
                    </div>
                 </div>
                 
                 {/* Patient Info Placeholder */}
                 <div className="grid grid-cols-2 gap-4 mb-8 text-sm border-b border-gray-200 pb-8">
                    <div>
                      <p className="mb-2"><span className="font-semibold text-gray-700 w-24 inline-block">Patient Name:</span> Jane Doe (Anonymized)</p>
                      <p className="mb-2"><span className="font-semibold text-gray-700 w-24 inline-block">DOB:</span> 01/01/1980</p>
                      <p><span className="font-semibold text-gray-700 w-24 inline-block">Gender:</span> Female</p>
                    </div>
                    <div>
                      <p className="mb-2"><span className="font-semibold text-gray-700 w-28 inline-block">Study Date:</span> {new Date().toLocaleDateString()}</p>
                      <p className="mb-2"><span className="font-semibold text-gray-700 w-28 inline-block">Modality:</span> Radiography (DX)</p>
                      <p><span className="font-semibold text-gray-700 w-28 inline-block">Body Part:</span> Chest (PA/AP)</p>
                    </div>
                 </div>

                 <h2 className="text-xl font-bold text-black mb-6 uppercase tracking-wider border-l-4 border-black pl-3">AI Diagnostic Findings</h2>
                 
                 <div className="grid grid-cols-2 gap-6 mb-10">
                    <div className="p-5 rounded-lg border border-gray-200 bg-gray-50">
                       <p className="text-xs text-gray-500 mb-1 uppercase font-semibold">Primary Detection</p>
                       <p className="text-2xl font-bold text-black">{result.disease}</p>
                    </div>
                    <div className="p-5 rounded-lg border border-gray-200 bg-gray-50">
                       <p className="text-xs text-gray-500 mb-1 uppercase font-semibold">Diagnostic Confidence (Fuzzy Interval)</p>
                       <p className="text-2xl font-mono text-black font-bold">
                         [{(result.interval[0] * 100).toFixed(1)}% - {(result.interval[1] * 100).toFixed(1)}%]
                       </p>
                    </div>
                 </div>

                 {result.heatmap_base64 && (
                   <div className="mb-10 page-break-inside-avoid">
                     <p className="text-sm font-semibold text-gray-700 mb-3">GradCAM Localization Heatmap</p>
                     <div className="w-full h-[350px] rounded-lg border border-gray-200 bg-white overflow-hidden flex justify-center p-2">
                       <img src={`data:image/png;base64,${result.heatmap_base64}`} className="h-full object-contain" alt="Heatmap" />
                     </div>
                     <p className="text-xs text-gray-500 mt-2 text-center">Highlighted regions indicate areas of high activation leading to the primary detection.</p>
                   </div>
                 )}

                 <div className="text-sm text-gray-800 leading-relaxed page-break-inside-avoid">
                   <ReactMarkdown
                     components={{
                       h1: ({node, ...props}) => <h1 className="text-lg font-bold text-black mt-8 mb-4 border-b border-gray-200 pb-2 uppercase tracking-wide" {...props} />,
                       h2: ({node, ...props}) => <h2 className="text-base font-bold text-black mt-6 mb-3 uppercase" {...props} />,
                       h3: ({node, ...props}) => <h3 className="text-sm font-bold text-black mt-4 mb-2" {...props} />,
                       p: ({node, ...props}) => <p className="mb-4 text-justify" {...props} />,
                       ul: ({node, ...props}) => <ul className="list-disc pl-6 mb-4 space-y-2" {...props} />,
                       ol: ({node, ...props}) => <ol className="list-decimal pl-6 mb-4 space-y-2" {...props} />,
                       li: ({node, ...props}) => <li className="pl-1" {...props} />,
                       strong: ({node, ...props}) => <strong className="font-bold text-black" {...props} />,
                     }}
                   >
                     {result.report}
                   </ReactMarkdown>
                 </div>
                 
                 <div className="mt-16 pt-8 border-t-2 border-gray-800 flex justify-between text-xs text-gray-500">
                    <p><strong>Disclaimer:</strong> This report is generated by Synaura AI and is intended for research purposes only. It does not replace professional medical diagnosis.</p>
                    <p className="font-bold">End of Report</p>
                 </div>
              </div>
            )}
          </motion.div>
        </div>
      </div>
    </section>
  );
}
