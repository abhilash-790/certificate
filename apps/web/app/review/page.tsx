'use client';

import { useState } from 'react';
import { AlertTriangle, CheckCircle, XCircle, Eye } from 'lucide-react';

export default function ReviewerQueuePage() {
  const [selectedTicket, setSelectedTicket] = useState<any | null>(null);
  const [notes, setNotes] = useState('');

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Reviewer Queue</h1>
        <p className="text-slate-600 mt-1">
          Review tickets flagged with high risk, evidence discrepancies, or unverifiable issuer claims.
        </p>
      </div>

      <div className="grid lg:grid-cols-12 gap-8">
        {/* Left Column: Priority Ticket Queue */}
        <div className="lg:col-span-6 bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-200 font-bold text-slate-900 text-base flex justify-between items-center">
            <span>Pending Flagged Tickets</span>
            <span className="bg-amber-100 text-amber-800 text-xs font-extrabold px-2.5 py-0.5 rounded-full">
              HIGH Priority First
            </span>
          </div>

          <div className="divide-y divide-slate-100">
            <div
              onClick={() => setSelectedTicket({ id: "rev_1", holder: "Vikram Malhotra", type: "marksheet", risk: 85.0, reason: "Arithmetic total mismatch (sum 420 != 490 printed)" })}
              className="p-5 hover:bg-slate-50 cursor-pointer transition-colors space-y-2 border-l-4 border-amber-500"
            >
              <div className="flex justify-between items-center">
                <span className="font-bold text-slate-900 text-base">Vikram Malhotra</span>
                <span className="bg-red-100 text-red-800 text-xs font-bold px-2 py-0.5 rounded">
                  Risk: 85.0 (HIGH)
                </span>
              </div>
              <p className="text-xs text-slate-500">Marksheet • Hard Arithmetic Failure</p>
              <p className="text-xs text-amber-700 bg-amber-50 p-2 rounded border border-amber-200">
                Sum of subject marks (420) does not equal printed total (490).
              </p>
            </div>
          </div>
        </div>

        {/* Right Column: Ticket Inspection & Decision Panel */}
        <div className="lg:col-span-6 bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-6">
          {selectedTicket ? (
            <div className="space-y-6">
              <div className="border-b border-slate-200 pb-4">
                <h3 className="font-bold text-slate-900 text-xl">{selectedTicket.holder}</h3>
                <p className="text-xs text-slate-500 capitalize">Ticket ID: {selectedTicket.id} • Type: {selectedTicket.type}</p>
              </div>

              <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-2 text-xs">
                <p className="font-bold text-slate-700">Discrepancy Details:</p>
                <p className="text-slate-900">{selectedTicket.reason}</p>
              </div>

              <div className="space-y-2 text-xs">
                <label className="font-semibold text-slate-700 block">Reviewer Decision Notes (Required):</label>
                <textarea
                  rows={4}
                  required
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Enter detailed notes explaining the audit decision..."
                  className="w-full bg-white border border-slate-300 rounded-lg p-3 text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900"
                />
              </div>

              <div className="flex space-x-3 pt-2">
                <button
                  disabled={!notes.trim()}
                  className="flex-1 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-300 text-white font-bold text-xs shadow flex items-center justify-center space-x-1"
                >
                  <CheckCircle className="w-4 h-4" />
                  <span>Approve (VERIFIED)</span>
                </button>
                <button
                  disabled={!notes.trim()}
                  className="flex-1 py-2.5 rounded-lg bg-red-600 hover:bg-red-700 disabled:bg-slate-300 text-white font-bold text-xs shadow flex items-center justify-center space-x-1"
                >
                  <XCircle className="w-4 h-4" />
                  <span>Reject (NOT VERIFIED)</span>
                </button>
              </div>
            </div>
          ) : (
            <div className="text-center py-16 space-y-3 text-slate-400">
              <Eye className="w-10 h-10 mx-auto" />
              <p className="text-sm font-semibold">Select a flagged ticket from the queue to inspect side-by-side evidence.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
