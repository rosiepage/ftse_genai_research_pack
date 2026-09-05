# FTSE 100 Generative AI Research Project — Analysis Memo

**Prepared:** 2026-08-08 (analysis/report-preparation phase)
**Empirical source:** `outputs/intermediate/analysis_snapshot_2026-08-08_final_closure/` (read-only; not modified in preparing this memo)
**Companion tables:** `outputs/analysis/table_1_coverage.csv` through `table_7_blocked_sensitivity.csv`, all in this directory

This memo is a working analysis document, not the final report. It exists to establish, verify
and stress-test the headline numbers before any polished narrative is written, per
`04_VALIDATION_PLAN.md`'s spirit of evaluating the project's own outputs rather than assuming
they are correct.

---

## 0. Methodology reminder

- **Population:** FTSE 100 constituents following the 19 June 2026 index changes (100 companies;
  `ftse100_constituents_2026-06-19.csv`).
- **Evidence window:** 1 January 2023 – 14 July 2026 (`01_PROJECT_BRIEF.md`).
- **Unit of analysis:** one distinct publicly reported generative-AI use case (a different task,
  user group, business process, product or deployment context counts as distinct).
- **Inclusion bar (`is_genai = yes`):** the source must explicitly say generative AI/GenAI,
  explicitly identify an LLM/foundation model, name an unambiguously generative product (e.g.
  Microsoft 365 Copilot, ChatGPT, Claude, Gemini), or describe generation of text/code/images/audio
  through a clearly identified generative model. Predictive AI, conventional ML, and vague "AI is
  important" statements are explicitly excluded.
- **`disclosed_use_case_count`** (recorded in the source file as `confirmed_use_case_count`; the strict count used throughout this memo unless stated
  otherwise): `is_genai=yes`, `evidence_strength` in `{2_moderate, 3_strong}` (never `1_weak`),
  `review_status` in `{reviewed_disclosed, reviewed_corrected}`, `duplicate_of_record_id` blank.
- **`provisional_use_case_count`**: as above but also includes `1_weak` evidence and
  not-yet-reviewed rows — a looser, "appears to qualify" count.
- Companies are in one of three final states: **`promoted_complete`** (operational evidence found
  and promoted), **`completed_null_result`** (no qualifying evidence found in collected/reviewed
  sources), or **`blocked_manual_browser`** (source collection genuinely could not be completed
  with the tools available).

---

## 1. Dataset coverage — verified against the snapshot

| Status | Companies | Source |
|---|---|---|
| Evidence-based final status (in `company_summary_template.csv`) | 87 | direct row count |
| — of which disclosed operational (`disclosed_use_case_count >= 1`) | 38 | recomputed field sum |
| — of which null result (`disclosed_use_case_count == 0`) | 49 | recomputed field sum |
| Blocked (`manual_browser_resolution_queue_controller.csv`) | 13 | distinct `company` values |
| **Total FTSE 100 constituents** | **100** | cross-checked against `ftse100_constituents_2026-06-19.csv`: every constituent appears in exactly one of the two files above, no omissions, no duplicates |

Disclosed operational use cases: **58**. Provisional use cases: **63**. Both independently
recomputed by summing `disclosed_use_case_count` / `provisional_use_case_count` across all 87
company-summary rows, and cross-checked by recomputing directly from `use_case_dataset_template.csv`
(63 rows total; 58 pass the strict disclosed-row test defined above; the other 5 are either
`1_weak` evidence or `not_reviewed`). Both routes agree.

### Important correction to the input brief's figures

The task brief for this phase stated 47 `promoted_complete` companies. **The authoritative dataset
(`company_summary_template.csv`) supports 38, not 47.** Investigating the gap: nine companies
(Admiral Group, Barratt Redrow, British Land, Croda International, Informa, National Grid plc,
Next plc, Smiths Group, Whitbread) were carried in the project's session-tracking checkpoint
(`master_controller_checkpoint.json`) under `promoted_companies`, but every one of them has
`disclosed_use_case_count = 0` in the actual dataset — genuine null results, several explicitly
documented as such in `PROJECT_PROGRESS.md`'s own Loop 3 notes (e.g. "Next plc: provisional 0,
disclosed 0 (no qualifying GenAI evidence found)"). The checkpoint's "promoted_complete" label
drifted from its own definition somewhere over the project's long multi-session history — most
plausibly because early sessions used it loosely to mean "the company's pipeline run completed
successfully" rather than strictly "has a disclosed operational use case." **This memo treats
`company_summary_template.csv` as ground truth throughout**, per the instruction to use the
snapshot's actual datasets, not secondary tracking artifacts. This is flagged again in §9
(Limitations) as a project transparency matter, not swept under the rug.

### A second data-quality note carried into this analysis

Sector labels in `company_summary_template.csv` contain two case-inconsistent duplicate pairs —
`"Financial Services"` (1 company) vs `"Financial services"` (8 companies), and `"Investment
Trusts"` (1) vs `"investment trusts"` (1) — despite `03_CODING_MANUAL.md`'s explicit rule against
exactly this ("This prevents sector-label inconsistencies... from diverging across files"). Table
4 and all sector-level statistics below merge these pairs for analysis; the underlying CSVs are
left untouched per the read-only rule.

---

## 2. Headline adoption statistics — two denominators, clearly labelled

