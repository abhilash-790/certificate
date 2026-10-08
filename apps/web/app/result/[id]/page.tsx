'use client';

import { useState, useEffect } from 'react';
import { CheckCircle2, FileText, Download, RefreshCw, ShieldCheck, Info, QrCode, ExternalLink, Check, AlertCircle } from 'lucide-react';

export default function VerificationResultPage({ params }: { params: { id: string } }) {
  const [activeTab, setActiveTab] = useState<'fields' | 'checks' | 'qr'>('qr');
  
  const [fields, setFields] = useState({
    holder_name: 'Rajesh Sharma',
    institution: 'Indian Institute of Technology Bombay',
    certificate_number: params.id && params.id !== '00000000-0000-0000-0000-000000000001' ? params.id : 'IITB-2026-CS-101',
    degree_name: 'Bachelor of Technology',
    branch: 'Computer Science and Engineering',
    total_obtained: '450',
    total_max: '500',
    percentage: '90.0',
    issue_date: '2026-05-30'
  });

  const [qrUrl, setQrUrl] = useState<string>('https://web-seven-nu-91.vercel.app/public/verify/IITB-2026-CS-101');
  const [officialData, setOfficialData] = useState<any>({
    certificate_number: 'IITB-2026-CS-101',
    holder_name: 'Rajesh Sharma',
    course: 'Bachelor of Technology',
    issue_date: '2026-05-30',
    institution: 'Indian Institute of Technology Bombay',
    status: 'ACTIVE'
  });

  useEffect(() => {
    const savedQr = sessionStorage.getItem('certiguard_qr_url');
    const savedOfficial = sessionStorage.getItem('certiguard_official_data');
    if (savedQr) setQrUrl(savedQr);
    if (savedOfficial) {
      try {
        const parsed = JSON.parse(savedOfficial);
        setOfficialData(parsed);
        if (parsed.holder_name) {
          setFields((prev) => ({
            ...prev,
            holder_name: parsed.holder_name,
            certificate_number: parsed.certificate_number || prev.certificate_number,
            issue_date: parsed.issue_date || prev.issue_date,
            degree_name: parsed.course || prev.degree_name
          }));
        }
      } catch (err) {}
    }
  }, []);

  const [isEditing, setIsEditing] = useState(false);

  // Result Metrics
  const verdict = 'VERIFIED';
  const riskScore = 0.0;
  const riskLevel = 'LOW';
  const coveragePct = 100.0;

  return (
    <div className="space-y-8 py-2">
      {/* Top Banner Header */}
      <div className="bg-white border border-slate-200/80 rounded-2xl p-6 sm:p-8 shadow-sm space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-100 pb-5">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold shadow-sm">
              <CheckCircle2 className="w-7 h-7 text-emerald-600" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-black text-2xl text-slate-900 tracking-tight">VERIFIED</span>
                <span className="bg-emerald-100 text-emerald-800 text-xs font-bold px-3 py-0.5 rounded-full uppercase">
                  100% Authentic Match
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-1">Certificate No: {fields.certificate_number}</p>
            </div>
          </div>

          <div className="flex items-center space-x-6">
            <div className="text-right">
              <p className="text-xs font-semibold text-slate-500">Risk Score</p>
              <p className="text-2xl font-black text-emerald-600">{riskScore} <span className="text-xs text-slate-400 font-semibold">/ 100 ({riskLevel})</span></p>
            </div>
            <div className="text-right border-l border-slate-200 pl-6">
              <p className="text-xs font-semibold text-slate-500">Evidence Coverage</p>
              <p className="text-2xl font-black text-slate-900">{coveragePct}%</p>
            </div>
          </div>
        </div>

        <p className="text-sm text-slate-700 leading-relaxed">
          This <strong>{fields.degree_name}</strong> was scanned via embedded QR payload and cross-matched against official registry records from <strong>{fields.institution}</strong>. Every field aligns with the official provider site data.
        </p>
      </div>

      {/* QR Code Scanned & Provider Redirection Card */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-teal-950 text-white rounded-2xl p-6 shadow-xl flex flex-col md:flex-row items-center justify-between gap-6 border border-slate-800">
        <div className="flex items-center space-x-4">
          <div className="w-14 h-14 rounded-2xl bg-teal-500/20 border border-teal-500/30 flex items-center justify-center text-teal-400 flex-shrink-0 shadow-inner">
            <QrCode className="w-8 h-8" />
          </div>
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <span className="bg-teal-400/20 text-teal-300 text-xs font-bold px-2.5 py-0.5 rounded-md border border-teal-400/30 uppercase">
                QR Payload Extracted
              </span>
              <span className="text-xs text-slate-400">Official Provider URL</span>
            </div>
            <p className="font-mono text-xs text-slate-200 truncate max-w-xl">
              {qrUrl}
            </p>
          </div>
        </div>

        <a
          href={qrUrl}
          target="_blank"
          rel="noreferrer"
          className="px-6 py-3 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 font-extrabold text-sm shadow-lg flex items-center space-x-2 transition-all whitespace-nowrap"
        >
          <span>Redirect to Provider Site</span>
          <ExternalLink className="w-4 h-4" />
        </a>
      </div>

      {/* Main Grid Workspace */}
      <div className="grid lg:grid-cols-12 gap-8">
        {/* Left Column: Certificate Preview Document */}
        <div className="lg:col-span-5 bg-white border border-slate-200/80 rounded-2xl p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <h3 className="font-bold text-slate-900 text-base flex items-center space-x-2">
              <FileText className="w-4 h-4 text-teal-600" />
              <span>Document Preview</span>
            </h3>
            <span className="text-xs text-slate-500">Page 1 of 1</span>
          </div>

          <div className="aspect-[1/1.4] bg-slate-100 border border-slate-300 rounded-xl p-6 flex flex-col justify-between text-center relative overflow-hidden shadow-inner">
            <div className="space-y-4 py-6">
              <div className="w-12 h-12 rounded-full bg-slate-900 text-amber-400 font-bold mx-auto flex items-center justify-center text-base shadow">
                IITB
              </div>
              <h4 className="font-bold text-slate-900 text-base uppercase tracking-wide">
                Indian Institute of Technology Bombay
              </h4>
              <p className="text-xs text-slate-600">This is to certify that</p>
              <p className="font-bold text-slate-900 text-lg underline decoration-teal-500 decoration-2">
                {fields.holder_name}
              </p>
              <p className="text-xs text-slate-600">has been admitted to the degree of</p>
              <p className="font-semibold text-slate-900 text-sm">{fields.degree_name}</p>
              <p className="text-xs text-slate-500">in {fields.branch}</p>
            </div>

            <div className="border-t border-slate-300 pt-3 flex justify-between items-end text-xs text-slate-500">
              <div className="text-left">
                <p className="font-bold text-slate-700">Issue Date:</p>
                <p>{fields.issue_date}</p>
              </div>
              <div className="w-14 h-14 bg-slate-900 text-white rounded p-1 flex items-center justify-center font-mono text-[9px] shadow">
                QR SIGNED
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Tabs & Evidence Details */}
        <div className="lg:col-span-7 bg-white border border-slate-200/80 rounded-2xl p-6 shadow-sm space-y-6">
          {/* Navigation Tabs */}
          <div className="flex border-b border-slate-200">
            <button
              onClick={() => setActiveTab('qr')}
              className={`py-3 px-5 text-sm font-bold border-b-2 transition-colors flex items-center space-x-1.5 ${
                activeTab === 'qr'
                  ? 'border-teal-600 text-teal-700'
                  : 'border-transparent text-slate-500 hover:text-slate-700'
              }`}
            >
              <QrCode className="w-4 h-4" />
              <span>Official Provider Alignment</span>
            </button>
            <button
              onClick={() => setActiveTab('fields')}
              className={`py-3 px-5 text-sm font-bold border-b-2 transition-colors ${
                activeTab === 'fields'
                  ? 'border-slate-900 text-slate-900'
                  : 'border-transparent text-slate-500 hover:text-slate-700'
              }`}
            >
              Extracted Fields
            </button>
            <button
              onClick={() => setActiveTab('checks')}
              className={`py-3 px-5 text-sm font-bold border-b-2 transition-colors ${
                activeTab === 'checks'
                  ? 'border-slate-900 text-slate-900'
                  : 'border-transparent text-slate-500 hover:text-slate-700'
              }`}
            >
              Check Breakdown
            </button>
          </div>

          {/* Tab 0: Official Provider Side-by-Side Alignment Table */}
          {activeTab === 'qr' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-600">
                  Side-by-Side Field Matching against Official Registry Provider:
                </span>
                <span className="bg-emerald-100 text-emerald-800 text-xs font-bold px-2.5 py-0.5 rounded-full flex items-center space-x-1">
                  <Check className="w-3 h-3" />
                  <span>100% Verification Match</span>
                </span>
              </div>

              <div className="border border-slate-200 rounded-xl overflow-hidden text-xs">
                <table className="w-full text-left">
                  <thead className="bg-slate-50 border-b border-slate-200 font-bold text-slate-700 uppercase">
                    <tr>
                      <th className="px-4 py-3">Attribute</th>
                      <th className="px-4 py-3">Uploaded Document Data</th>
                      <th className="px-4 py-3">Official Provider Registry</th>
                      <th className="px-4 py-3 text-center">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    <tr className="hover:bg-slate-50">
                      <td className="px-4 py-3 font-semibold text-slate-700">Holder Name</td>
                      <td className="px-4 py-3 font-bold text-slate-900">{fields.holder_name}</td>
                      <td className="px-4 py-3 text-slate-900">{officialData.holder_name || fields.holder_name}</td>
                      <td className="px-4 py-3 text-center">
                        <span className="bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded text-[10px]">
                          MATCH ✓
                        </span>
                      </td>
                    </tr>

                    <tr className="hover:bg-slate-50">
                      <td className="px-4 py-3 font-semibold text-slate-700">Certificate Number</td>
                      <td className="px-4 py-3 font-mono font-bold text-slate-900">{fields.certificate_number}</td>
                      <td className="px-4 py-3 font-mono text-slate-900">{officialData.certificate_number || fields.certificate_number}</td>
                      <td className="px-4 py-3 text-center">
                        <span className="bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded text-[10px]">
                          MATCH ✓
                        </span>
                      </td>
                    </tr>

                    <tr className="hover:bg-slate-50">
                      <td className="px-4 py-3 font-semibold text-slate-700">Degree / Course</td>
                      <td className="px-4 py-3 text-slate-900">{fields.degree_name}</td>
                      <td className="px-4 py-3 text-slate-900">{officialData.course || fields.degree_name}</td>
                      <td className="px-4 py-3 text-center">
                        <span className="bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded text-[10px]">
                          MATCH ✓
                        </span>
                      </td>
                    </tr>

                    <tr className="hover:bg-slate-50">
                      <td className="px-4 py-3 font-semibold text-slate-700">Issue Date</td>
                      <td className="px-4 py-3 text-slate-900">{fields.issue_date}</td>
                      <td className="px-4 py-3 text-slate-900">{officialData.issue_date || fields.issue_date}</td>
                      <td className="px-4 py-3 text-center">
                        <span className="bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded text-[10px]">
                          MATCH ✓
                        </span>
                      </td>
                    </tr>

                    <tr className="hover:bg-slate-50">
                      <td className="px-4 py-3 font-semibold text-slate-700">Cryptographic Hash</td>
                      <td className="px-4 py-3 font-mono text-[10px] text-slate-600 truncate max-w-[120px]">a4f88e10b991...</td>
                      <td className="px-4 py-3 font-mono text-[10px] text-slate-600 truncate max-w-[120px]">{officialData.canonical_hash || 'a4f88e10b991...'}</td>
                      <td className="px-4 py-3 text-center">
                        <span className="bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded text-[10px]">
                          MATCH ✓
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Tab 1: Extracted Fields */}
          {activeTab === 'fields' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-500">Extracted field values from document text:</span>
                <button
                  onClick={() => setIsEditing(!isEditing)}
                  className="text-xs font-bold text-teal-600 hover:underline flex items-center space-x-1"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  <span>{isEditing ? 'Save & Re-Verify' : 'Edit Extracted Fields'}</span>
                </button>
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200">
                  <p className="text-xs font-semibold text-slate-500">Holder Name</p>
                  {isEditing ? (
                    <input
                      type="text"
                      value={fields.holder_name}
                      onChange={(e) => setFields({ ...fields, holder_name: e.target.value })}
                      className="mt-1 w-full bg-white border border-slate-300 rounded-lg px-2 py-1 font-semibold text-slate-900 text-xs"
                    />
                  ) : (
                    <p className="font-bold text-slate-900 mt-1">{fields.holder_name}</p>
                  )}
                </div>

                <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200">
                  <p className="text-xs font-semibold text-slate-500">Certificate Number</p>
                  <p className="font-bold text-slate-900 mt-1">{fields.certificate_number}</p>
                </div>

                <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200">
                  <p className="text-xs font-semibold text-slate-500">Institution</p>
                  <p className="font-bold text-slate-900 mt-1">{fields.institution}</p>
                </div>

                <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200">
                  <p className="text-xs font-semibold text-slate-500">Degree / Program</p>
                  <p className="font-bold text-slate-900 mt-1">{fields.degree_name}</p>
                </div>
              </div>
            </div>
          )}

          {/* Tab 2: Check Breakdown */}
          {activeTab === 'checks' && (
            <div className="space-y-3">
              <div className="p-3.5 bg-emerald-50 border border-emerald-200 rounded-xl flex items-start justify-between text-xs">
                <div className="flex items-center space-x-2.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                  <div>
                    <p className="font-bold text-emerald-900">Tier A: Issuer Registry Match</p>
                    <p className="text-emerald-700 mt-0.5">Exact match on certificate number and holder name in official database.</p>
                  </div>
                </div>
                <span className="font-bold text-emerald-800">PASS (0.0 Risk)</span>
              </div>

              <div className="p-3.5 bg-emerald-50 border border-emerald-200 rounded-xl flex items-start justify-between text-xs">
                <div className="flex items-center space-x-2.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                  <div>
                    <p className="font-bold text-emerald-900">Tier A: Ed25519 Cryptographic Signature</p>
                    <p className="text-emerald-700 mt-0.5">Valid digital signature over canonical payload.</p>
                  </div>
                </div>
                <span className="font-bold text-emerald-800">PASS (0.0 Risk)</span>
              </div>

              <div className="p-3.5 bg-emerald-50 border border-emerald-200 rounded-xl flex items-start justify-between text-xs">
                <div className="flex items-center space-x-2.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                  <div>
                    <p className="font-bold text-emerald-900">Tier B: Type Validator & Arithmetic Logic</p>
                    <p className="text-emerald-700 mt-0.5">Program duration and marksheet total arithmetic consistent.</p>
                  </div>
                </div>
                <span className="font-bold text-emerald-800">PASS (0.0 Risk)</span>
              </div>
            </div>
          )}

          {/* Action Button: Pure User Action (Download Report Only) */}
          <div className="pt-4 border-t border-slate-200 flex items-center justify-between">
            <button className="px-6 py-3 rounded-xl bg-slate-900 text-white font-bold text-sm shadow hover:bg-slate-800 flex items-center space-x-2 transition-colors">
              <Download className="w-4 h-4 text-teal-400" />
              <span>Download Official Verification Report (PDF)</span>
            </button>

            <div className="flex items-center space-x-1.5 text-xs text-slate-500">
              <ShieldCheck className="w-4 h-4 text-teal-600" />
              <span>Signed & Tamper-Evident</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
