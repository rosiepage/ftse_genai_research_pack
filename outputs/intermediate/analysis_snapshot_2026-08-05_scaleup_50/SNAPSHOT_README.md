# Analysis snapshot -- 2026-08-05 (Persistent scale-up controller, session 2, Batch 6)

## Snapshot date
2026-08-05

## Total promoted companies
**50 of 100** FTSE 100 constituents have a final status of `promoted_complete` or
`completed_null_result` (39 `promoted_complete`, 11 `completed_null_result`).

## New companies completed this batch (5)
- **Kingfisher plc** (`promoted_complete`) -- 1 confirmed operational use case: Hello Casto, a
  generative-AI DIY assistant built on Kingfisher's proprietary Athena multi-LLM framework,
  launched at Castorama France in 2023 and corroborated as still live via a quantified c.
  500,000-interaction figure in the FY2024-25 Annual Report; 1 governance finding also promoted.
- **British American Tobacco** (`completed_null_result`) -- thorough review found only general
  AI/ML governance discussion, agricultural-prediction tools and portfolio investments in
  AI-related companies; 3 strategic and 10 governance findings promoted.
- **Glencore** (`completed_null_result`) -- every AI mention discussed AI only as an external
  commodity-demand driver or a generic cyber-security risk, never Glencore's own GenAI use.
- **IHG Hotels & Resorts** (`completed_null_result`) -- a detailed live-beta "AI Conversational
  Search" feature and a named "IHG app in ChatGPT" were both found, but neither alone satisfied
  both the explicit-GenAI-language and concrete-task requirements together; 7 strategic findings
  promoted. This is a notable close-call precedent, documented in full in `source_manifest.csv`.
- **Computacenter** (`blocked_manual_browser`) -- both required annual reports timed out on every
  automated fetch attempt against investors.computacenter.com (2 direct WebFetch attempts, 2
  download-script attempts); a corrected redirect URL and a National Storage Mechanism alternative
  were both tried without success.

## Blocked companies (not promoted)
9 companies now `blocked_manual_browser`: **Lloyds Banking Group, BAE Systems, Unilever, Sage
Group, BP, Compass Group, Imperial Brands, Haleon** (carried forward) and **Computacenter** (newly
blocked this batch -- persistent domain-wide timeout, a different failure mode from the HTTP 403
blocks seen elsewhere). All 9 are documented with exact manual actions in
`manual_browser_resolution_queue_controller.csv` (20 rows).

## Provisional and confirmed operational-use-case totals
**51 provisional / 46 confirmed**, re-verified directly against `company_summary_template.csv`
row-by-row (50 rows).

## Validation totals
`promoted_data_validation_report.csv` (this snapshot): **0 errors, 1821 warnings, 49 information**
across all 50 promoted/null-result companies.

## Remaining warnings (categories, not exhaustive)
- The large majority are unreviewed staging rows outside each batch's exception-focused review
  scope (blank `reviewer_decision`) -- expected.
- Blank/`unknown` `publication_date` fields where no exact date was confirmed on-page.
- Sources with no promoted finding attached (e.g. Glencore's two annual reports, which discuss AI
  only as an external market driver rather than Glencore's own use).
- `manual_review_status` interpretive mismatches (information, not error) for most companies.

None of the above are errors; none were suppressed or reclassified to force a pass.

## Recurring methodological note (staging-engine limitation)
Kingfisher's Hello Casto finding was found only after manually reading the full extracted source
text, because the automated staging engine had mis-classified the qualifying press-release passage
as webpage boilerplate (a variant of the same recurring local-context-window limitation seen in
every earlier batch, first identified with RELX) -- no script logic was changed to compensate.

## Methodological note: the IHG null result
IHG Hotels & Resorts is a deliberately close call. Its official press release describes, in real
detail, a live-beta "AI Conversational Search" feature and separately names a live "IHG app in
ChatGPT." Per this project's core rules, a use case may be recorded only where the source
explicitly refers to generative AI, LLMs, foundation models, copilots, or a clearly identified
generative-AI product -- and only where a concrete task, user group and deployment stage are all
evidenced together. The conversational-search feature has task detail but never uses explicit
GenAI/LLM language (only generic "AI-powered"/"AI search"); the ChatGPT mention clears the
explicit-product bar but has no concrete task description beyond context. Neither passage alone
clears both bars, so this was coded a genuine null result rather than operational -- the same
standard applied to Anglo American plc in Session 1.

## Suitability of this snapshot
Report drafting may use this snapshot for **updated preliminary findings**, alongside
methodology, coding framework, pilot discussion and limitations sections already supported by
prior snapshots.

**Final FTSE 100-wide conclusions remain premature.** With 50 of 100 constituents at a final
status (plus 9 more known and partially researched but blocked), 41 companies remain entirely
`not_started`. This snapshot still does not constitute a representative sample of the FTSE 100;
sector comparisons and index-wide claims must wait for substantially broader coverage.
