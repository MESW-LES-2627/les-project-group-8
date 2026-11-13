"""Count resolved picks and assign competition ranks within a pool."""

from picks.service import PickService
from pools.service import PoolService

from .models import LeaderboardEntry


class ScoreService:
    def __init__(self, pools: PoolService, picks: PickService):
        self._pools = pools
        self._picks = picks

    def get_leaderboard(self, pool_id: str) -> list[LeaderboardEntry]:
        pool = self._pools.get_pool(pool_id)
        winners = {bet.id: bet.winning_outcome_id for bet in pool.bets}
        records = {}
        for pick in self._picks.list_all_picks(pool):
            if pick.user_id not in records:
                records[pick.user_id] = LeaderboardEntry(pick.user_id, pick.user.name)
            record = records[pick.user_id]
            winning_outcome_id = winners[pick.bet_id]
            if winning_outcome_id is not None:
                if pick.outcome_id == winning_outcome_id:
                    record.wins += 1
                else:
                    record.losses += 1

        entries = sorted(records.values(), key=lambda entry: (-entry.wins, entry.losses, entry.user_id))
        previous_score = None
        rank = 0
        for position, entry in enumerate(entries, start=1):
            score = (entry.wins, entry.losses)
            if score != previous_score:
                rank = position
            entry.rank = rank
            previous_score = score
        return entries
