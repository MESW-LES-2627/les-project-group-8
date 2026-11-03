<script lang="ts">
	import { enhance } from '$app/forms';
	import type { PageProps } from './$types';

	let { form }: PageProps = $props();

	const inputClass =
		'mt-1 w-full border border-black bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-black';
	const labelClass = 'font-mono text-[10px] font-bold uppercase tracking-widest';
	const errorClass = 'mt-1 text-xs font-bold';

	let submitting = $state(false);
</script>

<svelte:head>
	<title>Sign up · LES</title>
</svelte:head>

<h1 class="text-3xl font-bold tracking-tight">Create an account</h1>
<p class="mt-1 text-sm text-neutral-600">
	Your name is how other people see you in pools. Already have an account?
	<a href="/login" class="underline">Log in</a>
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
			aria-invalid={form?.fields?.email ? 'true' : undefined}
		/>
		{#if form?.fields?.email}<p class={errorClass}>{form.fields.email}</p>{/if}
	</div>

	<div>
		<label for="password" class={labelClass}>Password</label>
		<input
			id="password"
			name="password"
			type="password"
			autocomplete="new-password"
			required
			minlength="6"
			class={inputClass}
			aria-invalid={form?.fields?.password ? 'true' : undefined}
		/>
		{#if form?.fields?.password}<p class={errorClass}>{form.fields.password}</p>{/if}
	</div>

	<div>
		<label for="name" class={labelClass}>Name</label>
		<input
			id="name"
			name="name"
			autocomplete="nickname"
			required
			maxlength="80"
			value={form?.values?.name ?? ''}
			class={inputClass}
			aria-invalid={form?.fields?.name ? 'true' : undefined}
		/>
		{#if form?.fields?.name}<p class={errorClass}>{form.fields.name}</p>{/if}
	</div>

	<div class="flex items-center gap-4 border-t border-black pt-5">
		<button
			type="submit"
			disabled={submitting}
			class="border border-black bg-black px-4 py-2 text-sm font-bold text-white hover:bg-white hover:text-black disabled:cursor-not-allowed disabled:opacity-50"
		>
			{submitting ? 'Signing up…' : 'Sign up'}
		</button>
		<a href="/" class="text-sm underline">Cancel</a>
	</div>
</form>
