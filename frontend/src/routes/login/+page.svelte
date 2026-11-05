<script lang="ts">
	import Form from '#lib/components/Form.svelte';
	import { inputClass, labelClass, submitClass } from '#lib/form.ts';
	import type { PageProps } from './$types';

	let { form }: PageProps = $props();
</script>

<svelte:head>
	<title>Log in · LES</title>
</svelte:head>

<h1 class="text-3xl font-bold tracking-tight">Log in</h1>
<p class="mt-1 text-sm text-neutral-600">
	No account yet? <a href="/signup" class="underline">Sign up</a>
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
			<button type="submit" disabled={submitting} class={submitClass}>
				{submitting ? 'Logging in…' : 'Log in'}
			</button>
			<a href="/" class="text-sm underline">Cancel</a>
		</div>
	{/snippet}
</Form>
