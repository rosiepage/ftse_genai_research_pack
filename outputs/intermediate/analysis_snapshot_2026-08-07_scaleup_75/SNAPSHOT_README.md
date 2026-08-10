# Analysis snapshot -- 2026-08-07 (Persistent scale-up controller, session 3, Batch 12 -- session 3 complete)

## Snapshot date
2026-08-07

## Total promoted companies
**75 of 100** FTSE 100 constituents have a final status of `promoted_complete` or
`completed_null_result` (44 `promoted_complete`, 31 `completed_null_result`).

## New companies completed this batch (5) -- final batch of session 3
- **Metlen Energy & Metals** (`promoted_complete`) -- 1 confirmed operational use case:
  "Avokado CORTEX," a named GenAI digital assistant offered by METLEN's own technology subsidiary
  Avokado (METLEN Group is sole shareholder), operating on top of Avokado's AVOX platform to
  assist B2B customers with energy management and cost budgeting. Explicitly described as "an
  Energy Assistant based on GenAI" and "a smart GenAI CORTEX digital assistant for B2B customers,"
  consistently across both the FY2024 and FY2025 annual reports; content was fragmented across
  four over-consolidated/duplicate rejected rows and consolidated into a single operational row
  (evidence_strength=2_moderate, confidence=medium, given some ambiguity between "offers" and
  "creation...underway" phrasing and no quantified benefit/customer count). One strategic finding
  (GenAI digital assistants integrated into internal Central Functions processes) and two
  governance findings (Sustainability Committee briefed on the "AI Ethics Answers platform") were
  also promoted.
- **Aberdeen Group** (`completed_null_result`) -- all AI mentions are vague/general: predictive
  email-filtering ("deployed AI to client-facing mailboxes to filter requests more efficiently"),
  AI-related market/stock commentary, ordinary automation, and AI risk/governance oversight. One
  governance finding promoted.
- **St. James's Place** (`completed_null_result`) -- "AI tools" that "respond to questions on our
  advice framework" for advisers are described only in generic AI-tools language, with no
  generative-AI/LLM/named-product language anywhere nearby -- matches the IHG Hotels & Resorts
  (batch 6) / IG Group (batch 11) precedent. The FY2024 annual report was only available as
  sectioned component PDFs; the Strategic Report section was used. One governance finding
  promoted.
- **Land Securities** (`completed_null_result`) -- the one named AI product found, Brainbox AI (a
  12-month trial controlling heating/cooling at 80-100 Victoria Street), is predictive
  building-control automation, not generative.
- **Endeavour Mining** (`completed_null_result`) -- AI mentions describe predictive
  exploration-targeting tools; the one "generative AI"/"foundation models" mention describes a
  Non-Executive Director's own outside company (Earth Dynamics.ai), not Endeavour Mining's own
  use -- correctly excluded per Core Rule 1 (unit of analysis is a use case by the company
  itself).

## Blocked companies (not promoted)
14 companies `blocked_manual_browser` (unchanged this session), documented with exact manual
actions in `manual_browser_resolution_queue_controller.csv`.

## Provisional and confirmed operational-use-case totals
**57 provisional / 52 confirmed**, re-verified directly against `company_summary_template.csv`
row-by-row (75 rows).

## Validation totals
`promoted_data_validation_report.csv` (this snapshot): **0 errors, 2326 warnings, 74 information**
across all 75 promoted/null-result companies.

## Session 3 close-out
This snapshot marks the end of session 3's 4-batch/20-company limit (batches 9-12: Airtel Africa,
Beazley, Coca-Cola HBC, Howdens Joinery, Weir Group, Antofagasta plc, DCC plc, Diploma, Investec,
United Utilities, Melrose Industries, Spirax Group, 3i, IG Group, Fresnillo plc, Metlen Energy &
Metals, Aberdeen Group, St. James's Place, Land Securities, Endeavour Mining -- 20 companies
processed, 5 promoted / 15 null-result, 0 newly blocked). Four genuine operational GenAI use cases
were added this session (Investec/Microsoft Copilot for Sales, Spirax Group/MiM, Metlen/Avokado
CORTEX, plus DCC's/IG Group's/3i's/Fresnillo's/Aberdeen's/St. James's Place's governance and
strategic-only findings). One reproducible process lesson was consolidated this session: when a
required source row is genuinely unobtainable but other sources give substantial evidence, mark
that row `approval_status=pending` (not `approved`) rather than treating the company as
`blocked_manual_browser` -- confirmed working correctly for Investec, Melrose Industries, and
implicitly available for any future partial-source company.

## Suitability of this snapshot
Report drafting may use this snapshot for **updated preliminary findings**, alongside
methodology, coding framework, pilot discussion and limitations sections already supported by
prior snapshots.

**Final FTSE 100-wide conclusions remain premature.** With 75 of 100 constituents at a final
status (plus 14 more known and partially researched but blocked), 11 companies remain entirely
`not_started` (Alliance Witan, F&C Investment Trust, Intermediate Capital Group, Lion Finance
Group, LondonMetric Property, Pershing Square Holdings, Polar Capital Technology Trust, Scottish
Mortgage Investment Trust, Segro, Standard Life, Tritax Big Box REIT -- heavily weighted toward
investment trusts and REITs). This snapshot still does not constitute a representative sample of
the FTSE 100; sector comparisons and index-wide claims must wait for substantially broader
coverage, and the investment-trust/REIT sub-sector in particular is entirely unrepresented so far.
