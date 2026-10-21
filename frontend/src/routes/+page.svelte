<script lang="ts">
	import '../app.css';
	import { enhance } from '$app/forms';
	import type { PageProps } from './$types';
	import type { PoolStatus } from './+page.server';

	let { data, form }: PageProps = $props();

	let submitting = $state(false);
	let hydrated = $state(false);
	$effect(() => {
		hydrated = true;
	});

	let createdId = $derived(form && 'created' in form ? form.created : null);
	let values = $derived(form && 'values' in form ? form.values : undefined);
	let error = $derived(form && 'error' in form ? form.error : undefined);

	const statusStyles: Record<PoolStatus, string> = {
		OPEN: 'bg-emerald-50 text-emerald-700 border-emerald-200',
		LOCKED: 'bg-amber-50 text-amber-700 border-amber-200',
		RESOLVED: 'bg-sky-50 text-sky-700 border-sky-200'
	};

	function formatDeadline(deadline: string, localTime: boolean): string {
		return (
			new Intl.DateTimeFormat('en-GB', {
				dateStyle: 'medium',
				timeStyle: 'short',
				timeZone: localTime ? undefined : 'UTC'
			}).format(new Date(deadline)) + (localTime ? '' : ' UTC')
		);
	}
</script>

<svelte:head>
	<title>Friendly Pools: call it before it happens</title>
	<meta
		name="description"
		content="Create zero-money prediction pools with your friends and settle who was right."
	/>
</svelte:head>

