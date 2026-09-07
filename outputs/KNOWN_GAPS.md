# Known Gaps

This file records project gaps that are known and deliberately deferred, not oversights
discovered later and left unaddressed.

## `outputs/final/` was never assembled

`CLAUDE.md` specifies a `outputs/final/` directory containing six named deliverables:

- `outputs/final/ftse100_genai_use_cases.csv`
- `outputs/final/company_summary.csv`
- `outputs/final/sector_summary.csv`
- `outputs/final/methodology_log.md`
- `outputs/final/manual_validation_sample.csv`
- `outputs/final/figures/`

None of these exist. The directory itself does not exist on disk.

This is not a case of the underlying work being missing — equivalent content exists, but it is
scattered across `outputs/report/` and `outputs/analysis/` rather than assembled into the
structure `CLAUDE.md` specifies:

- The coded use-case dataset lives at the project root (`use_case_dataset_template.csv` and
  related root-level CSVs), not as a cleaned `outputs/final/ftse100_genai_use_cases.csv`.
- Company- and sector-level summary content is reported in prose and tables inside
  `outputs/report/02_results.md` (and the assembled `FTSE100_GenAI_Report_FINAL.md`), not as
  standalone `company_summary.csv` / `sector_summary.csv` files.
- Methodology content lives in `outputs/report/01_methodology_and_limitations.md`, not a separate
  `outputs/final/methodology_log.md`.
- The validation sample is documented in `outputs/analysis/disclosed_use_case_spot_check.md`, not
  as a standalone `outputs/final/manual_validation_sample.csv`.
- No `figures/` directory (charts) has been produced at all, in `outputs/final/` or anywhere else.

**Status: known, deliberately deferred — not a blocker for the current report.** The report in
`outputs/report/` is the primary deliverable and does not depend on `outputs/final/` existing.
Assembling `outputs/final/` to match `CLAUDE.md` (or, alternatively, updating `CLAUDE.md` to
point at where the content actually lives) is a post-publish task, to be picked up separately.
