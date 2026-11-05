<script lang="ts">
	import BetCard from '#lib/components/BetCard.svelte';
	import BetForm from '#lib/components/BetForm.svelte';
	import StatusBadge from '#lib/components/StatusBadge.svelte';
	import { formatDeadline } from '#lib/format.ts';
	import type { PageProps } from './$types';

	let { data, form }: PageProps = $props();
</script>

<svelte:head>
	<title>{data.pool ? `${data.pool.name} · LES` : 'Pool · LES'}</title>
</svelte:head>

<a href="/" class="font-mono text-[10px] uppercase tracking-widest underline">← Back to pools</a>

{#if data.loadError}
	<p role="alert" class="mt-6 border border-black px-3 py-2 text-sm">Could not load the pool: {data.loadError}</p>
{:else if data.pool}
	{@const pool = data.pool}
	<div class="mt-4 flex items-start justify-between gap-4">
		<h1 class="text-3xl font-bold tracking-tight">{pool.name}</h1>
		<StatusBadge status={pool.status} />
	</div>
	{#if pool.description}
		<p class="mt-2 text-sm text-neutral-700">{pool.description}</p>
	{/if}
	<p class="mt-3 font-mono text-[10px] uppercase tracking-widest text-neutral-500">Deadline {formatDeadline(pool.deadline)}</p>
	<p class="mt-1 text-[11px] uppercase tracking-wide text-neutral-500">By {pool.creator.name}</p>
	{#if data.created}
		<p role="status" class="mt-6 border border-black bg-neutral-100 px-3 py-2 text-sm font-bold">
			Pool created. Add your first bet below.
		</p>
	{/if}
	{#if data.pickLoadError}
		<p role="alert" class="mt-6 border border-black px-3 py-2 text-sm">
			Could not load your saved picks: {data.pickLoadError}
		</p>
	{/if}
	{#if form?.action === 'pick' && !pool.bets.some((bet) => bet.id === form?.betId)}
		<p role="alert" class="mt-6 border border-black px-3 py-2 text-sm">{form.error}</p>
	{/if}

	<section class="mt-8 space-y-4" aria-labelledby="bets-heading">
		<h2 id="bets-heading" class="text-xl font-bold">Bets</h2>
		{#if pool.bets.length === 0}
			<p class="border border-dashed border-neutral-400 p-6 text-sm text-neutral-600">No bets yet.</p>
		{/if}
		{#each pool.bets as bet (bet.id)}
			<BetCard
				{bet}
				poolStatus={pool.status}
				pick={data.picks.find((pick) => pick.bet_id === bet.id)}
				loggedIn={data.loggedIn}
				user={data.user}
				loginHref={`/login?redirectTo=${encodeURIComponent(`/pools/${pool.id}`)}`}
				form={form?.action === 'pick' && form.betId === bet.id ? form : null}
			/>
		{/each}
	</section>

	{#if data.user?.id === pool.creator.id}
		<section class="mt-10 border-t border-black pt-6" aria-labelledby="add-bet-heading">
			<h2 id="add-bet-heading" class="mb-5 text-xl font-bold">Add a bet</h2>
			{#if pool.status === 'OPEN'}
				{#if form?.action === 'addBet' && form.added}
					<p role="status" class="mb-5 text-sm font-bold">Bet added.</p>
				{/if}
				<BetForm form={form?.action === 'addBet' ? form : null} />
			{:else}
				<p class="text-sm text-neutral-600">The pool deadline has passed. Bets cannot be added.</p>
			{/if}
		</section>
	{/if}
{/if}
