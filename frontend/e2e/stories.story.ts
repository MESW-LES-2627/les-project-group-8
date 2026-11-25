import { test as base, expect, type Browser, type BrowserContextOptions, type Locator, type Page } from '@playwright/test';
import { PASSWORD, signUp, waitForHydration } from './account.ts';
import { addBet, betCard, closePool, createPool, GOALS, pick, pickOutcome, resolve, WINNER, type NewBet } from './pool.ts';

// One test per Done user story with a UI, titled `USn …`: stories.yml turns each recording
// into stories/USn.gif. Obsolete and Later stories get none. Only the page from `record()`
// is filmed; setup by other Users happens off camera, in contexts of their own.
const test = base.extend<{ record: (options?: BrowserContextOptions) => Promise<Page> }>({
	record: async ({ browser }, use, testInfo) => {
		let page: Page | undefined;
		await use(async (options) => {
			const context = await browser.newContext({ ...options, recordVideo: { dir: testInfo.outputPath('video') } });
			page = await context.newPage();
			return page;
		});
		if (!page) return;
		if (testInfo.status !== 'passed') return await page.context().close(); // a failed story stays out of the gallery
		await page.waitForTimeout(1500); // the GIF lingers on the end state before it loops
		await page.context().close();
		await page.video()!.saveAs(`stories/${testInfo.title}.webm`);
	}
});

test.use({ launchOptions: { slowMo: 150 } }); // slow enough for a viewer to follow
test.describe.configure({ timeout: 120_000 });

/** Fixed names, and emails unique to the story, since every test shares one database. */
function people() {
	const id = test.info().title.split(' ')[0].toLowerCase();
	const person = (first: string, name: string) => ({ email: `${first}.${id}@example.test`, name });
	return { ana: person('ana', 'Ana Silva'), ben: person('ben', 'Ben Costa'), cleo: person('cleo', 'Cleo Dias') };
}

/** Runs `act` as a signed-up `account` in a browser of its own, off camera. */
async function offCamera(browser: Browser, account: { email: string; name: string }, act: (page: Page) => Promise<void>) {
	const context = await browser.newContext();
	const page = await context.newPage();
	await signUp(page, account);
	await act(page);
	await context.close();
}

/** Creates a Pool with `bets` and returns its path. */
async function poolWith(page: Page, name: string, bets: NewBet[] = [WINNER, GOALS]): Promise<string> {
	const path = await createPool(page, name, 'Saturday’s derby, before kick-off.');
	for (const bet of bets) await addBet(page, bet);
	return path;
}

/** Scrolls the Leaderboard into view, so the recording ends on it, and returns it. */
async function leaderboard(page: Page) {
	const region = page.getByRole('region', { name: 'Leaderboard' });
	await region.scrollIntoViewIfNeeded();
	return region;
}

const row = (region: Locator, name: string) =>
	region.getByRole('row').filter({ has: region.page().getByRole('rowheader', { name, exact: true }) });

async function open(page: Page, path: string): Promise<void> {
	await page.goto(path);
	await waitForHydration(page);
}

test('US1 Create an account', async ({ record }) => {
	const page = await record();
	await open(page, '/signup');
	await page.getByLabel('Email').fill(people().ana.email);
	await page.getByLabel('Password').fill(PASSWORD);
	await page.getByLabel('Name').fill(' Ana ');
	await page.getByRole('button', { name: 'Sign up' }).click();
	await page.waitForURL('/');
	await expect(page.getByRole('banner').getByText('Ana', { exact: true })).toBeVisible();
});

test('US2 Create a two-option pool', async ({ record }) => {
	const page = await record();
	await signUp(page, people().ana);
	const penalties: NewBet = { statement: 'Will it go to penalties?', options: ['Yes', 'No'], presentation: 'Radio buttons' };
	await poolWith(page, 'Weekend derby', [penalties]);
	await expect(page.getByText('Picks open')).toBeVisible();
	await expect(page.getByText('By Ana Silva')).toBeVisible();
	await expect(betCard(page, penalties.statement).getByRole('radio')).toHaveCount(2);
});

