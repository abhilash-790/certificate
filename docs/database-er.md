# CertiGuard Database Model & Entity-Relationship Specification

## 1. Overview
The CertiGuard database is designed for PostgreSQL 15+ using SQLAlchemy 2.0 and Alembic migrations. It combines strict relational integrity (foreign keys, check constraints, unique indexes) with JSONB documents for document-type schemas, variable extracted fields, and check details.

---

## 2. Entity-Relationship Schema & Core Tables

### 2.1 `users`
Stores user identities, credentials (argon2 hashed), and roles.
* `id`: UUID (Primary Key, default `gen_random_uuid()`)
* `name`: VARCHAR(255) NOT NULL
* `email`: VARCHAR(255) UNIQUE NOT NULL
* `password_hash`: VARCHAR(255) NOT NULL (Argon2id format)
* `role`: VARCHAR(50) NOT NULL CHECK (`role` IN ('VERIFIER', 'INSTITUTION', 'REVIEWER', 'ADMIN'))
* `status`: VARCHAR(50) NOT NULL DEFAULT 'ACTIVE'
* `institution_id`: UUID NULL (Foreign Key $\rightarrow$ `institutions.id`)
* `created_at`: TIMESTAMP WITH TIME ZONE DEFAULT `NOW()`
* `updated_at`: TIMESTAMP WITH TIME ZONE DEFAULT `NOW()`

### 2.2 `institutions`
Stores registered certificate issuing entities.
* `id`: UUID (Primary Key)
* `name`: VARCHAR(255) NOT NULL
* `registration_number`: VARCHAR(100) UNIQUE NOT NULL
* `email`: VARCHAR(255) NOT NULL
* `address`: TEXT NULL
* `domain_allowlist`: TEXT[] NOT NULL DEFAULT '{}'
* `approval_status`: VARCHAR(50) NOT NULL DEFAULT 'PENDING' CHECK (`approval_status` IN ('PENDING', 'APPROVED', 'REJECTED'))
* `public_key`: TEXT NULL (Ed25519 public key in PEM/HEX format)
* `created_at`: TIMESTAMP WITH TIME ZONE DEFAULT `NOW()`

### 2.3 `certificate_types`
Configurable schema definitions and check weights per certificate type (`degree`, `marksheet`, `training`).
* `id`: UUID (Primary Key)
* `code`: VARCHAR(50) UNIQUE NOT NULL (e.g., 'degree', 'marksheet', 'training')
* `name`: VARCHAR(100) NOT NULL
* `schema_json`: JSONB NOT NULL (Pydantic / JSON Schema for field definitions)
* `weights_json`: JSONB NOT NULL (Weights configuration for risk engine)
* `validators_config`: JSONB NOT NULL (Specific validation thresholds)
* `version`: INTEGER NOT NULL DEFAULT 1
* `created_at`: TIMESTAMP WITH TIME ZONE DEFAULT `NOW()`

### 2.4 `issuer_certificates` (Registry Table)
Authoritative registry of certificates issued by registered institutions.
* `id`: UUID (Primary Key)
* `institution_id`: UUID NOT NULL (FK $\rightarrow$ `institutions.id`)
* `certificate_type_id`: UUID NOT NULL (FK $\rightarrow$ `certificate_types.id`)
* `certificate_number`: VARCHAR(100) NOT NULL
* `holder_name`: VARCHAR(255) NOT NULL
* `holder_identifier_hash`: VARCHAR(64) NULL (Hashed identifier, e.g. SHA-256 of student ID)
* `course`: VARCHAR(255) NOT NULL
* `data_json`: JSONB NOT NULL (Type-specific fields: marks, GPA, degree branch)
* `issue_date`: DATE NOT NULL
* `expiry_date`: DATE NULL
* `status`: VARCHAR(50) NOT NULL DEFAULT 'ACTIVE' CHECK (`status` IN ('ACTIVE', 'REVOKED'))
* `canonical_hash`: VARCHAR(64) NOT NULL (SHA-256 of canonical payload)
* `signature`: TEXT NOT NULL (Ed25519 signature over `canonical_hash`)
* `verification_token`: VARCHAR(128) UNIQUE NOT NULL (Random 128-bit hex string)
* `created_at`: TIMESTAMP WITH TIME ZONE DEFAULT `NOW()`
* **Constraints**: `UNIQUE(institution_id, certificate_number)`

### 2.5 `revocations`
Log of revoked certificates with issuer notes.
* `id`: UUID (Primary Key)
* `issuer_certificate_id`: UUID UNIQUE NOT NULL (FK $\rightarrow$ `issuer_certificates.id`)
* `reason`: TEXT NOT NULL
* `revoked_by`: UUID NOT NULL (FK $\rightarrow$ `users.id`)
* `revoked_at`: TIMESTAMP WITH TIME ZONE DEFAULT `NOW()`

### 2.6 `certificate_files`
Metadata for uploaded files held in object storage.
* `id`: UUID (Primary Key)
* `owner_user_id`: UUID NOT NULL (FK $\rightarrow$ `users.id`)
* `storage_key`: VARCHAR(512) UNIQUE NOT NULL (S3 / MinIO object key)
* `mime_type`: VARCHAR(100) NOT NULL
* `size`: BIGINT NOT NULL
* `sha256`: VARCHAR(64) NOT NULL
* `phash`: VARCHAR(64) NULL
* `page_count`: INTEGER NOT NULL DEFAULT 1
* `retention_until`: TIMESTAMP WITH TIME ZONE NOT NULL
* `created_at`: TIMESTAMP WITH TIME ZONE DEFAULT `NOW()`
* **Indexes**: `INDEX idx_files_sha256 (sha256)`, `INDEX idx_files_phash (phash)`

