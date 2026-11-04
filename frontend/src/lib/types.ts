export type PoolStatus = 'OPEN' | 'LOCKED' | 'RESOLVED';
export type PoolPresentation = 'radio' | 'dropdown';

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
	statement: string;
	deadline: string;
	status: PoolStatus;
	presentation: PoolPresentation;
	winning_outcome_id: string | null;
	creator: UserSummary;
	decider: UserSummary;
	options: Outcome[];
	created_at?: string;
}

export interface CreatePoolInput {
	name: string;
	statement: string;
	deadline: string;
	options: string[];
	presentation: PoolPresentation;
}

export interface Pick {
	id: string;
	pool_id: string;
	user_id: string;
	outcome_id: string;
	created_at: string;
}
