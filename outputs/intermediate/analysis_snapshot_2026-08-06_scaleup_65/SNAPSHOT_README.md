# Analysis snapshot -- 2026-08-06 (Persistent scale-up controller, session 3, Batch 10)

## Snapshot date
2026-08-06

## Total promoted companies
**65 of 100** FTSE 100 constituents have a final status of `promoted_complete` or
`completed_null_result` (42 `promoted_complete`, 23 `completed_null_result`).

## New companies completed this batch (5)
- **Investec** (`promoted_complete`) -- 1 confirmed operational use case: Microsoft Copilot for
  Sales, with Investec described as "the very first customer to go live in production" with the
  product, deployed to 900 UK bankers with a further 700-banker rollout underway in South Africa,
  saving an estimated 200 hours/year across the bank. The current-year (FY2025) annual report could
  not be located after a guessed URL 404'd and a follow-up landing-page fetch returned HTTP 403;
  this was recorded as a single pending source rather than a company blocker, since the FY2024
  annual report plus a verified Microsoft technology-partner case study together provided
  substantial evidence (the same pattern used for Schroders in Session 1).
- **DCC plc** (`completed_null_result`) -- notable: DCC's own annual report explicitly states its
  internal AI platform favours "practical, actionable AI solutions...rather than exploratory or
  generative AI technologies," a rare explicit company self-disclaimer against generative AI. One
  governance finding (a "Generative AI applications" acceptable-use policy) was still promoted.
- **Antofagasta plc** (`completed_null_result`) -- all AI mentions are predictive/optimisation
  mining systems (SIRO, Machine Vision, desalination scheduling), not generative.
- **Diploma** (`completed_null_result`) -- only vague general-AI mentions.
- **United Utilities** (`completed_null_result`) -- all AI mentions describe predictive/ML systems
  (Dynamic Network Management, leak-detection sensors).

## Blocked companies (not promoted)
14 companies `blocked_manual_browser` (unchanged this batch), documented with exact manual actions
in `manual_browser_resolution_queue_controller.csv` (30 rows).

## Provisional and confirmed operational-use-case totals
**55 provisional / 50 confirmed**, re-verified directly against `company_summary_template.csv`
row-by-row (65 rows).

## Validation totals
`promoted_data_validation_report.csv` (this snapshot): **0 errors, 2160 warnings, 64 information**
across all 65 promoted/null-result companies.

## Methodological note: partial-source companies
Investec is this project's first company promoted with one of its two required annual reports
unobtainable (recorded as `approval_status=pending` in its source-candidates file, distinct from
`blocked_manual_browser` at the company level). This required a small process correction: the
first real-promotion attempt failed with "BLOCKED: approved candidate has no known downloaded
filename mapping" because the row's `approval_status` was still `approved` despite never being
successfully downloaded. Correcting it to `pending` (the status the promotion script's own logic
already handles gracefully) resolved this without any change to promotion script logic itself.
The company was not treated as blocked because substantial, well-corroborated evidence was
available from its other properly-collected sources -- the same judgment applied to Schroders in
Session 1.

## Suitability of this snapshot
Report drafting may use this snapshot for **updated preliminary findings**, alongside
methodology, coding framework, pilot discussion and limitations sections already supported by
prior snapshots.

**Final FTSE 100-wide conclusions remain premature.** With 65 of 100 constituents at a final
status (plus 14 more known and partially researched but blocked), 21 companies remain entirely
`not_started`. This snapshot still does not constitute a representative sample of the FTSE 100;
sector comparisons and index-wide claims must wait for substantially broader coverage.
