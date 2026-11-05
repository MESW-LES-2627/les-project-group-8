export type PoolStatus = 'OPEN' | 'LOCKED';
export type BetStatus = PoolStatus | 'RESOLVED';
export type BetPresentation = 'radio' | 'dropdown';

export interface UserSummary {
	id: string;
	name: string;
}

export interface Outcome {
	id: string;
	label: string;
}

export interface Pool {
	id: string;
	name: string;
	description: string;
	deadline: string;
	status: PoolStatus;
	creator: UserSummary;
	decider: UserSummary;
	bets: Bet[];
	created_at: string;
}

export interface Bet {
	id: string;
	pool_id: string;
	statement: string;
	presentation: BetPresentation;
	winning_outcome_id: string | null;
	options: Outcome[];
	created_at: string;
}

export interface CreatePoolInput {
	name: string;
	description: string;
	deadline: string;
}

export interface CreateBetInput {
	statement: string;
	options: string[];
	presentation: BetPresentation;
}

export interface Pick {
	id: string;
	bet_id: string;
	user_id: string;
	outcome_id: string;
	created_at: string;
}
