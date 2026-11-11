<script lang="ts">
	import { enhance } from '$app/forms';
	import { invalidateAll } from '$app/navigation';
	import { page } from '$app/state';
	import { inputClass, labelClass, submitClass } from '#lib/form.ts';
	import type { Bet } from '#lib/types.ts';

	let { bet }: { bet: Bet } = $props();
	let submitting = $state(false);
	const form = $derived(page.form?.action === 'resolve' && page.form.betId === bet.id ? page.form : null);
	const winner = $derived(bet.options.find((option) => option.id === bet.winning_outcome_id));
</script>

{#if winner}
	<p class="mt-5 border-t border-black pt-4 text-sm" role="status">
		Resolved — winning outcome: <strong>{winner.label}</strong>
	</p>
{:else if page.data.user}
	<form
		method="POST"
		action="?/resolve"
		class="mt-5 space-y-3 border-t border-black pt-4"
		use:enhance={() => {
			submitting = true;
			return async ({ update, result }) => {
				try {
					await update();
					if (result.type === 'failure') await invalidateAll();
				} finally {
					submitting = false;
				}
			};
		}}
	>
		<input type="hidden" name="bet_id" value={bet.id} />
		{#if form?.error}
			<p role="alert" class="text-sm">{form.error}</p>
		{/if}
		<label for={`winner-${bet.id}`} class={labelClass}>Winning outcome</label>
		<select id={`winner-${bet.id}`} name="winning_outcome_id" required class={inputClass}>
			<option value="">Select the winner</option>
			{#each bet.options as option (option.id)}
				<option value={option.id} selected={form?.winningOutcomeId === option.id}>{option.label}</option>
			{/each}
		</select>
		<button type="submit" disabled={submitting} class={submitClass}>
			{submitting ? 'Resolving…' : 'Resolve bet'}
		</button>
	</form>
{/if}
