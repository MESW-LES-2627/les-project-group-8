# Prediction Pools

Friends create pools around a yes/no-style statement and each person picks the outcome they think will happen.

## Language

### People

**Account**:
The sign-in identity of a person: the email and password they log in with.
_Avoid_: Login, credentials, auth user

**User**:
The person as the app knows them, with a display name; the one who creates pools and makes picks. Each Account has exactly one User, and each User exactly one Account.
_Avoid_: Profile, application profile, member, player

### Pools

**Pick**:
A User's choice of one outcome in a pool.
_Avoid_: Prediction, bet, vote
