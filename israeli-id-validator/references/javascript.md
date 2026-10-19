# JavaScript / TypeScript Implementation

A port of `scripts/validate_id.py` for browser forms and Node services. It was
cross-checked against the Python script on the golden vectors in
`id-formats.md` plus 300 random 9-digit inputs, with zero mismatches.

```js
// Separators a human or a spreadsheet legitimately puts inside an ID. Soft hyphen,
// zero-width characters, word joiner and the BOM are ignored by the bidi algorithm, so they cannot change
// the displayed digit order and are safe to drop anywhere.
const SEPARATORS = new Set([' ', '-', '\u2010', '\u2011', '\u2013', '\u2014', '\u202f',
  '\u00a0', '\u00ad', '\u200b', '\u200c', '\u200d', '\u2060', '\ufeff']);
// Trimmed from the ENDS only: whitespace and tabs, a CSV line break, the BOM, and LRM/RLM/ALM
// around a number pasted from a Hebrew page. Inside the number they stay errors (a tab is a TSV cell boundary), and
// bidi overrides/isolates are never dropped: '\u202e287654321' displays as 123456782.
const EDGE = /^[ \t\u00a0\r\n\u200b\ufeff\u200e\u200f\u061c]+|[ \t\u00a0\r\n\u200b\ufeff\u200e\u200f\u061c]+$/g;

/** Returns { ok: true, digits } or { ok: false, error }. */
export function parseIsraeliId(raw) {
  // Accept strings only: a Number has already lost its leading zeros.
  if (typeof raw !== 'string') return { ok: false, error: 'not a string' };
  const stripped = [...raw.replace(EDGE, '')].filter((c) => !SEPARATORS.has(c)).join('');
  if (stripped === '') return { ok: false, error: 'empty input' };
  // Literal [0-9], not \p{Nd} and not Number(): ASCII digits only.
  if (!/^[0-9]+$/.test(stripped)) return { ok: false, error: 'non-digit characters' };
  if (stripped.length > 9) return { ok: false, error: 'too long' };
  return { ok: true, digits: stripped.padStart(9, '0') };
}

export function isValidIsraeliId(raw) {
  const parsed = parseIsraeliId(raw);
  if (!parsed.ok) return false;
  const id = parsed.digits;
  if (id === '000000000') return false; // passes the checksum, never a real ID
  let total = 0;
  for (let i = 0; i < 9; i++) {
    let val = Number(id[i]) * (i % 2 === 0 ? 1 : 2);
    if (val > 9) val -= 9; // same as summing the two digits of 10..18
    total += val;
  }
  return total % 10 === 0;
}
```

## Where JavaScript ports usually break

- **Numbers instead of strings.** `Number("012345678")` is `12345678`, and an
  `<input type="number">` or a JSON number column has already dropped the zero.
  Keep the ID a string end to end. The function above rejects a non-string
  rather than guessing.
- **`padStart`, not `parseInt`.** `padStart(9, '0')` is the equivalent of
  Python's `zfill(9)`. Converting through `parseInt` first loses the zeros you
  are trying to restore.
- **`\p{Nd}` matches Arabic-Indic digits.** In JavaScript `\d` is ASCII-only
  even with the `u` flag, but a Unicode property class such as `/\p{Nd}/u`
  accepts `١٢٣`, as Python's `\d` and `str.isdigit()` do. Use the literal class
  `[0-9]`, which says what it means in every language.
- **`replace(/\D/g, '')`.** The same strip-everything bug as in Python: it turns
  `62819482.1` into the valid `628194821`, and it silently deletes Arabic-Indic
  digits instead of rejecting them. Remove only the named separators.
- **Three outcomes, one boolean.** If the form needs to say "this field is
  empty" or "letters are not allowed" rather than "invalid ID", call
  `parseIsraeliId()` first and show its `error`.
