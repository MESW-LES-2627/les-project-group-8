"""Business rules for picks."""

from pools.models import PoolStatus
from pools.service import PoolService
from shared.errors import NotFoundError, ValidationError
from shared.validation import require_json_object
from users.models import User

from .models import Pick


class PickService:
    def __init__(self, repository, pools: PoolService):
        self._repository = repository
        self._pools = pools

    def list_picks(self, pool_id, user: User) -> list[Pick]:
        pool = self._pools.get_pool(pool_id)
        if not pool.bets:
            return []
        user_id = user.id if pool.status() == PoolStatus.OPEN else None
        return self._repository.list_picks(tuple(bet.id for bet in pool.bets), user_id)

    def save_pick(self, pool_id, bet_id, payload, user: User) -> Pick:
        payload = require_json_object(payload)

        if "user_id" in payload:
            # The participant is the logged-in User; refuse an id so impersonation is obvious.
            raise ValidationError(
                "Field 'user_id' is not accepted: the participant is the logged-in user."
            )

        try:
            pool = self._pools.get_pool(pool_id)
        except NotFoundError:
            raise ValidationError("Field 'pool_id' must be the id of an existing pool.")

        bet = pool.find_bet(str(bet_id))
        if bet is None:
            raise ValidationError("Field 'bet_id' must be the id of a bet in this pool.")

        if pool.status() != PoolStatus.OPEN:
            raise ValidationError("Picks are closed for this pool.")
        if bet.winning_outcome_id is not None:
            raise ValidationError("Picks are closed for this bet.")

        outcome_id = payload.get("outcome_id")
        if not isinstance(outcome_id, str) or outcome_id not in {
            option.id for option in bet.options
        }:
            raise ValidationError("Field 'outcome_id' must be one of the bet's options.")

        return self._repository.create_or_replace(bet.id, user.id, outcome_id)
