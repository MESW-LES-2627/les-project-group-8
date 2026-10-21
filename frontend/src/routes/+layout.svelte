<script lang="ts">
	import '../app.css';
	import favicon from '#lib/assets/favicon.svg';
	import type { LayoutProps } from './$types';

	let { children }: LayoutProps = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<title>LES</title>
</svelte:head>

<div class="flex min-h-screen flex-col bg-white text-black">
	<header class="border-b border-black">
		<nav class="mx-auto flex w-full max-w-3xl items-center justify-between px-6 py-4">
			<a href="/" class="font-mono text-sm font-bold uppercase tracking-[0.2em]">LES</a>
			<a
				href="/pools/new"
				class="border border-black px-3 py-1.5 text-[10px] font-bold uppercase tracking-widest hover:bg-black hover:text-white"
			>
				New pool
			</a>
		</nav>
	</header>

	<main class="mx-auto w-full max-w-3xl flex-1 px-6 py-10">
		{@render children()}
	</main>

	<footer class="border-t border-black">
		<div
			class="mx-auto flex w-full max-w-3xl items-center justify-between px-6 py-5 font-mono text-[10px] uppercase tracking-widest text-neutral-500"
		>
			<span>LES — prediction pools</span>
			<span>Iteration 0</span>
		</div>
	</footer>
</div>
