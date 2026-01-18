import { createClient as createSupabaseClient } from "@supabase/supabase-js";

let client: ReturnType<typeof createSupabaseClient> | null = null;

/**
 * Creates a Supabase browser client singleton.
 * Reads configuration from NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY.
 *
 * Returns null if environment variables are not configured (graceful degradation).
 */
export function createClient() {
  if (client) {
    return client;
  }

  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

  if (!supabaseUrl || !supabaseAnonKey) {
    console.warn(
      "[Supabase] Missing NEXT_PUBLIC_SUPABASE_URL or NEXT_PUBLIC_SUPABASE_ANON_KEY"
    );
    return null;
  }

  client = createSupabaseClient(supabaseUrl, supabaseAnonKey);
  return client;
}

/**
 * Get the Supabase client, throwing if not configured.
 * Use this when Supabase is required (not optional).
 */
export function getClient() {
  const c = createClient();
  if (!c) {
    throw new Error("Supabase client not configured");
  }
  return c;
}
