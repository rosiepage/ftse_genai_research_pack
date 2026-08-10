# FTSE 100 Generative AI Research Project — Progress Log

Last updated: 2026-08-05

## Persistent scale-up controller — session 1, Batch 1 complete (34 of 100 companies have a final status)

A new persistent, resumable controller began this session, targeting a documented final status
(`promoted_complete`, `completed_null_result`, `blocked_manual_browser`, or
`excluded_with_documented_reason`) for all 100 FTSE 100 constituents, processing in batches of 5,
validating after every batch, and checkpointing to
`outputs/intermediate/master_controller_checkpoint.json` so the session can be safely interrupted
and resumed. The session survived one interruption ("API Error: Response stalled mid-stream")
during Batch 1; recovery confirmed via checkpoint/dataset-timestamp inspection that no promotion
had yet occurred, so the batch resumed from the promotion-configuration step with no rework.

**Batch 1** (5 companies): **Barclays** (1 confirmed operational use case: Microsoft 365 Copilot,
c.100,000 licences bank-wide), **Aviva** (3 confirmed operational use cases: GenAI claims
summarisation tool for 500+ handlers; generative-AI GP-medical-report summarisation tool for
underwriters; Microsoft 365 Copilot Chat/GitHub Copilot company-wide), **Severn Trent** (1
confirmed operational use case: Copilot "which offers the capabilities of GPT-4" for colleagues),
**Halma plc** (`completed_null_result` — no qualifying generative-AI evidence in either annual
report; PeriGen's clinical-decision-support AI is predictive, not generative), and **Compass
Group** (`blocked_manual_browser` — both annual reports return HTTP 403 domain-wide on
compass-group.com, confirmed after one alternative-URL search).

**Recurring staging-engine limitation, same as prior loops**: Barclays, Aviva and Severn Trent
each had genuine, concrete, well-quantified GenAI evidence auto-classified into a single
over-consolidated `vague_general_ai_reference` rejected row by the ±450-char local-context
matcher. All were manually read from the full extracted source text and split into distinct,
individually-sourced operational staging rows before promotion.

Cross-company validation (`08_validate_promoted_data.py`, real run, all 28 promoted companies):
**0 errors, 1077 warnings, 27 information**. No duplicate IDs found in any of the 6 main datasets
(source_manifest, use_case_dataset_template, strategic/governance/rejected findings,
company_summary_template).

**Cumulative operational counts across all 28 promoted companies: 37 provisional / 32 confirmed.**

Batch summary: `outputs/intermediate/scaleup_batch_1_summary.csv`. Manual-browser queue (this
controller session, carrying forward the 5 companies still blocked from Loop 4 plus Compass
Group): `outputs/intermediate/manual_browser_resolution_queue_controller.csv`. Controller
checkpoint: `outputs/intermediate/master_controller_checkpoint.json`.

Status count after Batch 1: 28 `promoted_complete`/`completed_null_result` (24 carried forward +
Barclays, Aviva, Severn Trent, Halma plc), 6 `blocked_manual_browser` (5 carried forward + Compass
Group), 66 `not_started`.

**Batch 2** (5 companies): **Marks & Spencer** (1 confirmed operational use case: Microsoft 365
Copilot for 11,000 store-manager/support-centre licences, authored directly from the full
press-release text after the automated staging engine captured only page boilerplate), **Standard
Chartered** (2 confirmed operational use cases: SC GPT, a bespoke in-house LLM rolled out to
70,000+ employees across 41 markets; GitHub Copilot for developers), **Prudential plc**
(`completed_null_result` — the MedLM/Google Cloud medical-claims tool is explicitly self-described
by the company as a "pilot launch" with a bounded 3-4 month test, so was coded strategic rather
than operational despite one corroborating passage using more definite "launched" language),
**International Airlines Group** (`completed_null_result` — only general AI risk-factor language,
no discrete GenAI task or product found), and **Imperial Brands** (`blocked_manual_browser` — both
annual reports return HTTP 403 domain-wide on imperialbrandsplc.com).

Same recurring staging-engine limitation as Batch 1: Standard Chartered's entire official AI
webpage (26 passages) was auto-consolidated into one rejected row; both SC GPT and GitHub Copilot
were manually split out before promotion. Marks & Spencer's press release was captured only as
page-navigation boilerplate by the automated engine; the operational finding was authored directly
from the full extracted article text.

Cross-company validation (real run, all 32 promoted companies): **0 errors, 1220 warnings, 31
information**. No duplicate IDs found in any of the 6 main datasets.

**Cumulative operational counts across all 32 promoted companies: 40 provisional / 35 confirmed**
(re-verified directly against `company_summary_template.csv`).

Batch summary: `outputs/intermediate/scaleup_batch_2_summary.csv`. Manual-browser queue updated
with Imperial Brands (14 rows total).

Status count after Batch 2: 32 `promoted_complete`/`completed_null_result`, 7
`blocked_manual_browser`, 61 `not_started`.

**Batch 3** (5 companies): **NatWest Group** (1 confirmed operational use case: AI Digital Enabler,
an internal ChatGPT-like platform, plus Microsoft Copilot Chat, rolled out together to 99% of
colleagues), **SSE plc** (1 confirmed operational use case: Nero, a generative-AI customer virtual
assistant built on Microsoft Copilot Studio and Azure OpenAI, handling ~280 conversations/day —
sourced from an official Microsoft technology-partner case study), **Auto Trader Group** (1
confirmed operational use case: Co-Driver/AI Generated Descriptions, an LLM-based vehicle-listing
product, with the Board's own risk disclosure confirming real-time LLM use), **Intertek** (1
confirmed operational use case found during the anti-overconsolidation check: Intertek People
Assurance's partnership with Synthesia, a named generative-AI video platform, for client
training-video creation — distinct from Intertek's separate general-AI assurance/certification
service line, which was correctly excluded), and **Persimmon** (`completed_null_result` — zero
Stage A hits in either annual report, genuine no-disclosure company).

Same recurring staging-engine limitation as Batches 1–2: NatWest's press release and SSE's
technology-partner case study were both captured only as page-navigation boilerplate by the
automated engine; both operational findings were authored directly from the full extracted text.

Cross-company validation (real run, all 37 promoted companies): **0 errors, 1419 warnings, 36
information**. No duplicate IDs found in any of the 6 main datasets.

**Cumulative operational counts across all 37 promoted companies: 44 provisional / 39 confirmed**
(re-verified directly against `company_summary_template.csv`).

Batch summary: `outputs/intermediate/scaleup_batch_3_summary.csv`.

Status count after Batch 3: 37 `promoted_complete`/`completed_null_result`, 7
`blocked_manual_browser`, 56 `not_started`.

**Batch 4** (5 companies, the last batch of this session): **Convatec** (1 confirmed operational
use case: Microsoft Copilot and Synthesia, both named as part of an "enterprise-scale" AI
deployment), **Entain** (1 confirmed operational use case: SportingBOT, a named generative-AI
chatbot/personalised betting assistant that reached over 65,000 users in Brazil — judged
operational rather than merely a pilot because it is already serving real customers at quantified
scale, despite the company's own "pilot-then-scale" framing), **Schroders** (2 confirmed
operational use cases: GAiiA, a Generative AI Investment Analyst used in 40+ private-equity
investment cases, and Genie, a GPT-based internal assistant used by 1,000+ colleagues daily
globally — both annual-report sources resolved to an identical JavaScript document-viewer shell
with zero screening hits, so both findings came entirely from a separately fetch-verified press
release), **Anglo American plc** (`completed_null_result` — a genuine explicit generative-AI
mention was found but coded strategic, not operational, since no specific named tool, user group
or deployment stage was confirmed), and **Bunzl** (`completed_null_result` — only a thin
GenAI-tool-use governance policy mention, no operational use case).

Same recurring staging-engine limitation as Batches 1–3: Convatec's Microsoft Copilot/Synthesia
mention and Schroders' GAiiA/Genie mentions were both found via the anti-overconsolidation check
inside over-consolidated strategic/rejected staging rows.

Cross-company validation (real run, all 42 promoted companies): **0 errors, 1517 warnings, 41
information**. No duplicate IDs found in any of the 6 main datasets.

**Cumulative operational counts across all 42 promoted companies: 48 provisional / 43 confirmed**
(re-verified directly against `company_summary_template.csv`).

Batch summary: `outputs/intermediate/scaleup_batch_4_summary.csv`.

Status count after Batch 4 (end of controller session 1 — 20 companies processed this session,
the session limit): 42 `promoted_complete`/`completed_null_result`, 7 `blocked_manual_browser`, 51
`not_started`. The full FTSE 100 study remains **not complete**.

## Persistent scale-up controller — session 2, Batch 5 complete (46 of 100 companies have a final status)

Controller resumed cleanly from `master_controller_checkpoint.json` at the start of session 2.
Verified session 1's stated end-state (42 companies with final status, 0 validation errors, no
duplicate IDs) against live files before starting new work.

