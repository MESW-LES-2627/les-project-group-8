<script lang="ts">
	import type { PoolStatus } from '../types';

	let { status }: { status: PoolStatus } = $props();

	const styles: Record<PoolStatus, string> = {
		OPEN: 'bg-black text-white',
		LOCKED: 'bg-white text-black'
	};
</script>

<span
	class="border border-black px-2 py-0.5 font-mono text-[10px] font-bold uppercase tracking-widest {styles[
		status
	]}"
>
	{status === 'OPEN' ? 'Picks open' : 'Picks closed'}
</span>
