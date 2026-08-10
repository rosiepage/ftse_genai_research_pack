# Analysis snapshot -- 2026-08-05 (Persistent scale-up controller, session 1, end of session)

## Snapshot date
2026-08-05

## Total promoted companies
**42 of 100** FTSE 100 constituents have a final status of `promoted_complete` or
`completed_null_result` (34 `promoted_complete`, 8 `completed_null_result`).

## New companies completed this session (20)
Processed across 4 batches by the new persistent, resumable scale-up controller:

- **Batch 1**: Barclays, Aviva, Severn Trent (`promoted_complete`); Halma plc
  (`completed_null_result`); Compass Group (`blocked_manual_browser`).
- **Batch 2**: Marks & Spencer, Standard Chartered (`promoted_complete`); Prudential plc,
  International Airlines Group (`completed_null_result`); Imperial Brands
  (`blocked_manual_browser`).
- **Batch 3**: NatWest Group, SSE plc, Auto Trader Group, Intertek (`promoted_complete`);
  Persimmon (`completed_null_result`).
- **Batch 4**: Convatec, Entain, Schroders (`promoted_complete`); Anglo American plc, Bunzl
  (`completed_null_result`).

This session survived one interruption ("API Error: Response stalled mid-stream") during Batch 1;
recovery confirmed via checkpoint and dataset-timestamp inspection that no promotion had yet
occurred at that point, so no rework was needed.

## Blocked companies (not promoted)
7 companies remain `blocked_manual_browser`: **Lloyds Banking Group, BAE Systems, Unilever, Sage
Group, BP** (carried forward, unresolved, from earlier loops) and **Compass Group, Imperial
Brands** (newly blocked this session — both show a domain-wide HTTP 403 to automated fetch on
every annual-report download attempt, confirmed after one follow-up search for an alternative
official URL each). All 7 are documented with exact manual actions in
`manual_browser_resolution_queue_controller.csv` (16 rows).

## Provisional and confirmed operational-use-case totals
**48 provisional / 43 confirmed**, re-verified directly against `company_summary_template.csv`
row-by-row (42 rows, sum matches the validation script's independent recomputation exactly).

## Validation totals
`promoted_data_validation_report.csv` (this snapshot): **0 errors, 1517 warnings, 41 information**
across all 42 promoted/null-result companies.

## Remaining warnings (categories, not exhaustive)
- The large majority are unreviewed staging rows outside each batch's exception-focused review
  scope (blank `reviewer_decision`) -- expected, since only operational/borderline-evidence
  clusters were individually reviewed; a representative sample of each company's rejected rows
  was logged for the audit trail rather than every row.
- Blank `publication_date` fields where no exact date was confirmed on-page.
- Sources with no promoted finding attached (including Schroders' two annual-report entries,
  which resolved to an identical JavaScript document-viewer shell rather than genuine distinct
  content -- documented in `source_manifest.csv`'s notes for those two rows).
- `manual_review_status` interpretive mismatches (information, not error) for most companies.

None of the above are errors; none were suppressed or reclassified to force a pass.

## Recurring methodological note (staging-engine limitation)
As in all prior loops, several genuine operational findings this session (Barclays, Aviva,
Standard Chartered, NatWest Group, SSE plc, Auto Trader Group, Intertek, Convatec, Entain,
Schroders) were found only after manually reading full extracted source text, because the
automated staging engine's local-context-window matching had consolidated the genuine evidence
into a single `vague_general_ai_reference` rejected (or, in a few cases, strategic) row. This is
the same known, previously-documented limitation from earlier loops (first identified with
RELX); no script logic was changed to compensate -- each case was resolved by manual review and
documented in the relevant company's staging-file `reviewer_notes`.

## Suitability of this snapshot
Report drafting may use this snapshot for **updated preliminary findings**, alongside
methodology, coding framework, pilot discussion and limitations sections already supported by
prior snapshots.

**Final FTSE 100-wide conclusions remain premature.** With 42 of 100 constituents at a final
status (plus 7 more known and partially researched but blocked), 51 companies remain entirely
`not_started`. This snapshot still does not constitute a representative sample of the FTSE 100;
sector comparisons and index-wide claims must wait for substantially broader coverage.