**Batch 5** (5 companies): **Pearson plc** (1 confirmed operational use case: Claude and Claude
Code deployed across engineering and business functions "to accelerate development and enhance
productivity and quality" — split out from an over-consolidated strategic staging row via the
anti-overconsolidation check; 18 further strategic findings and 28 governance findings promoted),
**Centrica** (1 confirmed operational use case: a Microsoft 365 Copilot Agent Builder
email-compliance-checking agent enabled for all employees, "saving employees hundreds of hours a
year" — split out from an over-consolidated rejected staging row; two further agents in the same
source were explicitly still in development and excluded; 7 governance findings promoted),
**Sainsbury's** (`completed_null_result` — both required annual reports downloaded and screened
directly with zero Stage A hits; only ordinary automation/ML-forecasting and vague unqualified AI
language found), **Smith & Nephew** (`completed_null_result` — current-year annual report
extracted genuine narrative content and was screened/searched for GenAI keywords, finding only
general AI/ML/ERP language; the previous-year source resolved to pure navigation boilerplate but
this was not treated as a blocker since the current-year source gave real substantive coverage),
and **Haleon** (`blocked_manual_browser` — both required annual reports confirmed HTTP 403
Forbidden on haleon.com even after a corrected direct-PDF URL was located via one follow-up
search; a genuine domain-wide automated-fetch block, the same pattern as Sage Group/BP/Compass
Group/Imperial Brands).

Same recurring staging-engine limitation as every prior batch: Pearson's Claude/Claude Code
mention and Centrica's email-compliance-agent mention were both found via the anti-
overconsolidation check inside over-consolidated strategic/rejected staging rows.

Cross-company validation (real run, all 46 promoted/null-result companies): **0 errors, 1677
warnings, 45 information**. No duplicate IDs found in any of the 6 main datasets.

**Cumulative operational counts across all 46 promoted companies: 50 provisional / 45 confirmed**
(re-verified directly against `company_summary_template.csv`).

Batch summary: `outputs/intermediate/scaleup_batch_5_summary.csv`.

Status count after Batch 5: 46 `promoted_complete`/`completed_null_result`, 8
`blocked_manual_browser`, 46 `not_started`. The full FTSE 100 study remains **not complete**.

## Persistent scale-up controller — session 2, Batch 6 complete (50 of 100 companies have a final status)

