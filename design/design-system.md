# CertiGuard UI/UX Design System & Screen Specifications

## 1. Design Direction & Core Principles

CertiGuard follows a **fintech / high-trust security dashboard** design aesthetic. It avoids decorative AI tropes (no glowing glassmorphism, no fake matrix grids, no dark-only requirements). 

* **Theme**: Light theme primary. High-contrast typography and semantic visual indicators.
* **Colors**: Deep Navy (`#0F172A`) for primary branding, Slate Grays (`#334155`, `#64748B`, `#F8FAFC`) for UI framing, Teal (`#0D9488`) for actionable highlights.
* **Semantic Status System**:
  * **Verified / Low Risk**: Emerald Green (`#059669` bg light `#ECFDF5`, icon `CheckCircle`)
  * **Medium Risk / Needs Review**: Amber (`#D97706` bg light `#FFFBEB`, icon `AlertTriangle`)
  * **High Risk / Not Verified**: Red (`#DC2626` bg light `#FEF2F2`, icon `XCircle`)
  * **Revoked**: Slate / Dark Red (`#991B1B` bg light `#FEE2E2`, icon `Ban`)
  * **Unverifiable Issuer**: Blue-Gray (`#475569` bg light `#F1F5F9`, icon `HelpCircle`)
* **UX Rule**: Status colors are **ALWAYS** paired with an icon AND explicit text label. Colors are never used alone for state (WCAG 1.4.1 compliance).

---

## 2. Component Specifications

### 2.1 `VerdictBadge`
Displays the proven verdict.
* Variants: `VERIFIED`, `REVOKED`, `NOT_VERIFIED`, `NEEDS_REVIEW`, `UNVERIFIABLE_ISSUER`.
* Renders icon + label + popover explanation.

### 2.2 `RiskBadge` & `CoverageMeter`
* **Risk Meter**: Horizontal bar (0 to 100) divided into LOW (0-30), MEDIUM (31-65), HIGH (66-100).
* **Coverage Meter**: Percentage indicator reflecting the proportion of applicable checks evaluated. Displays warning tag `"Limited evidence (<40%)"` when coverage is low.

### 2.3 `UploadDropzone`
Drag-and-drop file uploader supporting `PDF`, `PNG`, `JPEG` up to 10 MB. Shows:
* Idle state with privacy reassurance note.
* File loading / progress animation.
* Instant client-side validation error (oversized, invalid mime type).
* Detected type badge (`Degree`, `Marksheet`, `Training`) with confidence meter and manual override selector.

### 2.4 `FieldEditor` (Side-by-Side Verification)
Displays extracted field list beside the certificate preview.
* Highlights low-confidence fields in Amber.
* Displays original raw OCR value alongside current value.
* Inline edit form with "Save & Re-Verify" trigger.

### 2.5 `CheckBreakdown`
Groups check results into Evidence Tiers:
* **Tier A**: Authoritative Proof
* **Tier B**: Deterministic Logic
* **Tier C**: Forensic Indicators
* Each check row displays: Check Name, Pass/Warn/Fail/N/A icon, Tier Badge, Score, and Detail Tooltip.

---

## 3. Screen Inventory & Layout Contracts

1. **Landing Page (`app/page.tsx`)**:
   - Hero banner with instant upload CTA.
   - 4-step workflow breakdown (Upload $\rightarrow$ Extract $\rightarrow$ Validate $\rightarrow$ Verdict).
   - Trust and privacy assurance section (encrypted storage, no data resale).

2. **Upload & Processing (`app/verify/page.tsx`)**:
   - Drag-and-drop upload workspace.
   - Stepper progression: `Ingest` $\rightarrow$ `Classify` $\rightarrow$ `Extract` $\rightarrow$ `Integrity` $\rightarrow$ `Forensics` $\rightarrow$ `Score`.

3. **Verification Result Dashboard (`app/result/[id]/page.tsx`)**:
   - Header: Verdict badge, Risk level, Risk score, Evidence coverage %, Plain-language summary.
   - Left Column: Interactive Zoomable Document Viewer with Tamper Overlay toggle.
   - Right Column (Tabs): `Extracted Fields`, `Check Details`, `Issuer Comparison`.
   - Bottom Section: Structured Reasons list, Action buttons (`Download PDF Report`, `Send to Reviewer`).

4. **Public Verification Page (`app/public/verify/[token]/page.tsx`)**:
   - Clean, mobile-first lookup card for QR code scans.
   - Shows: Issuer Name, Certificate Number, Holder Name (Masked), Issue Date, Verification Status.
   - Stripped of internal risk scores, storage paths, and sensitive internal evidence.

5. **Reviewer Workspace (`app/review/page.tsx` & `app/review/[id]/page.tsx`)**:
   - Queue table prioritized by `HIGH` risk items.
   - Side-by-side comparison workspace: uploaded document vs registry master record.
   - Required reviewer decision panel (`APPROVE`, `REJECT`, `NEEDS_INFO`) with required note text area.

6. **Institution Portal (`app/issuer/page.tsx`)**:
   - Registry table of issued certificates.
   - Certificate issuance form generating signed Ed25519 payloads and QR tokens.
   - Revocation workflow modal with audit reason capture.

7. **Admin Dashboard (`app/admin/page.tsx`)**:
   - System analytics, institution approvals, template manager, audit logs, and evaluation metrics dashboard.
