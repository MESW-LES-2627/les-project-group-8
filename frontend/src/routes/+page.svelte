<script lang="ts">
	let count = $state(0);
</script>

<main class="mx-auto max-w-2xl px-6 py-16 font-sans text-slate-800">
	<h1 class="text-4xl font-bold tracking-tight text-slate-900">LES</h1>
	<p class="mt-2 text-slate-600">SvelteKit 3 · TypeScript · Tailwind CSS 4.</p>

	<button
		type="button"
		onclick={() => count++}
		class="mt-8 rounded-lg bg-slate-900 px-4 py-2 font-medium text-white transition hover:bg-slate-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900"
	>
		count is {count}
	</button>

	<p class="mt-8 text-sm text-slate-500">
		Edit <code class="rounded bg-slate-100 px-1.5 py-0.5 text-slate-700">src/routes/+page.svelte</code>
		to get started.
	</p>
</main>
