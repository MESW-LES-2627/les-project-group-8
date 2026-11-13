<script lang="ts">
	import { page } from '$app/state';
	import type { Bet, Pick } from '#lib/types.ts';

	let { bet }: { bet: Bet } = $props();
	const picks = $derived((page.data.picks ?? []).filter((pick: Pick) => pick.bet_id === bet.id));
</script>

{#if page.data.pool?.status === 'LOCKED' && page.data.user && !page.data.pickLoadError}
	<section class="mt-5 border-t border-black pt-4" aria-labelledby={`picks-${bet.id}`}>
		<h4 id={`picks-${bet.id}`} class="text-sm font-bold">Everyone's picks</h4>
		{#if picks.length === 0}
			<p class="mt-2 text-sm text-neutral-600">No picks for this bet.</p>
		{:else}
			<ul class="mt-3 space-y-2">
				{#each picks as pick (pick.id)}
					<li class="flex flex-wrap items-baseline gap-x-3 gap-y-1 text-sm">
						<span class="font-bold">{pick.user.name}</span>
						<span>{bet.options.find((option) => option.id === pick.outcome_id)?.label}</span>
						{#if pick.outcome_id === bet.winning_outcome_id}
							<strong class="text-xs">Winner</strong>
						{/if}
					</li>
				{/each}
			</ul>
		{/if}
	</section>
{/if}