test('US3 See the pools', async ({ record }) => {
	const page = await record();
	await signUp(page, people().ana);
	await closePool(await createPool(page, 'Spring league', 'The older one, already closed.'));
	await createPool(page, 'Autumn cup', 'The newest one, still open.');
	await open(page, '/');
	const card = (name: string) => page.getByRole('article').filter({ has: page.getByRole('heading', { name }) });
	await expect(card('Spring league').getByText('Picks closed')).toBeVisible();
	await expect(card('Autumn cup').getByText('Picks open')).toBeVisible();
	// Other stories' Pools share the list, so only the order of these two is checked.
	const names = await page.getByRole('article').getByRole('heading').allTextContents();
	expect(names.indexOf('Autumn cup')).toBeLessThan(names.indexOf('Spring league'));
});

test('US5 See who I am', async ({ record }) => {
	const page = await record();
	await signUp(page, people().ana);
	await expect(page.getByRole('banner').getByText('Ana Silva')).toBeVisible();
	await page.reload();
	await expect(page.getByRole('banner').getByText('Ana Silva')).toBeVisible();
});

test('US6 Set a deadline in my local time', async ({ record }) => {
	const page = await record({ timezoneId: 'America/New_York' });
	await signUp(page, people().ana);
	await createPool(page, 'Weekend derby', 'Closes at 12:30 in New York.'); // 2030-06-15T12:30 local
	await expect(page.getByText('Deadline 15 Jun 2030, 16:30 UTC')).toBeVisible();
});

test('US7 Share a pool link', async ({ record, browser }) => {
	let link = '';
	await offCamera(browser, people().ana, async (page) => {
		link = await poolWith(page, 'Weekend derby');
	});
	const page = await record(); // a friend who never signed up
	const response = await page.goto('/pools/00000000-0000-0000-0000-000000000000');
	expect(response?.status()).toBe(404);
	await open(page, link);
	await expect(page.getByRole('heading', { name: 'Weekend derby' })).toBeVisible();
	await expect(page.getByText('Log in to save your pick.').first()).toBeVisible();
});

test('US8 Open a single pool', async ({ record }) => {
	const page = await record();
	await signUp(page, people().ana);
	await poolWith(page, 'Derby day');
	await open(page, '/');
	const card = page.getByRole('article').filter({ has: page.getByRole('heading', { name: 'Derby day' }) });
	await card.getByRole('link', { name: 'Open pool' }).click();
	await expect(page.getByRole('heading', { name: 'Derby day' })).toBeVisible();
	await expect(page.getByText('By Ana Silva')).toBeVisible();
	await expect(betCard(page, WINNER.statement).getByRole('radio')).toHaveCount(3);
});

test('US9 See a pool’s status on its page', async ({ record }) => {
	const page = await record();
	await signUp(page, people().ana);
	const path = await poolWith(page, 'Weekend derby', [WINNER]);
	await expect(page.getByText('Picks open')).toBeVisible();
	await closePool(path);
	await open(page, path);
	await expect(page.getByText('Picks closed', { exact: true })).toBeVisible();
	await resolve(page, WINNER.statement, 'Home');
});

test('US10 Pick an outcome', async ({ record }) => {
	const page = await record();
	await signUp(page, people().ana);
	const path = await poolWith(page, 'Weekend derby', [WINNER]);
	await pickOutcome(page, WINNER.statement, 'Home');
	await open(page, path);
	await expect(betCard(page, WINNER.statement).getByText('Saved: Home')).toBeVisible();
});

test('US11 Change my pick before the deadline', async ({ record }) => {
	const page = await record();
	await signUp(page, people().ana);
	const path = await poolWith(page, 'Weekend derby', [WINNER]);
	await pickOutcome(page, WINNER.statement, 'Home');
	await pickOutcome(page, WINNER.statement, 'Away');
	await open(page, path);
	await expect(betCard(page, WINNER.statement).getByText('Saved: Away')).toBeVisible();
});

test('US12 See my own pick', async ({ record }) => {
	const page = await record();
	await signUp(page, people().ana);
	const path = await poolWith(page, 'Weekend derby', [WINNER]);
	await expect(betCard(page, WINNER.statement).getByRole('button', { name: 'Save pick' })).toBeVisible();
	await pickOutcome(page, WINNER.statement, 'Home');
	await closePool(path);
	await open(page, path);
	await expect(betCard(page, WINNER.statement).getByText('Your pick: Home')).toBeVisible();
});

