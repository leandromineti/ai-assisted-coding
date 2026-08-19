export interface Range {
  start: number;
  end: number;
}

// Parses "a..b" into a Range. Throws on malformed input.
export function parseRange(input: string): Range {
  const m = /^(\d+)\.\.(\d+)$/.exec(input.trim());
  if (!m) throw new Error(`malformed range: ${input}`);
  const start = parseInt(m[1], 10);
  const end = parseInt(m[2], 10);
  if (end < start) throw new Error(`inverted range: ${input}`);
  return { start, end };
}

export function expand(r: Range): number[] {
  const out: number[] = [];
  for (let i = r.start; i < r.end; i++) out.push(i);
  return out;
}
