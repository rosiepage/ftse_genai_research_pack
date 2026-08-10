# Analysis snapshot -- 2026-07-20 (Scale-up Loop 3)

## Snapshot date
2026-07-20

## Total promoted companies
**19 of 100** FTSE 100 constituents.

## New companies promoted this loop (5)
- **GSK plc** (Track A)
- **RELX** (Track A)
- **Next plc** (Track A)
- **Shell plc** (Track B -- fully unblocked and resolved this loop)
- **HSBC** (Track B -- fully unblocked and resolved this loop)

## Blocked companies (not promoted)
- **Lloyds Banking Group** (Track A): 2 of 4 candidate rows genuinely ambiguous -- both GenAI press releases return application-error pages on `lloydsbankinggroup.com`.
- **BAE Systems** (Track A): cleared the ambiguity threshold (its one AI lead was fetch-verified and confirmed *not* generative AI), but both approved annual reports are actively blocked at download by Incapsula bot-protection on `baesystems.com`/`investors.baesystems.com`.
- **Unilever, Sage Group, BP** (Track B, carried over from Loop 2): still blocked -- `unilever.com`, `sage.com`, `bp.com` all return HTTP 403 to automated fetch on every remaining pending row, confirmed across repeated attempts and multiple sessions. Each needs an actual human browser session, not further automated retries.

None of these six companies' data appears in the main datasets.

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
| Shell plc | 1 | 1 |
| HSBC | 2 | 2 |
| GSK plc | 1 | 1 |
| RELX | 4 | 4 |
| Next plc | 0 | 0 |
| **Total** | **30** | **26** |

Counts are as recomputed independently by `08_validate_promoted_data.py` on 2026-07-20 and match the stored values in `company_summary_template.csv` for every company -- no correction was required.

## Validation totals
`promoted_data_validation_report.csv` (this snapshot): **0 errors, 776 warnings, 18 information** across all 19 promoted companies.

## Remaining warnings (categories, not exhaustive)
- The large majority are unreviewed staging rows outside each round's exception-focused review scope (blank `reviewer_decision`) -- expected, since only operational/borderline-evidence clusters were reviewed.
- Blank `publication_date` fields where no exact date was confirmed on-page -- correctly left blank rather than inferred.
- Sources with no promoted finding attached.
- AstraZeneca's known legacy `.pdf.pdf` filenames (unchanged from prior snapshots).
- `manual_review_status` interpretive mismatches (information, not error) for most companies: stored `review_complete` vs. recomputed `pending_review`, because many rows remain genuinely unreviewed even though none are stuck at `needs_more_evidence`.

None of the above are errors; none were suppressed or reclassified to force a pass.

## Suitability of this snapshot
Report drafting may use this snapshot for **updated preliminary findings**, alongside methodology, coding framework, pilot discussion and limitations sections already supported by prior snapshots.

**Final FTSE 100-wide conclusions remain premature.** With 19 of 100 constituents promoted (plus 6 more -- Lloyds, BAE, Unilever, Sage, BP, and the still-incomplete original 5-company blocked set overlap -- known and partially researched but not yet promoted), this snapshot still does not constitute a representative sample of the FTSE 100. Sector comparisons and index-wide claims must wait for substantially broader coverage.
