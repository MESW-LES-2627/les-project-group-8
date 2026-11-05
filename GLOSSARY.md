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