<main class="mx-auto max-w-6xl px-6 py-12 lg:py-16">
	<header class="max-w-2xl">
		<p
			class="inline-flex items-center gap-2 rounded-full border border-orange-200 bg-orange-50 px-3 py-1 text-xs font-medium text-orange-700"
		>
			<span class="size-1.5 rounded-full bg-[#ff3e00]"></span>
			Iteration 0 · thin vertical slice
		</p>
		<h1 class="mt-4 text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
			Call it <span class="text-[#ff3e00]">before it happens</span>.
		</h1>
		<p class="mt-3 text-lg text-slate-600">
			Create a pool, pick a side, and settle once and for all who saw it coming. Bragging rights
			only.
		</p>
	</header>

	<div class="mt-10 grid gap-8 lg:grid-cols-[minmax(0,26rem)_1fr]">
		<section
			aria-labelledby="create-heading"
			class="h-fit rounded-xl border border-slate-200 bg-white p-6 shadow-xs lg:sticky lg:top-8"
		>
			<h2 id="create-heading" class="text-xl font-semibold text-slate-900">New pool</h2>

			<form
				id="create-pool-form"
				method="POST"
				action="?/create"
				class="mt-6 space-y-4"
				use:enhance={({ formData }) => {
					formData.set('tzOffset', String(new Date().getTimezoneOffset()));
					submitting = true;
					return async ({ update }) => {
						await update();
						submitting = false;
					};
				}}
			>
				<div>
					<label class="mb-1.5 block text-sm font-medium text-slate-700" for="pool-name">Title</label>
					<input
						id="pool-name"
						name="name"
						class="block w-full rounded-lg border border-slate-300 bg-white px-3.5 py-2.5 text-slate-900 placeholder:text-slate-400 focus:border-[#ff3e00] focus:ring-2 focus:ring-[#ff3e00]/20"
						required
						maxlength="120"
						placeholder="Champions League Final"
						value={values?.name ?? ''}
					/>
				</div>

				<div>
					<label class="mb-1.5 block text-sm font-medium text-slate-700" for="pool-statement">Statement</label>
					<textarea
						id="pool-statement"
						name="statement"
						class="block w-full rounded-lg border border-slate-300 bg-white px-3.5 py-2.5 text-slate-900 placeholder:text-slate-400 focus:border-[#ff3e00] focus:ring-2 focus:ring-[#ff3e00]/20 min-h-24 resize-y"
						required
						maxlength="500"
						placeholder="Real Madrid wins in 90 minutes."
						value={values?.statement ?? ''}
					></textarea>
				</div>

				<fieldset>
					<legend class="mb-1.5 block text-sm font-medium text-slate-700">Outcomes</legend>
					<div class="grid grid-cols-2 gap-3">
						<input
							id="pool-option-a"
							name="optionA"
							class="block w-full rounded-lg border border-slate-300 bg-white px-3.5 py-2.5 text-slate-900 placeholder:text-slate-400 focus:border-[#ff3e00] focus:ring-2 focus:ring-[#ff3e00]/20"
							required
							maxlength="100"
							placeholder="Yes"
							aria-label="First outcome"
							value={values?.optionA ?? ''}
						/>
						<input
							id="pool-option-b"
							name="optionB"
							class="block w-full rounded-lg border border-slate-300 bg-white px-3.5 py-2.5 text-slate-900 placeholder:text-slate-400 focus:border-[#ff3e00] focus:ring-2 focus:ring-[#ff3e00]/20"
							required
							maxlength="100"
							placeholder="No"
							aria-label="Second outcome"
							value={values?.optionB ?? ''}
						/>
					</div>
				</fieldset>

				<div>
					<label class="mb-1.5 block text-sm font-medium text-slate-700" for="pool-deadline">Locks at</label>
					<input
						id="pool-deadline"
						name="deadline"
						type="datetime-local"
						class="block w-full rounded-lg border border-slate-300 bg-white px-3.5 py-2.5 text-slate-900 placeholder:text-slate-400 focus:border-[#ff3e00] focus:ring-2 focus:ring-[#ff3e00]/20"
						required
						value={values?.deadline ?? ''}
					/>
				</div>

				<!-- Overwritten by enhance with the browser's offset; 0 (UTC) without JS. -->
				<input type="hidden" name="tzOffset" value="0" />

				{#if error}
					<p
						id="create-pool-error"
						role="alert"
						class="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800"
					>
						{error}
					</p>
				{/if}

				<button
					id="create-pool-submit"
					type="submit"
					disabled={submitting}
					class="w-full rounded-lg bg-[#ff3e00] px-5 py-2.5 font-semibold text-white shadow-xs transition hover:bg-[#ea3600] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#ff3e00] disabled:cursor-wait disabled:opacity-60"
				>
					{submitting ? 'Creating…' : 'Create pool'}
				</button>
			</form>
		</section>

		<section aria-labelledby="pools-heading">
			<h2 id="pools-heading" class="text-xl font-semibold text-slate-900">Latest pools</h2>

			{#await data.pools}
				<div class="mt-6 space-y-4" aria-busy="true">
					{#each [0, 1, 2] as i (i)}
						<div class="h-44 rounded-xl border border-slate-200 bg-white p-6 shadow-xs animate-pulse"></div>
					{/each}
					<p class="text-sm text-slate-500">Waking up the server… this can take a few seconds.</p>
				</div>
			{:then result}
				{#if !result.ok}
					<p
						id="pools-error"
						role="alert"
						class="mt-6 rounded-xl border border-rose-200 bg-rose-50 p-6 text-sm text-rose-800"
					>
						{result.error}
					</p>
				{:else if result.items.length === 0}
					<div class="mt-6 rounded-xl border border-dashed border-slate-300 bg-white p-10 text-center">
						<p class="text-4xl">🎯</p>
						<p class="mt-3 font-semibold text-slate-900">No pools yet</p>
						<p class="mt-1 text-sm text-slate-500">Create the first one and start the debate.</p>
					</div>
				{:else}
					<div id="pool-list" class="mt-6 grid gap-4 xl:grid-cols-2">
						{#each result.items as pool (pool.id)}
							<article
								id="pool-{pool.id}"
								class="rounded-xl border bg-white p-6 shadow-xs transition hover:shadow-sm
									{pool.id === createdId ? 'border-orange-500 ring-2 ring-orange-500/20' : 'border-slate-200'}"
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
									<time datetime={pool.deadline}>Locks {formatDeadline(pool.deadline, hydrated)}</time>
								</footer>
							</article>
						{/each}
					</div>
				{/if}
			{/await}
		</section>
	</div>
</main>
