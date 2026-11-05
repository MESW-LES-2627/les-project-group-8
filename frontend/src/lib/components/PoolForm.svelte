<script lang="ts">
	import { errorClass, inputClass, labelClass, submitClass } from '#lib/form.ts';
	import Form from './Form.svelte';

	type FieldErrors = {
		name?: string;
		description?: string;
		deadline?: string;
	};

	type FormState = {
		error: string;
		fields?: FieldErrors;
		values?: {
			name?: string;
			description?: string;
			deadline?: string;
		};
	};

	let { form = null }: { form?: FormState | null } = $props();

	const HOUR = 60 * 60 * 1000;
	const DAY = 24 * HOUR;
	const WEEK = 7 * DAY;

	let deadlineInput: HTMLInputElement | undefined = $state();

	function setPreset(offsetMs: number) {
		if (!deadlineInput) {
			return;
		}
		const date = new Date(Date.now() + offsetMs);
		const pad = (value: number) => String(value).padStart(2, '0');
		deadlineInput.value = `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(
			date.getDate()
		)}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
	}

	// Default to one day from now; leave a submitted value untouched on failure.
	$effect(() => {
		if (deadlineInput && !deadlineInput.value) {
			setPreset(DAY);
		}
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
			{#if form?.fields?.name}
				<p class={errorClass}>{form.fields.name}</p>
			{/if}
		</div>

		<div>
			<label for="description" class={labelClass}>Description (optional)</label>
			<textarea
				id="description"
				name="description"
				maxlength="500"
				rows="3"
				class={inputClass}
				aria-invalid={form?.fields?.description ? 'true' : undefined}
			>{form?.values?.description ?? ''}</textarea>
			{#if form?.fields?.description}
				<p class={errorClass}>{form.fields.description}</p>
			{/if}
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
			{#if form?.fields?.deadline}
				<p class={errorClass}>{form.fields.deadline}</p>
			{/if}
		</div>

		<div class="flex items-center gap-4 border-t border-black pt-5">
			<button type="submit" disabled={submitting} class={submitClass}>
				{submitting ? 'Creating…' : 'Create pool'}
			</button>
			<a href="/" class="text-sm underline">Cancel</a>
		</div>
	{/snippet}
</Form>
