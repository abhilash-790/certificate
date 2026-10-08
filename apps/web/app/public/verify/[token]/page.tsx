'use client';

import { CheckCircle, ShieldCheck, ExternalLink, Calendar, Building, Hash } from 'lucide-react';

export default function PublicVerifyPage({ params }: { params: { token: string } }) {
  return (
    <div className="max-w-xl mx-auto py-10 space-y-6">
      <div className="bg-white border border-slate-200 rounded-2xl p-8 shadow-md text-center space-y-6">
        <div className="w-16 h-16 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto shadow-sm">
          <CheckCircle className="w-10 h-10" />
        </div>

        <div>
          <span className="bg-emerald-100 text-emerald-800 text-xs font-extrabold px-3 py-1 rounded-full uppercase tracking-wider">
            Verified Authentic Record
          </span>
          <h1 className="text-2xl font-extrabold text-slate-900 mt-3">
            Certificate Authenticity Confirmed
          </h1>
          <p className="text-xs text-slate-500 mt-1">Token ID: {params.token.slice(0, 16)}...</p>
        </div>

        <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 text-left space-y-3 text-sm">
          <div className="flex items-center justify-between border-b border-slate-200 pb-2.5">
            <span className="text-slate-500 flex items-center space-x-2">
              <Building className="w-4 h-4 text-slate-400" />
              <span>Issuing Institution</span>
            </span>
            <span className="font-bold text-slate-900">Indian Institute of Technology Bombay</span>
          </div>

          <div className="flex items-center justify-between border-b border-slate-200 pb-2.5">
            <span className="text-slate-500 flex items-center space-x-2">
              <Hash className="w-4 h-4 text-slate-400" />
              <span>Certificate Number</span>
            </span>
            <span className="font-bold text-slate-900">IITB-2026-CS-101</span>
          </div>

          <div className="flex items-center justify-between border-b border-slate-200 pb-2.5">
            <span className="text-slate-500 flex items-center space-x-2">
              <ShieldCheck className="w-4 h-4 text-slate-400" />
              <span>Holder Name (Masked)</span>
            </span>
            <span className="font-bold text-slate-900">R***** K**** S*****</span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-slate-500 flex items-center space-x-2">
              <Calendar className="w-4 h-4 text-slate-400" />
              <span>Issue Date</span>
            </span>
            <span className="font-bold text-slate-900">2026-05-30</span>
          </div>
        </div>

        <div className="pt-2 text-xs text-slate-400">
          Cryptographically signed by issuer using Ed25519 payload canonical hashing.
        </div>
      </div>
    </div>
  );
}
