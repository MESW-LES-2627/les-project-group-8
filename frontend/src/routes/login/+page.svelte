<script lang="ts">
	import { enhance } from '$app/forms';
	import type { PageProps } from './$types';

	let { form }: PageProps = $props();

	const inputClass =
		'mt-1 w-full border border-black bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-black';
	const labelClass = 'font-mono text-[10px] font-bold uppercase tracking-widest';

	let submitting = $state(false);
</script>

<svelte:head>
	<title>Log in · LES</title>
</svelte:head>

<h1 class="text-3xl font-bold tracking-tight">Log in</h1>
<p class="mt-1 text-sm text-neutral-600">
	No account yet? <a href="/signup" class="underline">Sign up</a>
</p>

<form
	method="POST"
	class="mt-8 space-y-5"
	use:enhance={() => {
		submitting = true;
		return async ({ update }) => {
			await update();
			submitting = false;
		};
	}}
>
	{#if form?.error}
		<p role="alert" class="border border-black bg-black px-3 py-2 text-sm text-white">
			{form.error}
		</p>
	{/if}

	<div>
		<label for="email" class={labelClass}>Email</label>
		<input
			id="email"
			name="email"
			type="email"
			autocomplete="email"
			required
			value={form?.values?.email ?? ''}
			class={inputClass}
		/>
	</div>

	<div>
		<label for="password" class={labelClass}>Password</label>
		<input
			id="password"
			name="password"
			type="password"
			autocomplete="current-password"
			required
			class={inputClass}
		/>
	</div>

	<div class="flex items-center gap-4 border-t border-black pt-5">
		<button
			type="submit"
			disabled={submitting}
			class="border border-black bg-black px-4 py-2 text-sm font-bold text-white hover:bg-white hover:text-black disabled:cursor-not-allowed disabled:opacity-50"
		>
			{submitting ? 'Logging in…' : 'Log in'}
		</button>
		<a href="/" class="text-sm underline">Cancel</a>
	</div>
</form>
