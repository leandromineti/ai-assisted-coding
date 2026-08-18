# Process instructions: gates

Before declaring the task complete:

1. Write `check.sh`: it runs your CLI against real input files (including every file
   in `samples/`) and asserts expected stdout, stderr, and exit codes.
2. Prove `check.sh` can fail: introduce a deliberate bug, confirm the script fails,
   revert the bug. A check that has never failed proves nothing.
3. Run `check.sh`; fix and re-run until it passes. Record every run and its result in
   `GATELOG.md`.

Do not declare completion until the final `check.sh` run passes.
