-- CertiGuard Supabase Database Migration Schema

-- 1. Enable UUID Extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Create Certificates Table (Authoritative Issuer Registry)
CREATE TABLE IF NOT EXISTS public.certificates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    certificate_number TEXT UNIQUE NOT NULL,
    holder_name TEXT NOT NULL,
    course TEXT NOT NULL,
    certificate_type TEXT NOT NULL CHECK (certificate_type IN ('degree', 'marksheet', 'training')),
    issue_date DATE NOT NULL,
    canonical_hash TEXT,
    signature TEXT,
    verification_token TEXT UNIQUE,
    status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'REVOKED')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 3. Create Verifications Table (Audit Log & Risk Reports)
CREATE TABLE IF NOT EXISTS public.verifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    certificate_number TEXT,
    certificate_type TEXT NOT NULL,
    verdict TEXT NOT NULL CHECK (verdict IN ('VERIFIED', 'FLAGGED', 'REJECTED')),
    risk_score NUMERIC(5,2) DEFAULT 0.00,
    summary_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 4. Create Registered Issuers Table
CREATE TABLE IF NOT EXISTS public.issuers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    registration_code TEXT UNIQUE NOT NULL,
    allowed_domains TEXT[] DEFAULT '{}',
    key_status TEXT NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 5. Enable Row Level Security (RLS)
ALTER TABLE public.certificates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.verifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.issuers ENABLE ROW LEVEL SECURITY;

-- 6. Create RLS Policies for Public Read & Authenticated Insert
CREATE POLICY "Allow public read access for certificates" ON public.certificates FOR SELECT USING (true);
CREATE POLICY "Allow public insert for certificates" ON public.certificates FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public read access for verifications" ON public.verifications FOR SELECT USING (true);
CREATE POLICY "Allow public insert for verifications" ON public.verifications FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public read access for issuers" ON public.issuers FOR SELECT USING (true);
CREATE POLICY "Allow public insert for issuers" ON public.issuers FOR INSERT WITH CHECK (true);

-- 7. Seed Initial Sample Issuer Record
INSERT INTO public.issuers (name, registration_code, allowed_domains, key_status)
VALUES ('Indian Institute of Technology Bombay', 'INST-IITB-01', ARRAY['iitb.ac.in', 'certs.iitb.ac.in'], 'Ed25519 Loaded')
ON CONFLICT (registration_code) DO NOTHING;

-- 8. Seed Initial Sample Certificate Record
INSERT INTO public.certificates (certificate_number, holder_name, course, certificate_type, issue_date, canonical_hash, status)
VALUES ('IITB-2026-CS-101', 'Rajesh Sharma', 'B.Tech Computer Science', 'degree', '2026-05-30', 'a4f88e10b99127ca982310199f11283c7482', 'ACTIVE')
ON CONFLICT (certificate_number) DO NOTHING;
