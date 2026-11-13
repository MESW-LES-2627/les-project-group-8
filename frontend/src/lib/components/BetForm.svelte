<script lang="ts">
	import { errorClass, inputClass, labelClass, submitClass } from '#lib/form.ts';
	import type { BetPresentation } from '#lib/types.ts';
	import Form from './Form.svelte';

	type FormState = {
		error?: string;
		added?: boolean;
		fields?: {
			statement?: string;
			options?: string;
			presentation?: string;
		};
		values?: {
			statement: string;
			options: string[];
			presentation: string;
		};
	};
	type OptionRow = { key: number; value: string };
	let { form = null }: { form?: FormState | null } = $props();
	let nextKey = 0;
	function rowsFrom(labels = ['', '']): OptionRow[] {
		return labels.map((value) => ({ key: nextKey++, value }));
	}
	// Initial values also render without JavaScript; the effect handles later submissions.
	// svelte-ignore state_referenced_locally
	let optionRows = $state<OptionRow[]>(rowsFrom(form?.values?.options));
	// svelte-ignore state_referenced_locally
	let presentation = $state<BetPresentation>(form?.values?.presentation === 'dropdown' ? 'dropdown' : 'radio');

	// Restore failed submissions; a successful addition starts a fresh Bet.
	$effect(() => {
		optionRows = rowsFrom(form?.values?.options);
		presentation = form?.values?.presentation === 'dropdown' ? 'dropdown' : 'radio';
	});
</script>

<Form action="?/addBet" error={form?.error} class="space-y-5">
	{#snippet children(submitting)}
		<div>
			<label for="statement" class={labelClass}>Bet statement</label>
			<textarea
				id="statement"
				name="statement"
				required
				maxlength="500"
				rows="3"
				class={inputClass}
				aria-invalid={form?.fields?.statement ? 'true' : undefined}
			>{form?.values?.statement ?? ''}</textarea>
			{#if form?.fields?.statement}
				<p class={errorClass}>{form.fields.statement}</p>
			{/if}
		</div>

		<fieldset class="border-t border-black pt-5">
			<legend class={labelClass}>Answer options</legend>
			<p class="mt-1 text-xs text-neutral-600">Add 2–10 different options in the order participants will see them.</p>
			<div class="mt-3 grid gap-3">
				{#each optionRows as row, index (row.key)}
					<div>
						<label for={`bet-option-${row.key}`} class={labelClass}>Option {index + 1}</label>
						<div class="flex gap-2">
							<input
								id={`bet-option-${row.key}`}
								name="options"
								required
								maxlength="100"
								bind:value={row.value}
								class={inputClass}
								aria-invalid={form?.fields?.options ? 'true' : undefined}
							/>
							{#if optionRows.length > 2}
								<button
									type="button"
									onclick={() => optionRows = optionRows.filter((item) => item.key !== row.key)}
									class="mt-1 shrink-0 border border-black px-2 py-1 text-[10px] font-bold uppercase tracking-widest hover:bg-black hover:text-white"
								>
									Remove
								</button>
							{/if}
						</div>
					</div>
				{/each}
			</div>
			{#if optionRows.length < 10}
				<button
					type="button"
					onclick={() => optionRows.push({ key: nextKey++, value: '' })}
					class="mt-3 border border-black px-2 py-1 text-[10px] font-bold uppercase tracking-widest hover:bg-black hover:text-white"
				>
					+ Add option
				</button>
			{/if}
			{#if form?.fields?.options}
				<p class={errorClass}>{form.fields.options}</p>
			{/if}
		</fieldset>

		<fieldset class="border-t border-black pt-5">
			<legend class={labelClass}>Presentation</legend>
			<div class="mt-2 flex flex-wrap gap-5">
				<label class="flex items-center gap-2 text-sm"><input type="radio" name="presentation" value="radio" bind:group={presentation} />Radio buttons</label>
				<label class="flex items-center gap-2 text-sm"><input type="radio" name="presentation" value="dropdown" bind:group={presentation} />Dropdown</label>
			</div>
			{#if form?.fields?.presentation}
				<p class={errorClass}>{form.fields.presentation}</p>
			{/if}
		</fieldset>

		<button type="submit" disabled={submitting} class={submitClass}>{submitting ? 'Adding…' : 'Add bet'}</button>
	{/snippet}
</Form>
