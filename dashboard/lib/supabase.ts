/**
 * Supabase client for dashboard (anon key).
 * Uses RLS for security - never use service_role in the dashboard.
 */

import { createClient } from '@supabase/supabase-js';

const url = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://placeholder.supabase.co';
const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'placeholder';

export const supabase = createClient(url, anonKey);
