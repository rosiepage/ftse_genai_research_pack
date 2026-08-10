# Analysis snapshot -- 2026-08-04 (Scale-up Loop 4)

## Snapshot date
2026-08-04

## Total promoted companies
**24 of 100** FTSE 100 constituents.

## New companies promoted this loop (5)
- **Whitbread** (Track A -- completed the original 10-company pilot roster, untouched since Loop 1)
- **Barratt Redrow** (Track A)
- **London Stock Exchange Group** (Track A)
- **Smiths Group** (Track A)
- **British Land** (Track A)

Track B was not restarted this loop (see below); no Track B companies were newly promoted.

## Blocked companies (not promoted)
- **Lloyds Banking Group**: AR2024 pending row is document-location-only (an alternative "Annual Review" PDF was found via search but returned the same site-wide application-error page on retry). Two GenAI press releases (Copilot scaling; AI-powered financial assistant) remain genuinely ambiguous and blocked by the same error.
- **BAE Systems**: both approved annual reports remain blocked by Incapsula bot-protection.
- **Unilever**: two pending GenAI press releases (Google Cloud/Vertex AI partnership; AI product-shoot content creation) blocked by HTTP 403 on unilever.com.
- **Sage Group**: three pending rows (Non-Financial Statement document-location question; Sage Copilot press release; Sage Copilot product page) blocked by HTTP 403 on sage.com.
- **BP**: two pending GenAI rows (Copilot for Microsoft 365; Wells Assistant) blocked by HTTP 403 on bp.com.

All five are documented in `manual_browser_resolution_queue_loop4.csv` (12 rows) with the exact manual action, evidence needed, and any official alternative found. None of these five companies' data appears in the main datasets.

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
| Whitbread | 0 | 0 |
| Barratt Redrow | 0 | 0 |
| London Stock Exchange Group | 2 | 1 |
| Smiths Group | 0 | 0 |
| British Land | 0 | 0 |
| **Total** | **32** | **27** |

Counts are as recomputed independently by `08_validate_promoted_data.py` on 2026-08-04 and match the stored values in `company_summary_template.csv` for every company -- no correction was required this round.

## Validation totals
`promoted_data_validation_report.csv` (this snapshot): **0 errors, 891 warnings, 23 information** across all 24 promoted companies.

## Remaining warnings (categories, not exhaustive)
- The large majority are unreviewed staging rows outside each round's exception-focused review scope (blank `reviewer_decision`) -- expected, since only operational/borderline-evidence clusters were individually reviewed; a representative sample of each company's rejected rows was logged for the audit trail rather than every row.
- Blank `publication_date` fields where no exact date was confirmed on-page -- correctly left blank rather than inferred.
- Sources with no promoted finding attached.
- AstraZeneca's known legacy `.pdf.pdf` filenames (unchanged from prior snapshots).
- `manual_review_status` interpretive mismatches (information, not error) for most companies: stored `review_complete` vs. recomputed `pending_review`, because many rows remain genuinely unreviewed even though none are stuck at `needs_more_evidence`.

None of the above are errors; none were suppressed or reclassified to force a pass.

## Suitability of this snapshot
Report drafting may use this snapshot for **updated preliminary findings**, alongside methodology, coding framework, pilot discussion and limitations sections already supported by prior snapshots.

**Final FTSE 100-wide conclusions remain premature.** With 24 of 100 constituents promoted (plus 5 more -- Lloyds Banking Group, BAE Systems, Unilever, Sage Group, BP -- known and partially researched but not yet promoted), this snapshot still does not constitute a representative sample of the FTSE 100. Sector comparisons and index-wide claims must wait for substantially broader coverage.
