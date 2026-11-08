# Prediction Pools

Friends create Pools containing Bets; each person picks one Outcome for each Bet.

## Language

### People

**Account**:
The sign-in identity of a person: the email and password they log in with.
_Avoid_: Login, credentials, auth user

**User**:
The person as the app knows them, with a display name; the one who creates pools and makes picks. Each Account has exactly one User, and each User exactly one Account.
_Avoid_: Profile, application profile, member, player

### Pools

**Pool**:
A container created empty, with a name, description, creator, decider and one shared deadline for its Bets.

**Bet**:
A statement inside a Pool, with 2–10 ordered Outcomes, radio/dropdown presentation and an optional winning Outcome.
_Avoid_: Question

**Pick**:
A User's choice of one Outcome for one Bet. Each User has at most one Pick per Bet.
_Avoid_: Prediction, bet, vote

**Decider**:
The one User of a Pool allowed to resolve its Bets. Today the Decider is always the Pool's creator.
_Avoid_: Judge, admin, owner

**Resolution**:
The Decider's final choice of the winning Outcome for one Bet, made once the Pool deadline has passed. A Bet is resolved at most once. Bets are resolved one by one; a Pool as a whole is never resolved.
_Avoid_: Resolving a pool, settling, result

### Scores

**Record**:
A User's wins and losses over the resolved Bets they picked on within a set of Pools, usually a single Pool: a win when their Pick is the winning Outcome, a loss otherwise. Bets without a Resolution don't count.
_Avoid_: Score, stats

**Leaderboard**:
The Users with a Pick in a Pool, ordered by their Records in that Pool: most wins first, then fewest losses. Users with equal wins and losses share a rank.
_Avoid_: Standings, ranking, results
