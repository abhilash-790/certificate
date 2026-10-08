'use client';

import { useState } from 'react';
import { PlusCircle, QrCode, Ban, ShieldCheck, CheckCircle2 } from 'lucide-react';

export default function IssuerPortalPage() {
  const [showIssueModal, setShowIssueModal] = useState(false);
  const [issuedCert, setIssuedCert] = useState<any | null>(null);

  const [form, setForm] = useState({
    certificate_type_code: 'degree',
    certificate_number: 'IITB-2026-CS-202',
    holder_name: 'Anita Verma',
    course: 'B.Tech Electrical Engineering',
    issue_date: '2026-06-15',
  });

  const handleIssueSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Simulate Ed25519 signing payload response
    const mockIssued = {
      id: "cert_9999",
      certificate_number: form.certificate_number,
      holder_name: form.holder_name,
      course: form.course,
      issue_date: form.issue_date,
      canonical_hash: "a4f88e10b99127ca982310199f11283c7482",
      signature: "30450221008f12a...ed25519",
      verification_token: "tok_991823ab182371",
      qr_resolve_url: `/public/verify/tok_991823ab182371`
    };
    setIssuedCert(mockIssued);
    setShowIssueModal(false);
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Institution Issuer Portal</h1>
          <p className="text-slate-600 mt-1">
            Register, issue, and manage cryptographically signed certificates with verification QR tokens.
          </p>
        </div>
        <button
          onClick={() => setShowIssueModal(true)}
          className="px-5 py-3 rounded-lg bg-slate-900 text-white font-bold text-sm shadow hover:bg-slate-800 flex items-center space-x-2 transition-colors"
        >
          <PlusCircle className="w-5 h-5" />
          <span>Issue New Certificate</span>
        </button>
      </div>

      {issuedCert && (
        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-6 space-y-4 shadow-sm">
          <div className="flex items-center space-x-2 text-emerald-800 font-bold text-lg">
            <CheckCircle2 className="w-6 h-6 text-emerald-600" />
            <span>Certificate Successfully Issued & Signed!</span>
          </div>

          <div className="grid md:grid-cols-2 gap-4 text-sm">
            <div className="space-y-1">
              <p className="text-xs text-slate-500 font-semibold">Certificate Number:</p>
              <p className="font-bold text-slate-900">{issuedCert.certificate_number}</p>
              <p className="text-xs text-slate-500 font-semibold mt-2">Recipient:</p>
              <p className="font-bold text-slate-900">{issuedCert.holder_name}</p>
            </div>
            <div className="space-y-1">
              <p className="text-xs text-slate-500 font-semibold">SHA-256 Canonical Payload Hash:</p>
              <p className="font-mono text-xs text-slate-700 bg-white p-2 rounded border border-slate-200 truncate">
                {issuedCert.canonical_hash}
              </p>
              <p className="text-xs text-slate-500 font-semibold mt-2">Public QR Verification Link:</p>
              <a href={issuedCert.qr_resolve_url} className="text-xs font-bold text-teal-600 underline truncate block">
                {issuedCert.qr_resolve_url}
              </a>
            </div>
          </div>
        </div>
      )}

      {/* Issued Registry Table */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 font-bold text-slate-900 text-base">
          Issued Certificate Registry
        </div>
        <table className="w-full text-left text-sm text-slate-600">
          <thead className="bg-slate-50 border-b border-slate-200 text-xs font-bold text-slate-700 uppercase">
            <tr>
              <th className="px-6 py-3">Cert Number</th>
              <th className="px-6 py-3">Holder Name</th>
              <th className="px-6 py-3">Course</th>
              <th className="px-6 py-3">Issue Date</th>
              <th className="px-6 py-3">Status</th>
              <th className="px-6 py-3">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            <tr className="hover:bg-slate-50">
              <td className="px-6 py-4 font-bold text-slate-900">IITB-2026-CS-101</td>
              <td className="px-6 py-4">Rajesh Sharma</td>
              <td className="px-6 py-4">B.Tech Computer Science</td>
              <td className="px-6 py-4">2026-05-30</td>
              <td className="px-6 py-4">
                <span className="bg-emerald-100 text-emerald-800 text-xs font-bold px-2 py-0.5 rounded-full">ACTIVE</span>
              </td>
              <td className="px-6 py-4">
                <button className="text-xs font-bold text-red-600 hover:underline flex items-center space-x-1">
                  <Ban className="w-3.5 h-3.5" />
                  <span>Revoke</span>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* Issue Modal */}
      {showIssueModal && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl p-6 max-w-lg w-full space-y-5 shadow-xl">
            <h3 className="font-bold text-slate-900 text-xl">Issue Signed Certificate</h3>

            <form onSubmit={handleIssueSubmit} className="space-y-4 text-sm">
              <div>
                <label className="font-semibold text-slate-700 block text-xs">Certificate Number</label>
                <input
                  type="text"
                  required
                  value={form.certificate_number}
                  onChange={(e) => setForm({ ...form, certificate_number: e.target.value })}
                  className="mt-1 w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 block text-xs">Holder Full Name</label>
                <input
                  type="text"
                  required
                  value={form.holder_name}
                  onChange={(e) => setForm({ ...form, holder_name: e.target.value })}
                  className="mt-1 w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 block text-xs">Degree / Course Title</label>
                <input
                  type="text"
                  required
                  value={form.course}
                  onChange={(e) => setForm({ ...form, course: e.target.value })}
                  className="mt-1 w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900"
                />
              </div>

              <div className="flex justify-end space-x-3 pt-4 border-t border-slate-200">
                <button
                  type="button"
                  onClick={() => setShowIssueModal(false)}
                  className="px-4 py-2 rounded-lg border border-slate-300 text-slate-700 font-semibold text-xs hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-lg bg-slate-900 text-white font-bold text-xs shadow hover:bg-slate-800"
                >
                  Sign & Issue Record
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
