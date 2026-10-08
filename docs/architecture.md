# CertiGuard Architecture & Verification Pipeline Specification

## 1. System Overview & Architecture

CertiGuard is architected as a modular monorepo containing a modern Next.js frontend, a FastAPI microservice backend, an asynchronous Celery task pipeline with Redis, PostgreSQL database, and MinIO object storage.

```
+-----------------------------------------------------------------------+
|                           Next.js Web Frontend                        |
|    (Verifier App | Reviewer Workspace | Issuer Portal | Admin Desk)    |
+-----------------------------------------------------------------------+
                                   | HTTPS REST / OpenAPI
+-----------------------------------------------------------------------+
|                          FastAPI API Gateway                          |
|         (Auth & RBAC | Ingestion | Results | Review | Admin)          |
+-----------------------------------------------------------------------+
                                   | Async Task Enqueue
+-----------------------------------------------------------------------+
|                         Celery Task Workers                           |
|                            (Redis Broker)                             |
+-----------------------------------------------------------------------+
   |             |            |            |            |           |
+------+     +-------+    +-------+    +-------+    +--------+   +------+
|Ingest|     |Classify|   |Extract|    | QR/   |    |Type    |   |Score/|
|Worker|     |Worker |    |Worker |    |Integr.|    |Validat.|   |Expln |
+------+     +-------+    +-------+    +-------+    +--------+   +------+
   |             |            |            |            |           |
+-----------------------------------------------------------------------+
|                   Data Storage & Persistence Layer                    |
|      PostgreSQL (Metadata & Results)  |  MinIO / S3 (Private Files)   |
+-----------------------------------------------------------------------+
```

---

## 2. 11-Stage Verification Pipeline Flow

Every document processing request runs through an 11-stage pipeline. Each stage operates independently, records structured evidence into `verification_checks`, and can be individually re-run upon user field edits.

1. **INGEST**:
   - Validate MIME type (`PDF`, `PNG`, `JPEG`), file size ($\le 10$ MB), magic bytes.
   - Compute SHA-256 file hash and perceptual hash (pHash).
   - Quarantine file in encrypted private object storage.
   - Check for duplicate upload (same SHA-256 or near-identical pHash).

2. **NORMALIZE**:
   - Convert PDF pages into uniform PNG page images ($300$ DPI, max 10 pages).
   - Strip active PDF streams, JavaScript objects, and external actions.

3. **CLASSIFY**:
   - Send first page image to vision LLM adapter.
   - Classify document into `degree`, `marksheet`, `training`, or `unknown`.
   - If confidence $< 0.70$, set status to `needs_type_confirmation` for user manual selection.

4. **EXTRACT**:
   - Execute PaddleOCR (or Tesseract fallback) to extract raw text and bounding boxes (`bbox`).
   - Pass OCR text and image to LLM extraction adapter with target JSON Schema.
   - Validate extracted fields against type-specific JSON Schema (`degree.json`, `marksheet.json`, `training.json`).
   - Validate that each extracted field string is anchored in raw OCR text to prevent hallucination.

5. **QR / TOKEN RESOLUTION**:
   - Detect and decode embedded QR code matrix.
   - Resolve token server-side via trusted HTTP client.
   - Enforce domain allow-listing and SSRF protections.
   - Compare QR payload payload fields against extracted OCR fields.

6. **INTEGRITY & SIGNATURE**:
   - Construct canonical payload from registry / extracted data.
   - Verify Ed25519 cryptographic signature against issuer's public key (for issued certificates).
   - Compare canonical payload SHA-256 hash.

7. **REGISTRY MATCHING**:
   - Exact query on `certificate_number` + `institution_id`.
   - Token-set fuzzy matching on `holder_name` (handling initials, name order, transliterated spellings).
   - Check revocation database for matching issuer record.