| Metric | Denominator A: all 100 FTSE 100 | Denominator B: 87 evidence-based only |
|---|---|---|
| Companies with **disclosed** operational GenAI use case | 38 / 100 = **38.0%** | 38 / 87 = **43.7%** |
| Companies with **null result** (no qualifying evidence) | 49 / 100 = **49.0%** | 49 / 87 = **56.3%** |
| Companies **blocked** (status unresolved) | 13 / 100 = **13.0%** | n/a (excluded from B by definition) |

**Neither denominator is "the" correct answer** — Denominator A is the honest population-level
statement (includes the unknown-status companies as unknown, not as null); Denominator B describes
adoption only among companies this project actually reached a verdict on. Every headline statistic
in the eventual report should state which denominator is in use. See §8 for the full sensitivity
analysis of what the 13 blocked companies could do to Denominator A.

**Distribution of disclosed use cases per company** (among the 38 companies with ≥1):

| Disclosed use cases | Companies |
|---|---|
| 1 | 26 |
| 2 | 6 |
| 3 | 4 |
| 4 | 2 |

Most adopting companies (26/38 = 68%) have exactly one disclosed use case. A small number of
companies with the richest, most itemised disclosures (BT Group and RELX with 4 disclosed rows
each; AstraZeneca, Diageo, Aviva and BAE Systems with 3 each; Vodafone Group, HSBC, Standard
Chartered, Schroders, Hiscox and Lion Finance Group with 2 each — 12 companies with 2–4 disclosed
rows in total) disproportionately shape the operational-use-case totals; see §5.

---

## 3. Operational use-case categories (business function, deployment stage, orientation)

Full breakdown in `table_3_use_case_categories.csv`. Using the project's own coding-manual
categories (no new categories invented):

**Primary business function** (n=58): customer_service 10 (17%); knowledge_document_work 9 (16%);
other 8 (14%); research_development 6 (10%); risk_legal_compliance 6 (10%); software_development_it
5 (9%); product_service_innovation 4 (7%); marketing_content 3 (5%); operations_supply_chain 2
(3%); cybersecurity 2 (3%); sales 2 (3%); human_resources 1 (2%).

The large "other" category (8 rows, 14%) is almost entirely general-purpose internal productivity
Copilot-style rollouts with no single named function (e.g. Barclays', Severn Trent's, Standard
Chartered's SC GPT, NatWest's AI Digital Enabler, Schroders' Genie, Aviva's/Convatec's/Segro's
company-wide rollouts) — these are real, disclosed deployments, but the "task" is deliberately
generic (broad employee productivity), which is itself an analytically meaningful pattern, not a
gap in the coding.

**Deployment stage** (n=58): live_limited 26 (45%); live_scaled 24 (41%); pilot 8 (14%). **86% of
disclosed use cases are already live in some form** (limited or scaled), not merely planned or
piloted — consistent with the strict evidence bar requiring a detailed operational description.

**Orientation** (n=58): internal 32 (55%); customer_facing 11 (19%); product_embedded 9 (16%);
mixed 6 (10%). Internal employee-productivity use still dominates, though less exclusively than
first recorded (corrected 2026-08-09: 3 of 58 rows moved from internal to mixed after their
quotations were found to name an external party the original coding missed --
`outputs/analysis/disclosed_use_case_spot_check.md`).

**User group** (n=58): employees 32 (55%); customers 19 (33%); mixed 5 (9%); suppliers_or_partners
1 (2%); developers 1 (2%). (Same 2026-08-09 correction as orientation, above.)

**Technology partner** (named, n=58, some rows list more than one): Microsoft 13 (22%, by far the
most frequently named — mostly Microsoft 365/GitHub Copilot variants); AWS/Amazon 5 (9%); Google
4 (7%); no external partner named (proprietary/in-house or unclear) 12 (21%). This directly matches
`01_PROJECT_BRIEF.md` subquestion 5 ("which model providers and technology partners are most
frequently named") — Microsoft's Copilot family is the single dominant technology signature in
this dataset.

**Correction (2026-09-05):** the AWS and Google counts above were originally undercounted, both
for the same reason — the same vendor recorded under more than one text label. AWS/Amazon was
recorded as "AWS" 3 (5%) "plus 1 more" 1, missing a third variant entirely; the true count is
**5** (**9%**), across three distinct labels: "AWS" (BT-UC-001, BT-UC-002, BT-UC-004, all BT
Group), "Amazon Web Services (AWS)" (AZN-UC-003, AstraZeneca), and "Amazon AWS (also named:
Phantom, Hybrid Software, GMG, Roland DG)" (DGE-UC-001, Diageo). Google was originally recorded
as "3 combined," missing REL-UC-001's multi-partner row ("Anthropic; Google; OpenAI (underlying
model providers)"), which a plain "Google Cloud" string match does not catch; the true count is
**4** (**7%**): HSBA-UC-001 (HSBC), RTO-UC-001 (Rentokil Initial), HSX-UC-001 (Hiscox), and
REL-UC-001 (RELX).

