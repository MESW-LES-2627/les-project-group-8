/**
 * Seeded by `backend/migrations/001_init.sql` as the Iteration 0 guest user.
 * `POST /api/pools` requires it as `creator_id`; the backend does not supply a default.
 */
export const GUEST_USER_ID = '00000000-0000-0000-0000-000000000001';
