'use client';

import { ShieldCheck, FileCheck2, Cpu, CheckCircle2, Lock, ArrowRight, Layers, Eye, Sparkles } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="space-y-16 py-4">
      {/* Hero Section */}
      <section className="text-center max-w-4xl mx-auto space-y-8">
        <div className="inline-flex items-center space-x-2 bg-teal-50 border border-teal-200/80 px-4 py-1.5 rounded-full text-xs font-bold text-teal-800 shadow-sm">
          <Sparkles className="w-3.5 h-3.5 text-teal-600 animate-pulse" />
          <span>AI-Powered Multi-Tier Certificate Verification</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-black text-slate-900 tracking-tight leading-[1.15]">
          Instant Certificate Integrity & <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-slate-900 via-teal-700 to-teal-600">
            Fraud Risk Detection
          </span>
        </h1>

        <p className="text-lg text-slate-600 max-w-2xl mx-auto leading-relaxed">
          Verify academic degrees, university marksheets, and professional training credentials against authoritative issuer registries, Ed25519 signatures, and automated image forensics.
        </p>

        <div className="pt-2 flex justify-center">
          <a
            href="/verify"
            className="group px-8 py-4 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold shadow-lg hover:shadow-xl transition-all duration-200 flex items-center space-x-3 text-base"
          >
            <FileCheck2 className="w-5 h-5 text-teal-400" />
            <span>Verify a Certificate Now</span>
            <ArrowRight className="w-5 h-5 text-slate-400 group-hover:translate-x-1 transition-transform" />
          </a>
        </div>

        {/* Quick Trust Badges */}
        <div className="pt-6 flex flex-wrap items-center justify-center gap-8 text-xs font-semibold text-slate-500 border-t border-slate-200/60 max-w-3xl mx-auto">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>Deterministic Issuer Matching</span>
          </div>
          <div className="flex items-center space-x-2">
            <Lock className="w-4 h-4 text-teal-600" />
            <span>Ed25519 Payload Signatures</span>
          </div>
          <div className="flex items-center space-x-2">
            <Cpu className="w-4 h-4 text-indigo-600" />
            <span>Error Level Analysis (ELA)</span>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="max-w-5xl mx-auto space-y-8 bg-white border border-slate-200/80 rounded-2xl p-8 sm:p-10 shadow-sm">
        <div className="text-center space-y-2">
          <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900">How Verification Works</h2>
          <p className="text-sm text-slate-600">4-stage automated pipeline evaluating document evidence</p>
        </div>

        <div className="grid md:grid-cols-4 gap-6 pt-4">
          <div className="p-5 bg-slate-50 border border-slate-200 rounded-xl space-y-3 relative">
            <div className="w-8 h-8 rounded-lg bg-slate-900 text-teal-400 font-extrabold flex items-center justify-center text-sm shadow">
              1
            </div>
            <h3 className="font-bold text-slate-900 text-base">Ingest & Sanitize</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Magic-byte inspection, pixel caps, and PDF sanitization against active script streams.
            </p>
          </div>

          <div className="p-5 bg-slate-50 border border-slate-200 rounded-xl space-y-3 relative">
            <div className="w-8 h-8 rounded-lg bg-slate-900 text-teal-400 font-extrabold flex items-center justify-center text-sm shadow">
              2
            </div>
            <h3 className="font-bold text-slate-900 text-base">Classify & Extract</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              OCR text extraction & vision schema parsing into degree, marksheet, or training format.
            </p>
          </div>

          <div className="p-5 bg-slate-50 border border-slate-200 rounded-xl space-y-3 relative">
            <div className="w-8 h-8 rounded-lg bg-slate-900 text-teal-400 font-extrabold flex items-center justify-center text-sm shadow">
              3
            </div>
            <h3 className="font-bold text-slate-900 text-base">Registry & Signature</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Canonical payload SHA-256 hash matching and Ed25519 public key verification.
            </p>
          </div>

          <div className="p-5 bg-slate-50 border border-slate-200 rounded-xl space-y-3 relative">
            <div className="w-8 h-8 rounded-lg bg-slate-900 text-teal-400 font-extrabold flex items-center justify-center text-sm shadow">
              4
            </div>
            <h3 className="font-bold text-slate-900 text-base">Forensics & Scoring</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Error Level Analysis (ELA), mark arithmetic validation, and plain-language risk report.
            </p>
          </div>
        </div>
      </section>

      {/* Feature Cards Grid */}
      <section className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
        <div className="p-7 bg-white border border-slate-200/80 rounded-2xl shadow-sm hover:shadow-md transition-shadow space-y-4">
          <div className="w-12 h-12 rounded-xl bg-teal-50 border border-teal-200 text-teal-700 flex items-center justify-center text-xl">
            🏛️
          </div>
          <h3 className="font-bold text-slate-900 text-lg">Authoritative Registry</h3>
          <p className="text-sm text-slate-600 leading-relaxed">
            Direct deterministic cross-checking against official university databases and registered issuer records.
          </p>
        </div>

        <div className="p-7 bg-white border border-slate-200/80 rounded-2xl shadow-sm hover:shadow-md transition-shadow space-y-4">
          <div className="p-3 w-12 h-12 rounded-xl bg-indigo-50 border border-indigo-200 text-indigo-700 flex items-center justify-center text-xl">
            🔍
          </div>
          <h3 className="font-bold text-slate-900 text-lg">Type-Specific Validators</h3>
          <p className="text-sm text-slate-600 leading-relaxed">
            Automated mark arithmetic validation, CGPA conversion rules, degree duration logic, and mill watchlists.
          </p>
        </div>

        <div className="p-7 bg-white border border-slate-200/80 rounded-2xl shadow-sm hover:shadow-md transition-shadow space-y-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700 flex items-center justify-center text-xl">
            🛡️
          </div>
          <h3 className="font-bold text-slate-900 text-lg">Explainable Risk Output</h3>
          <p className="text-sm text-slate-600 leading-relaxed">
            Transparent evidence coverage metrics and bulleted plain-language explanations. Never opaque black-box verdicts.
          </p>
        </div>
      </section>

      {/* Privacy Guarantee Footer Note */}
      <section className="bg-slate-900 text-white rounded-2xl p-8 sm:p-10 max-w-5xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6 shadow-xl">
        <div className="space-y-2 text-center md:text-left">
          <div className="flex items-center justify-center md:justify-start space-x-2 text-teal-400 font-bold text-sm">
            <ShieldCheck className="w-5 h-5" />
            <span>Strict Privacy & Data Minimization</span>
          </div>
          <h3 className="text-xl font-bold text-white">Your uploaded documents are encrypted and safe</h3>
          <p className="text-xs text-slate-400 max-w-xl">
            CertiGuard never sells document data. All uploads are stored in private encrypted object storage with automated 30-day retention cleanup.
          </p>
        </div>

        <a
          href="/verify"
          className="px-6 py-3 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-sm shadow whitespace-nowrap transition-colors"
        >
          Start Instant Verification
        </a>
      </section>
    </div>
  );
}