**Batch 6** (5 companies): **Kingfisher plc** (1 confirmed operational use case: Hello Casto, a
generative-AI DIY assistant built on Kingfisher's proprietary Athena multi-LLM framework, launched
at Castorama France in 2023 and still live per a quantified c. 500,000-interaction figure in the
FY2024-25 Annual Report — split out from a staging row the automated engine had mis-routed to
rejected as webpage boilerplate; 1 governance finding also promoted), **British American Tobacco**
(`completed_null_result` — thorough review found only general AI/ML governance discussion,
agricultural-prediction tools and portfolio investments in AI-related companies, no operational
use case; 3 strategic and 10 governance findings promoted), **Glencore**
(`completed_null_result` — every AI mention discussed AI only as an external commodity-demand
driver or a generic cyber-security risk, never Glencore's own GenAI use), **IHG Hotels & Resorts**
(`completed_null_result` — a detailed "AI Conversational Search" feature and a separately-mentioned
"IHG app in ChatGPT" were both found, but neither alone satisfied both the explicit-GenAI-language
and concrete-task requirements together, so this was judged a genuine null result rather than
operational, consistent with the project's precedent for close-but-not-qualifying evidence; 7
strategic findings promoted), and **Computacenter** (`blocked_manual_browser` — both required
annual reports timed out on every automated fetch attempt against investors.computacenter.com,
including two direct WebFetch attempts and two download-script attempts; a corrected redirect URL
and a National Storage Mechanism alternative were both tried without success).

Same recurring staging-engine limitation as every prior batch: Kingfisher's Hello Casto mention was
found via the anti-overconsolidation check inside a staging row mis-classified as webpage
boilerplate rather than genuine content.

Cross-company validation (real run, all 50 promoted/null-result companies): **0 errors, 1821
warnings, 49 information**. No duplicate IDs found in any of the 6 main datasets.

**Cumulative operational counts across all 50 promoted companies: 51 provisional / 46 confirmed**
(re-verified directly against `company_summary_template.csv`).

Batch summary: `outputs/intermediate/scaleup_batch_6_summary.csv`.

Status count after Batch 6: 50 `promoted_complete`/`completed_null_result`, 9
`blocked_manual_browser`, 41 `not_started`. The full FTSE 100 study remains **not complete**.

## Persistent scale-up controller — session 2, Batch 7 complete (52 of 100 companies have a final status)

**Batch 7** (5 companies): **Rentokil Initial** (1 confirmed operational use case: Google Gemini AI
rolled out as an integrated Google Workspace productivity tool to the entire c.63,400-strong global
workforce, with over one million uses recorded in six months — split out from an over-consolidated
staging row that also described a distinct, not-yet-live in-house "AI Portal"/RatGPT agent platform
(c.100 agents "in development"), which was re-captured separately as a strategic finding since it
is not yet operational; a computer-vision rodent-detection tool, PestConnect Optix, was correctly
left unclassified as predictive AI rather than generative; 3 governance findings also promoted),
**Babcock International** (`completed_null_result` — only general AI-ethics governance discussion
and a predictive/ML supply-chain monitoring tool found, no operational use case), and three
`blocked_manual_browser` companies: **Associated British Foods** and **Burberry Group** (both
confirmed HTTP 403 domain-wide on their respective official domains, the same pattern as several
earlier companies this session — Burberry's block is notable because a third-party industry-awards
writeup, not usable as evidence, describes a specific named generative-AI platform, "Penguin", that
remains an unconfirmed lead pending manual access) and **M&G** (a new blocker category: both
required annual reports downloaded successfully as genuine PDFs but are AES-encrypted, and this
pipeline's extraction stage cannot decrypt them without a Python dependency that is not installed
and was not installed automatically, per the project's rule against changing methodology/
environment merely to keep automation going).

Same recurring staging-engine limitation as every prior batch: Rentokil's Gemini AI mention was
found via the anti-overconsolidation check inside a staging row that bundled it with a distinct,
not-yet-live initiative.

Cross-company validation (real run, all 52 promoted/null-result companies): **0 errors, 1875
warnings, 51 information**. No duplicate IDs found in any of the 6 main datasets.

**Cumulative operational counts across all 52 promoted companies: 52 provisional / 47 confirmed**
(re-verified directly against `company_summary_template.csv`).

Batch summary: `outputs/intermediate/scaleup_batch_7_summary.csv`.

Status count after Batch 7: 52 `promoted_complete`/`completed_null_result`, 12
`blocked_manual_browser`, 36 `not_started`. The full FTSE 100 study remains **not complete**.

## Persistent scale-up controller — session 2, Batch 8 complete (56 of 100 companies have a final status — session limit reached)

**Batch 8** (5 companies, the last batch of session 2): **Hiscox** (2 confirmed operational use
cases: a Google Cloud Gemini-powered lead underwriting model for the London Market sabotage/
terrorism line, live since August 2024 and cutting submission-to-quote time from 3 days to 3
minutes, split out from a staging row that had only captured the source press release's navigation
boilerplate; and Microsoft 365 Copilot rolled out to 3,000+ employees across 14 countries for
claims handling, cutting claim-detail capture time from up to an hour to as little as 10 minutes;
3 strategic and 5 governance findings also promoted), **JD Sports** (`completed_null_result` — an
official press release describes a concrete, named-platform agentic-commerce announcement via
Microsoft Copilot, Google Gemini and OpenAI ChatGPT, but is explicitly future-tense throughout and
not yet live, so it was coded as a planned strategic finding rather than operational), **Coca-Cola
Europacific Partners** (`completed_null_result` — only predictive/IoT AI and general Responsible-AI
governance language found; a third-party trade-media claim about an AI translation tool was
checked directly against the source text and not found, so not used as evidence), **Games
Workshop** (`completed_null_result` — no generative-AI evidence in either annual report; a
third-party report that the CEO has stated a policy against generative AI was not locatable in
this company's required source set and is not coded as a finding), and **IMI**
(`blocked_manual_browser` — both required annual reports returned HTTP 403 on the download script;
a WebFetch retry did not reproduce the 403 but instead hit the fetch tool's own size limit, so
accessibility could not be independently confirmed).

Same recurring staging-engine limitation as every prior batch: Hiscox's Gemini underwriting
finding was found via the anti-overconsolidation check inside a staging row that had captured only
page-navigation boilerplate rather than the genuine press-release content.

Cross-company validation (real run, all 56 promoted/null-result companies): **0 errors, 1967
warnings, 55 information**. No duplicate IDs found in any of the 6 main datasets.

**Cumulative operational counts across all 56 promoted companies: 54 provisional / 49 confirmed**
(re-verified directly against `company_summary_template.csv`).

Batch summary: `outputs/intermediate/scaleup_batch_8_summary.csv`.

Status count after Batch 8 (end of controller session 2 — 20 companies processed this session,
the session limit): 56 `promoted_complete`/`completed_null_result` (41 `promoted_complete`, 15
`completed_null_result`), 13 `blocked_manual_browser`, 31 `not_started`. The full FTSE 100 study
remains **not complete**.

## Persistent scale-up controller — session 3, Batch 9 complete (60 of 100 companies have a final status)

Controller resumed cleanly from `master_controller_checkpoint.json` at the start of session 3.
Verified session 2's stated end-state (56 companies with final status, 0 validation errors, no
duplicate IDs, no partial files) against live files before starting new work.

**Batch 9** (5 companies): **Airtel Africa** (`completed_null_result` — the 'Airtel AI Spam Alert
Service' is a predictive/classification AI system, not generative), **Beazley**
(`completed_null_result` — only AI governance/risk-oversight discussion, including AI sublimits on
insured risk, no operational evidence of Beazley's own GenAI use), **Howdens Joinery**
(`completed_null_result` — only AGM Q&A and risk-register AI/cyber mentions), **Weir Group**
(`completed_null_result` — a single vague "Generative AI initiatives accelerated" mention with no
named tool/task/user-group, confirmed via direct grep as the only such mention; Motion Metrics/
SentianAI investee technology is predictive/computer-vision, not generative), and **Coca-Cola HBC**
(`blocked_manual_browser` — both required annual reports confirmed HTTP 403 domain-wide on
coca-colahellenic.com; a third-party trade-media claim about an OpenAI/energy-consumption use case
was not usable as evidence and remains an unconfirmed lead). No operational findings this batch —
all four accessible companies were genuine, thoroughly-reviewed null results.

Cross-company validation (real run, all 60 promoted/null-result companies): **0 errors, 2050
warnings, 59 information**. No duplicate IDs found in any of the 6 main datasets.

**Cumulative operational counts across all 60 promoted companies: 54 provisional / 49 confirmed**
(unchanged from end of session 2, since no operational findings were added this batch; re-verified
directly against `company_summary_template.csv`).

Batch summary: `outputs/intermediate/scaleup_batch_9_summary.csv`.

Status count after Batch 9: 60 `promoted_complete`/`completed_null_result` (41 `promoted_complete`,
19 `completed_null_result`), 14 `blocked_manual_browser`, 26 `not_started`. The full FTSE 100 study
remains **not complete**.

## Final closure — manual-browser resolution pass (87 of 100 companies fully processed, 13 remain blocked)

A dedicated manual-browser resolution pass worked through every row of the existing
`manual_browser_resolution_queue_controller.csv` for the 14 companies left `blocked_manual_browser`
at the end of session 4. This environment has no true interactive browser — only `WebFetch` (an
automated fetcher distinct from the pipeline's own Python download script) and `WebSearch` were
available, so every result is labelled "fetch-verified," never "browser-verified," per the
project's established capability-honesty convention.

**1 company resolved: BAE Systems** (`blocked_manual_browser` → `promoted_complete`). The
previously-documented Incapsula bot-protection block on `investors.baesystems.com` no longer
reproduced — both annual reports downloaded cleanly as genuine, correctly-sized PDFs via the
pipeline's own download script. Yielded **3 confirmed operational GenAI use cases**, all
explicitly naming LLMs/generative AI and fragmented across over-consolidated rejected staging rows
(the same recurring staging-engine limitation seen throughout this project): (1) LLM/generative-AI
natural-language drone command and self-reconfiguration; (2) a "Typhoon AI assistant" — an LLM
trained on aircraft maintenance manuals; (3) an "operationalised" AI cyber-threat-insight system
for customers, using an LLM trained on nearly a decade of expert analysis. One further governance
finding accepted (BAE's own AI/cyber/data workforce-training investment).

**13 companies remain genuinely blocked**, every one re-attempted and re-confirmed this pass (not
assumed): Lloyds Banking Group, Unilever, Sage Group, BP, Imperial Brands, Haleon, Computacenter,
Associated British Foods, Burberry Group, IMI and Coca-Cola HBC all return persistent domain-wide
HTTP 403/timeout/bot-challenge blocks. **M&G** is a distinct blocker category, precisely
re-diagnosed this pass: both annual reports download successfully but are AES-encrypted; a local
diagnostic (no new packages installed, per the project's environment-stability rule) confirms
`pypdf` raises `DependencyError("cryptography>=3.1 is required for AES algorithm")` immediately on
open — a text-extraction blocker, not an access blocker. **IMI** surfaced a documented nuance:
WebFetch's failure mode shifted from an implicit block to its own size-limit error, suggesting the
network-level block may have eased, but the project's authoritative collection path
(`03_download_sources.py`) was re-run and still returns a clean HTTP 403 — so IMI is kept blocked,
not resolved, despite the differing WebFetch behaviour. Full per-company detail, including a dated
`2026-08-08 manual-browser resolution pass` note on every row (appended, not overwriting the
original documentation), is in `manual_browser_resolution_queue_controller.csv`.

Cross-company validation (real run, all 87 promoted/null-result companies): **0 errors, 2619
warnings, 86 information**. No duplicate IDs in any of the 6 main datasets; row-count deltas
verified (`source_manifest` +2, `use_case` +3, `governance` +1, `company_summary` +1 for BAE
Systems); no `*.partial`/`*.tmp` files remain. Every one of the 100 FTSE 100 constituents has
exactly one final status, independently cross-checked (87 + 13 = 100, no company missing or
double-counted).

**Cumulative operational counts across all 87 promoted/null-result companies: 63 provisional / 58
confirmed.**

**Final status count: 47 `promoted_complete`, 40 `completed_null_result`, 13
`blocked_manual_browser`, 0 `not_started`.** Final snapshot:
`outputs/intermediate/analysis_snapshot_2026-08-08_final_closure/` (SHA256-verified). This
represents the practical end state of the automated-plus-manual-browser-attempted collection
effort — the 13 remaining companies require an actual human browser session (M&G alternatively
needs either an out-of-pipeline PDF-to-text conversion or a deliberate future decision to add the
`cryptography` package to the environment). **The FTSE 100 dataset is ready for final report
drafting**, provided any FTSE 100-wide summary statistics or sector comparisons explicitly
disclose the 13-company gap rather than treating the 87-company dataset as fully representative of
the index.

## Persistent scale-up controller — session 4 complete: ALL 100 FTSE 100 constituents now have a final status

Session 4 processed all 11 remaining `not_started` companies in a single continuous run (no batch
limit this session): **Alliance Witan**, **F&C Investment Trust**, **Intermediate Capital Group**,
**Lion Finance Group**, **LondonMetric Property**, **Pershing Square Holdings**, **Polar Capital
Technology Trust**, **Scottish Mortgage Investment Trust**, **Segro**, **Standard Life** (formerly
Phoenix Group Holdings plc, renamed 24 February 2026), and **Tritax Big Box REIT**.

**2 companies promoted:**
- **Lion Finance Group** (Bank of Georgia) — the richest finding of the session, with 2 confirmed
  operational use cases: an in-house-developed Georgian-language Generative AI customer-service
  chatbot (resolving 65% of queries without human intervention, 91% customer satisfaction), and an
  internal "enterprise AI platform" letting employees build 300+ custom AI assistants (freeing
  ~6,600 hours/month, weekly adoption 10%→56% in six months, tracked via a formal "GenAI
  engagement" executive KPI). Also yielded a named "Generative AI (GenAI) policy" governance
  finding and further strategic/governance findings.
- **Segro** — 1 confirmed operational use case: a named, live, company-wide Microsoft Copilot
  rollout to all employees with a structured training programme.

**9 companies genuine null results:** Alliance Witan, F&C Investment Trust, Intermediate Capital
Group, LondonMetric Property, Pershing Square Holdings, Polar Capital Technology Trust, Scottish
Mortgage Investment Trust, Standard Life, and Tritax Big Box REIT — several (Intermediate Capital
Group, Standard Life, Tritax Big Box REIT) still yielded genuine governance/strategic findings
about the company's own AI oversight, without a qualifying operational deployment.

**Methodological pattern established this session — investment-trust portfolio commentary:** Four
of the eleven companies (Alliance Witan, F&C Investment Trust, Pershing Square Holdings, Polar
Capital Technology Trust, Scottish Mortgage Investment Trust) are pure investment trusts with no
operating business of their own. Their annual reports are extremely AI-keyword-dense (Polar
Capital Technology Trust alone produced 344 candidate passages, 60 Stage-A hits) but virtually all
of this content is the Investment Manager's market commentary on the AI investment theme or
portfolio holdings' own AI adoption — not the Trust's own operational or governance use of
generative AI. Applying Core Rule 1 (the unit of analysis is a use case *by* the FTSE constituent
itself), every such passage across all five trusts was rejected, extending the same principle
already used to exclude a Non-Executive Director's own outside company (Endeavour Mining, session
3).

**Process correction applied mid-session (documented, not hidden):** SGRO-STR-001 was initially
marked `reviewer_decision=correct`, following the convention established for the *rejected*-
candidates staging file (where `correct` means "correctly rejected, exclude from promotion," since
`REJECTED_PROMOTABLE_DECISIONS = {"accept"}` only). However, `STRATEGIC_PROMOTABLE_DECISIONS =
{"accept", "correct"}` — both values promote a *strategic* staging row. This caused the same
Microsoft Copilot evidence to be briefly double-promoted as both a strategic finding and an
operational use case. Caught before the session's final validation pass: corrected the staging
decision to `reject`, manually removed the erroneous duplicate row from
`strategic_capability_building_findings.csv`, and re-ran full validation and duplicate-ID checks
to confirm a clean state. No other staging decisions this session used `correct` outside the
rejected-candidates file, so this was an isolated, fully-corrected error.

Cross-company validation (real run, all 86 promoted/null-result companies): **0 errors, 2607
warnings, 85 information**. No duplicate IDs found in any of the 6 main datasets; row-count deltas
verified against expected additions (`source_manifest` +21, `use_case` +3, `strategic` +3,
`governance` +12, `rejected` +0, `company_summary` +11); no `*.partial` or `*.tmp` files remain.

**Cumulative operational counts across all 86 promoted/null-result companies: 60 provisional / 55
confirmed**, re-verified directly against `company_summary_template.csv`.

Session summary: `outputs/intermediate/session4_summary.csv`.

**Final status count: all 100 FTSE 100 constituents now have a status** — 46 `promoted_complete`,
40 `completed_null_result`, 14 `blocked_manual_browser`, 0 `not_started`. The **automated portion
of the FTSE 100 scale-up is now complete**. The only remaining work is a dedicated manual-browser
resolution pass for the 14 companies genuinely blocked by domain-level automated-fetch
restrictions (Lloyds Banking Group, BAE Systems, Unilever, Sage Group, BP, Compass Group, Imperial
Brands, Haleon, Computacenter, Associated British Foods, Burberry Group, M&G, IMI, Coca-Cola HBC)
— documented with exact manual actions in
`outputs/intermediate/manual_browser_resolution_queue_controller.csv`. Final report drafting may
now proceed using the full 86-company dataset, while treating the 14 blocked companies as a
known, documented gap rather than a silent absence.

## Persistent scale-up controller — session 3, Batch 12 complete, session 3 ends (75 of 100 companies have a final status)

**Batch 12** (5 companies, the final batch of session 3): **Metlen Energy & Metals**
(`promoted_complete` — 1 confirmed operational use case: "Avokado CORTEX," a named GenAI digital
assistant offered by METLEN's own technology subsidiary Avokado, operating on top of Avokado's
AVOX platform to assist B2B customers with energy management and cost budgeting. Explicitly
described as "an Energy Assistant based on GenAI," consistently across both the FY2024 and FY2025
annual reports; content was fragmented across four over-consolidated/duplicate rejected rows and
consolidated into a single operational row — evidence_strength=2_moderate/confidence=medium given
some ambiguity between "offers" and "creation...underway" phrasing and no quantified benefit. One
strategic and two governance findings also promoted), **Aberdeen Group** (`completed_null_result`
— all AI mentions are vague/general: predictive email-filtering, AI-related market commentary,
ordinary automation, and AI risk/governance oversight; one governance finding accepted),
**St. James's Place** (`completed_null_result` — "AI tools" that "respond to questions on our
advice framework" for advisers are described only in generic AI-tools language, with no
generative-AI/LLM/named-product language anywhere nearby, matching the IHG/IG Group precedent; one
governance finding accepted), **Land Securities** (`completed_null_result` — the one named AI
product, Brainbox AI, is predictive building-control automation for heating/cooling, not
generative), and **Endeavour Mining** (`completed_null_result` — AI mentions describe predictive
exploration-targeting tools; the one "generative AI"/"foundation models" mention describes a
Non-Executive Director's own outside company, not Endeavour Mining's own use, correctly excluded
per Core Rule 1).

Cross-company validation (real run, all 75 promoted/null-result companies): **0 errors, 2326
warnings, 74 information**. No duplicate IDs found in any of the 6 main datasets; row-count
deltas verified against expected additions (`source_manifest` +10, `use_case` +1, `strategic` +1,
`governance` +4, `rejected` +0, `company_summary` +5).

**Cumulative operational counts across all 75 promoted companies: 57 provisional / 52 confirmed**
(re-verified directly against `company_summary_template.csv`).

Batch summary: `outputs/intermediate/scaleup_batch_12_summary.csv`.

Status count after Batch 12: 75 `promoted_complete`/`completed_null_result` (44
`promoted_complete`, 31 `completed_null_result`), 14 `blocked_manual_browser`, 11 `not_started`.
**This completes Session 3's 4-batch/20-company limit** (Batches 9–12: Airtel Africa, Beazley,
Coca-Cola HBC, Howdens Joinery, Weir Group, Antofagasta plc, DCC plc, Diploma, Investec, United
Utilities, Melrose Industries, Spirax Group, 3i, IG Group, Fresnillo plc, Metlen Energy & Metals,
Aberdeen Group, St. James's Place, Land Securities, Endeavour Mining — 20 companies processed).
The full FTSE 100 study remains **not complete**: 11 companies remain entirely `not_started`
(Alliance Witan, F&C Investment Trust, Intermediate Capital Group, Lion Finance Group,
LondonMetric Property, Pershing Square Holdings, Polar Capital Technology Trust, Scottish
Mortgage Investment Trust, Segro, Standard Life, Tritax Big Box REIT), plus 14
`blocked_manual_browser` companies still needing a real human browser session.

## Persistent scale-up controller — session 3, Batch 11 complete (70 of 100 companies have a final status)

**Batch 11** (5 companies): **Spirax Group** (1 confirmed operational use case: "MiM," a
proprietary, company-developed large language model tool for sales-engineer training and
productivity, explicitly described using "generative AI" and "large language model" language.
Piloted with 200 sales colleagues during 2025 — freeing approximately four hours per person per
week, redeployed into customer-facing activity — and now rolled out to over 1,000 sales
colleagues as its sector-based content is expanded; content was fragmented across five
over-consolidated/duplicate rejected rows spanning both annual reports and consolidated into a
single operational row per the anti-overconsolidation check. Five genuine AI-governance-framework
findings were also promoted), **Melrose Industries** (`completed_null_result` — the current-year
FY2025 annual report could not be located, a 404/403/only-a-41.7KB-RNS-notice pattern already
seen with Investec, recorded as a single `approval_status=pending` source row rather than a
company blocker; the previous-year AR contains only ordinary automation/robotics), **3i**
(`completed_null_result` — rich engagement with the *topic* of generative AI, including a named
"Group AI policy," an "AI steering group," and CTO Forum/Board GenAI briefings, but no concrete
operational deployment by 3i itself was found; one strategic finding accepted), **IG Group**
(`completed_null_result` — a live, customer-facing "AI chatbot" and an "AI-powered engagement
tool" are described only in generic AI-powered language, with no generative-AI/LLM/named-product
language anywhere nearby, confirmed via direct grep of the source text; excluded per the IHG
Hotels & Resorts precedent from Batch 6; three governance and one strategic finding accepted
instead), and **Fresnillo plc** (`completed_null_result` — only vague general-AI references and
ordinary automation, plus one governance finding on Board AI training sessions).

Cross-company validation (real run, all 70 promoted/null-result companies): **0 errors, 2239
warnings, 69 information**. No duplicate IDs found in any of the 6 main datasets; row-count
deltas verified against expected additions (`source_manifest` +9, `use_case` +1, `strategic` +2,
`governance` +9, `rejected` +0, `company_summary` +5).

**Cumulative operational counts across all 70 promoted companies: 56 provisional / 51 confirmed**
(re-verified directly against `company_summary_template.csv`).

Batch summary: `outputs/intermediate/scaleup_batch_11_summary.csv`.

Status count after Batch 11: 70 `promoted_complete`/`completed_null_result` (43
`promoted_complete`, 27 `completed_null_result`), 14 `blocked_manual_browser`, 16 `not_started`.
The full FTSE 100 study remains **not complete**.

## Persistent scale-up controller — session 3, Batch 10 complete (65 of 100 companies have a final status)

**Batch 10** (5 companies): **Investec** (1 confirmed operational use case: Microsoft Copilot for
Sales, with Investec described as "the very first customer to go live in production" with the
product — deployed to 900 UK bankers with a further 700-banker rollout underway in South Africa,
saving an estimated 200 hours/year across the bank; split out from an over-consolidated
technology-partner case-study staging row. The current-year (FY2025) annual report could not be
located after a guessed URL 404'd and a follow-up landing-page fetch returned HTTP 403; this was
recorded as a single pending source rather than a company blocker, since the FY2024 annual report
plus the Microsoft case study together provided substantial evidence — the same pattern used for
Schroders in Session 1), **DCC plc** (`completed_null_result` — DCC's own annual report explicitly
states its internal AI platform favours "practical, actionable AI solutions...rather than
exploratory or generative AI technologies," a rare explicit company self-disclaimer against
generative AI; one governance finding on a "Generative AI applications" acceptable-use policy was
still promoted), **Antofagasta plc** (`completed_null_result` — all AI mentions are predictive/
optimisation mining systems, not generative), **Diploma** (`completed_null_result` — only vague
general-AI mentions), and **United Utilities** (`completed_null_result` — all AI mentions describe
predictive/ML systems such as Dynamic Network Management and leak-detection sensors).

Two source-URL corrections this batch (United Utilities' previous-year AR, and an unsuccessful
attempt for Investec's current-year AR) followed the same "search once, document if unresolved"
discipline used throughout the project.

Cross-company validation (real run, all 65 promoted/null-result companies): **0 errors, 2160
warnings, 64 information**. No duplicate IDs found in any of the 6 main datasets.

**Cumulative operational counts across all 65 promoted companies: 55 provisional / 50 confirmed**
(re-verified directly against `company_summary_template.csv`).

Batch summary: `outputs/intermediate/scaleup_batch_10_summary.csv`.

Status count after Batch 10: 65 `promoted_complete`/`completed_null_result` (42 `promoted_complete`,
23 `completed_null_result`), 14 `blocked_manual_browser`, 21 `not_started`. The full FTSE 100 study
remains **not complete**.

## Scale-up Loop 4 complete — 24 of 100 companies promoted

Two parallel tracks ran this loop. **Track A** (5 newly-selected companies, all fully
promoted): **Whitbread** (completing the original 10-company pilot roster, untouched since
Loop 1 — no qualifying GenAI evidence, one thin strategic Board-briefing mention only),
**Barratt Redrow** (no qualifying GenAI evidence — genuine no-disclosure company),
**London Stock Exchange Group** (the richest AI disclosure of any company processed this
loop — 2 operational use cases: Financial Meeting Prep, a Gen AI meeting-briefing generator
explicitly launched/generally available by end of 2024; and AI Insights API, a weaker-evidence
Gen AI summarisation product; plus 16 strategic and 7 governance findings), **Smiths Group**
(no qualifying operational GenAI evidence — one thin strategic megatrend mention; note Smiths
Detection, its predictive-AI threat-detection business, is being divested and does not involve
generative AI regardless), and **British Land** (no qualifying GenAI evidence — its sole
"generative AI" mention names a tenant, Synthesia, not British Land's own use).

**Known staging-engine limitation recurred and was handled the same way as RELX in Loop 3**:
LSEG's automated staging pass initially proposed **zero** operational candidates despite
genuine qualifying evidence, because two distinct passage clusters (the Financial Meeting
Prep/AI Insights API disclosure; the ChatGPT/MCP and 4,000-employee ChatGPT Enterprise
announcements) were each over-consolidated by the ±450-char local-context matcher into a
single `vague_general_ai_reference` rejected row. Both were manually read from the full
extracted source text and split into distinct, individually-sourced staging rows — 2 promoted
as operational (Financial Meeting Prep), 2 as strategic (the ChatGPT/MCP items, which are
concrete and dated but explicitly future-tense/planned in their own source text, so were
**not** classified as operational per this loop's explicit rule against treating planned
deployments as operational evidence).

**Track B** (the five companies left blocked since Loop 2/3) was **not restarted** this loop —
per this loop's instructions, known 403/Incapsula/application-error URLs were not repeatedly
retried. Instead, `outputs/intermediate/manual_browser_resolution_queue_loop4.csv` was built:
12 rows across Lloyds Banking Group (2 ambiguous GenAI rows + 1 document-location row), BAE
Systems (2 Incapsula-blocked annual reports), Unilever (2 blocked GenAI rows), Sage Group (2
blocked GenAI rows + 1 document-location row), and BP (2 blocked GenAI rows) — each with the
exact manual action, evidence needed, and an official alternative where one was found. One
new lead was found for Lloyds' AR2024 (an "Annual Review" PDF) but it also returned the same
site-wide application-error page on retry, so it was logged as a lead, not treated as
resolved. All five companies remain checkpoint-stopped/blocked, unchanged in the main
datasets.

Cross-company validation (`08_validate_promoted_data.py`, real run, all 24 promoted
companies): **0 errors, 891 warnings, 23 information**. Warnings follow the same established
pattern (unresolved-review rows outside each round's exception-focused scope, honestly-blank
publication dates, sources with no attached finding) — none converted to false passes.

**Cumulative operational counts across all 24 promoted companies: 32 provisional / 27
confirmed**, re-verified directly against `company_summary_template.csv` row-by-row (matches
the validation script's independent recomputation exactly, so no arithmetic discrepancy this
round).

New snapshot: `outputs/intermediate/analysis_snapshot_2026-08-04_scaleup4/`.

Companies still blocked (unchanged from Loop 3, not re-researched this loop, see the manual
queue above for exact next actions): Lloyds Banking Group, BAE Systems, Unilever, Sage Group,
BP.

The full FTSE 100 study remains **not complete** — 24 of 100 constituents promoted, plus 5
more partially researched but blocked.

## Scale-up Loop 3 complete — 19 of 100 companies promoted

Two parallel tracks ran this loop. **Track A** (5 newly-selected companies): GSK plc, RELX
and Next plc were fully promoted; Lloyds Banking Group stopped at the approval checkpoint
(50% genuinely ambiguous, `lloydsbankinggroup.com` returning application-error pages on
every GenAI-press-release fetch attempt); BAE Systems cleared the ambiguity threshold (its
one AI-adjacent lead was fetch-verified and confirmed *not* generative AI) but is blocked at
the **download** stage — both annual reports are actively challenged by Incapsula
bot-protection. **Track B** (the five companies left blocked from Loop 2): **Shell plc and
HSBC were both fully resolved and promoted this round**; Unilever, Sage Group and BP remain
genuinely blocked (`unilever.com`, `sage.com`, `bp.com` all return HTTP 403 to automated
fetch on every remaining pending row, across repeated attempts and sessions) and need an
actual human browser session, not further automated retries.

**Newly promoted this loop (5 companies):**
- GSK plc: provisional 1, confirmed 1 (generative AI implemented at 20+ manufacturing sites for investigation-data review)
- RELX: provisional 4, confirmed 4 (Lexis+ with Protege; PharmaPendium AI; ClinicalKey AI; Ask ICIS -- a representative, non-exhaustive sample of a much richer official GenAI-product portfolio; several further named products not separately coded this round)
- Next plc: provisional 0, confirmed 0 (no qualifying GenAI evidence; AI/LLM mentions blended into a general-AI strategy narrative)
- Shell plc: provisional 1, confirmed 1 (SparkCognition/Shell generative-AI subsurface exploration imaging) -- **Shell's Annual Report 2024 404 is now resolved** (a working replacement URL was located and verified on the same shell.com archive page)
- HSBC: provisional 2, confirmed 2 (HSBC/Google Cloud Gemini-powered decision assistant; HSBC/Mistral AI productivity platform)

**Script fix applied (reproducible shared defect):** `03_download_sources.py`'s error-page
detection did not recognise Incapsula's bot-challenge interstitial, so it had silently
accepted two BAE Systems "downloads" that were actually ~1KB challenge-page stubs, not real
PDFs. Added `incapsula`/`request unsuccessful` to `ERROR_PAGE_MARKERS`; the two invalid files
were renamed aside (not deleted) as `*.invalid_incapsula_block` for the record. This is a
genuine, reusable fix (affects any future company hitting the same protection), not a
one-off workaround.

**Cross-company validation** (scope now extended to all 19 promoted companies): 0 errors,
776 warnings, 18 information. Warnings remain the same established pattern (unresolved-
review rows outside each round's exception-focused scope, honestly-blank publication dates,
sources with no attached finding) -- none converted to false passes.

**Cumulative operational counts across all 19 promoted companies: 30 provisional / 26
confirmed** (re-verified directly against `company_summary_template.csv` row-by-row).

**Dated validated snapshot:** `outputs/intermediate/analysis_snapshot_2026-07-20_scaleup3/`
(see its `SNAPSHOT_README.md`). The prior `analysis_snapshot_2026-07-20_scaleup2/` snapshot
was left unmodified.

**Companies still blocked, with exact reasons:**
- Lloyds Banking Group: 2 of 4 rows ambiguous -- lloydsbankinggroup.com error pages
- BAE Systems: 0% ambiguous, but both approved annual reports blocked by Incapsula at download
- Unilever: 2 of 5 rows ambiguous -- unilever.com HTTP 403
- Sage Group: 3 of 5 rows ambiguous -- sage.com HTTP 403
- BP: 2 of 4 rows ambiguous -- bp.com HTTP 403

**Next operational step:** a further bounded batch loop for the remaining unprocessed FTSE
100 companies (81 of 100 not yet started), plus a dedicated manual-browser follow-up pass
for the five still-blocked companies above (Lloyds, BAE, Unilever, Sage, BP) -- none of
these are methodology gaps, all are domain-level automated-fetch restrictions requiring a
real browser session. **The full FTSE 100 study remains not complete.**

## Scale-up Batch Loop 2 complete — 14 of 100 companies promoted

Two further batches of 5 companies each were processed. Of the 10 selected,
6 reached full promotion and 4 stopped at the approval checkpoint (each
exceeding the 30% ambiguous-candidate threshold, driven almost entirely by
`unilever.com`, `sage.com`, and `bp.com` consistently blocking automated
fetch — a genuine access constraint, not a methodology gap).

**Companies newly promoted this round:**
- Diageo: provisional 3, confirmed 3 (bottle/label personalisation pilot — Amazon Titan Bedrock; generative-AI cybersecurity phishing-simulation chatbot; "What's Your Cocktail?" food-pairing platform)
- National Grid plc: provisional 0, confirmed 0 (no qualifying GenAI evidence — all Stage-A hits were generic industry-trend/board-agenda commentary)
- Vodafone Group: provisional 2, confirmed 2 (SuperTOBi customer virtual assistant on Azure OpenAI; Copilot for Microsoft 365 rollout to 50,000+ employees)
- Legal & General: provisional 1, confirmed 1 (Microsoft 365 Copilot rollout to ~10,000 employees plus an already-live Retail-business AI tool, +8-point NPS)
- Reckitt: provisional 1, confirmed 1 (GenAI marketing pilots — Gaviscon, Finish — with Boston Consulting Group; FY2024 Annual Report reverted to `pending` after a genuine HTTP 403 download failure)
- Croda International: provisional 0, confirmed 0 (no qualifying GenAI evidence found in either annual report)

**Companies left at the approval checkpoint (not promoted this round):**
- Unilever, HSBC, Sage Group (Batch loop 2, part 1) and BP (part 2) — each has 2-3 pending, genuinely ambiguous GenAI-relevant candidate sources (mostly blocked by repeated HTTP 403 on their own domains), exceeding the 30% threshold. Each needs a follow-up manual-browser verification pass, not further automated attempts.

**Structural fix applied:** `pilot_companies.csv` (originally a fixed 10-row
pilot roster) was extended with the 10 newly-selected companies, sourced
verbatim from `ftse100_constituents_2026-06-19.csv` — every pipeline script
(`01`–`08`) resolves companies only via this file via
`pipeline_common.find_company_row()`, so this was a genuine reproducible
blocker affecting the whole scale-up loop, not a one-off. No evidentiary
data was invented; only roster rows (company/ticker/sector) were added.

**Cross-company validation** (scope now extended to all 14 promoted
companies): 0 errors, 381 warnings, 14 information. Warnings remain the
same established pattern (unresolved-review rows outside each round's
exception-focused scope, honestly-blank publication dates, sources with no
attached finding) — none converted to false passes.

**Cumulative operational counts across all 14 promoted companies: 22
provisional / 20 confirmed.**

**Dated validated snapshot:** `outputs/intermediate/analysis_snapshot_2026-07-20_scaleup2/`
(see its `SNAPSHOT_README.md`). The original pilot+Batch-1 snapshot at
`outputs/intermediate/analysis_snapshot_2026-07-20/` was left unmodified.

**Next operational step:** a further bounded batch loop for the remaining
unprocessed FTSE 100 companies (86 of 100 not yet started), plus a
dedicated manual-browser follow-up pass for Shell, Unilever, HSBC, Sage
Group and BP (5 companies genuinely blocked by domain-level fetch
restrictions, not methodology gaps). **The full FTSE 100 study remains not
complete.**

## Batch 1 promoted — full FTSE 100 scale-up underway

The four-company pilot (below) is complete. Batch 1 promotion is now also
complete for four further companies: **Experian, Rio Tinto, Admiral Group,
Informa**. The project has entered full FTSE 100 scale-up — report drafting
may begin using the dated validated snapshot at
`outputs/intermediate/analysis_snapshot_2026-07-20/` (see that folder's
`SNAPSHOT_README.md` for full detail). **Findings remain preliminary**: 8 of
100 FTSE 100 constituents are promoted so far, and final sector comparisons
or FTSE 100-wide conclusions must wait for wider coverage.

**Batch 1 confirmed operational counts:**
- Experian: provisional 1, confirmed 1 (Experian Assistant for Model Risk Management)
- Rio Tinto: provisional 1, confirmed 1 (GPT-like knowledge agent, Annual Planning Review workshop)
- Admiral Group: provisional 0, confirmed 0 (Google Cloud generative-AI partnership retained as strategic, not operational — no concrete task/user group/deployment described)
- Informa: provisional 0, confirmed 0 (Generative AI Use Policy/AI Governance Charter retained as governance, not operational)

**Cross-company validation** (`08_validate_promoted_data.py`, scope now
extended to all 8 promoted companies): 0 errors, 216 warnings, 8 information
across the combined dataset. Warnings are overwhelmingly unresolved-review
rows outside this round's exception-focused review scope (blank
`reviewer_decision`), blank `publication_date` fields honestly left
unconfirmed, and sources with no promoted finding attached — none converted
to false passes.

**Shell plc remains incomplete.** 2 of 3 approved sources downloaded (Annual
Report 2025; SparkCognition/Shell generative-AI release); the Annual Report
2024 returned a genuine HTTP 404 on retry — the recorded direct-download URL
is stale, not a transient network issue. Shell requires a separate
source-resolution task (locating a current, valid URL for the 2024 report)
before it can proceed through extraction/screening/staging/review/promotion.
No Shell staging or promotion has occurred; Shell is not among the 8
promoted companies.

**Next operational step:** a bounded, recurring batch loop for the remaining
unprocessed FTSE 100 companies (91 of 100 not yet started, plus Shell's
separate resolution task), reusing `01`–`08` unchanged except for the
per-company data additions (`CLUSTER_RULES`, `SOURCE_CANDIDATE_TO_FILENAME`,
`SOURCE_MANIFEST_OVERRIDES`, `OPERATIONAL_OVERRIDES`) that this scale-up
phase has repeatedly shown to be the normal, expected way of extending the
frozen pipeline to a new company. The full FTSE 100 study is **not**
complete.

## Pilot complete — four companies

The batch-1 pilot is methodologically complete. This section is the closeout
record; it does not replace or invalidate the AstraZeneca-only notes below,
which remain the detailed history of the first company.

**Pilot companies completed:**
- AstraZeneca
- Tesco
- BT Group
- Rolls-Royce Holdings

**Pipeline stages exercised end to end, across at least one company each:**
- Source discovery
- Human approval of candidate sources
- Download (PDF and HTML, with signature/content validation)
- Text extraction (PDF via pypdf with page markers; HTML via stdlib `html.parser`)
- Keyword screening (Stage A/B)
- Staging and mechanical triage (`06_prepare_staging_candidates.py`)
- Human review of staging rows (operational, strategic, governance, rejected, duplicate flags)
- Promotion into the six main datasets (`07_promote_reviewed_staging.py`), with idempotency verified for every promoted company
- Cross-company validation audit (`08_validate_promoted_data.py`)

**Confirmed operational counts (unchanged through the AstraZeneca repair):**
- AstraZeneca: provisional 6, confirmed 3
- Tesco: provisional 2, confirmed 1
- BT Group: provisional 4, confirmed 4
- Rolls-Royce Holdings: provisional 1, confirmed 1

**Remaining warnings and unresolved rows (not claimed as settled):**
- AstraZeneca: 8 legacy `.pdf.pdf` filenames retained as a warning only (already referenced by promoted data, not corrected); 3 operational rows still `review_status=not_reviewed` (AZN-UC-004A, AZN-UC-004B, AZN-UC-004E); AZN-003/AZN-006/AZN-009/AZN-010 are logged sources with no promoted finding attached (expected — general-AI-only or redundant documents); `manual_review_status` is stored as `review_complete` but a stricter recomputation would read `pending_review` given the three not-yet-reviewed rows above — flagged, not corrected.
- Tesco: TSCO-STR-007 unresolved (`needs_more_evidence`).
- BT Group: BT-OP-005, BT-REJ-032 unresolved (`needs_more_evidence`).
- Rolls-Royce Holdings: RR-OP-002, RR-STR-003, RR-REJ-021, RR-REJ-030 unresolved (`needs_more_evidence`).
- Every company has one or more sources with a blank `publication_date` where no exact date was confirmed on-page — accepted per the project's rule against inferring dates, not an error.

None of the above unresolved rows have been converted to accepted, rejected,
or confirmed as part of pilot closeout — they remain open judgment calls for
a future review pass.

**Scripts status:** `01`–`08` are frozen for scale-up. They should not be
re-architected for the next batch of companies unless a reproducible bug is
found that affects more than one company (a company-specific fix — e.g. a
new `CLUSTER_RULES` entry in `06`, or a new company's `OPERATIONAL_OVERRIDES`/
`SOURCE_MANIFEST_OVERRIDES` entry in `07` — is expected and is not itself a
sign the pipeline is broken).

**Next phase:** batch processing of the remaining FTSE 100 companies beyond
this four-company pilot, reusing `01`–`08` unchanged except for the
per-company data additions described above.

## Completed
- Research schema and controlled vocabularies finalised (`03_CODING_MANUAL.md`).
- 10-company pilot selected (`pilot_companies.csv`).
- AstraZeneca source collection completed (`sources/astrazeneca/`).
- 9 AstraZeneca sources verified and logged in `source_manifest.csv` (AZN-001 to AZN-006, AZN-008 to AZN-010; AZN-007 excluded — publication date 2021-04-12 falls outside the project's evidence window).
- 6 operational records saved to `use_case_dataset_template.csv`.
- 3 confirmed (AZN-UC-002, AZN-UC-003, AZN-UC-004C) and 3 provisional/not-yet-reviewed (AZN-UC-004A, AZN-UC-004B, AZN-UC-004E) operational records.
- Strategic capability, governance/enablement, and rejected/aspirational findings saved separately (`strategic_capability_building_findings.csv`, `governance_and_enablement_findings.csv`, `rejected_or_aspirational_findings.csv`) — excluded from operational use-case counts.
- AstraZeneca company summary completed (`company_summary_template.csv`): provisional_use_case_count = 6, confirmed_use_case_count = 3, no_disclosure_confirmed = disclosure_found, manual_review_status = review_complete.

## Next step
Design a semi-automated pipeline for the remaining nine pilot companies (do not begin collecting the next company yet — this is a design task only).

### What should be automated
- Populating `source_manifest.csv` scaffold rows (source_id, company, ticker, sector via lookup from `ftse100_constituents_2026-06-19.csv`, document_category) once a document is identified.
- Keyword pre-screening of downloaded/extracted text against the generative-AI keyword list, to flag candidate passages for a human/coding pass rather than to auto-code them.
- Draft population of `use_case_dataset_template.csv` and the three findings CSVs from flagged passages, always left at `review_status = not_reviewed`.
- Recalculation of `provisional_use_case_count` and `confirmed_use_case_count` in `company_summary_template.csv` once `use_case_dataset_template.csv` changes, using the exact formulas in `03_CODING_MANUAL.md`.
- Duplicate-candidate detection (same deployment described in multiple sources) for human confirmation, per Core Rule 7/duplicate_of_record_id handling.

### Where human review is still required
- Confirming a passage actually meets the generative-AI test (Core Rules 2–3) rather than general/predictive AI — this judgment is not being automated.
- Setting `review_status` to `reviewed_confirmed` / `reviewed_corrected` / `reviewed_excluded` — only a human reviewer moves a row out of `not_reviewed`.
- Resolving `evidence_strength` and `confidence` for borderline passages.
- Verifying exact document titles, publication dates, and URLs against the actually saved source file (not a search snippet or filename) — the AZN-004 title/date issues in this pilot show why this step cannot be automated away.
- Approving `no_disclosure_confirmed = no_disclosure_confirmed` (the "genuinely nothing found" state) — this is explicitly a manual-only value per the coding manual.
- Setting `manual_review_status = review_complete` for the manual validation sample (`04_VALIDATION_PLAN.md`).

### Current important filenames
- `source_manifest.csv`, `use_case_dataset_template.csv`, `company_summary_template.csv` — core schemas, one row per company/use case added as each pilot company completes.
- `strategic_capability_building_findings.csv`, `governance_and_enablement_findings.csv`, `rejected_or_aspirational_findings.csv` — non-operational findings, kept out of the operational counts.
- `sources/astrazeneca/` — downloaded source files; `MANUAL_DOWNLOAD_CHECKLIST.md` is the template used for pre-download candidate tracking before a source is confirmed and logged.
- `backups/` — timestamped pre-edit backups of the CSVs above.
- `pilot_companies.csv`, `ftse100_constituents_2026-06-19.csv` — pilot selection and sector lookup source of truth.

### Unresolved issues to carry into the next company
- **`.pdf.pdf` double-extension problem**: every AstraZeneca source file on disk in `sources/astrazeneca/` carries a doubled `.pdf.pdf` extension (e.g. `AZN_company_annual_report_FY2024.pdf.pdf`). This has been treated as the authoritative on-disk filename and used verbatim in `local_filename` fields rather than silently corrected. Not yet decided whether to (a) rename the underlying files to a single `.pdf` for the remaining nine companies going forward, or (b) continue recording whatever the actual on-disk extension is, doubled or not, on a per-file basis. Needs a decision before the next company's downloads begin.
- **AZN-004 publication-date convention difference**: `source_manifest.csv` records AZN-004's `publication_date` as 2024-08-02 (the page's own "last updated" date), while `use_case_dataset_template.csv` records the same source's `publication_date` as 2024-07-11 (the original publish date), with the update date moved to `reviewer_notes`. This is an intentional, flagged divergence between the two files for this one source, not an error — but it means the two files do not always agree on `publication_date` for a given `source_id`, and this convention (manifest = last-updated; use-case table = original-publish-date when both are known) should be applied consistently, and documented, for any future source with the same "originally published X, last updated Y" pattern.
- **provisional_use_case_count wording**: the coding manual defines `provisional_use_case_count` as cumulative — it includes confirmed rows, not just not-yet-reviewed ones (AstraZeneca's value is 6, not 3, even though only 3 of those 6 are also confirmed). Any future notes or summaries describing "X confirmed + Y provisional" should be phrased so they don't imply the two counts are mutually exclusive, since they are not.