test('US13 Be refused a pick after the deadline', async ({ record }) => {
	const page = await record();
	await signUp(page, people().ana);
	const path = await poolWith(page, 'Weekend derby', [WINNER]);
	await pickOutcome(page, WINNER.statement, 'Home');
	await closePool(path); // while the page still offers the pick
	const card = betCard(page, WINNER.statement);
	await card.getByRole('radio', { name: 'Away' }).check();
	await card.getByRole('button', { name: 'Change pick' }).click();
	await expect(card.getByText('Picks are closed.')).toBeVisible();
	await expect(card.getByText('Your pick: Home')).toBeVisible();
});

test('US15 See everyone’s picks after the deadline', async ({ record, browser }) => {
	const { ana, ben } = people();
	const page = await record();
	await signUp(page, ana);
	const path = await poolWith(page, 'Weekend derby', [WINNER]);
	await pickOutcome(page, WINNER.statement, 'Home');
	await offCamera(browser, ben, async (other) => {
		await open(other, path);
		await pickOutcome(other, WINNER.statement, 'Away');
	});
	await closePool(path);
	await open(page, path);
	const card = betCard(page, WINNER.statement);
	await expect(card.getByRole('region', { name: "Everyone's picks" }).getByRole('listitem')).toHaveCount(2);
	await resolve(page, WINNER.statement, 'Home');
	await expect(card.getByRole('region', { name: "Everyone's picks" }).getByText('Winner')).toBeVisible();
});

test('US16 Not see others’ picks before the deadline', async ({ record, browser }) => {
	const { ana, ben } = people();
	let path = '';
	await offCamera(browser, ana, async (other) => {
		path = await poolWith(other, 'Weekend derby', [WINNER]);
		await pickOutcome(other, WINNER.statement, 'Home');
	});
	const page = await record();
	await signUp(page, ben);
	await open(page, path);
	await pickOutcome(page, WINNER.statement, 'Away');
	await expect(page.getByRole('heading', { name: "Everyone's picks" })).toHaveCount(0);
});

test('US17 Resolve a Bet by choosing the winner', async ({ record }) => {
	const page = await record();
	await signUp(page, people().ana);
	const path = await poolWith(page, 'Weekend derby', [WINNER]);
	await pickOutcome(page, WINNER.statement, 'Home');
	await closePool(path);
	await open(page, path);
	await resolve(page, WINNER.statement, 'Home');
	await expect(page.getByRole('region', { name: 'Correct pickers — Home' })).toContainText('Ana Silva');
});

test('US18 Resolve only as the decider', async ({ record, browser }) => {
	const { ana, ben } = people();
	let path = '';
	await offCamera(browser, ana, async (other) => {
		path = await poolWith(other, 'Weekend derby', [WINNER]);
	});
	await closePool(path);
	const page = await record();
	await signUp(page, ben);
	await open(page, path);
	await expect(page.getByText('Picks closed', { exact: true })).toBeVisible();
	await expect(page.getByRole('button', { name: 'Resolve bet' })).toHaveCount(0);
});

test('US19 Resolve only after the deadline', async ({ record }) => {
	const page = await record();
	await signUp(page, people().ana);
	const path = await poolWith(page, 'Weekend derby', [WINNER]);
	await expect(page.getByRole('button', { name: 'Resolve bet' })).toHaveCount(0);
	await closePool(path);
	await open(page, path);
	await resolve(page, WINNER.statement, 'Home');
});

test('US20 Resolve a Bet only once', async ({ record }) => {
	const page = await record();
	await signUp(page, people().ana);
	const path = await poolWith(page, 'Weekend derby', [WINNER]);
	await closePool(path);
	await open(page, path);
	await resolve(page, WINNER.statement, 'Home');
	await open(page, path);
	await expect(page.getByText('Resolved — winning outcome: Home')).toBeVisible();
	await expect(page.getByRole('button', { name: 'Resolve bet' })).toHaveCount(0);
});

test('US22 See my wins and losses', async ({ record }) => {
	const page = await record();
	await signUp(page, people().ana);
	const path = await poolWith(page, 'Weekend derby');
	await pick(page, 'Home', '2–3');
	await closePool(path);
	await open(page, path);
	await resolve(page, WINNER.statement, 'Home');
	await resolve(page, GOALS.statement, '0–1');
	await expect(row(await leaderboard(page), 'Ana Silva (you)').getByRole('cell')).toHaveText(['1', '1', '1']);
});

