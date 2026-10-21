// Mirrors components.schemas in docs/iterations/0/openapi.yaml.

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
	creator: UserSummary;
	decider: UserSummary;
	options: Outcome[];
	winning_outcome_id: string | null;
}

export interface CreatePoolRequest {
	name: string;
	statement: string;
	deadline: string;
	options: [string, string];
}
