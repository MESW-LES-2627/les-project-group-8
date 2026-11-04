<script lang="ts">
	import { errorClass, inputClass, labelClass, submitClass } from '#lib/form.ts';
	import Form from './Form.svelte';

	type FieldErrors = {
		name?: string;
		statement?: string;
		options?: string;
		deadline?: string;
	};

	type FormState = {
		error: string;
		fields?: FieldErrors;
		values?: {
			name?: string;
			statement?: string;
			deadline?: string;
			options?: string[];
			presentation?: string;
		};
	};

	type OptionRow = { key: number; value: string };

	let { form = null }: { form?: FormState | null } = $props();

	const MAX_OPTIONS = 10;
	const HOUR = 60 * 60 * 1000;
	const DAY = 24 * HOUR;
	const WEEK = 7 * DAY;

	let nextOptionKey = 1;

	function optionRowsFrom(values?: string[]): OptionRow[] {
		const labels = values && values.length > 0 ? [...values] : ['', ''];
		while (labels.length < 2) labels.push('');
		return labels.map((value) => ({ key: nextOptionKey++, value }));
	}

	// These read the initial form values on purpose; the effect below re-syncs
	// with every later submission.
	// svelte-ignore state_referenced_locally
	let optionRows = $state<OptionRow[]>(optionRowsFrom(form?.values?.options));
	// svelte-ignore state_referenced_locally
	let presentation = $state<'radio' | 'dropdown'>(
		form?.values?.presentation === 'dropdown' ? 'dropdown' : 'radio'
	);

	// A failed submission replaces the form prop; restore what the user typed.
	let appliedForm: FormState | null = null;
	$effect(() => {
		if (form && form !== appliedForm) {
			appliedForm = form;
			optionRows = optionRowsFrom(form.values?.options);
			presentation = form.values?.presentation === 'dropdown' ? 'dropdown' : 'radio';
		}
	});

	function addOption() {
		if (optionRows.length < MAX_OPTIONS) {
			optionRows.push({ key: nextOptionKey++, value: '' });
		}
	}

	function removeOption(key: number) {
		if (optionRows.length > 2) {
			optionRows = optionRows.filter((row) => row.key !== key);
		}
	}

	let deadlineInput: HTMLInputElement | undefined = $state();

	function setPreset(offsetMs: number) {
		if (!deadlineInput) return;
		const date = new Date(Date.now() + offsetMs);
		const pad = (value: number) => String(value).padStart(2, '0');
		deadlineInput.value = `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(
			date.getDate()
		)}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
	}

	// Default to one day from now; leave a submitted value untouched on failure.
	$effect(() => {
		if (deadlineInput && !deadlineInput.value) setPreset(DAY);
	});
</script>

<Form error={form?.error} class="space-y-5">
	{#snippet children(submitting)}
		<div>
			<label for="name" class={labelClass}>Name</label>
			<input
				id="name"
				name="name"
				required
				maxlength="120"
				value={form?.values?.name ?? ''}
				class={inputClass}
				aria-invalid={form?.fields?.name ? 'true' : undefined}
			/>
			{#if form?.fields?.name}<p class={errorClass}>{form.fields.name}</p>{/if}
		</div>

		<div>
			<label for="statement" class={labelClass}>Statement</label>
			<textarea
				id="statement"
				name="statement"
				required
				maxlength="500"
				rows="3"
				class={inputClass}
				aria-invalid={form?.fields?.statement ? 'true' : undefined}
			>{form?.values?.statement ?? ''}</textarea>
			{#if form?.fields?.statement}<p class={errorClass}>{form.fields.statement}</p>{/if}
		</div>

		<div>
			<label for="deadline" class={labelClass}>Deadline</label>
			<input
				id="deadline"
				name="deadline"
				type="datetime-local"
				required
				bind:this={deadlineInput}
				value={form?.values?.deadline ?? ''}
				class={inputClass}
				aria-invalid={form?.fields?.deadline ? 'true' : undefined}
			/>
			<div class="mt-2 flex flex-wrap gap-2">
				<button
					type="button"
					onclick={() => setPreset(HOUR)}
					class="border border-black px-2 py-1 text-[10px] font-bold uppercase tracking-widest hover:bg-black hover:text-white"
				>
					+1 hour
				</button>
				<button
					type="button"
					onclick={() => setPreset(DAY)}
					class="border border-black px-2 py-1 text-[10px] font-bold uppercase tracking-widest hover:bg-black hover:text-white"
				>
					+1 day
				</button>
				<button
					type="button"
					onclick={() => setPreset(WEEK)}
					class="border border-black px-2 py-1 text-[10px] font-bold uppercase tracking-widest hover:bg-black hover:text-white"
				>
					+1 week
				</button>
			</div>
			{#if form?.fields?.deadline}<p class={errorClass}>{form.fields.deadline}</p>{/if}
		</div>

		<fieldset class="border-t border-black pt-5">
			<legend class={labelClass}>Answer options</legend>
			<p class="mt-1 text-xs text-neutral-600">
				Two or more different labels. They keep the order shown here.
			</p>
			<div class="mt-3 grid gap-3">
				{#each optionRows as row, index (row.key)}
					<div>
						<label for={`option-${row.key}`} class={labelClass}>Option {index + 1}</label>
						<div class="flex gap-2">
							<input
								id={`option-${row.key}`}
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
									onclick={() => removeOption(row.key)}
									class="mt-1 shrink-0 border border-black px-2 py-1 text-[10px] font-bold uppercase tracking-widest hover:bg-black hover:text-white"
								>
									Remove
								</button>
							{/if}
						</div>
					</div>
				{/each}
			</div>
			{#if optionRows.length < MAX_OPTIONS}
				<button
					type="button"
					onclick={addOption}
					class="mt-3 border border-black px-2 py-1 text-[10px] font-bold uppercase tracking-widest hover:bg-black hover:text-white"
				>
					+ Add option
				</button>
			{/if}
			{#if form?.fields?.options}<p class={errorClass}>{form.fields.options}</p>{/if}
		</fieldset>

		<fieldset class="border-t border-black pt-5">
			<legend class={labelClass}>Presentation</legend>
			<div class="mt-2 flex flex-wrap gap-5">
				<label class="flex items-center gap-2 text-sm">
					<input type="radio" name="presentation" value="radio" bind:group={presentation} />
					Radio buttons
				</label>
				<label class="flex items-center gap-2 text-sm">
					<input type="radio" name="presentation" value="dropdown" bind:group={presentation} />
					Dropdown
				</label>
			</div>
		</fieldset>

		<div class="flex items-center gap-4 border-t border-black pt-5">
			<button type="submit" disabled={submitting} class={submitClass}>
				{submitting ? 'Creating…' : 'Create pool'}
			</button>
			<a href="/" class="text-sm underline">Cancel</a>
		</div>
	{/snippet}
</Form>
