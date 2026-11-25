export type PoolStatus = 'OPEN' | 'LOCKED';
export type BetStatus = PoolStatus | 'RESOLVED';
export type BetPresentation = 'radio' | 'dropdown';
/** What kind of answer a Bet accepts; presentation only applies to choice Bets. */
export type AnswerType = 'choice' | 'text';

export interface UserSummary {
	id: string;
	name: string;
}

export interface LeaderboardEntry {
	user: UserSummary;
	wins: number;
	losses: number;
	rank: number;
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
	answer_type: AnswerType;
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

export type CreateBetInput =
	| { answer_type: 'choice'; statement: string; options: string[]; presentation: BetPresentation }
	| { answer_type: 'text'; statement: string };

/** The body of a saved Pick: an Outcome for choice Bets, free text for text Bets. */
export type PickAnswer = { outcome_id: string } | { answer_text: string };

export interface Pick {
	id: string;
	bet_id: string;
	user_id: string;
	user: UserSummary;
	/** Exactly one of these is set, matching the Bet's answer type. */
	outcome_id: string | null;
	answer_text: string | null;
	created_at: string;
}
