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

## A small, identified cluster of use cases missed within already-collected sources

A post-finalization spot-check — prompted by a direct question about whether Vodafone's
"SuperAgent" product was already captured — was extended in two stages: first to the 13 other
press releases that yielded exactly one coded use case, then to all 72 collected annual reports
(current + previous, where available) for the 38 companies with at least one disclosed use case.
Both checks used the same method: a targeted scan for signal phrases ("as well as," "also
launched," "complemented by," "called X," "named X") combined with an explicit generative-AI
signal nearby, followed by a manual read of every hit in context.

**Three confirmed instances were found, across three companies:**

- **SuperAgent (Vodafone Group).** The press release already cited for VOD-UC-001 (SuperTOBi) also
  names SuperAgent, an internal agent-assist tool "based on Microsoft Azure OpenAI's Agent Copilot
  solution" — the same basis on which SuperTOBi itself was coded. Never given its own row.
- **Cora+ (NatWest Group).** NatWest's previous-year annual report (source `NWG-002`, already
  marked `reviewed_evidence_found`) describes Cora+, a customer-facing assistant that "uses
  generative AI to deliver responsive answers within the mobile app and e-banking platforms." The
  only currently-coded NatWest row (NWG-UC-001) came from a separate press release describing a
  different, internal-facing tool (AI Digital Enabler + Microsoft Copilot Chat). Cora+ was never
  coded.
- **EmbaseAI (RELX).** RELX's 2025 Annual Report describes EmbaseAI as "the generative AI-powered
  version of Embase, the leading biomedical database" — distinct from all four already-coded RELX
  rows (legal, pharma-regulatory, clinical, energy/commodities). Never coded.

**This suggests the 58-count is a modest, non-random undercount even among already-captured
companies — not evidence of pervasive miscoding.** The strongest evidence for that distinction is
what *didn't* get added: roughly 20 other candidates surfaced by the same scan were read and
correctly excluded, for reasons that held up consistently across a much larger sample than the
original single-company check —
generic "AI platform"/"AI operating system" language with no explicit generative-AI signal (e.g.
Metlen Energy & Metals' AVOX™, AVOS™, and AVOKADO AI™ sub-brands), forward-looking partnership or
strategic-collaboration announcements rather than described live deployments (e.g. Vodafone's
Google/Gemini partnership extension, AstraZeneca's Modella AI acquisition), training/enablement
mentions describing education *about* a tool rather than the tool's use (e.g. Pearson's Microsoft
Copilot training sessions, RELX's Gen AI Academy for Health), re-mentions of an already-coded tool
in a second source, and — the case worth naming specifically — **Reaxys AI Search (RELX)**, which
sits in the very same sentence as EmbaseAI but is described only as enabling "natural language
discovery," with no explicit generative-AI, LLM, or foundation-model signal anywhere in this
project's RELX sources, including RELX's own dedicated generative-AI strategy page. It was checked
and excluded, not overlooked — a direct illustration that the "AI-powered language alone doesn't
qualify" standard (Methodology 3) held even when a genuinely-qualifying sibling product sat one
sentence away.

**This check was stopped after covering press releases and annual reports for the 38 adopting
companies — the two dominant, already-collected source types.** Technology-partner case studies,
sustainability/ESG reports, and the sources collected for the 49 null-result companies were **not**
re-checked; the 49 null-result question (was something missed entirely, rather than under-split
within an already-coded company) is a different, harder question this check does not answer.

**Status: known, deliberately deferred — not incorporated into current figures.** All three
findings are deliberately **not** incorporated into the live n=58 dataset or any report figure —
doing so would require re-deriving every dependent percentage in the Results and Discussion
sections over a change of this size, which is out of proportion to what a spot-check can justify.
Fully drafted candidate rows for Cora+ and EmbaseAI are preserved in
`outputs/analysis/uncommitted_candidate_rows.md` alongside the existing SuperAgent draft, for a
future dataset revision. (Reaxys AI Search has no candidate row — it was excluded, not deferred.)
This finding is cited as a concrete, named example in the Limitations section of the report (see
`outputs/report/01_methodology_and_limitations.md`, Limitations item 6).
