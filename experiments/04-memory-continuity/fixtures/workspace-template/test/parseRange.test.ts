import { test } from "node:test";
import assert from "node:assert";
import { parseRange, expand } from "../src/parseRange";

test("parses a simple range", () => {
  assert.deepStrictEqual(parseRange("1..5"), { start: 1, end: 5 });
});

test("expands a range", () => {
  assert.deepStrictEqual(expand({ start: 1, end: 4 }), [1, 2, 3]);
});
