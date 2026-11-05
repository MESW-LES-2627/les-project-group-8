# Pools contain Bets and share one deadline

For #29, a Pool becomes a container with its own name, description, creator,
decider, creation date and deadline. It is created empty; its creator adds Bets
afterwards. A Bet holds the statement, 2–10 ordered Outcomes, radio/dropdown
presentation and an optional winning Outcome. The Pool's deadline closes Picks
for all its Bets.

Pool is the aggregate root for authoring. Bets and Outcomes stay inside the
existing `pools` module, with changes going through `PoolService`. A Pick remains
in the separate `picks` module and belongs to one User and one Bet. Its service
uses `PoolService` to check the Bet and its Pool; it does not use the pool
repository directly. One Pick per `(bet_id, user_id)` allows independent answers
within the same Pool.

## Considered options

- **Keep Pool as a question:** cannot group several Bets under one event.
- **Introduce Round now:** adds a concept and table that this increment does not
  need. Rounds remain a future design decision.

## Consequences

- Existing Pools keep their IDs and URLs. Each gets one Bet reusing the old ID;
  Outcome and Pick IDs, option order, presentation and results are preserved.
  New Bets have independently generated IDs.
- A winning Outcome belongs to a Bet. It does not resolve the whole Pool.
- New tables follow [ADR 0003](0003-flask-is-the-only-door-to-app-tables.md): RLS
  enabled without policies; Flask enforces access through the current User.
- Apply the migration together with the adapted backend: old pool columns and
  `picks.pool_id` are removed. This schema-only change is not deployed on its own.
- Membership, new question formats, resolution endpoints and the Psycopg work
  in #31 are outside this change.
