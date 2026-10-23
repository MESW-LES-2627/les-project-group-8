<script lang="ts">
	import PoolCard from '../lib/components/PoolCard.svelte';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
</script>

<svelte:head>
	<title>Pools · LES</title>
</svelte:head>

<div class="flex items-end justify-between gap-4">
	<div>
		<h1 class="text-3xl font-bold tracking-tight">Pools</h1>
		<p class="mt-1 text-sm text-neutral-600">
			Create a prediction pool and see who gets it right.
		</p>
	</div>
	<a
		href="/pools/new"
		class="border border-black bg-black px-4 py-2 text-sm font-bold text-white hover:bg-white hover:text-black"
	>
		New pool
	</a>
</div>

{#if data.created}
	<p class="mt-6 border border-black bg-neutral-100 px-3 py-2 text-sm font-bold">Pool created.</p>
{/if}

{#if data.loadError}
	<p role="alert" class="mt-6 border border-black px-3 py-2 text-sm">
		Could not load pools: {data.loadError}
	</p>
{/if}

{#if data.pools.length === 0}
	<p class="mt-10 border border-dashed border-neutral-400 p-8 text-center text-sm text-neutral-600">
		No pools yet. Create the first one.
	</p>
{:else}
	<div class="mt-8 grid gap-4">
		{#each data.pools as pool (pool.id)}
			<PoolCard {pool} />
		{/each}
	</div>
{/if}
