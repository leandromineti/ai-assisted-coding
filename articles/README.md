# Articles

`created: 2026-08-17`

Public-facing writing drawn from this repo's findings. Drafts live **here**, next to
the evidence, so every claim can carry a repo-relative link while it stabilizes —
methodology rule 4 applied to prose. The personal site gets a copy only when a draft
matures.

## Workflow

1. **Draft here.** One file per article, filename = the intended site slug.
   Frontmatter is exactly the site's schema (`title`, `date`, `description`, `tags`,
   `maturity`, `draft`, `series`, `seriesOrder`) — no repo-only keys, so publishing
   is nearly copy-paste. Keep `draft: true` and `maturity: seed` until published.
2. **Cite inward.** Every empirical claim links to the note, conclusion, ref, or
   experiment it comes from, with its date. A claim that can't be linked doesn't go
   in the article. Numbers are copied from the source file, never from memory.
3. **Publish outward.** When a draft is ready: copy into
   `mineti-dev/src/content/articles/<slug>.md`, rewrite repo-relative links to
   absolute GitHub URLs (`https://github.com/leandromineti/ai-assisted-coding/blob/main/...`),
   set `draft: false`, pick `maturity`, add an OG image if wanted. The repo draft
   stays canonical; site edits flow back here first.
   **Diagrams:** SVGs live in [`img/`](img/) and are embedded with the site's
   `<figure>` convention using relative `src="img/<name>.svg"` (renders on GitHub
   too). At publish time, copy the SVGs to `mineti-dev/public/diagrams/` and rewrite
   `src` to `/diagrams/<name>.svg`. Alt text is a dense descriptive sentence, per
   the site's accessibility convention.
4. **Record it.** Update the status table below (hand-kept — it is tiny and
   article-shaped, not a generated index).

## Rules

- This repo is public-facing (see [`../CLAUDE.md`](../CLAUDE.md)): no private paths,
  no employer references; work-derived observations restated generically.
- Findings keep their dates. "As of 2026-08-17" is load-bearing, not hedging — the
  field drifts monthly and the articles should age honestly.
- n=1 experiments are called probes in prose, exactly as they are in the repo.

## Status

| Article | Series order | Status | Site slug | Last synced |
|---|---|---|---|---|
| [The AI-Coding Stack](the-ai-coding-stack.md) | 1 | draft | `the-ai-coding-stack` | — |
| [Measuring AI-Coding Frameworks](measuring-ai-coding-frameworks.md) | 2 | draft | `measuring-ai-coding-frameworks` | — |

Series: **"AI-Assisted Coding, Measured"** — room for part 3+ as experiments land
(exp-03, the local open-weights arm).