### 2.7 `verification_requests`
Primary verification session record.
* `id`: UUID (Primary Key)
* `file_id`: UUID NOT NULL (FK $\rightarrow$ `certificate_files.id`)
* `submitted_by`: UUID NOT NULL (FK $\rightarrow$ `users.id`)
* `detected_type`: VARCHAR(50) NULL
* `type_confidence`: FLOAT NULL
* `confirmed_type`: VARCHAR(50) NULL
* `status`: VARCHAR(50) NOT NULL DEFAULT 'PENDING' CHECK (`status` IN ('PENDING', 'PROCESSING', 'NEEDS_TYPE_CONFIRMATION', 'COMPLETED', 'FAILED'))
* `verdict`: VARCHAR(50) NULL CHECK (`verdict` IN ('VERIFIED', 'REVOKED', 'NOT_VERIFIED', 'NEEDS_REVIEW', 'UNVERIFIABLE_ISSUER'))
* `risk_score`: FLOAT NULL (0.0 to 100.0)
* `risk_level`: VARCHAR(20) NULL CHECK (`risk_level` IN ('LOW', 'MEDIUM', 'HIGH'))
* `coverage_pct`: FLOAT NULL (0.0 to 100.0)
* `rule_version`: VARCHAR(50) DEFAULT 'v1.0'
* `model_version`: VARCHAR(50) DEFAULT 'v1.0'
* `created_at`: TIMESTAMP WITH TIME ZONE DEFAULT `NOW()`
* `completed_at`: TIMESTAMP WITH TIME ZONE NULL
* **Indexes**: `INDEX idx_verifications_status (status)`, `INDEX idx_verifications_verdict (verdict)`

### 2.8 `extracted_fields`
Field-level OCR and LLM extraction outputs.
* `id`: UUID (Primary Key)
* `verification_id`: UUID NOT NULL (FK $\rightarrow$ `verification_requests.id` ON DELETE CASCADE)
* `field_name`: VARCHAR(100) NOT NULL
* `ocr_value`: TEXT NULL
* `value`: TEXT NOT NULL
* `confidence`: FLOAT NOT NULL DEFAULT 1.0
* `bbox_json`: JSONB NULL (Bounding box `{x1, y1, x2, y2}`)
* `source`: VARCHAR(20) NOT NULL DEFAULT 'LLM' CHECK (`source` IN ('OCR', 'LLM', 'USER'))

### 2.9 `verification_checks`
Detailed check execution results across all evidence tiers.
* `id`: UUID (Primary Key)
* `verification_id`: UUID NOT NULL (FK $\rightarrow$ `verification_requests.id` ON DELETE CASCADE)
* `check_type`: VARCHAR(100) NOT NULL (e.g., 'C01_FILE_INTEGRITY', 'C05_REGISTRY_MATCH', 'C06_MARKSHEET_ARITHMETIC', 'C09_TAMPER_ELA')
* `tier`: VARCHAR(10) NOT NULL CHECK (`tier` IN ('TIER_A', 'TIER_B', 'TIER_C', 'TIER_D'))
* `result`: VARCHAR(20) NOT NULL CHECK (`result` IN ('PASS', 'WARN', 'FAIL', 'NOT_APPLICABLE', 'ERROR'))
* `score`: FLOAT NOT NULL DEFAULT 0.0 (0-100 risk score)
* `details_json`: JSONB NOT NULL DEFAULT '{}'
* `duration_ms`: INTEGER NOT NULL DEFAULT 0

### 2.10 `risk_results`
Component breakdown and generated reasons.
* `id`: UUID (Primary Key)
* `verification_id`: UUID UNIQUE NOT NULL (FK $\rightarrow$ `verification_requests.id` ON DELETE CASCADE)
* `component_scores_json`: JSONB NOT NULL
* `hard_rules_triggered`: TEXT[] NOT NULL DEFAULT '{}'
* `reasons_json`: JSONB NOT NULL DEFAULT '[]'
* `explanation_text`: TEXT NOT NULL

### 2.11 `reviews`
Human reviewer decision record.
* `id`: UUID (Primary Key)
* `verification_id`: UUID NOT NULL (FK $\rightarrow$ `verification_requests.id`)
* `reviewer_id`: UUID NOT NULL (FK $\rightarrow$ `users.id`)
* `decision`: VARCHAR(50) NOT NULL CHECK (`decision` IN ('APPROVE', 'REJECT', 'NEEDS_INFO'))
* `notes`: TEXT NOT NULL
* `created_at`: TIMESTAMP WITH TIME ZONE DEFAULT `NOW()`

### 2.12 `audit_log` (Append-Only)
Immutable audit trail for security and compliance.
* `id`: UUID (Primary Key)
* `actor_id`: UUID NULL (FK $\rightarrow$ `users.id`)
* `action`: VARCHAR(100) NOT NULL
* `resource_type`: VARCHAR(100) NOT NULL
* `resource_id`: VARCHAR(255) NOT NULL
* `ip_hash`: VARCHAR(64) NULL
* `metadata_json`: JSONB NOT NULL DEFAULT '{}'
* `created_at`: TIMESTAMP WITH TIME ZONE DEFAULT `NOW()`
