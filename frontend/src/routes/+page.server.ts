import { listPools } from '../lib/server/api';
import type { Pool } from '../lib/types';

export async function load({ url }) {
	let pools: Pool[] = [];
	let loadError: string | null = null;

	try {
		pools = await listPools();
	} catch (error) {
		loadError = error instanceof Error ? error.message : 'Could not load pools.';
	}

	return {
		pools,
		loadError,
		created: url.searchParams.has('created')
	};
}
