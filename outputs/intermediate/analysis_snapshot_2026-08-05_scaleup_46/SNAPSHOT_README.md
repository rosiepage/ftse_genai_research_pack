# Analysis snapshot -- 2026-08-05 (Persistent scale-up controller, session 2, Batch 5)

## Snapshot date
2026-08-05

## Total promoted companies
**46 of 100** FTSE 100 constituents have a final status of `promoted_complete` or
`completed_null_result` (36 `promoted_complete`, 10 `completed_null_result`).

## New companies completed this session so far (5)
Processed in Batch 5, the first batch of session 2, per the session-2 kickoff instruction to save
a validated snapshot after every completed batch (rather than only every 20 companies, as in
session 1):

- **Pearson plc** (`promoted_complete`) -- 1 confirmed operational use case: Claude and Claude
  Code deployed across engineering and business functions ("to accelerate development and enhance
  productivity and quality"); 18 strategic findings and 28 governance findings also promoted.
- **Centrica** (`promoted_complete`) -- 1 confirmed operational use case: a Microsoft 365 Copilot
  Agent Builder email-compliance-checking agent enabled for all employees ("saving employees
  hundreds of hours a year"); 7 governance findings also promoted.
- **Sainsbury's** (`completed_null_result`) -- both required annual reports downloaded and
  screened directly, zero Stage A hits; only ordinary automation/ML-forecasting and vague
  unqualified AI language found.
- **Smith & Nephew** (`completed_null_result`) -- current-year annual report extracted genuine
  narrative content and was screened/searched for GenAI keywords, finding only general AI/ML/ERP
  language; previous-year source resolved to pure navigation boilerplate (not treated as a
  blocker, since the current-year source gave real substantive coverage).
- **Haleon** (`blocked_manual_browser`) -- both required annual reports confirmed HTTP 403
  Forbidden on haleon.com, even after a corrected direct-PDF URL was located via one follow-up
  search; a genuine domain-wide automated-fetch block.

## Blocked companies (not promoted)
8 companies now `blocked_manual_browser`: **Lloyds Banking Group, BAE Systems, Unilever, Sage
Group, BP, Compass Group, Imperial Brands** (carried forward, unresolved) and **Haleon** (newly
blocked this batch -- domain-wide HTTP 403 on both required annual reports, confirmed after one
follow-up search for an alternative URL). All 8 are documented with exact manual actions in
`manual_browser_resolution_queue_controller.csv` (18 rows).

## Provisional and confirmed operational-use-case totals
**50 provisional / 45 confirmed**, re-verified directly against `company_summary_template.csv`
row-by-row (46 rows).

## Validation totals
`promoted_data_validation_report.csv` (this snapshot): **0 errors, 1677 warnings, 45 information**
across all 46 promoted/null-result companies.

## Remaining warnings (categories, not exhaustive)
- The large majority are unreviewed staging rows outside each batch's exception-focused review
  scope (blank `reviewer_decision`) -- expected, since only operational/borderline-evidence
  clusters were individually reviewed.
- Blank `publication_date` fields where no exact date was confirmed on-page (e.g. the Pearson and
  Centrica technology-partner/press-release sources, dated `unknown`).
- Sources with no promoted finding attached (e.g. Smith & Nephew's two annual-report entries and
  Centrica's previous-year annual report, which contributed no qualifying finding individually).
- `manual_review_status` interpretive mismatches (information, not error) for most companies.

None of the above are errors; none were suppressed or reclassified to force a pass.

## Recurring methodological note (staging-engine limitation)
As in every prior batch, both of this batch's operational findings (Pearson's Claude/Claude Code
deployment, Centrica's email-compliance Copilot agent) were found only after manually reading the
full extracted source text, because the automated staging engine's local-context-window matching
had consolidated the genuine evidence into a single over-consolidated strategic (Pearson) or
rejected (Centrica) row alongside vaguer or still-in-development content. This is the same known,
previously-documented limitation from every earlier batch (first identified with RELX); no script
logic was changed to compensate -- each case was resolved by manual review and documented in the
relevant company's staging-file `reviewer_notes`.

## Suitability of this snapshot
Report drafting may use this snapshot for **updated preliminary findings**, alongside
methodology, coding framework, pilot discussion and limitations sections already supported by
prior snapshots.

**Final FTSE 100-wide conclusions remain premature.** With 46 of 100 constituents at a final
status (plus 8 more known and partially researched but blocked), 46 companies remain entirely
`not_started`. This snapshot still does not constitute a representative sample of the FTSE 100;
sector comparisons and index-wide claims must wait for substantially broader coverage.
