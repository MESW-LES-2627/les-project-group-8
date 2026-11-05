<script lang="ts">
	import PoolForm from '#lib/components/PoolForm.svelte';
	import type { PageProps } from './$types';

	let { form }: PageProps = $props();
</script>

<svelte:head>
	<title>New pool · LES</title>
</svelte:head>

<a href="/" class="font-mono text-[10px] uppercase tracking-widest underline">← Back to pools</a>

<h1 class="mt-4 text-3xl font-bold tracking-tight">New pool</h1>
<p class="mt-1 text-sm text-neutral-600">
	Create your pool with a shared deadline, then add its bets.
</p>

<div class="mt-8">
	<PoolForm {form} />
</div>
