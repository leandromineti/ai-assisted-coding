import { Range } from "./parseRange";

export function formatRange(r: Range): string {
  return `${r.start}..${r.end}`;
}

export function formatList(ranges: Range[]): string {
  return ranges.map(formatRange).join(", ");
}
