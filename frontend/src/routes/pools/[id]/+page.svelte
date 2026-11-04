<script lang="ts">
	import { enhance } from '$app/forms';
	import StatusBadge from '../../../lib/components/StatusBadge.svelte';
	import { formatDeadline } from '../../../lib/format';
	import type { PageProps } from './$types';

	let { data, form }: PageProps = $props();

	const labelClass = 'font-mono text-[10px] font-bold uppercase tracking-widest';
	const inputClass =
		'mt-1 w-full border border-black bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-black';

	let submitting = $state(false);
</script>

<svelte:head>
	<title>{data.pool ? `${data.pool.name} · LES` : 'Pool · LES'}</title>
</svelte:head>

<a href="/" class="font-mono text-[10px] uppercase tracking-widest underline">← Back to pools</a>

{#if data.loadError}
	<p role="alert" class="mt-6 border border-black px-3 py-2 text-sm">
		Could not load the pool: {data.loadError}
	</p>
{:else if data.pool}
	{@const pool = data.pool}
	{@const picked = data.pick
		? pool.options.find((option) => option.id === data.pick?.outcome_id)
		: undefined}

	<div class="mt-4 flex items-start justify-between gap-4">
		<h1 class="text-3xl font-bold tracking-tight">{pool.name}</h1>
		<StatusBadge status={pool.status} />
	</div>

	<p class="mt-2 text-sm text-neutral-700">{pool.statement}</p>

	<p class="mt-3 font-mono text-[10px] uppercase tracking-widest text-neutral-500">
		Deadline {formatDeadline(pool.deadline)}
	</p>
	<p class="mt-1 text-[11px] uppercase tracking-wide text-neutral-500">By {pool.creator.name}</p>

	{#if form?.error}
		<p role="alert" class="mt-6 border border-black bg-black px-3 py-2 text-sm text-white">
			{form.error}
		</p>
	{/if}
	{#if form?.saved}
		<p role="status" class="mt-6 border border-black bg-neutral-100 px-3 py-2 text-sm font-bold">
			Pick saved.
		</p>
	{/if}

	<div class="mt-8 border border-black p-5">
		{#if pool.status === 'OPEN'}
			{#if !data.loggedIn}
				<p class="text-sm">Log in to save your pick.</p>
				<a
					href={`/login?redirectTo=${encodeURIComponent(`/pools/${pool.id}`)}`}
					class="mt-4 inline-block border border-black bg-black px-4 py-2 text-sm font-bold text-white hover:bg-white hover:text-black"
				>
					Log in
				</a>
			{:else if !data.user}
				<p class="text-sm">This account has no User profile yet.</p>
				<a href="/no-user" class="mt-4 inline-block text-sm underline">What now?</a>
			{:else}
				<form
					method="POST"
					class="space-y-4"
					use:enhance={() => {
						submitting = true;
						return async ({ update }) => {
							await update();
							submitting = false;
						};
					}}
				>
					{#if pool.presentation === 'dropdown'}
						<label for="outcome_id" class={labelClass}>Your pick</label>
						<select id="outcome_id" name="outcome_id" required class={inputClass}>
							<option value="">Select an option</option>
							{#each pool.options as option (option.id)}
								<option value={option.id} selected={data.pick?.outcome_id === option.id}>
									{option.label}
								</option>
							{/each}
						</select>
					{:else}
						<fieldset>
							<legend class={labelClass}>Your pick</legend>
							<div class="mt-2 grid gap-2">
								{#each pool.options as option (option.id)}
									<label
										class="flex items-center gap-3 border border-black px-3 py-2 text-sm has-[:checked]:bg-black has-[:checked]:text-white"
									>
										<input
											type="radio"
											name="outcome_id"
											value={option.id}
											required
											checked={data.pick?.outcome_id === option.id}
										/>
										<span>{option.label}</span>
										{#if data.pick?.outcome_id === option.id}
											<span class="ml-auto font-mono text-[10px] uppercase tracking-widest">
												Your pick
											</span>
										{/if}
									</label>
								{/each}
							</div>
						</fieldset>
					{/if}

					<div class="flex flex-wrap items-center gap-4 border-t border-black pt-4">
						<button
							type="submit"
							disabled={submitting}
							class="border border-black bg-black px-4 py-2 text-sm font-bold text-white hover:bg-white hover:text-black disabled:cursor-not-allowed disabled:opacity-50"
						>
							{submitting ? 'Saving…' : data.pick ? 'Change pick' : 'Save pick'}
						</button>
						{#if picked}
							<span class="font-mono text-[10px] uppercase tracking-widest text-neutral-600">
								Saved: {picked.label}
							</span>
						{/if}
					</div>
				</form>
			{/if}
		{:else}
			<p class="font-mono text-[10px] font-bold uppercase tracking-widest">Picks are closed.</p>
			{#if !data.loggedIn}
				<p class="mt-3 text-sm text-neutral-600">Log in to see your saved pick.</p>
				<a
					href={`/login?redirectTo=${encodeURIComponent(`/pools/${pool.id}`)}`}
					class="mt-4 inline-block text-sm underline"
				>
					Log in
				</a>
			{:else if picked}
				<p class="mt-3 text-sm">Your pick: <strong>{picked.label}</strong></p>
			{:else}
				<p class="mt-3 text-sm text-neutral-600">You did not pick an option.</p>
			{/if}
		{/if}
	</div>
{:else}
	<p class="mt-6 text-sm">Pool not found.</p>
{/if}
