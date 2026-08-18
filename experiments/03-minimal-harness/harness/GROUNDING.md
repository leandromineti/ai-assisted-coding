# Process instructions: grounding

Before writing any implementation code:

1. Enumerate every file in `samples/` and examine each with real commands (`file`,
   `hexdump`, parsing probes in Python) — never assume a format you have not probed.
2. Record every probe command and its actual output in `MEASUREMENTS.md`.
3. List every behavior decision the tool must make (formats accepted, error handling,
   edge rendering). Resolve each by citing a measurement from `MEASUREMENTS.md`; if a
   decision cannot be resolved by measurement, record it as an explicit assumption.

Do not begin implementation until `MEASUREMENTS.md` exists.
