/** A text field from a submitted form; '' when missing or a file. */
export function readField(form: FormData, key: string): string {
	const value = form.get(key);
	return typeof value === 'string' ? value : '';
}

export const inputClass =
	'mt-1 w-full border border-black bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-black';
export const labelClass = 'font-mono text-[10px] font-bold uppercase tracking-widest';
export const errorClass = 'mt-1 text-xs font-bold';
export const submitClass =
	'border border-black bg-black px-4 py-2 text-sm font-bold text-white hover:bg-white hover:text-black disabled:cursor-not-allowed disabled:opacity-50';
