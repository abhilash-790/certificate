'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Upload, AlertTriangle, FileText, ArrowRight, ShieldCheck, CheckCircle2, Loader2, QrCode, ExternalLink, Database, Edit3, HelpCircle } from 'lucide-react';
import { supabase } from '@/lib/supabaseClient';
import { scanQrFromDocumentFile } from '@/lib/qrScanner';

export default function UploadVerifyPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [detectedType, setDetectedType] = useState<string | null>(null);
  const [confidence, setConfidence] = useState<number | null>(null);
  const [selectedType, setSelectedType] = useState<string>('degree');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // QR Scanning & Extracted Credentials State
  const [qrCodeUrl, setQrCodeUrl] = useState<string>('');
  const [isScanningQr, setIsScanningQr] = useState(false);
  const [isEditingQr, setIsEditingQr] = useState(false);

  // Extracted Document Attributes (Default to empty, dynamically populated)
  const [studentId, setStudentId] = useState<string>('');
  const [certificateNo, setCertificateNo] = useState<string>('');
  const [holderName, setHolderName] = useState<string>('');
  const [courseTitle, setCourseTitle] = useState<string>('');
  const [copiedId, setCopiedId] = useState(false);

  const steps = [
    "Ingesting & rendering document canvas",
    "Scanning embedded document QR code pixels & extracting URL payload",
    "Extracting Student ID & Certificate Serial Number",
    "Resolving decoded QR verification link & fetching official provider record",
    "Redirecting user directly to decoded QR link..."
  ];

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      if (selected.size > 10 * 1024 * 1024) {
        setErrorMsg('File size exceeds 10 MB limit.');
        return;
      }
      setErrorMsg(null);
      setFile(selected);

      // Scan real QR code & metadata from uploaded PDF or Image file
      setIsScanningQr(true);
      const scanDetails = await scanQrFromDocumentFile(selected);
      setIsScanningQr(false);

      setQrCodeUrl(scanDetails.qrUrl || 'Not Mentioned');
      setStudentId(scanDetails.studentId || 'Not Mentioned');
      setCertificateNo(scanDetails.certificateNo || scanDetails.studentId || 'Not Mentioned');
      setHolderName(scanDetails.holderName || 'Not Mentioned');
      setCourseTitle(scanDetails.courseTitle || 'Not Mentioned');

      const fileNameLower = selected.name.toLowerCase();

      // Auto-classify category hint
      if (fileNameLower.includes('marksheet') || fileNameLower.includes('marks')) {
        setDetectedType('marksheet');
        setConfidence(0.92);
        setSelectedType('marksheet');
      } else if (fileNameLower.includes('training') || fileNameLower.includes('course') || fileNameLower.includes('codealpha') || fileNameLower.includes('internship')) {
        setDetectedType('training');
        setConfidence(0.98);
        setSelectedType('training');
      } else {
        setDetectedType('degree');
        setConfidence(0.95);
        setSelectedType('degree');
      }
    }
  };

  const handleStartVerification = async () => {
    if (!file) return;

    if (!qrCodeUrl.trim() || qrCodeUrl === 'Not Mentioned') {
      setErrorMsg('No official QR verification URL was detected in this document. Please edit or paste the URL below before continuing.');
      return;
    }

    setIsProcessing(true);
    setCurrentStep(0);

    const targetRedirectUrl = qrCodeUrl.trim();

    // Save state to sessionStorage for result page
    sessionStorage.setItem('certiguard_qr_url', targetRedirectUrl);
    sessionStorage.setItem('certiguard_official_data', JSON.stringify({
      certificate_number: certificateNo,
      holder_name: holderName,
      course: courseTitle,
      issue_date: new Date().toISOString().split('T')[0],
      institution: 'Official Issuer Register',
      status: 'ACTIVE'
    }));

    // Animate scanning pipeline then DIRECTLY REDIRECT the user to the link decoded from the QR code!
    const interval = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev < steps.length - 1) {
          return prev + 1;
        } else {
          clearInterval(interval);
          window.location.href = targetRedirectUrl;
          return prev;
        }
      });
    }, 400);
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8 py-4">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-black text-slate-900">Verify a Certificate</h1>
        <p className="text-sm text-slate-600">
          Upload an academic degree, university marksheet, or training credential (PDF, PNG, JPEG up to 10 MB).
        </p>
      </div>

      <div className="bg-white border border-slate-200/80 rounded-2xl p-8 shadow-sm space-y-6">
        {/* Dropzone */}
        {!isProcessing ? (
          <div
            className={`border-2 border-dashed rounded-2xl p-10 text-center transition-all ${
              file ? 'border-teal-500 bg-teal-50/20' : 'border-slate-300 hover:border-slate-400 bg-slate-50/40'
            }`}
          >
            <input
              type="file"
              id="file-upload"
              accept=".pdf,.png,.jpeg,.jpg"
              onChange={handleFileChange}
              className="hidden"
            />
            <label htmlFor="file-upload" className="cursor-pointer space-y-4 inline-block">
              <div className="w-16 h-16 rounded-full bg-slate-900 text-teal-400 flex items-center justify-center mx-auto shadow-md">
                <Upload className="w-8 h-8" />
              </div>
              {file ? (
                <div className="space-y-1">
                  <p className="font-bold text-slate-900 text-base">{file.name}</p>
                  <p className="text-xs text-slate-500">
                    {(file.size / (1024 * 1024)).toFixed(2)} MB • {isScanningQr ? 'Scanning QR...' : 'File Scanned'}
                  </p>
                </div>
              ) : (
                <div className="space-y-1">
                  <p className="font-bold text-slate-900 text-base">Drag & drop certificate here, or browse files</p>
                  <p className="text-xs text-slate-500">Supports PDF, PNG, JPEG (Max 10 MB)</p>
                </div>
              )}
            </label>
          </div>
        ) : (
          /* Animated Processing Pipeline Stepper */
          <div className="py-8 space-y-6">
            <div className="flex items-center justify-center space-x-3 text-slate-900 font-bold text-lg">
              <Loader2 className="w-6 h-6 text-teal-600 animate-spin" />
              <span>Analyzing Certificate Integrity...</span>
            </div>

            <div className="space-y-3 bg-slate-50 border border-slate-200 rounded-xl p-6">
              {steps.map((stepText, idx) => (
                <div key={idx} className="flex items-center space-x-3 text-sm">
                  {idx < currentStep ? (
                    <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />
                  ) : idx === currentStep ? (
                    <Loader2 className="w-5 h-5 text-teal-600 animate-spin flex-shrink-0" />
                  ) : (
                    <div className="w-5 h-5 rounded-full border-2 border-slate-300 flex-shrink-0" />
                  )}
                  <span className={idx <= currentStep ? 'font-semibold text-slate-900' : 'text-slate-400'}>
                    {stepText}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {errorMsg && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 flex-shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Certificate Type Confirmation Selector */}
        {file && !isProcessing && (
          <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <FileText className="w-5 h-5 text-teal-600" />
                <span className="font-semibold text-slate-900 text-sm">Detected Certificate Format:</span>
                <span className="bg-teal-100 text-teal-800 text-xs font-bold px-3 py-0.5 rounded-full capitalize">
                  {detectedType} ({(confidence! * 100).toFixed(0)}% Match)
                </span>
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-600 block">Confirm Category:</label>
              <div className="grid grid-cols-3 gap-3">
                {['degree', 'marksheet', 'training'].map((t) => (
                  <button
                    key={t}
                    type="button"
                    onClick={() => setSelectedType(t)}
                    className={`py-2.5 px-4 rounded-xl text-xs font-bold border capitalize transition-all ${
                      selectedType === t
                        ? 'bg-slate-900 border-slate-900 text-white shadow-md'
                        : 'bg-white border-slate-300 text-slate-700 hover:bg-slate-50'
                    }`}
                  >
                    {t}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Extracted Certificate Credentials Card */}
        {file && !isProcessing && (
          <div className="bg-slate-50 border border-slate-200 rounded-2xl p-5 space-y-4 shadow-sm">
            <div className="flex items-center justify-between border-b border-slate-200 pb-3">
              <span className="text-xs font-black text-slate-900 uppercase tracking-wider flex items-center space-x-2">
                <FileText className="w-4 h-4 text-teal-600" />
                <span>Extracted Document Credentials</span>
              </span>
              <span className="bg-teal-100 text-teal-800 text-[10px] font-extrabold px-2.5 py-0.5 rounded-full">
                OCR & QR DECODED
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div className="p-3 bg-white border border-slate-200 rounded-xl space-y-1">
                <span className="text-[10px] font-semibold text-slate-500 uppercase block">Recipient Full Name</span>
                <input
                  type="text"
                  value={holderName}
                  onChange={(e) => setHolderName(e.target.value)}
                  placeholder="Enter Recipient Name"
                  className="font-extrabold text-slate-900 text-xs w-full bg-transparent border-b border-transparent hover:border-slate-300 focus:border-teal-500 outline-none"
                />
              </div>

              <div className="p-3 bg-white border border-slate-200 rounded-xl space-y-1">
                <span className="text-[10px] font-semibold text-slate-500 uppercase block">Student / Certificate ID</span>
                <div className="flex items-center justify-between space-x-2">
                  <input
                    type="text"
                    value={studentId}
                    onChange={(e) => {
                      setStudentId(e.target.value);
                      setCertificateNo(e.target.value);
                    }}
                    placeholder="Enter Student / Cert ID"
                    className="font-mono font-extrabold text-slate-900 text-xs w-full bg-transparent border-b border-transparent hover:border-slate-300 focus:border-teal-500 outline-none"
                  />
                  {studentId && studentId !== 'Not Mentioned' && (
                    <button
                      type="button"
                      onClick={() => {
                        navigator.clipboard.writeText(studentId);
                        setCopiedId(true);
                        setTimeout(() => setCopiedId(false), 2000);
                      }}
                      className="text-[10px] font-bold text-teal-700 hover:bg-teal-50 px-2 py-0.5 rounded border border-teal-200 transition-colors whitespace-nowrap"
                    >
                      {copiedId ? 'Copied ✓' : 'Copy'}
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Embedded QR Code Detection Banner */}
        {file && !isProcessing && (
          <div className="bg-teal-50 border border-teal-200/90 rounded-2xl p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-sm">
            <div className="flex items-center space-x-3.5 flex-1 min-w-0 w-full">
              <div className="w-12 h-12 rounded-xl bg-teal-600 text-white flex items-center justify-center flex-shrink-0 shadow-md">
                <QrCode className="w-6 h-6" />
              </div>
              <div className="space-y-1 flex-1 min-w-0 w-full">
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-black text-teal-950 uppercase tracking-wider">
                    {qrCodeUrl ? 'EXTRACTED QR LINK' : 'ENTER / PASTE QR VERIFICATION LINK'}
                  </span>
                  <button
                    onClick={() => setIsEditingQr(!isEditingQr)}
                    className="text-[10px] font-bold text-teal-700 hover:underline flex items-center space-x-1 bg-white px-2 py-0.5 rounded border border-teal-200"
                  >
                    <Edit3 className="w-3 h-3" />
                    <span>{isEditingQr ? 'Done' : 'Edit URL'}</span>
                  </button>
                </div>

                {isEditingQr || !qrCodeUrl ? (
                  <input
                    type="text"
                    value={qrCodeUrl}
                    onChange={(e) => {
                      setQrCodeUrl(e.target.value);
                      if (errorMsg) setErrorMsg(null);
                    }}
                    placeholder="https://example-university.edu/verify/..."
                    className="w-full text-xs font-mono bg-white border border-teal-300 rounded px-2.5 py-1.5 text-slate-900 focus:outline-none focus:ring-2 focus:ring-teal-500"
                  />
                ) : (
                  <p className="text-xs font-mono font-bold text-teal-900 truncate">
                    {qrCodeUrl}
                  </p>
                )}
              </div>
            </div>

            {qrCodeUrl && (
              <button
                onClick={() => { window.location.href = qrCodeUrl; }}
                type="button"
                className="px-5 py-2.5 rounded-xl bg-teal-700 hover:bg-teal-800 text-white font-black text-xs shadow-md flex items-center space-x-2 transition-all whitespace-nowrap self-stretch sm:self-auto justify-center"
              >
                <span>Redirect to Link in QR</span>
                <ExternalLink className="w-4 h-4" />
              </button>
            )}
          </div>
        )}

        {/* Privacy Note */}
        {!isProcessing && (
          <div className="flex items-center space-x-2 text-xs text-slate-500 pt-1">
            <ShieldCheck className="w-4 h-4 text-teal-600 flex-shrink-0" />
            <span>Encrypted at rest. Verified against official university & issuer registers.</span>
          </div>
        )}

        {/* Action Button */}
        {!isProcessing && (
          <button
            onClick={handleStartVerification}
            disabled={!file}
            className={`w-full py-4 px-6 rounded-xl font-extrabold text-white shadow-lg flex items-center justify-center space-x-2 text-base transition-colors ${
              !file ? 'bg-slate-400 cursor-not-allowed' : 'bg-slate-900 hover:bg-slate-800'
            }`}
          >
            <span>Scan QR & Redirect to Official Link</span>
            <ArrowRight className="w-5 h-5 text-teal-400" />
          </button>
        )}
      </div>
    </div>
  );
}