**Claimed benefits** (multi-label, n=58 rows): productivity 29 (50%); time_saving 25 (43%);
service_quality 8 (14%); personalisation 4 (7%); accuracy 4 (7%); risk_reduction 3 (5%);
none_stated 3 (5%); accessibility 3 (5%); innovation 2 (3%); cost_reduction 2 (3%).
**`claimed_benefits` is a multi-select field: a use case can carry more than one claimed benefit.**
**25** of the **58** rows carry more than one value (e.g. `time_saving;productivity`), for **83**
total benefit labels across 58 rows — which is why the percentages above sum to well over 100%,
correctly.

**Benefit evidence** (n=58): expected 23 (40%); observed_unquantified 24 (41%); measured 11
(19%) — of which 8 are company-reported operational figures (though ranging from BGEO's five
precise metrics to REL-UC-002's unaveraged "up to 66%" ceiling), 1 is a self-reported employee
survey (AstraZeneca), 1 is a single-employee anecdote from vendor marketing material
(Hiscox/Microsoft), and 1 is a vague order-of-magnitude estimate (Centrica). See §6 for the full
distribution and `outputs/analysis/disclosed_use_case_spot_check.md` for the row-by-row basis and
the 2026-08-09/2026-08-11 recheck that corrected this from an original count of 1 measured row to
11, then split those 11 into four evidentiary tiers.

---

## 4. Task-based analysis: does the observed operational use fit the "suitable LLM task" criteria?

Each of the 58 disclosed use cases was individually read and classified against three axes: (a)
**input type** — is the model's input genuinely unstructured natural language, or structured/
non-language data pressed into a generative pipeline?; (b) **output type** — is the output
genuinely interpretive/generative (drafting, summarising, conversing, synthesising), or does the
underlying task lean toward classification/analytics with generation as a wrapper?; (c) **cost of
error** — what happens if the output is wrong: low (internal, human-reviewed, easily corrected),
medium (customer-facing or process-relevant but not safety/financial-critical), or high
(financial, legal, medical, safety, or security stakes). Full row-by-row classification in
`table_3b_task_suitability_detail.csv`.

| Axis | Result | Share |
|---|---|---|
| Input: unstructured language | 47 / 58 | 81% |
| Input: structured/non-language (e.g. simulation data, algorithmic parameters, image/design generation) | 8 / 58 | 14% |
| Input: mixed | 3 / 58 | 5% |
| Output: generative/interpretive | 54 / 58 | 93% |
| Output: mixed or classification-leaning | 4 / 58 | 7% |
| Cost of error: low | 29 / 58 | 50% |
| Cost of error: medium | 18 / 58 | 31% |
| **Cost of error: high** | **11 / 58** | **19%** |

**"Classic good fit"** (unstructured language input + generative/interpretive output + low-or-medium
cost of error, simultaneously): **37 / 58 = 64%**. This is the pattern the thesis would predict
companies gravitate toward, and it is indeed the modal pattern — but it is not the overwhelming
majority; more than a third of disclosed use cases sit outside this "textbook" zone.

**The 11 high-cost-of-error use cases (19% of the dataset) are the most analytically important
group for the task-suitability question.** They are: RELX's Lexis+/Protege legal research,
PharmaPendium regulatory intelligence, and ClinicalKey AI clinical assistant (3 use cases — legal,
regulatory and clinical domains where hallucination has caused real, publicised incidents
elsewhere in the market); Aviva's GP medical-report summarisation for underwriting; Schroders'
GAiiA investment analyst; Hiscox's Gemini-powered underwriting-pricing model; Shell/SparkCognition's
subsurface exploration imaging; HSBC/Google Cloud's financial-crime-and-decision-assistant
partnership; and all three of BAE Systems' defence use cases (LLM-driven drone command,
Typhoon aircraft maintenance, and cyber-threat insight for customers).

