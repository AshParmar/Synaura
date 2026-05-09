"use client";

import { motion } from "framer-motion";
import { Activity } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_LINKS = [
  { name: "Home", href: "/" },
  { name: "Try Demo", href: "/demo" },
  { name: "Research", href: "/research" },
  { name: "GitHub", href: "/github" },
  { name: "About", href: "#about" },
  { name: "Contact", href: "#contact" },
];

export default function Navbar() {
  const pathname = usePathname();

  return (
    <header className="w-full z-50 border-b border-border bg-black">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-3 text-white">
          <Activity className="w-6 h-6 text-white" />
          <div className="flex flex-col">
            <span className="font-medium tracking-wider text-[15px] leading-tight">SYNAURA</span>
            <span className="text-[9px] text-gray-400 tracking-[0.15em]">AI RADIOLOGY INTELLIGENCE</span>
          </div>
        </Link>

        {/* Links */}
        <nav className="hidden lg:flex items-center gap-8">
          {NAV_LINKS.map((link) => {
            const isActive = pathname === link.href || (pathname === "/" && link.name === "Home");
            return (
              <Link
                key={link.name}
                href={link.href}
                className={`text-sm transition-colors pt-1 ${
                  isActive
                    ? "text-white font-medium border-b border-white pb-1"
                    : "text-gray-400 hover:text-white pb-1"
                }`}
              >
                {link.name}
              </Link>
            );
          })}
        </nav>

        {/* CTA */}
        <div className="flex items-center gap-4">
          <a
            href="https://github.com/ashparmar/synaura"
            target="_blank"
            rel="noopener noreferrer"
            className="w-9 h-9 rounded-full border border-border flex items-center justify-center text-white hover:bg-white/5 transition-colors"
          >
             <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.2c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"/><path d="M9 18c-4.51 2-5-2-7-2"/></svg>
          </a>
          <Link
            href="/demo"
            className="text-sm font-medium border border-border bg-transparent text-white px-5 py-2 rounded-full hover:bg-white/5 transition-colors flex items-center gap-2"
          >
             Try Demo →
          </Link>
        </div>
      </div>
    </header>
  );
}
