<script lang="ts">
	import { NAME_MAX } from '#lib/account.ts';
	import Form from '#lib/components/Form.svelte';
	import { errorClass, inputClass, labelClass, submitClass } from '#lib/form.ts';
	import type { PageProps } from './$types';

	type FormState = {
		error: string;
		fields?: { name?: string };
		values?: { name?: string };
	};

	let { data, form = null }: { data: PageProps['data']; form?: FormState | null } = $props();
</script>

<svelte:head>
	<title>Your account · LES</title>
</svelte:head>

<h1 class="text-3xl font-bold tracking-tight">Your account</h1>
<p class="mt-1 text-sm text-neutral-600">
	Your name is how other people see you in pools. Changing it keeps your pools, picks and
	record.
</p>

{#if data.saved}
	<p role="status" class="mt-6 border border-black bg-neutral-100 px-3 py-2 text-sm font-bold">
		Name updated.
	</p>
{/if}

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
				aria-invalid={form?.fields?.name ? 'true' : undefined}
			/>
			{#if form?.fields?.name}
				<p class={errorClass}>{form.fields.name}</p>
			{/if}
		</div>

		<div class="flex items-center gap-4 border-t border-black pt-5">
			<button type="submit" disabled={submitting} class={submitClass}>
				{submitting ? 'Saving…' : 'Save name'}
			</button>
			<a href="/" class="text-sm underline">Cancel</a>
		</div>
	{/snippet}
</Form>
