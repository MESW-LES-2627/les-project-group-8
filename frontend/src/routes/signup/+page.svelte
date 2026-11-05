<script lang="ts">
	import { NAME_MAX, PASSWORD_MIN } from '#lib/account.ts';
	import Form from '#lib/components/Form.svelte';
	import { errorClass, inputClass, labelClass, submitClass } from '#lib/form.ts';
	import type { PageProps } from './$types';

	let { form }: PageProps = $props();
</script>

<svelte:head>
	<title>Sign up · LES</title>
</svelte:head>

<h1 class="text-3xl font-bold tracking-tight">Create an account</h1>
<p class="mt-1 text-sm text-neutral-600">
	Your name is how other people see you in pools. Already have an account?
	<a href="/login" class="underline">Log in</a>
</p>

<Form error={form?.error} class="mt-8 space-y-5">
	{#snippet children(submitting)}
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
				minlength={PASSWORD_MIN}
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
				maxlength={NAME_MAX}
				value={form?.values?.name ?? ''}
				class={inputClass}
				aria-invalid={form?.fields?.name ? 'true' : undefined}
			/>
			{#if form?.fields?.name}<p class={errorClass}>{form.fields.name}</p>{/if}
		</div>

		<div class="flex items-center gap-4 border-t border-black pt-5">
			<button type="submit" disabled={submitting} class={submitClass}>
				{submitting ? 'Signing up…' : 'Sign up'}
			</button>
			<a href="/" class="text-sm underline">Cancel</a>
		</div>
	{/snippet}
</Form>
