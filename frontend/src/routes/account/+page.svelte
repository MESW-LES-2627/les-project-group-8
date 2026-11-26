<script lang="ts">
	import { NAME_MAX } from '#lib/account.ts';
	import Form from '#lib/components/Form.svelte';
	import { inputClass, labelClass, submitClass } from '#lib/form.ts';
	import type { PageProps } from './$types';

	let { data, form }: PageProps = $props();
</script>

<svelte:head>
	<title>Your account · LES</title>
</svelte:head>

<h1 class="text-3xl font-bold tracking-tight">Your account</h1>
<p class="mt-1 text-sm text-neutral-600">
	Your name is how other people see you in pools. Changing it keeps your pools, picks and
	record.
</p>

<Form error={form?.error} class="mt-8 space-y-5">
	{#snippet children(submitting)}
		<div>
			<label for="name" class={labelClass}>Name</label>
			<input
				id="name"
				name="name"
				autocomplete="nickname"
				required
				maxlength={NAME_MAX}
				value={form?.values?.name ?? data.user?.name ?? ''}
				class={inputClass}
			/>
		</div>

		<div class="flex items-center gap-4 border-t border-black pt-5">
			<button type="submit" disabled={submitting} class={submitClass}>
				{submitting ? 'Saving…' : 'Save name'}
			</button>
			<a href="/" class="text-sm underline">Cancel</a>
		</div>
	{/snippet}
</Form>
