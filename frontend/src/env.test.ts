import { describe, expect, it } from 'vitest';
import { variables } from './env.ts';

// defineEnvVars wraps each schema function as a Standard Schema: a throw becomes `issues`.
const validate = (name: keyof typeof variables, value: string | undefined) =>
	variables[name].schema['~standard'].validate(value);

describe.each(['API_URL', 'SUPABASE_URL'] as const)('%s', (name) => {
	it('keeps only the origin', () => {
		expect(validate(name, 'https://api.example:8443/api/')).toEqual({
			value: 'https://api.example:8443'
		});
	});

	it.each(['', undefined])('is undefined when %j', (value) => {
		expect(validate(name, value)).toEqual({ value: undefined });
	});

	it('rejects a value that is not a URL', () => {
		expect(validate(name, 'not a url')).toEqual({
			issues: [{ message: `${name} is not a valid URL: not a url` }]
		});
	});
});

describe('SUPABASE_PUBLISHABLE_KEY', () => {
	it('is undefined when empty and kept otherwise', () => {
		expect(validate('SUPABASE_PUBLISHABLE_KEY', '')).toEqual({ value: undefined });
		expect(validate('SUPABASE_PUBLISHABLE_KEY', 'sb_publishable_x')).toEqual({
			value: 'sb_publishable_x'
		});
	});
});
