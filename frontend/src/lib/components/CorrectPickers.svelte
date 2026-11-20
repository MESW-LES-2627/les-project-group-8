<script lang="ts">
	import { page } from '$app/state';
	import type { Bet, Pick } from '#lib/types.ts';

	let { bet }: { bet: Bet } = $props();
	const winner = $derived(bet.options.find((option) => option.id === bet.winning_outcome_id));
	const pickers = $derived(
		(page.data.picks ?? []).filter(
			(pick: Pick) => pick.bet_id === bet.id && pick.outcome_id === bet.winning_outcome_id
		)
	);
</script>

{#if winner && page.data.pool?.status === 'LOCKED' && page.data.user && !page.data.pickLoadError}
	<section class="mt-5 border-t border-black pt-4" aria-labelledby={`correct-pickers-${bet.id}`}>
		<h4 id={`correct-pickers-${bet.id}`} class="text-sm font-bold">
			Correct pickers — {winner.label}
		</h4>
		{#if pickers.length === 0}
			<p class="mt-2 text-sm text-neutral-600">Nobody picked the winner.</p>
		{:else}
			<ul class="mt-3 space-y-2">
				{#each pickers as pick (pick.id)}
					<li class="text-sm font-bold">{pick.user.name}</li>
				{/each}
			</ul>
		{/if}
	</section>
{/if}