test('US23 See the correct pickers on a resolved Bet', async ({ record, browser }) => {
	const { ana, ben, cleo } = people();
	const page = await record();
	await signUp(page, ana);
	const path = await poolWith(page, 'Weekend derby', [WINNER]);
	await pickOutcome(page, WINNER.statement, 'Home');
	await offCamera(browser, ben, async (other) => {
		await open(other, path);
		await pickOutcome(other, WINNER.statement, 'Home');
	});
	await offCamera(browser, cleo, async (other) => {
		await open(other, path);
		await pickOutcome(other, WINNER.statement, 'Away');
	});
	await closePool(path);
	await open(page, path);
	await resolve(page, WINNER.statement, 'Home');
	await expect(page.getByRole('region', { name: 'Correct pickers — Home' }).getByRole('listitem')).toHaveText([
		'Ana Silva',
		'Ben Costa'
	]);
});

test('US24 See another user’s record in a pool', async ({ record, browser }) => {
	const { ana, ben } = people();
	// Ana, the decider, stays logged in off camera to resolve after Ben has picked.
	const anaContext = await browser.newContext();
	const anaPage = await anaContext.newPage();
	await signUp(anaPage, ana);
	const path = await poolWith(anaPage, 'Weekend derby');
	await pick(anaPage, 'Home', '2–3');
	const page = await record();
	await signUp(page, ben);
	await open(page, path);
	await pick(page, 'Away', '2–3');
	await closePool(path);
	await open(anaPage, path);
	await resolve(anaPage, WINNER.statement, 'Home');
	await resolve(anaPage, GOALS.statement, '2–3');
	await anaContext.close();
	await open(page, path);
	await expect(row(await leaderboard(page), 'Ana Silva').getByRole('cell')).toHaveText(['1', '2', '0']);
	await expect(row(await leaderboard(page), 'Ben Costa (you)').getByRole('cell')).toHaveText(['2', '1', '1']);
});

test('US25 Create a pool as a group of Bets', async ({ record }) => {
	const page = await record();
	await signUp(page, people().ana);
	const path = await poolWith(page, 'Weekend derby');
	await pick(page, 'Home', '2–3');
	await open(page, path);
	await expect(betCard(page, WINNER.statement).getByText('Saved: Home')).toBeVisible();
	await expect(betCard(page, GOALS.statement).getByText('Saved: 2–3')).toBeVisible();
});

test('US26 Create a multiple-choice Bet with n options', async ({ record }) => {
	const page = await record();
	await signUp(page, people().ana);
	const scorer: NewBet = {
		statement: 'Who scores first?',
		options: ['Silva', 'Costa', 'Dias', 'Nobody'],
		presentation: 'Radio buttons'
	};
	await poolWith(page, 'Weekend derby', [scorer]);
	await expect(betCard(page, scorer.statement).getByRole('radio')).toHaveCount(4);
	await pickOutcome(page, scorer.statement, 'Dias');
});

test('US27 Display multiple choice as a dropdown', async ({ record }) => {
	const page = await record();
	await signUp(page, people().ana);
	const path = await poolWith(page, 'Weekend derby', [GOALS]);
	await open(page, path);
	const dropdown = betCard(page, GOALS.statement).getByRole('combobox', { name: 'Your pick' });
	await expect(dropdown).toHaveValue('');
	await pickOutcome(page, GOALS.statement, '4 or more');
});

test('US31 See a pool’s leaderboard', async ({ record, browser }) => {
	const { ana, ben, cleo } = people();
	const page = await record();
	await signUp(page, ana);
	const path = await poolWith(page, 'Cup final');
	await pick(page, 'Home', '2–3');
	// After resolving: Ana 2–0, Ben 1–1, Cleo 0–2, so no tie leaves the order to chance.
	await offCamera(browser, ben, async (other) => {
		await open(other, path);
		await pick(other, 'Home', '0–1');
	});
	await offCamera(browser, cleo, async (other) => {
		await open(other, path);
		await pick(other, 'Away', '4 or more');
	});
	await closePool(path);
	await open(page, path);
	await resolve(page, WINNER.statement, 'Home');
	await resolve(page, GOALS.statement, '2–3');
	await expect((await leaderboard(page)).getByRole('rowheader')).toHaveText([
		'Ana Silva (you)',
		'Ben Costa',
		'Cleo Dias'
	]);
});
