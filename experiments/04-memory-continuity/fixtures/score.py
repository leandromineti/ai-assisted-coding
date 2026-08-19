#!/usr/bin/env python3
"""exp-04 scorer: fails-closed binary key over a quiz-answers JSON.
Usage: score.py <answers.json> <arm-name>  -> writes <arm-name>.scored.json
Success is read from the artifact (rule 5e), never exit status alone."""
import json, re, sys, pathlib, datetime

answers_path, arm = sys.argv[1], sys.argv[2]
key = json.load(open(pathlib.Path(__file__).parent / "answer-key.json"))
raw = open(answers_path).read()
# The model may wrap JSON in prose/fences; extract the first {...} block.
m = re.search(r"\{.*\}", raw, re.DOTALL)
answers = json.loads(m.group(0)) if m else {}
result = {"arm": arm, "scored_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
          "per_question": {}, "score": 0, "answered": 0}
for q, pattern in key.items():
    ans = str(answers.get(q, ""))
    hit = bool(re.search(pattern, ans, re.IGNORECASE)) and ans.strip().upper() != "UNKNOWN"
    result["per_question"][q] = {"answer": ans[:200], "hit": hit}
    result["score"] += int(hit)
    result["answered"] += int(bool(ans.strip()) and ans.strip().upper() != "UNKNOWN")
out = pathlib.Path(answers_path).parent / f"{arm}.scored.json"
json.dump(result, open(out, "w"), indent=2)
print(f"{arm}: {result['score']}/10 hits, {result['answered']}/10 non-UNKNOWN answers -> {out}")
