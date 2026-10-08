# CertiGuard - AI-Powered Certificate Verification & Fraud Risk Detection

CertiGuard is an enterprise-grade platform that combines deterministic issuer verification, cryptographic signatures, per-type schema validation, and image forensics to detect altered or fraudulent academic and professional certificates.

---

## 🏛️ Architecture Overview

CertiGuard is organized as a monorepo:
* **`apps/web`**: Next.js 14+ (App Router) + TypeScript + Tailwind CSS + shadcn/ui.
* **`apps/api`**: FastAPI (Python 3.11+) backend, SQLAlchemy 2.0, Pydantic v2, Alembic migrations.
* **`apps/api/app/workers`**: Celery asynchronous pipeline execution backed by Redis.
* **`docs/`**: Architecture, Threat Model, ER Schemas, OpenAPI Specs.
* **`design/`**: UI/UX Design system specifications and handoff contracts.

---

## 🚀 Quick Start (Docker Compose)

### Prerequisites
* Docker & Docker Compose
* Node.js 18+ (for local frontend development)
* Python 3.11+ (for local API development)

### Running the Infrastructure Stack
1. Copy the example environment configuration:
   ```bash
   cp .env.example .env
   ```
2. Launch PostgreSQL, Redis, MinIO, FastAPI Backend, and Celery Workers:
   ```bash
   docker-compose up -d --build
   ```
3. Check system health:
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

---

## 🔒 Security Principles
1. **Issuer Confirmation Rules**: Deterministic issuer matches and cryptographic signatures override model heuristics.
2. **LLM Extraction Guard**: The LLM extracts and explains; it **never** decides pass/fail or final verdicts.
3. **Zero Untrusted Code Execution**: Uploaded files and QR codes are treated as untrusted data inputs.
