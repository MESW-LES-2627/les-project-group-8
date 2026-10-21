<script lang="ts">
	import type { Pool, PoolStatus } from '#lib/types.ts';

	let {
		pool,
		/** Format in the browser's zone once hydrated; UTC during SSR avoids a mismatch. */
		localTime = false,
		highlight = false
	}: { pool: Pool; localTime?: boolean; highlight?: boolean } = $props();

	const statusStyles: Record<PoolStatus, string> = {
		OPEN: 'bg-emerald-50 text-emerald-700 border-emerald-200',
		LOCKED: 'bg-amber-50 text-amber-700 border-amber-200',
		RESOLVED: 'bg-sky-50 text-sky-700 border-sky-200'
	};

	let deadline = $derived(
		new Intl.DateTimeFormat('en-GB', {
			dateStyle: 'medium',
			timeStyle: 'short',
			timeZone: localTime ? undefined : 'UTC'
		}).format(new Date(pool.deadline)) + (localTime ? '' : ' UTC')
	);
</script>

<article
	id="pool-{pool.id}"
	class="rounded-xl border bg-white p-6 shadow-xs transition hover:shadow-sm
		{highlight ? 'border-orange-500 ring-2 ring-orange-500/20' : 'border-slate-200'}"
>
	<header class="flex items-start justify-between gap-4">
		<h3 class="text-lg font-semibold text-slate-900">{pool.name}</h3>
		<span
			class="shrink-0 rounded-full border px-2.5 py-0.5 text-xs font-semibold tracking-wide {statusStyles[
				pool.status
			]}"
		>
			{pool.status}
		</span>
	</header>

	<p class="mt-2 text-slate-600">{pool.statement}</p>

	<ul class="mt-5 grid grid-cols-2 gap-3">
		{#each pool.options as option (option.id)}
			<li
				class="rounded-lg border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm font-medium text-slate-800
					{pool.winning_outcome_id === option.id ? 'border-emerald-500 bg-emerald-50 text-emerald-900 font-semibold' : ''}"
			>
				{option.label}
			</li>
		{/each}
	</ul>

	<footer class="mt-5 flex flex-wrap items-center justify-between gap-2 text-xs text-slate-500">
		<span>by <span class="font-medium text-slate-700">{pool.creator.name}</span></span>
		<time datetime={pool.deadline}>Locks {deadline}</time>
	</footer>
</article>

