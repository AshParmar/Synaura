"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { motion } from "framer-motion";
import { Loader2, AlertCircle, FileText, Trash2 } from "lucide-react";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface ScanReport {
  id: string;
  user_id: string;
  filename: string;
  disease: string;
  confidence: number;
  interval: number[];
  region: any;
  report: string;
  heatmap_base64: string;
  gcs_url: string | null;
  created_at: string;
}

export default function History() {
  const { isLoaded, userId, getToken } = useAuth();
  const [reports, setReports] = useState<ScanReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isLoaded) return;
    if (!userId) {
      setLoading(false);
      return;
    }

    const fetchHistory = async () => {
      try {
        setLoading(true);
        // Important: we just hit the public endpoint with the userId since Cloud Run handles it
        const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;
        const res = await fetch(`${backendUrl}/reports/${userId}?limit=10`);
        
        if (!res.ok) {
          throw new Error("Failed to fetch reports from the server.");
        }
        
        const data = await res.json();
        setReports(data.reports || []);
      } catch (err: any) {
        setError(err.message || "An error occurred");
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [isLoaded, userId]);

  const handleDelete = async (reportId: string) => {
    if (!confirm("Are you sure you want to delete this report?")) return;
    
    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;
      const res = await fetch(`${backendUrl}/reports/${reportId}`, {
        method: 'DELETE',
      });
      
      if (!res.ok) throw new Error("Failed to delete report");
      
      setReports((prev) => prev.filter((r) => ((r as any)._id || r.id) !== reportId));
    } catch (err) {
      alert("Error deleting report. Please try again.");
    }
  };


  if (!isLoaded || loading) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-gray-500" />
      </div>
    );
  }

  if (!userId) {
    return (
      <div className="flex h-[60vh] flex-col items-center justify-center">
        <AlertCircle className="mb-4 h-12 w-12 text-gray-500" />
        <h2 className="text-xl font-medium text-white mb-2">Sign in required</h2>
        <p className="text-gray-400 mb-6 text-center max-w-sm">
          You must be logged in to view your scan history.
        </p>
        <Link 
          href="/sign-in" 
          className="border border-white/20 bg-white/5 hover:bg-white/10 text-white px-6 py-2 rounded-full transition-colors"
        >
          Sign In
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl px-6 py-16">
      <div className="mb-10 text-center sm:text-left">
        <h1 className="text-3xl sm:text-4xl font-light tracking-tight text-white mb-3">
          My Scans
        </h1>
        <p className="text-gray-400">
          Review your past AI radiology analysis reports.
        </p>
      </div>

      {error ? (
        <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-6 text-center">
          <p className="text-red-400">{error}</p>
        </div>
      ) : reports.length === 0 ? (
        <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-12 text-center">
          <FileText className="mx-auto h-12 w-12 text-gray-600 mb-4" />
          <h3 className="text-xl font-medium text-white mb-2">No scans found</h3>
          <p className="text-gray-400 mb-6">
            You haven't uploaded any chest X-rays yet.
          </p>
          <Link 
            href="/demo" 
            className="inline-flex items-center justify-center rounded-full bg-white px-6 py-2.5 text-sm font-medium text-black hover:bg-gray-200 transition-colors"
          >
            Start New Analysis
          </Link>
        </div>
      ) : (
        <div className="grid gap-6">
          {reports.map((report, idx) => {
            const date = new Date(report.created_at);
            const dateString = new Intl.DateTimeFormat('en-US', {
              dateStyle: 'medium',
              timeStyle: 'short',
            }).format(date);

            return (
              <motion.div
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }}
                key={(report as any)._id || report.id || `report-${idx}`}
                className="flex flex-col md:flex-row gap-6 rounded-2xl border border-white/10 bg-[#0a0a0a] p-6 shadow-xl overflow-hidden relative group"
              >
                {/* Image Section */}
                <div className="shrink-0 flex justify-center">
                  {report.heatmap_base64 ? (
                    <img
                      src={`data:image/png;base64,${report.heatmap_base64}`}
                      alt="Scan Heatmap"
                      className="h-48 w-48 rounded-xl object-cover border border-white/10 shadow-lg"
                    />
                  ) : (
                    <div className="flex h-48 w-48 items-center justify-center rounded-xl border border-white/10 bg-white/5">
                      <FileText className="text-gray-500 w-10 h-10" />
                    </div>
                  )}
                </div>

                {/* Content Section */}
                <div className="flex-1 flex flex-col min-w-0">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-3 gap-2">
                    <div>
                      <h3 className="text-xl font-medium text-white capitalize truncate">
                        {report.disease.replace(/_/g, " ")}
                      </h3>
                      <p className="text-sm text-gray-500 mt-0.5">
                        {dateString}
                      </p>
                    </div>
                    
                    <div className="flex items-center gap-2 self-start sm:self-auto">
                      <span className={`text-xs font-mono px-2.5 py-1 rounded-full border ${
                        report.confidence >= 0.8 ? 'border-green-500/30 text-green-400 bg-green-500/10' :
                        report.confidence >= 0.5 ? 'border-yellow-500/30 text-yellow-400 bg-yellow-500/10' :
                        'border-red-500/30 text-red-400 bg-red-500/10'
                      }`}>
                        {(report.confidence * 100).toFixed(1)}% Confidence
                      </span>
                    </div>
                  </div>

                  <div className="prose prose-invert prose-sm max-w-none text-gray-300 mt-2 line-clamp-4 group-hover:line-clamp-none transition-all duration-300">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {report.report || "No medical report generated."}
                    </ReactMarkdown>
                  </div>
                  
                  <div className="mt-auto pt-4 flex flex-wrap items-center gap-3">
                    <span className="text-xs border border-white/10 bg-white/5 px-2 py-1 rounded text-gray-400 truncate max-w-[200px]">
                      {report.filename}
                    </span>
                    {report.gcs_url && (
                      <a 
                        href={report.gcs_url.replace("gs://", "https://storage.googleapis.com/")} 
                        target="_blank" 
                        rel="noopener noreferrer" 
                        className="text-xs text-blue-400 hover:text-blue-300 underline underline-offset-2"
                      >
                        View Original X-Ray
                      </a>
                    )}
                    <div className="flex-1" />
                    <button
                      onClick={() => handleDelete((report as any)._id || report.id)}
                      className="text-xs text-red-500/70 hover:text-red-400 hover:bg-red-500/10 px-2 py-1.5 rounded transition-colors flex items-center gap-1.5 ml-auto"
                      title="Delete report"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                      Delete
                    </button>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
}
