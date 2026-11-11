<script lang="ts">
	import { enhance } from '$app/forms';
	import { invalidateAll } from '$app/navigation';
	import BetPicks from '#lib/components/BetPicks.svelte';
	import { inputClass, labelClass, submitClass } from '#lib/form.ts';
	import type { Bet, BetStatus, Pick, PoolStatus, UserSummary } from '#lib/types.ts';

	let {
		bet,
		poolStatus,
		pick,
		loggedIn,
		user,
		loginHref,
		form = null
	}: {
		bet: Bet;
		poolStatus: PoolStatus;
		pick?: Pick;
		loggedIn: boolean;
		user: UserSummary | null;
		loginHref: string;
		form?: {
			error?: string;
			saved?: boolean;
			outcomeId?: string;
		} | null;
	} = $props();
	let submitting = $state(false);
	const status = $derived<BetStatus>(bet.winning_outcome_id ? 'RESOLVED' : poolStatus);
	const selected = $derived(form?.outcomeId ?? pick?.outcome_id ?? '');
	const picked = $derived(bet.options.find((option) => option.id === pick?.outcome_id));
</script>

<article class="border border-black p-5">
	<h3 class="text-lg font-bold">{bet.statement}</h3>
	{#if form?.error}
		<p role="alert" class="mt-4 border border-black bg-black px-3 py-2 text-sm text-white">
			{form.error}
		</p>
	{/if}
	{#if form?.saved}
		<p role="status" class="mt-4 text-sm font-bold">Pick saved.</p>
	{/if}

	{#if status === 'OPEN' && loggedIn && user}
		<form
			method="POST"
			action="?/pick"
			class="mt-4 space-y-4"
			use:enhance={() => {
				submitting = true;
				return async ({ update, result }) => {
					await update();
					// The shared deadline may have passed since this page was loaded.
					if (result.type === 'failure') {
						await invalidateAll();
					}
					submitting = false;
				};
			}}
		>
			<input type="hidden" name="bet_id" value={bet.id} />
			{#if bet.presentation === 'dropdown'}
				<label for={`outcome-${bet.id}`} class={labelClass}>Your pick</label>
				<select id={`outcome-${bet.id}`} name="outcome_id" required class={inputClass}>
					<option value="">Select an option</option>
					{#each bet.options as option (option.id)}
						<option value={option.id} selected={selected === option.id}>{option.label}</option>
					{/each}
				</select>
			{:else}
				<fieldset>
					<legend class={labelClass}>Your pick</legend>
					<div class="mt-2 grid gap-2">
						{#each bet.options as option (option.id)}
							<label class="flex items-center gap-3 border border-black px-3 py-2 text-sm has-[:checked]:bg-black has-[:checked]:text-white">
								<input type="radio" name="outcome_id" value={option.id} required checked={selected === option.id} />
								<span>{option.label}</span>
								{#if pick?.outcome_id === option.id}
									<span class="ml-auto font-mono text-[10px] uppercase tracking-widest">Your pick</span>
								{/if}
							</label>
						{/each}
					</div>
				</fieldset>
			{/if}
			<div class="flex flex-wrap items-center gap-4 border-t border-black pt-4">
				<button type="submit" disabled={submitting} class={submitClass}>{submitting ? 'Saving…' : pick ? 'Change pick' : 'Save pick'}</button>
				{#if picked}
					<span class="text-xs text-neutral-600">Saved: {picked.label}</span>
				{/if}
			</div>
		</form>
	{:else}
		<ul class="mt-4 grid gap-2 sm:grid-cols-2">
			{#each bet.options as option (option.id)}
				<li class="border border-black px-3 py-2 text-sm">
					{option.label}
					{#if bet.winning_outcome_id === option.id}
						<strong class="ml-2 text-xs">Winner</strong>
					{/if}
				</li>
			{/each}
		</ul>
		{#if status !== 'OPEN'}
			<p class="mt-4 text-sm font-bold">Picks are closed.</p>
		{/if}
		{#if !loggedIn}
			<p class="mt-3 text-sm">{status === 'OPEN' ? 'Log in to save your pick.' : 'Log in to see your saved pick.'}</p>
			<a href={loginHref} class="mt-3 inline-block text-sm underline">Log in</a>
		{:else if !user}
			<p class="mt-3 text-sm">This account has no User profile yet.</p>
			<a href="/no-user" class="mt-3 inline-block text-sm underline">What now?</a>
		{:else if picked}
			<p class="mt-3 text-sm">Your pick: <strong>{picked.label}</strong></p>
		{:else}
			<p class="mt-3 text-sm text-neutral-600">You did not pick an option.</p>
		{/if}
	{/if}
	<BetPicks {bet} />
</article>
