<svelte:head>
	<title>No User for this account · LES</title>
</svelte:head>

<!-- Where Flask's 403 sends people: the token is valid, but its Account has no User. -->
<h1 class="text-3xl font-bold tracking-tight">Your account has no User</h1>
<p class="mt-4 text-sm">
	You are logged in, but the app has no User for your account, so you can't create pools or make
	picks. This should not happen: every account gets a User when it signs up.
</p>
<p class="mt-4 text-sm">
	Log out and sign up again with another email, or ask the team to restore your User.
</p>

<div class="mt-8 flex items-center gap-4 border-t border-black pt-5">
	<form method="POST" action="/logout">
		<button
			type="submit"
			class="border border-black bg-black px-4 py-2 text-sm font-bold text-white hover:bg-white hover:text-black"
		>
			Log out
		</button>
	</form>
	<a href="/" class="text-sm underline">Home</a>
</div>
