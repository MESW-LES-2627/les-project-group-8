<script lang="ts">
	import { enhance } from '$app/forms';
	import type { Snippet } from 'svelte';

	// A POST form with the error banner on top; `children` is told whether it is submitting.
	let {
		error,
		class: className = '',
		children
	}: { error?: string; class?: string; children: Snippet<[boolean]> } = $props();

	let submitting = $state(false);
</script>

<form
	method="POST"
	class={className}
	use:enhance={() => {
		submitting = true;
		return async ({ update }) => {
			await update();
			submitting = false;
		};
	}}
>
	{#if error}
		<p role="alert" class="border border-black bg-black px-3 py-2 text-sm text-white">
			{error}
		</p>
	{/if}

	{@render children(submitting)}
</form>
