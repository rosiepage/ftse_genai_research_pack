# How Are FTSE 100 Companies Using Generative AI?

This project builds and analyses a dataset of publicly disclosed generative-AI use cases across
the 100 constituents of the FTSE 100 following its 19 June 2026 index reconstitution, covering
disclosures from 1 January 2023 to 14 July 2026. Every use case in the dataset had to meet an
explicit inclusion bar — the source must name generative AI, an LLM or foundation model, or an
unambiguously generative product, or describe generation of text, code, images, or audio through a
clearly identified generative model — so that ordinary predictive AI, automation, and vague "AI"
marketing language are excluded by design, not just in principle.

## Headline findings

- **Adoption is real but concentrated.** 38 of the 100 FTSE 100 constituents (38.0% of the full
  population, or 43.7% of the 87 companies actually reached a research verdict) have disclosed at
  least one qualifying generative-AI use case, for 58 distinct disclosed use cases in total.
- **Most disclosed use cases are already live, not just planned.** 86% of the 58 disclosed use
  cases are already live in some form (45% `live_limited`, 41% `live_scaled`), against only 14%
  still at pilot stage.
- **Adoption is broad but shallow per company.** 68% of adopting companies (26 of 38) disclose
  only a single use case each; the most detailed disclosures come from BT Group and RELX (4 use
  cases each).
- **Measured benefit is disclosed for a minority, and unevenly even within that minority.** Only
  19% of disclosed use cases (11 of 58) carry any quantified benefit figure, and of those 11, only
  8 rest on genuine company-wide operational data — the remaining 3 rest on a single employee
  survey, a single vendor-sourced anecdote, and a vague magnitude estimate, one each. None of the
  11 is independently audited.
- **Unintended consequences are almost entirely undisclosed.** Of 214 sources collected across the
  project, only 1 is a regulatory filing and zero are earnings-call transcripts; no source in the
  entire corpus falls into an incident, complaint, or regulatory-scrutiny category — so this report
  cannot make any reliable aggregate claim about disclosed risk, harm, or governance controls.

**Read the full report:** [`outputs/report/FTSE100_GenAI_Report_FINAL.md`](outputs/report/FTSE100_GenAI_Report_FINAL.md)
*(currently marked in the document itself as a full first draft, provisional pending a final read-through).*

## Methodology and Verification

The dataset was built from a fixed source-discovery process (two annual reports per company plus,
where available, a sustainability report and a targeted keyword search of company and vendor
websites), coded against a controlled-vocabulary schema (deployment stage, orientation, business
function, technology partner, claimed benefit, and evidence strength), and reviewed rather than
accepted automatically — every promoted row required an explicit reviewer decision. Full detail,
including the exact inclusion test and every coding field's definition, is in
[`03_CODING_MANUAL.md`](03_CODING_MANUAL.md) and the Methodology section of the final report.

This project treated its own coding as something to actively audit, not just produce. A random
20-row sample of the 58 disclosed use cases was independently checked against its own supporting
quotation; a full re-check of every "expected"/"observed_unquantified" row against the coding
manual's own definition of "measured" found 10 miscoded rows; and a separate audit of the nine
risk/governance fields found none of 75 "unclear" cells carried a documented rationale. Several
real data-quality issues were caught and corrected this way during drafting — not smoothed over in
the report text, but fixed at the source data and disclosed as corrections in the Methodology
section.

Every wording choice in the final report — including places where a plain restatement of a number
shaded into a more persuasive framing — was self-tested against a "plain fact vs. reader-management"
standard while drafting. The full record of those judgment calls, kept deliberately separate from
the reader-facing report, is in
[`outputs/report/AUDIT_TRAIL_judgment_calls.md`](outputs/report/AUDIT_TRAIL_judgment_calls.md).

## Data Sources & Copyright

This project's dataset was built by reviewing publicly available disclosures from FTSE 100
companies — annual reports, press releases, sustainability reports, and technology-partner case
studies — sourced directly from company and vendor websites. This repository does not republish
source documents; the raw extracted text is excluded (see `.gitignore`). What is published is the
coded dataset and analysis: structured fields plus short cited excerpts, with a source URL for
every entry so any claim can be checked against the original public document.

## Repository structure

```
01_PROJECT_BRIEF.md, 02_DOCUMENT_COLLECTION_GUIDE.md,     Project design documents: population,
03_CODING_MANUAL.md, 04_VALIDATION_PLAN.md, 05_KEYWORDS.txt   inclusion rules, coding schema, search terms
CLAUDE.md                                                  Governing rules for this project
ftse100_constituents_2026-06-19.csv                        Population definition (the 100 constituents)
source_manifest.csv, use_case_dataset_template.csv,        Root datasets: sources logged, coded use
strategic_capability_building_findings.csv,                cases, and adjacent non-use-case findings
governance_and_enablement_findings.csv,
rejected_or_aspirational_findings.csv,
company_summary_template.csv

pipeline/                                                  Extraction and coding pipeline (scripts
  scripts/01_setup_company.py ... 08_validate_...py         01–08), plus table-generation and the
  generate_tables.py, task_suitability.py                   task-suitability classification helper

outputs/
  analysis/            ANALYSIS_MEMO.md and supporting audit files (spot-checks, reachability audit,
                        corpus search strategy, risk-field audit)
  intermediate/        Staging data, candidate passages, and frozen analysis snapshots
  report/              The five drafted report sections, the assembled FTSE100_GenAI_Report_FINAL.md
                        (+ .pdf), and AUDIT_TRAIL_judgment_calls.md
  KNOWN_GAPS.md         Known, deliberately deferred gaps between CLAUDE.md's specified outputs and
                        what has actually been assembled

sources/                Raw downloaded source documents (PDFs/HTML/extracted text). Excluded from
                        git via .gitignore — see Data Sources & Copyright above.
```

## Tools used

Python (pipeline scripts and data processing), [Claude Code](https://claude.com/claude-code)
(Anthropic's CLI agent, used throughout for coding, analysis, verification, and report drafting),
and git (version control).
