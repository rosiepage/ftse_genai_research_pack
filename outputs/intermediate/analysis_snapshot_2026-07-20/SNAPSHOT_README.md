# Analysis snapshot -- 2026-07-20

## Snapshot date
2026-07-20

## FTSE 100 constituent snapshot used
`ftse100_constituents_2026-06-19.csv` (100 constituent companies, reflecting the 19 June 2026 index changes).

## Companies currently promoted (8 of 100)
Pilot (completed 2026-07-17):
- AstraZeneca
- Tesco
- BT Group
- Rolls-Royce Holdings

Batch 1 (promoted 2026-07-20, this session):
- Experian
- Rio Tinto
- Admiral Group
- Informa

## Companies not yet processed
91 of the remaining 96 FTSE 100 constituents have not yet entered the pipeline at all (no `01_setup_company.py` run). Shell plc is separately in-progress and incomplete (see below) -- it is not counted among the 8 promoted companies.

## Shell's incomplete status
Shell plc has 3 approved source candidates. Of these:
- 2 downloaded successfully (Annual Report and Accounts 2025; the SparkCognition/Shell generative-AI subsurface-imaging release).
- 1 (Annual Report and Accounts 2024) returned a genuine HTTP 404 on retry -- the recorded direct-download URL is stale, not a transient network issue.

Per the project's processing rule, promotion for Shell does not proceed until all three approved sources download successfully. Shell requires a separate source-resolution task (locating a current, valid direct URL for the 2024 Annual Report) before it can proceed through extraction, screening, staging, review and promotion. No Shell staging or promotion has occurred.

## Provisional and confirmed operational-use-case counts, by promoted company

| Company | Provisional | Confirmed |
|---|---|---|
| AstraZeneca | 6 | 3 |
| Tesco | 2 | 1 |
| BT Group | 4 | 4 |
| Rolls-Royce Holdings | 1 | 1 |
| Experian | 1 | 1 |
| Rio Tinto | 1 | 1 |
| Admiral Group | 0 | 0 |
| Informa | 0 | 0 |
| **Total** | **15** | **11** |

Counts are as recomputed independently by `08_validate_promoted_data.py` on 2026-07-20 and match the stored values in `company_summary_template.csv` for every company -- no correction was required.

## Validation totals
`promoted_data_validation_report.csv` (this snapshot): **0 errors, 216 warnings, 8 information** across all 8 promoted companies.

## Unresolved warnings (categories, not exhaustive)
- **Unresolved staging review** (the large majority of the 216 warnings): most Experian, Rio Tinto, Admiral Group and Informa staging rows outside the exception-focused review clusters still carry a blank `reviewer_decision` (never individually reviewed) -- this is expected; only operational and borderline-evidence clusters were reviewed this round, per the task's exception-focused scope.
- **Legacy `.pdf.pdf` filenames** (AstraZeneca only): retained as warnings, not errors, since they are already referenced by existing promoted data from the pilot phase.
- **Blank `publication_date`**: present for several sources across all companies where no exact date was confirmed on-page -- correctly left blank rather than inferred, per Core Rule 8.
- **Sources with no promoted finding**: several manifest rows (e.g. Experian's AR2026, Rio Tinto's AR2024, Informa's two annual reports/sustainability report) did not yield a promotable finding from the passages reviewed this round -- this reflects the exception-focused review scope, not a defect.
- **`manual_review_status` interpretive mismatch** (information, not warning/error): for AstraZeneca, Experian, Rio Tinto and Admiral Group, the stored `company_summary_template.csv` value (`review_complete`) differs from the validator's own recomputation (`pending_review`), because many rows remain genuinely unreviewed (blank `reviewer_decision`) even though no row is stuck at `needs_more_evidence`. Reported, not forced to agree.

None of the above are errors; none were suppressed or reclassified to force a pass.

## Suitability of this snapshot
This snapshot is suitable for drafting:
- Introduction
- Methodology
- Coding framework
- Pilot discussion
- Preliminary findings
- Limitations

**Final sector comparisons and FTSE 100-wide conclusions must wait for broader scale-up.** With 8 of 100 constituents promoted (and 1 further incomplete), this snapshot supports methodology and preliminary-findings narrative only -- it is not a representative sample of the FTSE 100 and must not be used to draw index-wide or sector-wide conclusions.
