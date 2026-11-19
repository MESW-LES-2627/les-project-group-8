<script lang="ts">
	import type { LeaderboardEntry } from '#lib/types.ts';

	let { entries, currentUserId }: {
		entries: LeaderboardEntry[];
		currentUserId: string | null;
	} = $props();
</script>

<section class="mt-8" aria-labelledby="leaderboard-heading">
	<h2 id="leaderboard-heading" class="text-xl font-bold">Leaderboard</h2>
	{#if entries.length === 0}
		<p class="mt-4 text-sm text-neutral-600">No picks in this pool yet.</p>
	{:else}
		<table class="mt-4 w-full border border-black text-left text-sm">
			<thead class="border-b border-black">
				<tr>
					<th scope="col" class="p-3">Rank</th>
					<th scope="col" class="p-3">Participant</th>
					<th scope="col" class="p-3">Wins</th>
					<th scope="col" class="p-3">Losses</th>
				</tr>
			</thead>
			<tbody>
				{#each entries as entry (entry.user.id)}
					<tr
						class:bg-neutral-200={entry.user.id === currentUserId}
						class:font-bold={entry.user.id === currentUserId}
					>
						<td class="p-3">{entry.rank}</td>
						<th scope="row" class="p-3" class:font-normal={entry.user.id !== currentUserId}>
							{entry.user.name}{entry.user.id === currentUserId ? ' (you)' : ''}
						</th>
						<td class="p-3">{entry.wins}</td>
						<td class="p-3">{entry.losses}</td>
					</tr>
				{/each}
			</tbody>
		</table>
	{/if}
</section>
