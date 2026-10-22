<script lang="ts">
	import { enhance } from '$app/forms';

	type FieldErrors = {
		name?: string;
		statement?: string;
		option1?: string;
		option2?: string;
		deadline?: string;
	};

	type FormState = {
		error: string;
		fields?: FieldErrors;
		values?: Record<string, string>;
	};

	let { form = null }: { form?: FormState | null } = $props();

	const HOUR = 60 * 60 * 1000;
	const DAY = 24 * HOUR;
	const WEEK = 7 * DAY;

	const inputClass =
		'mt-1 w-full border border-black bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-black';
	const labelClass = 'font-mono text-[10px] font-bold uppercase tracking-widest';
	const errorClass = 'mt-1 text-xs font-bold';

	let submitting = $state(false);
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

<form
	method="POST"
	class="space-y-5"
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

	<fieldset class="grid gap-4 border-t border-black pt-5 sm:grid-cols-2">
		<legend class="sr-only">Outcomes</legend>
		<div>
			<label for="option1" class={labelClass}>Option A</label>
			<input
				id="option1"
				name="option1"
				required
				maxlength="100"
				value={form?.values?.option1 ?? ''}
				class={inputClass}
				aria-invalid={form?.fields?.option1 ? 'true' : undefined}
			/>
			{#if form?.fields?.option1}<p class={errorClass}>{form.fields.option1}</p>{/if}
		</div>
		<div>
			<label for="option2" class={labelClass}>Option B</label>
			<input
				id="option2"
				name="option2"
				required
				maxlength="100"
				value={form?.values?.option2 ?? ''}
				class={inputClass}
				aria-invalid={form?.fields?.option2 ? 'true' : undefined}
			/>
			{#if form?.fields?.option2}<p class={errorClass}>{form.fields.option2}</p>{/if}
		</div>
	</fieldset>

	<div class="flex items-center gap-4 border-t border-black pt-5">
		<button
			type="submit"
			disabled={submitting}
			class="border border-black bg-black px-4 py-2 text-sm font-bold text-white hover:bg-white hover:text-black disabled:cursor-not-allowed disabled:opacity-50"
		>
			{submitting ? 'Creating…' : 'Create pool'}
		</button>
		<a href="/" class="text-sm underline">Cancel</a>
	</div>
</form>
