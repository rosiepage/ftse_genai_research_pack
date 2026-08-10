# Analysis snapshot -- 2026-08-07 (Persistent scale-up controller, session 3, Batch 11)

## Snapshot date
2026-08-07

## Total promoted companies
**70 of 100** FTSE 100 constituents have a final status of `promoted_complete` or
`completed_null_result` (43 `promoted_complete`, 27 `completed_null_result`).

## New companies completed this batch (5)
- **Spirax Group** (`promoted_complete`) -- 1 confirmed operational use case: "MiM," a
  proprietary, company-developed large language model tool for sales-engineer training and
  productivity, explicitly described using "generative AI" and "large language model" language.
  Piloted with 200 sales colleagues during 2025 (freeing approximately four hours per person per
  week, redeployed into customer-facing activity) and now rolled out to over 1,000 sales
  colleagues as its sector-based content is expanded. Content was fragmented across five
  over-consolidated/duplicate rejected rows spanning both annual reports and consolidated into a
  single operational row per the anti-overconsolidation check. Five genuine
  AI-governance-framework findings were also promoted.
- **Melrose Industries** (`completed_null_result`) -- the current-year (FY2025) annual report
  could not be located (guessed URL 404'd, landing-page fetch 403'd, the only 2025-dated PDF found
  was a 41.7KB RNS notice, far too small to be the full report) and was recorded as a single
  `approval_status=pending` source row rather than a company blocker, the same pattern used for
  Investec in Batch 10. The previous-year annual report contains only ordinary automation/robotics
  mentions.
- **3i** (`completed_null_result`) -- rich engagement with the *topic* of generative AI, including
  a named "Group AI policy," an "AI steering group" formed to assess/select/deploy AI tools, and
  CTO Forum/Board GenAI briefings, but no concrete operational deployment by 3i itself was found.
  One strategic finding was promoted (CTO Forum session explicitly on "enabling generative AI
  adoption in companies").
- **IG Group** (`completed_null_result`) -- a live, customer-facing "AI chatbot" and an
  "AI-powered engagement tool" are described only in generic AI-powered language; no
  generative-AI/LLM/foundation-model/named-product language appears anywhere nearby, confirmed via
  direct grep of the source text -- matches the IHG Hotels & Resorts precedent from Batch 6. Three
  governance findings (AI Governance Committee) and one strategic finding (AI-powered threat
  detection/security operations) were promoted instead.
- **Fresnillo plc** (`completed_null_result`) -- only vague general-AI references (datacentre
  demand commentary, computer-vision driver-fatigue detection, cybersecurity AI/ML monitoring, a
  forward-looking risk-register mention of "Generative Artificial Intelligence" as a named risk
  category rather than a deployed tool) and ordinary automation. One governance finding (Board AI
  training sessions) was promoted.

## Blocked companies (not promoted)
14 companies `blocked_manual_browser` (unchanged this batch), documented with exact manual actions
in `manual_browser_resolution_queue_controller.csv`.

## Provisional and confirmed operational-use-case totals
**56 provisional / 51 confirmed**, re-verified directly against `company_summary_template.csv`
row-by-row (70 rows).

## Validation totals
`promoted_data_validation_report.csv` (this snapshot): **0 errors, 2239 warnings, 69 information**
across all 70 promoted/null-result companies.

## Methodological note: consolidating a fragmented use case
Spirax Group's "MiM" tool was mentioned across five separate rejected staging rows spanning both
annual reports (each individually too fragmentary to code alone, a product of the ±450-character
local-context staging matcher over-consolidating/duplicating passages describing the same
deployment). All five were read directly against the full extracted source text, the richest
single passage (current AR, p.24) was used as the primary evidence quotation, and the other four
were marked `reviewer_decision=correct` with a note explaining their content had moved to the new
operational row -- the same anti-overconsolidation handling used for Investec (Batch 10) and DCC
plc (Batch 10).

## Methodological note: the generic "AI-powered" exclusion boundary
IG Group's chatbot and engagement-tool passages were the second time this project has directly
tested the boundary between "detailed, live AI feature" and "meets Core Rule 3's explicit
generative-AI/LLM/named-product language bar" (the first being IHG Hotels & Resorts in Batch 6).
Both were excluded on the same basis: however specific and customer-facing the feature, generic
"AI-powered"/"AI chatbot" language alone -- confirmed via direct reading of the surrounding source
text, not assumed -- does not meet the bar, regardless of how plausible it is that the underlying
technology is in fact generative.

## Suitability of this snapshot
Report drafting may use this snapshot for **updated preliminary findings**, alongside
methodology, coding framework, pilot discussion and limitations sections already supported by
prior snapshots.

**Final FTSE 100-wide conclusions remain premature.** With 70 of 100 constituents at a final
status (plus 14 more known and partially researched but blocked), 16 companies remain entirely
`not_started`. This snapshot still does not constitute a representative sample of the FTSE 100;
sector comparisons and index-wide claims must wait for substantially broader coverage.
