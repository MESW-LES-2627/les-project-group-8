// See https://svelte.dev/docs/kit/types#app.d.ts
// for information about these interfaces
import type { Session, SupabaseClient } from '@supabase/supabase-js';

declare global {
	namespace App {
		// interface Error {}
		interface Locals {
			/** Per-request Supabase client; reads and writes the session cookies. */
			supabase: SupabaseClient;
			/** The logged-in Account's session (renewed if expired), or null when logged out. */
			session: Session | null;
		}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}
}

export {};
