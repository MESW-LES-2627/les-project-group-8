import { expect, test, type Page } from '@playwright/test';
import { createClient } from '@supabase/supabase-js';
import { PASSWORD, logIn, newAccount } from './account.ts';

// Until Resolution has a UI (#73), setup writes the passed deadline, Picks and winning Outcomes
// straight to the database; the browser only reads. playwright.config.ts refuses a non-local
// SUPABASE_URL, so this secret key is always the throwaway stack's (ADR 0005).
declare const process: { env: Record<string, string | undefined> }; // no @types/node here
const db = createClient(process.env.SUPABASE_URL!, process.env.SUPABASE_KEY!, {
	auth: { persistSession: false }
});

/** Throws on a failed write, so a broken setup fails here rather than as a wrong Leaderboard. */
async function write<T>(query: PromiseLike<{ data: T | null; error: unknown }>): Promise<T> {
	const { data, error } = await query;
	if (error) throw error;
	return data!;
}

/** Creates a User through Supabase Auth; the sign-up trigger adds the User row. */
async function seedUser(): Promise<{ id: string; email: string; name: string }> {
	const { email, name } = newAccount();
	const { user } = await write<{ user: { id: string } | null }>(
		db.auth.admin.createUser({ email, password: PASSWORD, email_confirm: true, user_metadata: { name } })
	);
	return { id: user!.id, email, name };
}

/** A Pool whose deadline passed yesterday. */
async function seedPool(creatorId: string): Promise<string> {
	const [pool] = await write(
		db
			.from('pools')
			.insert({
				name: `Pool ${crypto.randomUUID().slice(0, 8)}`,
				description: '',
				deadline: new Date(Date.now() - 86_400_000).toISOString(),
				creator_id: creatorId,
				decider_id: creatorId
			})
			.select('id')
	);
	return pool.id;
}

/** A radio Bet with the given Outcomes; returns each Outcome's id by label. */
async function seedBet(poolId: string, labels: string[]): Promise<{ id: string; outcomes: Record<string, string> }> {
	const [bet] = await write(
		db.from('bets').insert({ pool_id: poolId, statement: 'Who wins?', presentation: 'radio' }).select('id')
	);
	const outcomes = await write(
		db
			.from('outcomes')
			.insert(labels.map((label, position) => ({ bet_id: bet.id, label, position })))
			.select('id, label')
	);
	return { id: bet.id, outcomes: Object.fromEntries(outcomes.map((o) => [o.label, o.id])) };
}

type SeededBet = Awaited<ReturnType<typeof seedBet>>;

async function seedPick(bet: SeededBet, userId: string, label: string): Promise<void> {
	await write(db.from('picks').insert({ bet_id: bet.id, user_id: userId, outcome_id: bet.outcomes[label] }));
}

async function resolve(bet: SeededBet, label: string): Promise<void> {
	await write(db.from('bets').update({ winning_outcome_id: bet.outcomes[label] }).eq('id', bet.id));
}

async function openPoolAs(page: Page, email: string, poolId: string): Promise<void> {
	await page.goto('/login');
	await logIn(page, email);
	await page.waitForURL('/');
	await page.goto(`/pools/${poolId}`);
}

/** Each Leaderboard row as [rank, participant, wins, losses]. */
function leaderboardRows(page: Page): Promise<string[][]> {
	return page
		.getByRole('region', { name: 'Leaderboard' })
		.locator('tbody tr')
		.evaluateAll((rows) => rows.map((row) => [...row.children].map((cell) => cell.textContent!.trim())));
}

test('after the deadline, a User sees every Record, ranked by wins then fewer losses, with ties sharing a rank (24.1, 31.1–31.3)', async ({
	page
}) => {
	const [top, tiedA, tiedB, viewer] = await Promise.all([seedUser(), seedUser(), seedUser(), seedUser()]);
	const poolId = await seedPool(top.id);
	const derby = await seedBet(poolId, ['Home', 'Away']);
	const goals = await seedBet(poolId, ['Yes', 'No']);
	await Promise.all([
		seedPick(derby, top.id, 'Home'),
		seedPick(goals, top.id, 'Yes'),
		seedPick(derby, tiedA.id, 'Home'),
		seedPick(derby, tiedB.id, 'Home'),
		seedPick(derby, viewer.id, 'Home'),
		seedPick(goals, viewer.id, 'No')
	]);
	await Promise.all([resolve(derby, 'Home'), resolve(goals, 'Yes')]);

	await openPoolAs(page, viewer.email, poolId);

	const rows = await leaderboardRows(page);
	expect(rows[0]).toEqual(['1', top.name, '2', '0']);
	// Equal Records share rank 2 in either order; the next rank is 4, not 3.
	expect(rows.slice(1, 3)).toEqual(
		expect.arrayContaining([
			['2', tiedA.name, '1', '0'],
			['2', tiedB.name, '1', '0']
		])
	);
	expect(rows[3]).toEqual(['4', `${viewer.name} (you)`, '1', '1']);
	expect(rows).toHaveLength(4);
});

test('after the deadline, a Pool with no Picks shows an empty Leaderboard (31.4)', async ({ page }) => {
	const viewer = await seedUser();
	const poolId = await seedPool(viewer.id);
	await resolve(await seedBet(poolId, ['Home', 'Away']), 'Home');

	await openPoolAs(page, viewer.email, poolId);

	const leaderboard = page.getByRole('region', { name: 'Leaderboard' });
	await expect(leaderboard.getByText('No picks in this pool yet.')).toBeVisible();
	await expect(leaderboard.getByRole('table')).toBeHidden();
});
