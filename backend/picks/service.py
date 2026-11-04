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

    def get_my_pick(self, pool_id, user: User) -> Pick | None:
        pool = self._pools.get_pool(pool_id)
        return self._repository.get(pool.id, user.id)

    def save_pick(self, pool_id, payload, user: User) -> Pick:
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

        if pool.status() != PoolStatus.OPEN:
            raise ValidationError("Picks are closed for this pool.")

        outcome_id = payload.get("outcome_id")
        if not isinstance(outcome_id, str) or outcome_id not in {
            option.id for option in pool.options
        }:
            raise ValidationError("Field 'outcome_id' must be one of the pool's options.")

        return self._repository.create_or_replace(pool.id, user.id, outcome_id)
