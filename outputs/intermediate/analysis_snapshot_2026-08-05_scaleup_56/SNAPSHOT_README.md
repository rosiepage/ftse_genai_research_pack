# Analysis snapshot -- 2026-08-05 (Persistent scale-up controller, session 2, end of session)

## Snapshot date
2026-08-05

## Total promoted companies
**56 of 100** FTSE 100 constituents have a final status of `promoted_complete` or
`completed_null_result` (41 `promoted_complete`, 15 `completed_null_result`).

## New companies completed this session (20)
Processed across 4 batches by the persistent, resumable scale-up controller, resumed cleanly from
the session-1 checkpoint:

- **Batch 5**: Pearson plc, Centrica (`promoted_complete`); Sainsbury's, Smith & Nephew
  (`completed_null_result`); Haleon (`blocked_manual_browser`).
- **Batch 6**: Kingfisher plc (`promoted_complete`); British American Tobacco, Glencore, IHG
  Hotels & Resorts (`completed_null_result`); Computacenter (`blocked_manual_browser`).
- **Batch 7**: Rentokil Initial (`promoted_complete`); Babcock International
  (`completed_null_result`); Associated British Foods, Burberry Group, M&G
  (`blocked_manual_browser`).
- **Batch 8**: Hiscox (`promoted_complete`); JD Sports, Coca-Cola Europacific Partners, Games
  Workshop (`completed_null_result`); IMI (`blocked_manual_browser`).

This session had no interruptions. A pre-existing session-1 checkpoint arithmetic error (the
totals field did not match the length of its own company-name arrays) was found and corrected
during Batch 5 reconciliation, with no changes made to any company's actual research data.

## Blocked companies (not promoted)
13 companies now `blocked_manual_browser`, spanning three distinct blocker categories:
- **Domain-wide HTTP 403**: Lloyds Banking Group, BAE Systems, Sage Group, BP, Compass Group,
  Imperial Brands, Haleon, Associated British Foods, Burberry Group, IMI (carried forward + newly
  blocked this session).
- **Domain-wide timeout**: Computacenter, Unilever.
- **Encrypted-PDF extraction blocker** (new this session): M&G -- both required annual reports
  downloaded successfully as genuine PDFs, but are AES-encrypted and this pipeline's extraction
  tooling cannot decrypt them without an uninstalled Python dependency; installing it was
  deliberately avoided per the project's rule against changing methodology/environment to keep
  automation going.

All 13 are documented with exact manual actions in `manual_browser_resolution_queue_controller.csv`
(28 rows).

## Provisional and confirmed operational-use-case totals
**54 provisional / 49 confirmed**, re-verified directly against `company_summary_template.csv`
row-by-row (56 rows).

## Validation totals
`promoted_data_validation_report.csv` (this snapshot): **0 errors, 1967 warnings, 55 information**
across all 56 promoted/null-result companies.

## Remaining warnings (categories, not exhaustive)
- The large majority are unreviewed staging rows outside each batch's exception-focused review
  scope (blank `reviewer_decision`) -- expected.
- Blank/`unknown` `publication_date` fields where no exact date was confirmed on-page.
- Sources with no promoted finding attached.
- `manual_review_status` interpretive mismatches (information, not error) for most companies.

None of the above are errors; none were suppressed or reclassified to force a pass.

## Recurring methodological note (staging-engine limitation)
As in every batch this session and last, several genuine operational findings (Pearson, Centrica,
Kingfisher, Rentokil, Hiscox) were found only after manually reading full extracted source text,
because the automated staging engine's local-context-window matching had bundled the qualifying
evidence with vaguer, unrelated, or navigation-boilerplate content in a single staging row. This is
the same known, previously-documented limitation from every earlier session (first identified with
RELX); no script logic was changed to compensate -- each case was resolved by manual review and
documented in the relevant company's staging-file `reviewer_notes`.

## Two notable close-call null results this session
- **IHG Hotels & Resorts**: a detailed, live-beta "AI Conversational Search" feature and a named
  "IHG app in ChatGPT" were both found, but neither alone satisfied both the explicit-GenAI-language
  and concrete-task requirements together -- coded a genuine null result.
- **JD Sports**: a concrete, named-platform (Copilot/Gemini/ChatGPT) agentic-commerce announcement
  via commercetools, but explicitly future-tense and not yet live -- coded a planned strategic
  finding rather than operational.

Both are documented in detail in their respective batch summaries and `source_manifest.csv` notes,
and illustrate the project's consistent standard: explicit GenAI language AND a concrete, evidenced
task/deployment stage are both required before a use case is counted as operational.

## Suitability of this snapshot
Report drafting may use this snapshot for **updated preliminary findings**, alongside
methodology, coding framework, pilot discussion and limitations sections already supported by
prior snapshots.

**Final FTSE 100-wide conclusions remain premature.** With 56 of 100 constituents at a final
status (plus 13 more known and partially researched but blocked), 31 companies remain entirely
`not_started`. This snapshot still does not constitute a representative sample of the FTSE 100;
sector comparisons and index-wide claims must wait for substantially broader coverage.
