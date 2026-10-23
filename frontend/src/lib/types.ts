export type PoolStatus = 'OPEN' | 'LOCKED' | 'RESOLVED';

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
	winning_outcome_id: string | null;
	creator: UserSummary;
	decider: UserSummary;
	options: Outcome[];
	created_at?: string;
}

export interface CreatePoolInput {
	creator_id: string;
	name: string;
	statement: string;
	deadline: string;
	options: [string, string];
}