8. **TYPE-SPECIFIC VALIDATORS**:
   - **Marksheet**: Verify subject mark sum $\equiv$ total mark; verify percentage $\equiv \frac{\text{total}}{\text{max}} \times 100$; verify CGPA formula matching issuer config; verify pass/fail consistency.
   - **Degree**: Verify issue date $\ge$ admission date + minimum duration; verify degree program offered by institution in issue year.
   - **Training**: Verify course provider status in trusted provider list; check ID pattern match; verify course hours vs date duration.

9. **FORENSIC HEURISTICS**:
   - **Metadata Analysis**: Check PDF producer, creation vs modification date anomalies, editing software footprints (e.g., Photoshop, Canva).
   - **Error Level Analysis (ELA)**: Re-compress image at 95% JPEG quality and detect local compression variance (tampered regions).
   - **Copy-Move & Font Detection**: Identify duplicated graphical regions and font rendering inconsistencies near critical fields.
   - **Perceptual Hash Duplicate**: Flag reused certificates across different holder names.

10. **RISK SCORING & HARD RULES**:
    - Evaluate Hard Rules (B5 decision rules: Revoked, Hard Arithmetic Failure, Contradicting Registry Record).
    - Compute weighted risk score across applicable checks:
      $$\text{Risk Score} = \frac{\sum w_i \cdot \text{Risk}_i}{\sum w_i \quad \text{for applicable checks}}$$
    - Compute Evidence Coverage %:
      $$\text{Coverage \%} = \frac{\sum w_i \quad \text{for applicable checks}}{\sum W_{\text{total}}}$$
    - If Coverage $< 40\%$, cap minimum risk level to `MEDIUM`.

11. **EXPLANATION & ROUTING**:
    - Pass structured evidence details to LLM explanation adapter (or template fallback).
    - Generate human-readable bullet points detailing reasons.
    - Assign verdict (`VERIFIED`, `REVOKED`, `NOT_VERIFIED`, `NEEDS_REVIEW`, `UNVERIFIABLE_ISSUER`).
    - If verdict is not `VERIFIED` (or risk is `MEDIUM`/`HIGH`), route to Reviewer Queue.

---

## 3. Evidence Tiers & Decision Rules

| Tier | Name | Description | Influence |
|---|---|---|---|
| **Tier A** | Authoritative Proof | Issuer database match, valid Ed25519 signature, issuer-resolved QR token, revocation log | Determines `VERIFIED`, `REVOKED`, or `NOT_VERIFIED` |
| **Tier B** | Deterministic Rules | Marksheet arithmetic, date range validity, ID regex pattern, duplicate SHA-256 | Hard rules override risk score; forces `NEEDS_REVIEW` |
| **Tier C** | Forensic Heuristics | ELA tamper analysis, metadata anomaly, copy-move detection, font variance | Adjusts risk score (0-100) & risk level |
| **Tier D** | LLM Extraction | Type classification, OCR extraction, summary phrasing | Informational only; **never** sets pass/fail |

### Sequential Decision Rules (First Match Wins):
1. **R1**: Tier A Revocation record exists $\rightarrow$ **`REVOKED`**.
2. **R2**: Tier A Registry / Signature match & fields agree:
   - Forensic Risk $< 66 \rightarrow$ **`VERIFIED`**.
   - Forensic Risk $\ge 66 \rightarrow$ **`NEEDS_REVIEW`** (Genuine record, suspicious image).
3. **R3**: Registry record found, but key field contradicts OR signature invalid $\rightarrow$ **`NOT_VERIFIED`** (Sent to Reviewer Queue).
4. **R4**: Hard Tier B failure (arithmetic mismatch, impossible date) with no Tier A match $\rightarrow$ **`NEEDS_REVIEW`** (Risk forced $\ge 66$).
5. **R5**: Issuer not in registry $\rightarrow$ **`UNVERIFIABLE_ISSUER`** (Risk calculated from Tier B & Tier C; `MEDIUM`/`HIGH` sent to Reviewer Queue).
6. **R6**: Low extraction confidence $\rightarrow$ **`NEEDS_REVIEW`** (Prompt user to correct fields).
