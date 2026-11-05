<script lang="ts">
	import { formatDeadline } from '../format';
	import type { Pool } from '../types';
	import StatusBadge from './StatusBadge.svelte';

	let { pool }: { pool: Pool } = $props();
</script>

<article class="border border-black p-5">
	<div class="flex items-start justify-between gap-4">
		<h2 class="text-xl font-bold tracking-tight">
			<a href={`/pools/${pool.id}`} class="hover:underline">{pool.name}</a>
		</h2>
		<StatusBadge status={pool.status} />
	</div>

	{#if pool.description}
		<p class="mt-2 text-sm text-neutral-700">{pool.description}</p>
	{/if}

	<p class="mt-3 font-mono text-[10px] uppercase tracking-widest text-neutral-500">
		Deadline {formatDeadline(pool.deadline)}
	</p>

	<p class="mt-4 text-sm">{pool.bets.length} {pool.bets.length === 1 ? 'bet' : 'bets'}</p>

	<p class="mt-3 text-[11px] uppercase tracking-wide text-neutral-500">
		By {pool.creator.name}
	</p>

	<a
		href={`/pools/${pool.id}`}
		class="mt-4 inline-block border border-black px-3 py-1.5 text-[10px] font-bold uppercase tracking-widest hover:bg-black hover:text-white"
	>
		Open pool
	</a>
</article>