**Pattern observed in these high-stakes cases:** every one pairs the generative capability with an
explicit mitigating control rather than deploying it as an autonomous decision-maker — human
underwriter/analyst review is retained (Hiscox drafts a broker email "for underwriter review";
Schroders' tool "assists" analysts who draft summaries; Aviva's tool converts reports into
"decision-ready insights," implying human sign-off), source grounding/citation is used to reduce
hallucination risk (RELX's PharmaPendium and Lexis+ both cite sources; BAE's Typhoon assistant
gives "references to exactly where it found the information"), and/or extensive pre-launch
validation is disclosed (RELX's ClinicalKey AI was "tested by more than 30,000 physicians before
launch"). **This is the single most direct empirical support in the dataset for the thesis**:
these companies are not treating "the task involves language, therefore an LLM is fine" as
sufficient — they are visibly layering additional controls onto exactly the use cases where the
task-suitability framework would predict the naive approach is riskiest.

**The 8 structured/non-language-input use cases (14%)** are a genuinely different pattern worth
flagging separately rather than folding into "good fit": Rolls-Royce/Databricks' cGAN engine-design
generation, Shell/SparkCognition's seismic-image generation, Diageo's bottle-personalisation and
cocktail-recommendation platforms, Tesco's ad-creative generator, Auto Trader's vehicle-description
writer, Intertek/Synthesia's training-video generator, and AstraZeneca's foundation-model
hypothesis generation from real-world-evidence data. These are legitimate, disclosed generative-AI
deployments (they meet `is_genai=yes` on named-model or generation-of-content grounds), but the
*input* is not "unstructured language" in the classic sense — it is structured data, design
parameters, or guided-selection inputs. **The dataset therefore does not support a claim that
GenAI adoption is confined to natural-language-input tasks**; a meaningful minority of disclosed
uses are multimodal/design-generation applications the "unstructured language input" criterion
does not neatly cover, which is itself relevant to how the report frames the suitability
framework's scope.

**What the dataset cannot show:** none of the 58 use cases includes a rigorous, independently
verified before/after controlled comparison — the 11 rows coded `measured` are not uniformly
strong evidence either (see §6 for the full four-tier breakdown: 8 aggregate company-reported
figures, 1 self-reported survey, 1 vendor-sourced anecdote, 1 vague magnitude estimate), and none
is audited or externally validated. The task-suitability classification above is a structural judgement about the *kind* of
task, not a verdict on whether each deployment is actually succeeding. **The thesis is about
selecting tasks appropriately, not about proving those tasks are always executed well — this
dataset can speak to the former far more confidently than the latter.**

---

## 5. Strategic/governance evidence vs actual operational deployment

| Group | Companies | Share of 87 |
|---|---|---|
| ≥1 disclosed operational use case | 38 | 43.7% |
| ≥1 strategic-capability-building finding (`strategic_capability_building_findings.csv`) | 33 | 37.9% |
| ≥1 governance/enablement finding (`governance_and_enablement_findings.csv`) | 50 | 57.5% |
| **Any** of the above three | 65 | 74.7% |
| **Strategic or governance evidence, but NO disclosed operational use case** | **27** | **31.0%** |
| **No qualifying evidence of any kind** (no strategic, governance or operational finding) | 22 | 25.3% |

The 27 "talk without disclosed deployment" companies include 3i, Aberdeen Group, Admiral Group,
Airtel Africa, Anglo American, Babcock International, Beazley, British American Tobacco, Bunzl,
Coca-Cola Europacific Partners, DCC plc, Diploma, Fresnillo, Howdens Joinery, IG Group, IHG Hotels
& Resorts, Informa, Intermediate Capital Group, International Airlines Group, JD Sports, Prudential
plc, Smiths Group, St. James's Place, Standard Life, Tritax Big Box REIT, Weir Group, and
Whitbread. This directly answers `01_PROJECT_BRIEF.md` subquestion 2 (proportion of live vs
planned/ambition-only disclosures) at the company level: **roughly 3 in 10 evidence-based
companies discuss AI strategy or governance without a single use case meeting this project's
operational bar.** Full list in `table_5_strategic_governance_vs_operational.csv`.

---

## 6. Evidence quality

| Field | Value | n | Share |
|---|---|---|---|
| evidence_strength (all 63 use-case rows) | 3_strong | 27 | 43% |
| | 2_moderate | 34 | 54% |
| | 1_weak | 2 | 3% |
| evidence_strength (58 **disclosed** rows only) | 3_strong | 27 | 47% |
| | 2_moderate | 31 | 53% |
| confidence (58 disclosed rows) | high | 30 | 52% |
| | medium | 28 | 48% |
| evidence_origin (58 disclosed rows) | company_primary | 49 | 84% |
| | technology_partner | 9 | 16% |
| benefit_evidence (58 disclosed rows) | expected | 23 | 40% |
| | observed_unquantified | 24 | 41% |
| | measured — aggregate_company_reported | 8 | 13.8% |
| | measured — survey_sample_self_reported | 1 | 1.7% |
| | measured — single_anecdote_vendor_sourced | 1 | 1.7% |
| | measured — imprecise_magnitude_single_example | 1 | 1.7% |
| | **measured (total)** | **11** | **19%** |

**Correction (2026-08-09, refined 2026-08-11):** `benefit_evidence` was originally recorded as
expected 32/55%, observed_unquantified 25/43%, measured 1/2%. A full-population recheck of all 58
quotations against the coding manual's own definition of `measured` ("quantified outcome with
defined metric or comparison") found 10 rows miscoded as `expected` or `observed_unquantified`
despite their quotation containing an explicit benefit-quantifying figure (e.g. RELX's "66
percent" time savings, Lion Finance Group's "6,600 hours per month...10% to 56%...40% reduction").
A second pass then split the resulting 11 `measured` rows into four evidentiary tiers, since
"measured" was masking real differences in evidence quality — an operational, company-wide metric
(Lion Finance Group's enterprise-platform figures) is not the same kind of evidence as a
self-reported employee survey (AstraZeneca), a single employee's account in a vendor's marketing
case study (Hiscox), or a vague "hundreds of hours" estimate (Centrica). Full row-by-row detail,
including the reasoning for numbers that were deliberately *not* reclassified (deployment-scale/reach
figures such as "70,000 employees" or "one million occasions" do not quantify a benefit), is in
`outputs/analysis/disclosed_use_case_spot_check.md`. The figures below use the corrected counts.

**Interpretation for reliability of conclusions:** the disclosed dataset is skewed toward
`2_moderate`/`3_strong` by construction (that is the inclusion rule), so this is not an
independent quality check — but within that filtered set, roughly half (53%) rest on `2_moderate`
evidence, meaning "the specific use case is clear, but scale, stage or outcomes are incomplete"
per the coding manual's own definition. Even with the corrected count, 81% of claimed benefits
are either purely anticipated or observed-but-unquantified, and the 19% that are `measured` are
not uniformly solid, and don't reduce to a single quality tier: 8 of the 11 draw on
company-reported operational data (usage logs, adoption tracking), but that group itself ranges
from BGEO-UC-002's five precise, independent metrics to a ceiling figure with no stated average or
sample size (RELX). The remaining 3 rest on a self-reported employee survey (AstraZeneca), one
named employee's account in a vendor's own marketing case study (Hiscox), and a rough, unsupported
magnitude (Centrica). None of the 11 — including the 8 operational-data rows — is independently
audited; all are self-reported by the company or its technology partner. **This dataset is
better-suited to answering "is the company doing X with generative AI" than "is X working" or "how
much value did X create," even after this correction.** Any report language about productivity
gains, efficiency improvements, or ROI must be attributed explicitly to the company's own claim,
not treated as independently verified.

16% of disclosed evidence (9/58 rows) is `evidence_origin=technology_partner` — i.e. sourced from
a vendor/partner case study rather than the company's own disclosure (e.g. Investec's Copilot for
Sales case study, Hiscox's Microsoft case study, Rolls-Royce's Databricks case study). Per Core
Rule 6, these are preserved with this label rather than treated as company-disclosed; they should
be flagged as such wherever cited in the final report.

---

## 7. Null results: what "completed_null_result" actually means here

**Zero of the 49 null-result companies has reached the project's own strict
`no_disclosure_confirmed` certification.** All 49 remain at `no_disclosure_confirmed =
pending_sources` in `company_summary_template.csv` — the coding manual's own rule states this
value is set "manually by a human reviewer, and only once" a five-point checklist is satisfied,
including that no collection field is left at `not_started`. Investigating why, three distinct
counts (corrected 2026-09-05 — these were previously conflated into a single "47 of 49" figure,
which combined two different conditions as though they were one):
- **46** of the **49** have both `annual_report_latest_collected` and
  `annual_report_previous_collected` set to `collected` (i.e. both required annual reports were
  obtained and reviewed). The other **3** (Admiral Group, Melrose Industries, F&C Investment
  Trust) each have at least one annual report still at `not_started`.
- **47** of the **49** have `separate_sustainability_report_collected` still at `not_started` —
  never advanced to `collected`, `unavailable`, or `not_applicable`, even in cases where
  sustainability content is plausibly integrated into the collected annual report (the coding
  manual explicitly permits `not_applicable` for exactly this scenario, but the field was never
  updated to reflect it). The other **2** (Informa, Whitbread) have this field marked `collected`.
- **44** of the **49** satisfy *both* conditions at once (both annual reports collected, and the
  sustainability field still `not_started`) — this is the correct joint figure; it is smaller
  than either individual count above because the 3-company and 2-company exception groups do not
  fully overlap.

`official_web_search_completed` is `incomplete` for 5 of the 49.

**Practical reading:** for **46** of the **49** null-result companies, the core, highest-value
sources (both years' annual reports) were genuinely collected and reviewed with no qualifying
generative-AI disclosure found — this is real negative evidence, not an absence of effort. But
none of them has been through the exhaustive, multi-source, human-certified closure process the
project's own methodology defines as sufficient to assert "no disclosure confirmed." **The report
must state "no qualifying evidence was identified in the collected and reviewed sources for this
company," not "this company does not use generative AI."** A company may use generative AI
internally without any external disclosure reaching the sources collectable within this project's
window and toolset, or the disclosure may exist in a source category (e.g. a dedicated
sustainability report, an investor presentation, a press release) that was not exhaustively pursued
for that specific company.

---

## 8. Blocked-company sensitivity analysis

The 13 blocked companies, with sector (merged labels) and blocker type:

| Company | Sector | Blocker |
|---|---|---|
| Lloyds Banking Group | Banks | Cloudflare block (persistent) |
| BP | Oil & gas producers | HTTP 403 (persistent) |
| Unilever | Personal goods | HTTP 403 (persistent) |
| Sage Group | Software & computer services | HTTP 403 (persistent) |
| Compass Group | Support services | HTTP 403 (persistent) |
| Imperial Brands | Tobacco | HTTP 403 (persistent) |
| Haleon | Pharmaceuticals & biotechnology | HTTP 403 (persistent) |
| Computacenter | Software & computer services | Timeout (persistent) |
| Associated British Foods | Food & tobacco | HTTP 403 (persistent) |
| Burberry Group | Personal goods | HTTP 403 (persistent) |
| M&G | Financial services | AES-encrypted PDF (download succeeds, extraction blocked) |
| IMI | Industrial engineering | HTTP 403 (persistent) |
| Coca-Cola HBC | Beverages | HTTP 403 (persistent) |

**Statistic A (all 100 FTSE 100 constituents):** 38/100 = **38.0%** disclosed operational adoption.
**Statistic B (87 evidence-based companies only):** 38/87 = **43.7%**.

**These 13 companies should not be assumed to resemble the 87 that were researched.** Two
specific reasons this project's own records give for caution, not for assuming either a higher or
lower true rate:

1. **Sector composition is not representative of the full population.** Banks (where the 4
   researched companies show 100% disclosed adoption) contain one blocked company (Lloyds); if
   Lloyds followed the observed within-sector pattern it alone would move Denominator A by a full
   percentage point, but this is speculation, not evidence — no Lloyds-specific GenAI disclosure
   was ever verified.
2. **The manual-browser queue itself records specific, named, unverified leads for several
   blocked companies** that — if eventually disclosed — could plausibly qualify: BP's "Wells
   Assistant" (described in an unreachable BP speech as an LLM-based automated-upstream tool);
   Sage's "Sage Copilot," a named generative-AI product with an unreachable one-year-anniversary
   press release; Unilever's AI-driven product-photography tooling. None of these could be
   independently verified this session (§ blocked-queue notes), so **none is counted**, but their
   existence as leads means the 13 blocked companies are not a random, evidence-free set — they
   are disproportionately companies with *some* signal of GenAI activity that this project could
   not confirm to its evidentiary standard.

**Illustrative (not predictive) bounds**, purely to show the scale of what remains genuinely
unknown:

| If this many of the 13 blocked companies would qualify | Statistic A becomes |
|---|---|
| 0 | 38.0% |
| 2 | 40.0% |
| 4 | 42.0% |
| 6 | 44.0% |
| 13 (all) | 51.0% |

**The correct scientific statement is: the true FTSE 100 disclosed-adoption rate lies somewhere
in the closed interval [38.0%, 51.0%], and this project's tools cannot narrow that interval
further.** 38.0% is a firm, evidence-based floor; 51.0% is a logical ceiling; the true value is
unknown and should not be estimated by extrapolating from the 87 researched companies, precisely
because the 13 blocked companies were not blocked at random (many are large, disclosure-averse
consumer/industrial conglomerates whose access-restriction pattern may correlate with broader
communications practices, not with GenAI adoption specifically — but this too is speculation the
dataset cannot resolve).

---

## 9. Limitations and potential bias (methodology-supported only)

1. **Official-source dependence.** The project's own inclusion rule requires company-primary or
   named-technology-partner sourcing; this systematically favours companies with detailed, English-
   language, easily-discoverable annual reports over companies that disclose GenAI use through
   channels this project's toolset does not reach (internal comms, non-English filings, investor
   calls without transcripts).
2. **Inaccessible domains (the 13 blocked companies), §8.** A structural, not random, gap.
3. **Selection/availability of public evidence.** A company that genuinely deploys GenAI but
   chooses not to disclose it publicly is indistinguishable in this dataset from a company that
   does not use it at all — the project measures *disclosed* adoption, not *actual* adoption.
4. **Disclosure-practice differences across companies and sectors** may drive as much of the
   sector variation in §Table 4 as true adoption differences (e.g. financial-services and media
   companies may simply have stronger disclosure cultures around technology than mining or tobacco
   companies, independent of actual GenAI use).
5. **Evidence-strength variation (§6).** Roughly half of disclosed use cases rest on `2_moderate`
   evidence; 11 of 58 rows have a measured, quantified outcome (corrected 2026-08-09, was recorded
   as 1), but they span a real range of evidentiary strength — 8 company-reported operational, 1
   self-reported survey, 1 single-employee vendor anecdote, 1 vague magnitude estimate — and none
   is independently audited.
6. **Likely under-reporting of internal deployments.** Given that 55% of disclosed use cases are
   already internal/employee-facing rather than customer-facing (corrected 2026-08-09, was
   recorded as 60%), and companies have limited
   incentive to publicise every internal tool, the true incidence of narrow, low-profile internal
   GenAI tools is almost certainly higher than what reaches annual-report-level disclosure.
7. **Null-result interpretation (§7).** Documented as "no qualifying evidence in reviewed sources,"
   not "no GenAI use," and none of the 49 null companies has reached the project's own strict
   closure certification.
8. **Sector-level small samples (§Table 4).** The majority of sector cells contain 1–4 companies;
   18 of the ~38 distinct sector labels have only one company in the entire researched-plus-blocked
   population. No sector-level claim in this memo or the eventual report should be treated as
   statistically robust below roughly n≥4–5 per sector, and even those should be described as
   descriptive/indicative, not inferential.
9. **Checkpoint/tracking-artifact drift (§1).** The session-level tracking checkpoint's
   "promoted_complete" label diverged from the dataset's own operational-use-case definition for 9
   companies over the project's multi-session history — a reminder that any number sourced from
   project tracking metadata (rather than the primary datasets) should be independently
   re-verified before use, exactly as this memo did.
10. **Sector-label data-quality gap (§1).** Two case-inconsistent sector-label pairs survived
    despite an explicit coding-manual rule against them — a small but real illustration that even
    carefully specified controlled vocabularies can drift in a long-running, multi-session project.
11. **claimed_benefits field reliability.** This field may in some rows reflect the coder's
    plausible inference from a tool's described function (e.g. inferring `productivity` from a
    quote that only describes what a tool does), rather than a benefit the company explicitly
    stated in the source text. This pattern was noted in at least 6 of the 20 rows in the random
    spot-check sample (`outputs/analysis/disclosed_use_case_spot_check.md`) — Tesco, GSK, Standard
    Chartered, SSE, Severn Trent, and London Stock Exchange Group — but has not been independently
    re-audited across all 58 rows this session. Treat `claimed_benefits` distributions in this
    report as indicative, not verified to the same standard as `benefit_evidence`.

---

## 10. Key findings (5–8, for the report's backbone)

1. **Disclosed operational GenAI adoption reaches 38.0% of the full FTSE 100 (38/100) and 43.7% of
   the 87 companies with an evidence-based final status.** *Qualification:* the true population
   rate could be as high as ~51% if all 13 blocked companies qualified (§8) — this is a floor, not
   an estimate of the true rate.
2. **Internal employee-productivity tools dominate the disclosed use-case landscape**: 55% of
   disclosed use cases (32/58) are internally oriented, 55% (32/58) serve employees as the primary
   user group (both corrected 2026-08-09 from an original 60%/35/58 each — 3 rows moved to
   `mixed` after their quotations were found to name an external party too), and Microsoft
   (chiefly via Copilot variants) is named in 22% of disclosed use cases (13/58) — more than any
   other single technology signature. *Qualification:* this reflects what
   companies choose to disclose, which may itself favour headline-grabbing enterprise-software
   rollouts over quieter, more specialised internal tools.
3. **Talk exceeds deployment**: 74.7% of evidence-based companies (65/87) show some AI-related
   evidence (strategic, governance, or operational), but only 43.7% (38/87) have a disclosed
   operational deployment — meaning 31.0% of the evidence-based sample (27/87) discusses AI
   strategy or governance with no disclosed use case. *Qualification:* "no disclosed use case"
   reflects this project's strict evidentiary bar, not proof the company has literally deployed
   nothing.
4. **The task-suitability framework is broadly, but not overwhelmingly, supported by the observed
   pattern of use**: 64% of disclosed use cases (37/58) combine unstructured language input,
   generative/interpretive output, and low-or-medium cost of error — the "classic good fit"
   pattern. *Qualification:* more than a third of disclosed use cases (21/58) fall outside this
   pattern, split between structured/non-language-input applications (14%) and higher-stakes,
   more-controlled deployments (19%) — the framework describes a *tendency*, not a rule the data
   universally obeys.
5. **The 19% of use cases (11/58) with high cost of error are consistently paired with mitigating
   controls** — human review, source-grounded/citation-backed outputs, or extensive pre-launch
   validation — rather than being deployed as unmitigated autonomous decision-makers. *Qualification:*
   this is the strongest single piece of evidence in the dataset for the selective-deployment
   thesis, but it describes disclosed design choices, not independently verified safety outcomes.
6. **A minority of claimed benefits are measured, and they vary considerably in evidentiary
   strength**: 11 of 58 disclosed use cases (19%, corrected 2026-08-09 from an original count of
   1/58) carry a quantified benefit figure — 8 from company-reported operational data, 1 from an
   employee survey, 1 a single vendor-sourced anecdote, and 1 a vague magnitude estimate; 40% are
   merely "expected." *Qualification:* none of the 11 is independently audited, and even the 8
   operational-data figures range from precise multi-metric disclosures (Lion Finance Group) to
   unaveraged ceiling claims (RELX) — this dataset still cannot support any claim about GenAI's
   actual, verified productivity or financial impact at FTSE 100 companies, only about what
   companies report having measured or say they expect.
7. **Sector adoption varies widely (Banks 100%, Media 75%, Mining 17% among sectors with ≥3
   researched companies) but nearly every sector cell is too small for statistical inference.**
   *Qualification:* differences plausibly reflect disclosure culture and business-model fit as
   much as true underlying adoption gaps; no sector ranking in this memo should be over-interpreted.
8. **Null results and blocked companies together account for 62% of the full FTSE 100 (49 null +
   13 blocked = 62/100)**, and neither group can be safely treated as "disclosed non-adopters."
   *Qualification:* the true adoption rate for the FTSE 100 as a whole remains genuinely
   uncertain; this project can defensibly claim a floor of 38%, not a point estimate.

---

## 11. Assessment of the central thesis

> "Companies should deploy LLMs/GenAI selectively according to the characteristics of the task,
> rather than assuming that any task involving language is automatically suitable for an LLM."

**Evidence supporting the thesis:**
- The modal, most common pattern of disclosed deployment (64%, §4) is exactly the "good fit"
  profile the thesis would predict: unstructured language in, generative/interpretive language
  out, low-or-medium consequence if wrong.
- Where companies do deploy GenAI into high-cost-of-error tasks (19% of use cases), the
  disclosures consistently show additional controls layered on top — human review, grounding/
  citation, pre-launch validation at scale — rather than blanket, unmitigated deployment. This is
  observable, disclosed behaviour consistent with task-sensitive deployment design, not merely
  companies claiming caution in the abstract.
- The existence of a substantial "talk without deployment" group (31% of evidence-based companies,
  §5) and a majority of use cases still at `live_limited` or `pilot` stage (59%, §3) is at least
  consistent with — though it does not prove — companies being deliberate/cautious about scope
  rather than deploying GenAI everywhere language appears.

**Evidence that complicates the thesis:**
- A meaningful minority of disclosed use cases (14%, §4) apply generative techniques to
  structured, non-language inputs (design generation, image synthesis, guided-parameter
  personalisation) — the thesis as stated is framed around *language* tasks, and this slice of
  the dataset sits partly outside that frame, suggesting real-world GenAI adoption is not neatly
  bounded by "is the input language."
- More than a third of disclosed use cases (36%, §4) fall outside the "classic good fit" pattern
  entirely — either by input type, output type, or cost-of-error — yet were still disclosed as
  live, operational deployments. If task-fit criteria were being applied strictly and
  consistently across the FTSE 100, one might expect a narrower, more homogeneous set of
  disclosed uses; the dataset instead shows real heterogeneity, including genuine live deployment
  in some of the highest-stakes categories (insurance-pricing underwriting, drone command).
- The dataset documents *what companies disclose about deployment*, not *how well matched the
  task actually is* or *whether the deployment succeeds*. A company pairing a high-stakes use
  case with "human review" language is disclosing an intended control, not proof the control is
  effective — this project cannot distinguish genuine selective-deployment discipline from
  reassuring boilerplate risk language.

**Claims the dataset cannot establish:**
- Whether companies that deploy GenAI into poorly-suited tasks experience worse outcomes than
  those that deploy it into well-suited tasks (no independently audited outcome/failure data
  exists in this dataset — even the 19% of rows with a measured benefit figure rely on the
  company's own self-reported measurement). See #6, §6/§10.
- Whether the observed pattern reflects deliberate task-suitability reasoning by companies, or
  simply reflects which tasks happen to be easiest/cheapest/least risky to disclose publicly.
- Any claim about the true FTSE 100-wide picture, given the unresolved 13-company gap (§8) and the
  non-certified status of all 49 null results (§7).

**Overall assessment:** *the evidence in this dataset is genuinely, moderately supportive of the
thesis — not because it proves selective deployment causes better outcomes (it cannot), but
because the observed pattern of what companies actually deploy, and how they deploy it, is more
consistent with task-sensitive behaviour than with indiscriminate "any language task will do"
deployment.* The report should present this as a real but bounded finding, explicitly naming the
minority of cases (structured-input uses; the 36% outside "classic good fit") that complicate a
simple version of the thesis, and explicitly declining to make any claim about deployment success
or failure that the dataset cannot support.

---

## 12. Recommended report structure and where these findings belong

| Section | Content from this analysis |
|---|---|
| **Introduction** | Research question (`01_PROJECT_BRIEF.md`), why FTSE 100, why generative AI specifically (not AI broadly) |
| **Research question** | "How are FTSE 100 companies using generative AI?" plus the 7 brief subquestions |
| **Conceptual framework** | The three-part task-suitability framework (§4) — state it explicitly as an analytical lens applied *to* the dataset, not a pre-coded field |
| **Methodology** | §0 methodology reminder; unit of analysis; inclusion/exclusion criteria; evidence window; population/date rule |
| **Source selection** | Company-primary-first sourcing; technology-partner case studies labelled distinctly (§6); the 13 blocked companies and why (§8, §9.2) |
| **Coding framework** | `03_CODING_MANUAL.md` summary: is_genai test, deployment stage, evidence strength/confidence, controlled vocabularies |
| **Definition of operational GenAI use** | The strict `disclosed_use_case_count` rule (§0); explicitly distinguish from provisional/strategic/governance (§5) |
| **Results** | §1–§3 coverage and headline stats; §Table 3 use-case categorisation; Table 1/2 |
| **Sector/use-case analysis** | §Table 4 sector comparison with explicit small-sample caveats (§9.8); §3 business-function/deployment-stage breakdown |
| **Discussion** | §4 task-suitability analysis in full; §5 strategic-vs-operational gap; §11 thesis assessment |
| **Limitations** | §9 in full, plus §1's two data-quality/tracking notes |
| **Implications** | What the 64%/36% split and the high-stakes-mitigation pattern (§4) suggest for how companies (and this report's likely readers) should think about GenAI deployment decisions — framed as *interpretation*, clearly separated from the *evidence* |
| **Conclusion** | Restate §11's bounded assessment: moderate, real support for selective deployment, with named complicating evidence and named unanswerable questions |

---

## Files created in this analysis phase

- `outputs/analysis/ANALYSIS_MEMO.md` — this document
- `outputs/analysis/table_1_coverage.csv` — FTSE 100 research coverage/status
- `outputs/analysis/table_2_adoption.csv` — operational GenAI adoption, both denominators
- `outputs/analysis/table_3_use_case_categories.csv` — business function / deployment stage / orientation / user group / partner / benefit distributions
- `outputs/analysis/table_3b_task_suitability_detail.csv` — row-by-row task-suitability classification of all 58 disclosed use cases
- `outputs/analysis/table_4_sector_comparison.csv` — sector-level researched/disclosed/use-case/null/blocked counts (sector labels merged for the case-inconsistency noted in §1), with a small-sample flag column
- `outputs/analysis/table_5_strategic_governance_vs_operational.csv` — the six comparison-group counts
- `outputs/analysis/table_5b_company_lists.csv` — the actual company names in the "strategic/governance but no operational" and "zero qualifying evidence" groups
- `outputs/analysis/table_6_evidence_quality.csv` — evidence_strength/confidence/benefit_evidence/evidence_origin distributions
- `outputs/analysis/table_7a_blocked_companies.csv` — the 13 blocked companies and their sectors
- `outputs/analysis/table_7b_blocked_sensitivity_bounds.csv` — illustrative bounds for Denominator A under different blocked-company-qualification scenarios

No file in `outputs/intermediate/analysis_snapshot_2026-08-08_final_closure/` or any of the six
underlying project datasets was modified in producing this memo.
