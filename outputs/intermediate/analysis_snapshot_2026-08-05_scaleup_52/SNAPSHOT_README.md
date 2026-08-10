# Analysis snapshot -- 2026-08-05 (Persistent scale-up controller, session 2, Batch 7)

## Snapshot date
2026-08-05

## Total promoted companies
**52 of 100** FTSE 100 constituents have a final status of `promoted_complete` or
`completed_null_result` (40 `promoted_complete`, 12 `completed_null_result`).

## New companies completed this batch (5)
- **Rentokil Initial** (`promoted_complete`) -- 1 confirmed operational use case: Google Gemini AI
  rolled out as an integrated Google Workspace productivity tool to the entire c.63,400-strong
  global workforce, with over one million uses recorded in the first six months. Split out from a
  staging row that also described a distinct, not-yet-live in-house "AI Portal"/RatGPT agent
  platform (c.100 agents "in development"), captured separately as a strategic finding; a
  computer-vision rodent-detection tool (PestConnect Optix) was correctly left unclassified as
  predictive AI rather than generative. 3 governance findings also promoted.
- **Babcock International** (`completed_null_result`) -- only general AI-ethics governance
  discussion and a predictive/ML supply-chain monitoring tool found, no operational use case.
- **Associated British Foods** (`blocked_manual_browser`) -- both required annual reports confirmed
  HTTP 403 Forbidden on abf.co.uk (download script + direct WebFetch retry).
- **Burberry Group** (`blocked_manual_browser`) -- same domain-wide HTTP 403 pattern on
  burberryplc.com. Notable: a third-party industry-awards writeup (DataIQ) describes a named
  generative-AI clientelling platform, "Penguin", but this was NOT used as evidence per the rule
  against third-party-media snippets -- it remains an unconfirmed lead pending manual access.
- **M&G** (`blocked_manual_browser`) -- a new blocker category: both required annual reports
  downloaded successfully as genuine PDFs but are AES-encrypted, and this pipeline's extraction
  stage cannot decrypt them without a Python dependency not installed in this environment (and
  deliberately not installed automatically, per the project's own script design and its rule
  against changing methodology/environment merely to keep automation going).

## Blocked companies (not promoted)
12 companies now `blocked_manual_browser`: **Lloyds Banking Group, BAE Systems, Unilever, Sage
Group, BP, Compass Group, Imperial Brands, Haleon, Computacenter** (carried forward) and
**Associated British Foods, Burberry Group, M&G** (newly blocked this batch). All 12 are
documented with exact manual actions in `manual_browser_resolution_queue_controller.csv` (26 rows).

## Provisional and confirmed operational-use-case totals
**52 provisional / 47 confirmed**, re-verified directly against `company_summary_template.csv`
row-by-row (52 rows).

## Validation totals
`promoted_data_validation_report.csv` (this snapshot): **0 errors, 1875 warnings, 51 information**
across all 52 promoted/null-result companies.

## Recurring methodological note (staging-engine limitation)
Rentokil's Gemini AI finding was found only after manually reading the full extracted source text,
because the automated staging engine had bundled it with a distinct, not-yet-live initiative in a
single over-consolidated passage -- the same recurring local-context-window limitation seen in
every earlier batch (first identified with RELX).

## Methodological note: third-party evidence and encrypted-PDF blockers
Two new blocker/evidence patterns emerged this batch, both handled conservatively:
- Burberry's "Penguin" platform is described only by third-party industry media (DataIQ), never by
  Burberry itself or a technology-partner case study in the sources collected so far -- consistent
  with the project's rule against treating search-result/third-party-media snippets as final
  evidence, this was left undocumented as a coded finding and instead flagged as an unconfirmed
  lead for manual follow-up.
- M&G's annual reports are AES-encrypted PDFs that download correctly but cannot be text-extracted
  by this pipeline's tooling (pypdf without the `cryptography` package). This is a genuine, novel
  blocker category (extraction-stage, not download-stage) and was resolved the same way as other
  access blockers -- by stopping and documenting rather than by installing new dependencies to
  route around it.

## Suitability of this snapshot
Report drafting may use this snapshot for **updated preliminary findings**, alongside
methodology, coding framework, pilot discussion and limitations sections already supported by
prior snapshots.

**Final FTSE 100-wide conclusions remain premature.** With 52 of 100 constituents at a final
status (plus 12 more known and partially researched but blocked), 36 companies remain entirely
`not_started`. This snapshot still does not constitute a representative sample of the FTSE 100;
sector comparisons and index-wide claims must wait for substantially broader coverage.
