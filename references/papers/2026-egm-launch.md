---
key: 2026-egm-launch
title: "Introducing the Elephant-Goldfish Model plugin: scaling design-driven AI software development"
authors: [Brian Suchy, Jim Quinn, Elise Ewing, Oliver Newth, Dave Rensin]
year: 2026
venue: "Google Open Source Blog"
peer_reviewed: false   # the makers' own launch post for their own plugin; testimony, not a measured result
url: https://opensource.googleblog.com/2026/10/introducing-elephant-goldfish-model-plugin.html
snapshot: https://web.archive.org/web/20261110151642/https://opensource.googleblog.com/2026/10/introducing-elephant-goldfish-model-plugin.html   # an EXISTING capture, not a save-page-now: the live page served this server's IP a CAPTCHA on 2026-11-10. Its body text is byte-identical (whitespace-normalised, 4,739 chars from "Shifting left" to "To get started") to the earliest capture, 20261023071206, so the post was not edited in place between 2026-10-23 and 2026-11-10
kind: method
read_depth: full   # the post body (33 non-blank lines in the local cache, after a one-line source header) read end to end 2026-11-10
retrieved: 2026-11-10
pdf: references/papers/pdf/2026-egm-launch.txt   # extracted page text, gitignored
bears_on: [elephant-goldfish-model, conclusion-6, context_isolation, taxonomy]
verdict: "maker testimony for EGM, confronted at v0.1.1: the design-doc contents hold, the 'strict go/no-go' does not exist (findings can always be proceeded past), 'zero-context' goldfish are reduced-context on the designer's own model, and the post's 'code right the first time' goal is untested by anything the repo ships; bears on conclusion 6 as a design betting on the spec half, not as evidence"
---

# Introducing the Elephant-Goldfish Model plugin (2026-10-22)

`retrieved: 2026-11-10` · `read_depth: full` · [live](https://opensource.googleblog.com/2026/10/introducing-elephant-goldfish-model-plugin.html) · [archived](https://web.archive.org/web/20261110151642/https://opensource.googleblog.com/2026/10/introducing-elephant-goldfish-model-plugin.html)

Text cache (gitignored, not a link): `references/papers/pdf/2026-egm-launch.txt`.

Locators are the post's own section headings. Every `> ` line is one contiguous verbatim span.

## What it does

The launch post for Google's open-sourced EGM plugin, written by five of its makers, one of
whom (Dave Rensin) wrote the essay the methodology comes from. Dated Thursday 2026-10-22: one
day after the repository's first public commit (`096e9ad`, 2026-10-21, "initial open-source
release") and five days before the first tag, `v0.1.0` (2026-10-27). It argues for a design
step before code, describes the elephant/goldfish split, and walks the three skills the post
calls phases. It is a pitch with no numbers in it.

## Design

What the makers say the method is, in their words.

**The two roles** (§ Understanding the Elephant-Goldfish Model):

> The “Elephant” is a context-rich, long-horizon AI session that holds the end-to-end architectural vision and project memory. No code is written here; it is purely dedicated to design, intent, and capturing micro-decisions.

> Conversely, “Goldfish” are stateless, zero-context sessions used strictly to validate specifications. Because they share no “blind spots” with the designer, they act as objective critics, probing for gaps and edge cases.

> The goal of this method is for the AI to correctly produce the code you wanted the first time after you press Enter.

**What the plugin automates** (§ Announcing the open source Elephant-Goldfish Model plugin):

> It automates the orchestration of the EGM lifecycle: managing context transfer between Elephants and Goldfish, facilitating validation loops, and rendering design documents, shifting the developer’s role from micromanager to executive reviewer.

**The three phases** (§ The EGM plugin in a nutshell): `egm-brainstorm` ("a “No Code” rule"),
`egm-draft` (a design document with "a detailed implementation plan that enumerates the
specific files to change"), and `egm-review`, "The Goldfish Protocol", described as "a
three-step validation sequence":

> Comprehension Check: A stateless Goldfish reads the complete design document and must explain the architecture and intent back to the Elephant. If the Goldfish cannot accurately summarize the plan, it indicates the document is ambiguous and requires further drafting.

> Antagonistic Review: Multiple Goldfish instances assume the role of skeptical, antagonistic technical reviewers.

> Implementation Readiness Check: A final Goldfish performs a strict go/no-go check. It verifies that all necessary information—file paths, data structures, and function signatures—is present and unambiguous.

## Numbers worth keeping

None measured. The one quantity is usage testimony, uncheckable from outside:

> Thousands of Googlers use this plugin every day to ship production Google code.

## What it means for this repo

The post is the makers' account of the method; the
[report](../../tools/4-workflow-frameworks/elephant-goldfish-model.md) confronts it claim by
claim against source at `v0.1.1` (§ The launch post, confronted). Three results carry weight:

- **The verification promise is stronger than the mechanism.** "A strict go/no-go check" is, at
  the tag, three reviewers emitting severity findings. Every review gate offers "Proceed" first,
  and after one re-audit the skill records residual findings as accepted trade-offs and
  advances on its own.
- **"Zero-context" means no shared conversation, not no shared context.** Reviewers get
  personas, standards and supplied files; instruction files leak on two hosts by the subject's
  own record; every adapter that names a model inherits the designer's.
- **The stated goal is a testable claim nobody has tested.** "For the AI to correctly produce
  the code you wanted the first time" is exactly the kind of outcome
  [conclusion 6](../../docs/conclusions.md) measured for a different framework and found
  carried by grounding and measured gates rather than spec ceremony. EGM puts its whole
  verification budget on the spec, so the post neither supports nor contradicts conclusion 6;
  it names a bet a preregistered arm could score.

## Limits

- **Maker testimony.** Every claim is the makers' own account of their own product.
- **It describes a pre-release state.** It predates both tags. Where it and the source
  disagree, the [report](../../tools/4-workflow-frameworks/elephant-goldfish-model.md)
  dates the disagreement to `v0.1.1`, not to the post's day.
- **The origin essay was not read.** Both the post and the README cite Dave Rensin's Medium
  essay "Elephants, Goldfish, and the New Golden Age of Software Engineering" as the source
  of the ideas. It is not ingested, so nothing here rests on it (rule 1b: the method's
  rationale, as distinct from the plugin's, was searched only through this post).
- **Read from an archive capture**, because the live page answered this server with a
  CAPTCHA; the capture comparison above is what makes that safe.
