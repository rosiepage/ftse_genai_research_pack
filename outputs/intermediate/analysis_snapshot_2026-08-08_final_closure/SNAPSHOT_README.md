# Analysis snapshot -- 2026-08-08 (Final closure: manual-browser resolution pass complete)

## Snapshot date
2026-08-08

## Total companies at final status
**87 of 100** FTSE 100 constituents have a final status of `promoted_complete` or
`completed_null_result` (47 `promoted_complete`, 40 `completed_null_result`). **13 companies**
remain `blocked_manual_browser` (down from 14). **0 companies are `not_started`.**

## What this pass did
Worked through every row of `manual_browser_resolution_queue_controller.csv` (the existing,
previously-compiled queue) rather than rediscovering sources from scratch. This environment has no
true interactive browser -- only `WebFetch` (an automated fetcher distinct from the pipeline's
Python download script) and `WebSearch`. Every blocked URL was retried via WebFetch; where
WebSearch could plausibly surface an official alternative (e.g. the FCA National Storage Mechanism
for Lloyds), that was also attempted. Results are labelled "fetch-verified," never
"browser-verified," per the project's established capability-honesty convention.

## Newly resolved this pass (1 company)
- **BAE Systems** (`blocked_manual_browser` -> `promoted_complete`) -- the previously-documented
  Incapsula bot-protection block on `investors.baesystems.com` no longer reproduced: both annual
  reports (2025, 2026 currency; 2024) downloaded cleanly via the pipeline's own download script as
  genuine, correctly-sized PDFs (11.5MB and 11.3MB respectively -- not tiny Incapsula
  challenge-page stubs, which is what the prior block looked like). Yielded **3 confirmed
  operational GenAI use cases**, all explicitly naming Large Language Models/generative AI:
  (1) LLM/generative-AI natural-language drone command and self-reconfiguration (2025 AR,
  demonstrated); (2) a "Typhoon AI assistant" -- an LLM trained on aircraft maintenance manuals,
  answering complex maintenance queries (2024 AR, demonstrated); (3) an "operationalised" AI
  system using an LLM trained on nearly a decade of cyber-threat analysis to generate insight for
  customers (2024 AR, live/operational). All three were fragmented across over-consolidated
  rejected staging rows and required manual reading of the full extracted source text to split
  out -- the same recurring staging-engine limitation documented throughout this project. One
  genuine governance finding (BAE's own AI/cyber/data workforce-training investment) also
  accepted.

## Still blocked (13 companies) -- exact status after this pass
Every remaining company was re-attempted this session; all failures are re-confirmed, not assumed.
See `manual_browser_resolution_queue_controller.csv` for the full per-row detail (each row now
carries a dated `2026-08-08 manual-browser resolution pass` note documenting exactly what was
retried and the outcome, appended after the original blocker documentation -- nothing was
overwritten).

- **Lloyds Banking Group** -- all 3 pending rows return a Cloudflare "Error 1007" block page
  (jobs-page redirect, no document content). Searched for an NSM (National Storage Mechanism)
  alternative; confirmed Lloyds filed its 2024 AR there, but the NSM's own search interface is
  JS-driven and not usable via WebFetch/WebSearch, so no direct artefact URL could be located.
- **Unilever** -- both press-release URLs return HTTP 403 Forbidden, domain-wide block persists.
- **Sage Group** -- all 3 pending rows return HTTP 403 Forbidden; could not confirm whether the
  Non-Financial Statement is group-wide or Germany-specific, nor verify Sage Copilot's task/user
  group/deployment stage.
- **BP** -- both press-release URLs return HTTP 403 Forbidden; the "Wells Assistant" lead (the
  highest-value pending BP item, which would clarify whether it is genuinely generative/LLM-based)
  remains unverified.
- **Imperial Brands** -- direct PDF returns HTTP 403; the investor-hub landing page returned a
  bot-challenge stub with no real content.
- **Haleon** -- both annual-report rows return HTTP 403 Forbidden.
- **Computacenter** -- both annual-report rows time out (60s) on WebFetch, consistent with the
  previously-documented persistent domain-wide timeout.
- **Associated British Foods** -- both annual-report rows return HTTP 403 Forbidden.
- **Burberry Group** -- current-year AR returns HTTP 403 Forbidden; could not check for the
  unconfirmed third-party "Penguin" clientelling-platform claim.
- **M&G** -- a genuinely different blocker category, precisely re-diagnosed this pass: both annual
  reports download successfully (the investor-relations page itself loaded fine via WebFetch, no
  403), but are AES-encrypted. A local diagnostic (no new packages installed, per the project's
  environment-stability rule) confirms `pypdf.PdfReader()` raises
  `DependencyError("cryptography>=3.1 is required for AES algorithm")` immediately on open, before
  any page or text access is possible. This is a text-extraction blocker, not an access blocker.
- **IMI** -- a documented nuance this pass: WebFetch's failure mode changed from an implicit block
  to its own 10MB size-limit error, suggesting the connection may no longer be actively blocked by
  imiplc.com's WAF at the network level. However, the project's authoritative collection path
  (`03_download_sources.py`) was re-run this pass and still returns a clean HTTP 403 Forbidden for
  both annual reports -- so IMI remains genuinely inaccessible to this project's automated tooling
  and is kept blocked, not resolved, despite the differing WebFetch behaviour.
- **Coca-Cola HBC** -- both annual-report rows return HTTP 403 Forbidden; could not check for the
  unconfirmed third-party OpenAI/Microsoft energy-consumption claim.

## Provisional and confirmed operational-use-case totals
**63 provisional / 58 confirmed**, re-verified directly against `company_summary_template.csv`
row-by-row (87 rows).

## Validation totals
`promoted_data_validation_report.csv` (this snapshot): **0 errors, 2619 warnings, 86 information**
across all 87 promoted/null-result companies. No duplicate IDs in any of the 6 main datasets. No
`*.partial` or `*.tmp` files remain anywhere in the project. Every one of the 100 FTSE 100
constituents (per `ftse100_constituents_2026-06-19.csv`) has exactly one final status --
independently cross-checked: 87 in `company_summary_template.csv` + 13 in the blocked queue = 100,
with no company missing and no company double-counted.

## Suitability of this snapshot
**This snapshot is suitable for full report drafting and represents the practical end state of
the automated + manual-browser-attempted collection effort.** The 13 remaining blocked companies
require an actual human browser session (not available in this environment) or, for M&G
specifically, either a manual PDF-to-text conversion outside this pipeline or a future session
with the `cryptography` package deliberately added to the environment (a decision for the project
owner, not something this session should do unilaterally). Any FTSE 100-wide summary statistics or
sector comparisons drawn from this dataset should disclose the 13-company gap explicitly rather
than treating the 87-company dataset as fully representative of the index.
