import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://zmkwnvnwxaukewtxakxp.supabase.co';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inpta3dudm53eGF1a2V3dHhha3hwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTE0NTY5MzEsImV4cCI6MjEwNzAzMjkzMX0.GWkdw6E-pzu5fbz04xnkV1s-Arz_ca2Y7tuv8BwTdKE';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
