<script lang="ts">
	let count = $state(0);
</script>

<main>
	<h1>LES</h1>
	<p>SvelteKit 3 · TypeScript · Vite 8.</p>

	<button onclick={() => count++}>
		count is {count}
	</button>

	<p>
		Edit <code>src/routes/+page.svelte</code> to get started. Add routes by creating
		folders under <code>src/routes/</code>.
	</p>
</main>

<style>
	main {
		max-width: 42rem;
		margin: 0 auto;
		padding: 4rem 1.5rem;
		font-family: system-ui, sans-serif;
	}
	h1 {
		margin: 0 0 0.25rem;
	}
	p {
		color: #444;
	}
	button {
		margin: 1rem 0;
		padding: 0.5rem 0.9rem;
		border: 1px solid #ccc;
		border-radius: 6px;
		background: #fff;
		cursor: pointer;
	}
	code {
		background: #f4f4f4;
		padding: 0.1rem 0.3rem;
		border-radius: 4px;
		font-size: 0.9em;
	}
</style>
