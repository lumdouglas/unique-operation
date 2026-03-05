/**
 * Supabase client with service_role key (bot backend only).
 * NEVER use this in the dashboard - use anon key + RLS there.
 */

import { createClient } from '@supabase/supabase-js';
import { config } from '../config.js';

export const supabase = createClient(
  config.supabase.url,
  config.supabase.serviceRoleKey,
  { auth: { persistSession: false } }
);
