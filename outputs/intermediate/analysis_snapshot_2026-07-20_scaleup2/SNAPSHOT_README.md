# Analysis snapshot -- 2026-07-20 (Scale-up Batch Loop 2)

## Snapshot date
2026-07-20

## Companies included
This snapshot covers all 14 companies promoted to date (pilot + Batch 1 + Scale-up Batch Loop 2):

Pilot: AstraZeneca, Tesco, BT Group, Rolls-Royce Holdings
Batch 1: Experian, Rio Tinto, Admiral Group, Informa
Scale-up Batch Loop 2: **Diageo, National Grid plc, Vodafone Group, Legal & General, Reckitt, Croda International**

## Total companies promoted
**14 of 100** FTSE 100 constituents.

## Companies at the approval checkpoint (not promoted)
Unilever, HSBC, Sage Group, BP -- each has 2-3 candidate rows that remain genuinely ambiguous (mostly blocked by repeated HTTP 403 on their own domains: unilever.com, sage.com, bp.com), exceeding the 30% ambiguous-candidate threshold. Each needs a manual-browser verification follow-up, not further automated attempts. None of these four companies' data appears in the main datasets.

## Shell's status
Unchanged from the prior snapshot: 2 of 3 approved sources downloaded; the Annual Report 2024 returned a genuine HTTP 404 (stale URL, not a transient issue). Shell requires a separate source-resolution task and has not entered staging or promotion.

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
| Diageo | 3 | 3 |
| National Grid plc | 0 | 0 |
| Vodafone Group | 2 | 2 |
| Legal & General | 1 | 1 |
| Reckitt | 1 | 1 |
| Croda International | 0 | 0 |
| **Total** | **22** | **20** |

Counts are as recomputed independently by `08_validate_promoted_data.py` on 2026-07-20 and match the stored values in `company_summary_template.csv` for every company -- no correction was required.

## Validation totals
`promoted_data_validation_report.csv` (this snapshot): **0 errors, 381 warnings, 14 information** across all 14 promoted companies.

## Remaining warnings (categories, not exhaustive)
- The large majority of warnings are unreviewed staging rows outside each round's exception-focused review scope (blank `reviewer_decision`) -- expected, since only operational/borderline-evidence clusters were reviewed, not every rejected keyword hit.
- Blank `publication_date` fields where no exact date was confirmed on-page -- correctly left blank rather than inferred.
- Sources with no promoted finding attached (e.g. several annual reports that yielded no qualifying passage this round).
- AstraZeneca's known legacy `.pdf.pdf` filenames (unchanged from prior snapshots).
- `manual_review_status` interpretive mismatch (information, not error) for several companies: stored `review_complete` vs. recomputed `pending_review`, because many rows remain genuinely unreviewed even though none are stuck at `needs_more_evidence`.

None of the above are errors; none were suppressed or reclassified to force a pass.

## Suitability of this snapshot
Report drafting may use this snapshot for **updated preliminary findings**, alongside the sections already supported by the prior snapshot (introduction, methodology, coding framework, pilot discussion, limitations).

**Final FTSE 100-wide conclusions remain premature.** With 14 of 100 constituents promoted (plus 5 more -- Shell, Unilever, HSBC, Sage Group, BP -- known and partially researched but not yet promoted), this snapshot still does not constitute a representative sample of the FTSE 100. Sector comparisons and index-wide claims must wait for substantially broader coverage.
