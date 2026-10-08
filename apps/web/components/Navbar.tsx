'use client';

import { usePathname } from 'next/navigation';
import { Shield, FileCheck, HelpCircle } from 'lucide-react';

export default function Navbar() {
  const pathname = usePathname();
  const isAdmin = pathname.startsWith('/admin');

  return (
    <header className="border-b border-slate-200 bg-white/95 backdrop-blur sticky top-0 z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <a href={isAdmin ? "/admin" : "/"} className="flex items-center space-x-3 group">
          <div className="w-10 h-10 rounded-xl bg-slate-900 flex items-center justify-center text-teal-400 font-bold text-xl shadow-md group-hover:scale-105 transition-transform">
            🛡️
          </div>
          <span className="font-extrabold text-xl tracking-tight text-slate-900">
            Certi<span className="text-teal-600">Guard</span>
            {isAdmin && (
              <span className="ml-2 bg-slate-900 text-teal-400 text-xs px-2.5 py-0.5 rounded-full font-mono font-medium">
                ADMIN
              </span>
            )}
          </span>
        </a>

        <nav className="flex items-center space-x-8 text-sm font-semibold text-slate-600">
          {!isAdmin && (
            <>
              <a
                href="/verify"
                className={`transition-colors flex items-center space-x-1.5 ${
                  pathname.startsWith('/verify') ? 'text-teal-600 font-bold' : 'hover:text-slate-900'
                }`}
              >
                <FileCheck className="w-4 h-4" />
                <span>Verify Certificate</span>
              </a>
              <a
                href="/#how-it-works"
                className="hover:text-slate-900 transition-colors flex items-center space-x-1.5"
              >
                <HelpCircle className="w-4 h-4 text-slate-400" />
                <span>How It Works</span>
              </a>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
