# How Are FTSE 100 Companies Using Generative AI?

**Status: final.**

## Table of contents

- [Introduction](#introduction)
- [Methodology and Limitations](#methodology-and-limitations)
- [Results](#results)
- [Discussion](#discussion)
- [Conclusion](#conclusion)

---

# Introduction

*Every number below restates a figure already established and verified in the Methodology,
Results, or Discussion sections; nothing new is computed here.*

## The research question

This report investigates **how FTSE 100 companies are implementing generative AI, and what
measurable and unintended consequences that implementation has had**. That two-part framing is
deliberate. A great deal of public commentary about corporate AI adoption asks only the first
half — which companies have deployed what — and treats disclosure of a deployment as if it were
evidence the deployment is working, or evidence that nothing has gone wrong with it. This report
treats those as three separate questions, requiring three separate kinds of evidence, and reports
each on its own terms rather than assuming an answer to one implies an answer to the others.

**FTSE 100** companies are a natural population for this question. They are large, closely
covered, and under continuous pressure — from investors, regulators, and the press — to describe
their use of new technology in public filings, annual reports, and press communications. If any
set of companies were going to leave a detailed, comparable public record of generative-AI
adoption, it would be this one. What that record does and does not contain is the subject of this
report.

## What this report does

This report builds and analyses a dataset of publicly disclosed generative-AI use cases across
the **100** constituents of the **FTSE 100** following its **19 June 2026** index reconstitution,
covering disclosures from **1 January 2023** to **14 July 2026**. Every use case in the dataset
meets an explicit inclusion bar: the source must name generative AI, an LLM or foundation model,
or an unambiguously generative product, or describe generation of text, code, images, or audio
through a clearly identified generative model. Predictive or classification-based AI, ordinary
automation, and vague references to "AI" without a generative-specific signal are excluded.

Of the **100** companies in the population, **87** were researched to a full, evidence-based
verdict; the remaining **13** could not be, for reasons detailed in the Limitations section. Among
the **87**, **38** disclosed at least one qualifying generative-AI use case, for **58** distinct
disclosed use cases in total. Every figure in this report is stated against one of two
denominators — the full population of **100**, or the **87** companies actually reached a verdict
on — and the Methodology and Results sections state throughout which of the two is in use for any
given figure.

The report's central finding, argued in full in the Discussion section, is that these three
questions — what was implemented, whether it worked, and what it may have cost or broken — are
answerable to very different degrees from the same public record. Implementation can be described
in comparable, codable detail across the **58** disclosed use cases. Measurable outcomes are
disclosed for a minority of them, and unevenly even within that minority. Unintended consequences
are almost entirely undisclosed, for reasons this report can identify precisely rather than merely
note. That asymmetry — not the adoption figure on its own — is this report's principal
contribution.

## How the report is organised

The **Methodology** section sets out the population, evidence window, inclusion criteria, source
discovery process, and coding framework, including several corrections made to the underlying
analysis during this project's own review of its work. The **Limitations** section states, with
specific figures rather than general caveats, what this dataset's evidentiary boundaries are. The
**Results** section reports what was found: adoption rates, the composition of the **58**
disclosed use cases, the evidentiary strength behind claimed benefits, and the near-absence of
disclosed unintended consequences. The **Discussion** section argues the report's central finding
from those results, and separately introduces a secondary, explicitly-labelled analytical lens —
a task-based classification of the **58** disclosed use cases — used to describe the *kind* of
work being implemented, not to reframe the report's central question.

---

# Methodology and Limitations

## Methodology 1. Research question and the claim under examination

Building on the research question set out in the Introduction, this section sets out the
population, evidence window, inclusion criteria, source discovery process, and coding framework
used to answer it. That two-part question — implementation, then consequences — shapes every
methodological choice described below, because the two halves turned out to require very
different kinds of evidence.

The claim this report evaluates is the following: that FTSE 100 companies' public disclosures
describe generative-AI implementation — what has been deployed, where, and by whom — in
reasonably codable detail, but that these disclosures are structurally asymmetric. They say far
less about whether deployments worked, and almost nothing about what they may have cost, broken,
or endangered. If that claim holds, the finding is as much about the state of corporate AI
transparency as it is about AI adoption itself. The methodology below was built to test that
claim directly, not to assume it — the classification scheme separately tracks *what was
deployed*, *what benefit was claimed and how strongly evidenced*, and *what risks or
unintended consequences were disclosed*, precisely so these three questions could be answered (or
found unanswerable) independently of one another.

## Methodology 2. Population and evidence window

The population is the **100** constituents of the FTSE 100 following the **19 June 2026** index
reconstitution, per `ftse100_constituents_2026-06-19.csv` (every row's `membership_effective_date`
is `2026-06-19`) and `01_PROJECT_BRIEF.md` ("Population: companies listed in the FTSE 100
following the 19 June 2026 changes"). The evidence window runs from **1 January 2023** to
**14 July 2026**, per the same brief ("Evidence window: 1 January 2023 to 14 July 2026"), which
also requires both facts to be stated in the final report, "because FTSE 100 membership changes
over time." A company that joined the index after 19 June 2026, or left it before that date,
falls outside the population regardless of its generative-AI activity.

The unit of analysis is a single, distinct, publicly reported generative-AI use case: a
different task, user group, business process, product, or deployment context is counted as a
separate use case even where the same underlying model or vendor tool is involved.

## Methodology 3. Inclusion criterion: what counts as a generative-AI use case

A source qualifies (`is_genai = yes`) only where it does at least one of the following:
explicitly uses the term "generative AI" or "GenAI"; explicitly identifies a large language
model or foundation model; names an unambiguously generative product (**Microsoft 365
Copilot**, **ChatGPT**, **Claude**, **Gemini**, and equivalents); or describes the generation of
text, code, images, or audio through a clearly identified generative model. Predictive or
classification-based machine learning, ordinary automation, and vague references to "AI" without
a generative-specific signal are explicitly excluded, even where a company markets them under an
"AI" or "intelligent" banner.

This bar was applied conservatively throughout. Where a source used generic language such as
"AI-powered" or "AI-driven" for a feature that, on inspection, may plausibly have been
generative, the source was excluded rather than assumed to qualify.

## Methodology 4. Source discovery: what was searched for, and what was not

Two annual reports (the latest available by **14 July 2026**, and the immediately preceding
one) were the required minimum for every company, supplemented by a separate sustainability or
ESG report where one exists as a standalone document, and by a targeted search of each company's
own website and press materials for a fixed, thirty-term keyword list. That list — reproduced in
full in `outputs/analysis/corpus_search_strategy.md` — is composed entirely of technology and
product-name terms (generative AI, LLM, foundation model, named vendor products such as
**Microsoft 365 Copilot** and **Amazon Bedrock**, and related phrases such as "retrieval-augmented
generation"). It contains no terms oriented toward incidents, complaints, litigation, regulatory
enforcement, or workforce/union disclosures.

Regulatory filings, RNS announcements, earnings-call transcripts, and parliamentary or regulator
evidence submitted by a company were all permitted as *optional* source categories under the
project's collection guide, but in practice they were barely used: of the **214** sources
actually logged in the master source manifest, only **1** is a regulatory filing, and **none** is
an earnings-call transcript, despite both being explicitly allowed. The remaining **213**
sources — **84** current annual reports, **82** prior-year annual reports, **26** press releases,
**10** technology-partner case studies, **5** sustainability reports, **4** strategy or technology
webpages, **1** results presentation, and **1** official case study — are, without exception,
company-authored or vendor-promotional material.

This has a direct bearing on what this report can and cannot say. The corpus was built to answer
"what has this company deployed," using sources the company itself (or its technology vendor)
chose to publish. It was never built to surface incidents, failures, complaints, regulatory
findings, or workforce impact, and it did not do so: **no** source in the entire corpus falls
into any of those categories. A near-total absence of unintended-consequence evidence in the
Results section that follows should be read as a property of this corpus, not as evidence that
no such consequences exist. Section 12 below returns to this point as a formal limitation.

The literal search terms typed into any web search during source discovery were not preserved in
any file or log — discovery was carried out interactively, guided by the fixed keyword list and
collection guide above, rather than executed as a scripted, replayable query. This report's
description of "what was searched for" is therefore reconstructed from the collection guide and
from the actual, empirical mix of source types collected (the figures in the paragraph above),
which is the more reliable record of the two.

## Methodology 5. Document reachability and format

Of the **100** companies in the population, **87** were fully researched to an evidence-based
final status and **13** could not be researched to completion. For those **13**, source access
failed before a document could even be opened in the large majority of cases: a persistent
**HTTP 403** error affected **10** companies — **BP**, **Unilever**, **Compass Group**, **Imperial
Brands**, **Haleon**, **Associated British Foods**, **Burberry Group**, **IMI**, **Coca-Cola
HBC**, and **Sage Group**; **Lloyds Banking Group** was blocked by a distinct, persistent
Cloudflare error page rather than a plain HTTP 403; and a persistent timeout affected
**Computacenter**. Only one blocked company, **M&G**, got as far as a successfully downloaded
document: its principal source is an AES-encrypted PDF that downloads correctly but cannot be
extracted with this project's tools. Full detail, including the exact blocker recorded for each
company, is in `outputs/analysis/reachability_audit_blocked_and_null.md`.

Among the **49** companies that were fully researched but yielded no qualifying evidence (the
null-result group), document format was not an obstacle: **47** of **49** had at least one native,
text-extractable PDF successfully processed, and the remaining **2** companies' sources were clean
HTML only. No scanned or image-based PDF was identified in this group by the available diagnostic (an
extracted-text-length check against each source). Optical character recognition (OCR) was never
used anywhere in this project's pipeline, for any company, regardless of format — confirmed
directly in the extraction script's own documentation, not inferred. This matters for
interpreting the null-result group specifically: their absence of qualifying evidence cannot be
attributed to a technical extraction failure. The sources were opened and read; they did not
contain a qualifying disclosure.

## Methodology 6. Coding framework and evidentiary classification

Every candidate use case was coded against a fixed set of controlled-vocabulary fields, including
business function, deployment stage (`pilot`, `live_limited`, `live_scaled`, and related planned
or discontinued states), orientation (`internal`, `customer_facing`, `product_embedded`, or
`mixed`), user group, named technology partner, claimed benefit category, and an evidence-strength
and confidence rating. Coding was reviewed rather than accepted automatically: every promoted row
required an explicit reviewer decision, and evidence strength and confidence were separately
assigned and cross-checked against the supporting quotation before a use case counted toward any
headline figure.

**Benefit evidence** — whether a claimed benefit was merely anticipated (`expected`), reported as
experienced but without a figure (`observed_unquantified`), or reported with a specific number or
comparison (`measured`) — was found, on later audit, to need finer treatment than a single
`measured` category could support. A full re-check of every quotation initially coded `expected`
or `observed_unquantified` found **10** rows whose quotation in fact contained an explicit,
unambiguous benefit figure and had been miscoded; a further review then split the resulting **11**
`measured` rows into four evidentiary tiers, because a single label was masking real differences
in the strength of the underlying evidence. Of the **11**: **8** rest on company-reported
operational or platform data (though this group itself ranges from precise, independently
verifiable multi-metric disclosures to a single unaveraged "up to" ceiling figure with no stated
sample size); **1** rests on a self-reported employee survey; **1** rests on a single named
employee's account published in a technology vendor's own marketing material, not the company's
disclosure; and **1** rests on a vague, unquantified order-of-magnitude estimate tied to one
illustrative example rather than a programme-wide figure. **None** of the **11**, including the
strongest **8**, is independently audited: all are self-reported by the company or its technology
partner. This tiering is reported in full in the Results section and should be read wherever a
"measured benefit" figure appears in this report.

**Orientation and user group** were similarly subject to a full-population re-check against the
recorded quotation text, after an initial spot-check surfaced rows coded as purely internal that
their own quotation in fact contradicted by naming an external party (for example, a use case
whose quotation named both internal staff *and* named external customers, but had been coded
`internal` only). **3** of **58** rows were corrected on this basis. **Two** of the **58**
rows — **HSBA-UC-001** (**HSBC**) and **BA-UC-002** (**BAE Systems**) — show the opposite
pattern: both are coded `mixed`, but their captured quotation names only one party. Both were
identified but deliberately not corrected, because the absence of a second party in a short
quotation excerpt is not equivalent to evidence that no second party exists in the fuller source
document; only positive contradiction, not silence, was treated as grounds for reclassification.

A separate audit examined the nine risk- and governance-related fields recorded for every use
case (whether a risk or limitation was discussed, whether human review, privacy, security,
accuracy, bias, monitoring, restricted-use, or impact-assessment controls were disclosed). Of the
**75** instances across these fields coded `unclear` on the **58** confirmed use cases, **none**
were found to carry a documented, field-specific rationale in the reviewer's own notes — every
note addressed only the evidence-strength decision, not the risk or governance field itself. This
is treated as a limitation, not a finding: these nine fields cannot support any claim of the form
"most use cases do not disclose a human-review control," because the `unclear` and `no` values
cannot be reliably distinguished from fields that were simply never actively assessed. Full detail
is in `outputs/analysis/unclear_risk_field_audit.md`.

## Methodology 7. A note on terminology: "disclosed" rather than "confirmed"

The project's own working dataset uses the field name `confirmed_use_case_count` for the strict
count of use cases meeting the inclusion bar above. That word is retained in the underlying data
file for continuity with the project's audit trail, but this report and its supporting analysis
tables use **"disclosed"** instead, throughout. The distinction matters: "confirmed" risks
implying that a use case's existence, scale, or claimed benefit was independently verified,
when in fact every row in this dataset — including the most solidly evidenced ones — rests on
what the company (or its technology partner) chose to publish. "Disclosed" is the accurate word
for that. Nothing about the underlying inclusion criteria changed with this rename; it is a
labelling correction, not a re-coding.

## Methodology 8. Validation and this report's own audit trail

Beyond the coding review described above, a random sample of **20** of the **58** disclosed use
cases (drawn using a seed generated from system entropy, not hand-selected, and reproducible from
the recorded seed value) was independently checked, row by row, against its own supporting
quotation. Of the **20**, **6** clearly checked out against every coded field; the remaining
**14** had at least one field — most often deployment scale, a claimed benefit, or orientation —
that the specific quotation captured in the dataset did not, on its own, clearly support. This
does not mean **14** of **20** rows are wrong: the fuller source document, which this
spot-check did not re-read in every case, may support a field the short quotation excerpt does
not. In a majority of cases — **70%** — the recorded quotation is not sufficient on
its own to independently verify the coded fields, and this report treats that as a live
limitation rather than a resolved question. Full row-by-row detail is in
`outputs/analysis/disclosed_use_case_spot_check.md`.

---

# Limitations

The following limitations are methodology-supported: each is grounded in a specific, checkable
finding from this project's own audit process, not a generic caveat.

1. **Official-source dependence, sharpened by what was actually collected.** The inclusion rule
   requires company-primary or named-technology-partner sourcing. In practice this produced a
   corpus of **214** logged sources that is **essentially entirely** company-authored or
   vendor-promotional: **1** regulatory filing and **zero** earnings-call transcripts, against
   **202** annual reports, press releases, and technology-partner case studies combined. This
   systematically favours companies with detailed, English-language, easily discoverable annual
   reports over companies that disclose generative-AI use through channels this project's toolset
   never reached.
2. **Inaccessible domains.** **13** companies could not be researched to completion. For **12**
   of the **13**, the block occurred before any document was ever opened (**10** persistent HTTP
   403 errors, **1** persistent Cloudflare-specific error, **1** timeout); only **M&G** reached a downloaded but
   unreadable (encrypted) document. This is a structural gap, not a random one: several of the
   blocked companies are large, disclosure-averse consumer or industrial conglomerates whose
   access-restriction pattern may correlate with broader communications practices rather than with
   generative-AI adoption specifically — though this too cannot be confirmed from this dataset.
3. **Selection and availability of public evidence.** A company that genuinely deploys generative
   AI but does not disclose it publicly is indistinguishable in this dataset from a company that
   does not use it at all. This project measures *disclosed* adoption, not *actual* adoption, at
   every point.
4. **Disclosure-practice differences across companies and sectors** may drive as much of any
   observed sector-level variation as true differences in adoption — for example, financial-
   services and media companies may simply disclose technology use more readily than mining or
   tobacco companies, independent of their actual generative-AI activity.
5. **Evidence-strength and benefit-evidence variation.** Roughly half of disclosed use cases rest
   on the weaker of the two evidence-strength bands accepted for inclusion. Of the **58** disclosed
   use cases, **11** carry a measured, quantified benefit figure, but only **8** of those **11**
   are genuine company-wide or clearly-scoped operational figures — the remaining **3** are a
   single employee survey, a single vendor-sourced individual anecdote, and a vague magnitude
   estimate — and **none** of the **11** is independently audited.
6. **Likely under-reporting of internal deployments.** More than half of disclosed use cases are
   internally oriented rather than customer-facing, and companies have limited commercial
   incentive to publicise every internal tool; the true incidence of narrow, low-profile internal
   generative-AI use is almost certainly higher than what reaches annual-report-level disclosure.
   This is not only a theoretical concern: a post-finalization spot-check of already-collected
   sources for the 38 companies with at least one disclosed use case found three confirmed
   instances of a second qualifying use case missed within a source this project had already
   collected — Vodafone Group's SuperAgent, NatWest Group's Cora+, and RELX's EmbaseAI — against
   roughly 20 other candidates from the same check that were read and correctly excluded, evidence
   that this is a small, identified gap rather than a sign of pervasive miscoding.
7. **Null-result interpretation.** None of the **49** null-result companies has been through this
   project's own strict, human-certified closure process for asserting "no disclosure." The
   accurate statement for each is "no qualifying evidence was identified in the sources collected
   and reviewed for this company," not "this company does not use generative AI." Document
   reachability and format were checked and ruled out as an explanation for this group specifically
   (Section 5, above): the sources were opened and read.
8. **Small sector samples.** The majority of sector categories contain between **1** and **4**
   companies; **18** of roughly **38** distinct sector labels have only a single company in the
   entire researched-plus-blocked population. No sector-level comparison in this report should be
   treated as statistically robust below roughly **4** to **5** companies per sector.
9. **A tracking-artifact discrepancy in the project's own history.** An earlier project
   tracking file recorded **47** companies as having a confirmed deployment; the authoritative
   dataset supports **38**. Investigation traced this to **9** specific companies whose pipeline
   run had completed successfully but which had **zero** qualifying disclosed use cases — the
   tracking label had drifted from its own definition over a long, multi-session project history.
   This report uses **38** throughout, and treats the discrepancy itself as a reminder that any
   number sourced from project tracking metadata, rather than the primary dataset, requires
   independent re-verification before use.
10. **A sector-labelling inconsistency.** Two pairs of sector labels in the underlying data differ
    only in capitalisation (for example, "Financial Services" against "Financial services") despite
    an explicit project rule against exactly this kind of drift. These pairs were merged for
    analysis purposes only; the underlying data was left unchanged.
11. **claimed_benefits field reliability.** This field may, in some rows, reflect the coder's
    plausible inference from a tool's described function — for example, inferring "productivity"
    from a quotation that only describes what a tool does, without the company itself stating a
    benefit — rather than a benefit the source text explicitly claimed. This pattern was found in
    **at least 6** of the **20** rows in the random spot-check sample, but has not been
    independently re-audited across all **58** disclosed use cases. `claimed_benefits`
    distributions in this report should be read as indicative, not verified to the same standard
    as `benefit_evidence`.
12. **Risk and governance-control fields cannot support an aggregate claim.** Across the nine
    fields recording whether a risk, limitation, or specific governance control was disclosed for
    each use case, **none** of the **75** `unclear`-coded instances on the **58** disclosed rows
    carries a documented rationale distinguishing "the source did not discuss this" from "this
    field was not actively assessed." Only one of the nine fields is even defined in the project's
    own coding manual. This report accordingly does not make any aggregate claim of the form "most
    disclosed use cases lack a stated risk control" from these fields directly; where risk-related
    findings are reported, they are drawn from a direct reading of the free-text supporting
    quotation, case by case, not from these structured fields.
13. **This report's own spot-check found the underlying quotations only partially sufficient for
    independent verification.** Of a random sample of **20** disclosed use cases, **6** checked out
    cleanly against every coded field from the quotation alone; the other **14** had at least one
    field the specific captured quotation did not clearly support (most often deployment scale, a
    claimed benefit, or orientation). This does not establish that those **14** rows are
    miscoded — the fuller source document may support them — but it does mean the dataset's
    recorded quotations cannot, on their own, be treated as sufficient documentation for every
    coded field, and this report's own claims are qualified accordingly wherever they rely on a
    field this limitation touches.

---

# Results

*All figures below are drawn from the final, corrected state of `ANALYSIS_MEMO.md` §§2–7.*

## Results 1. How many companies, and how many use cases

Of the **100** FTSE 100 constituents in the population, **38** have at least one disclosed
generative-AI use case meeting this report's inclusion bar — **38.0%** of the full population, or
**43.7%** of the **87** companies this project reached an evidence-based verdict on (the
remaining **13** could not be researched to completion; see the Limitations section). Both
denominators are reported throughout this section rather than collapsed into one, because neither
is more "correct" than the other: the population-wide figure (**38.0%**) treats the **13**
unresolved companies as genuinely unknown, while the evidence-based figure (**43.7%**) describes
adoption only among companies a verdict was actually reached for.

Those **38** companies disclosed **58** distinct generative-AI use cases between them, but
unevenly: **26** of the **38** (**68%**) disclosed exactly **one** use case, while **12**
companies accounted for the remaining **32** use cases. The richest disclosures came from
**BT Group** and **RELX** (**4** use cases each); **AstraZeneca**, **Diageo**, **Aviva**, and
**BAE Systems** (**3** each); and **Vodafone Group**, **HSBC**, **Standard Chartered**,
**Schroders**, **Hiscox**, and **Lion Finance Group** (**2** each). A small number of companies
with unusually detailed public disclosure practices therefore shape a disproportionate share of
what this report can say about *how* generative AI is being used.

## Results 2. What has been implemented

**Deployment stage.** **86%** of the **58** disclosed use cases are already live in some form:
**live_limited** (**26**, **45%**) or **live_scaled** (**24**, **41%**), against only **8**
(**14%**) still at pilot stage. This is a live picture of active deployment, not a survey of
future intentions — a direct consequence of this report's evidence bar, which requires a detailed
operational description rather than an announced intention.

**Orientation and user group.** Use is more often internal than customer-facing, but less
lopsidedly than an earlier pass through the same data suggested: **internal** orientation
accounts for **32** of **58** use cases (**55%**), **customer_facing** for **11** (**19%**),
**product_embedded** for **9** (**16%**), and **mixed** for **6** (**10%**). (**3** of the **58**
rows were moved from `internal` to `mixed` on review, after their own supporting quotation was
found to name an external party — a customer or intermediary — that the original coding had
missed; see Methodology §6.) The user-group breakdown mirrors this: **employees** (**32**,
**55%**), **customers** (**19**, **33%**), **mixed** (**5**, **9%**), **suppliers_or_partners**
(**1**), and **developers** (**1**).

**Business function.** The most common named functions are **customer_service** (**10**,
**17%**) and **knowledge_document_work** (**9**, **16%**), followed by **research_development**
and **risk_legal_compliance** (**6** each, **10%**), **software_development_it** (**5**, **9%**),
and smaller categories down to **human_resources** (**1**, **2%**). A further **8** use cases
(**14%**) fall into an "**other**" category that is almost entirely general-purpose internal
productivity rollouts with no single named function — real, live deployments, but of a
deliberately generic kind (broad employee productivity tooling) rather than a specific business
task.

**Technology partner.** **Microsoft** is named in **13** of **58** use cases (**22%**) — mostly
Microsoft 365 Copilot or GitHub Copilot variants — making it the single most frequently named
technology signature in the dataset, ahead of **AWS/Amazon** (**5**, **9%**, recorded under three
different text labels for the same vendor — **BT Group** ×3, **AstraZeneca**, and **Diageo**) and
**Google** (**4**, **7%**: **HSBC**, **Rentokil Initial**, **Hiscox**, and **RELX**, the last of
which names Google alongside two other model providers in a single row). **12** use cases
(**21%**) name no external technology partner at all (in-house or proprietary tooling, or the
partner is unclear). Like `claimed_benefits`, this field is multi-value: **4** of the **58** rows
name more than one partner (for example RELX's single row names Anthropic, Google, *and* OpenAI
together), for **41** total individual partner labels across the 58 rows overall — so the
percentages above should not be read as mutually exclusive shares that sum to 100%.

## Results 3. Talk versus deployment

A confirmed operational use case is only one of several ways a company's generative-AI activity
can appear in this dataset. Counting any of three kinds of evidence — a disclosed operational use
case, a strategic-capability-building finding, or a governance/enablement finding — **65** of the
**87** evidence-based companies (**74.7%**) show *some* AI-related evidence. But only **38**
(**43.7%**) clear the operational bar. The gap between those two figures is **27** companies
(**31.0%**, roughly **3 in 10** of the evidence-based sample) that discuss AI strategy or
governance publicly without a single use case meeting this report's operational threshold. A
further **22** companies (**25.3%**) show no qualifying evidence of any kind — no operational use
case, no strategic finding, no governance finding.

## Results 4. Measurable consequences: what companies claim, and how well evidenced it is

Every disclosed use case was coded for its claimed benefit and for how strongly that benefit is
evidenced. The claimed-benefit distribution itself should be read cautiously: this report's own
review found that in at least **6** of a **20**-row random sample, a claimed benefit (most often
"**productivity**") appears to have been inferred by the coder from what a tool does, rather than
stated by the company — a limitation this report has not resolved across all **58** rows (see
Limitations, item 11). This field is multi-select — a use case can carry more than one claimed
benefit, and **25** of the **58** rows do (**83** benefit labels in total across 58 rows), which
is why the percentages below sum to well over 100%. With that caveat, the most frequently claimed
benefits are **productivity** (**29**, **50%**) and **time_saving** (**25**, **43%**), followed by
**service_quality** (**8**, **14%**) and smaller categories.

The strength of evidence behind those claims is uneven, and was itself corrected during this
project's own review. **40%** of disclosed use cases (**23** of **58**) carry only a prospective,
"**expected**" benefit; **41%** (**24**) report an experienced benefit with no number attached
(**observed_unquantified**); and **19%** (**11**) carry a specific, quantified figure
(**measured**). That last figure — **11** of **58** — was originally recorded as just **1**; a
full re-check of every quotation against the coding manual's own definition of "measured" found
**10** rows that had been miscoded despite their quotation containing an explicit
benefit-quantifying number.

Even within those **11** measured rows, the strength of evidence varies considerably and does not
reduce to a single category:

- **8** rest on company-reported operational or platform data — for example **Lion Finance
  Group**'s enterprise AI platform, disclosed with five separate figures (**6,600** hours per
  month freed up, adoption rising from **10%** to **56%** over six months, **80%** adoption in
  back-office roles specifically, **310,000+** monthly interactions, and a **40%** reduction in
  document-analysis time). This is the strongest
  evidence in the dataset, but the tier as a whole is not uniform: it also includes **RELX**'s
  claim of "**up to 66%**" time savings, a ceiling figure with no stated average or sample size.
- **1** rests on a self-reported employee survey (**AstraZeneca**: **92%** of **1,200** employees
  surveyed report experiencing time savings — explicitly not a company-wide measurement, by its
  own account).
- **1** rests on a single named employee's account published in a technology vendor's own
  marketing material (**Hiscox**, via a **Microsoft** customer-story case study), not the
  company's own disclosure.
- **1** rests on a vague, unquantified order-of-magnitude estimate tied to one illustrative
  example rather than a programme-wide figure (**Centrica**: "**hundreds of hours** a year," with
  no more specific number given).

**None** of the **11** measured rows, including the strongest **8**, is independently audited —
every figure is self-reported by the company or its technology partner. Separately, **16%** of
disclosed evidence (**9** of **58** rows) is sourced from a technology-partner case study rather
than the company's own disclosure (for example **Investec**'s Copilot for Sales case study,
**Hiscox**'s Microsoft case study, and **Rolls-Royce**'s Databricks case study); these are
preserved as such and not treated as company-confirmed.

**Taken together: measurable-consequence evidence exists for a minority of disclosed use cases
(19%), it is weighted toward company-reported figures of uneven precision, and none of it has
been independently verified.** This is a materially different picture from an earlier
mid-project estimate of roughly **2%**, and the revision matters: **19%** is still a minority, and
still entirely self-reported, but it is not "**almost no companies measure anything**" — a
non-trivial number do, even if imperfectly.

## Results 5. Unintended consequences: an evidentiary void, for two distinct reasons

This report's research question asks about unintended consequences as well as implementation and
measurable benefit. On that question, this dataset has almost nothing to say — and it is
important to be precise about *why*, because there are two separate reasons, not one.

**First, the corpus was never built to find this kind of evidence.** The keyword list and
document-collection guide behind source discovery are composed entirely of generative-AI product
and technology terms; they contain no terms oriented toward incidents, complaints, litigation,
regulatory enforcement, or workforce/union impact. Of the **214** sources actually collected,
only **1** is a regulatory filing and **none** is an earnings-call transcript, despite both being
permitted. Every other source is a company annual report, press release, sustainability report,
or technology-partner case study — channels a company controls the content of. **No** source in
the entire corpus falls into an incident, complaint, or regulatory-scrutiny category. This
report's near-total silence on unintended consequences is therefore, at least in significant
part, a property of what this corpus was built to find, not evidence that nothing went wrong at
any FTSE 100 company using generative AI.

**Second, even the structured fields this project's own coding schema built to capture risk and
governance controls cannot support a reliable aggregate claim.** Every disclosed use case was
coded for whether a risk or limitation was discussed, and for whether human review, privacy,
security, accuracy, bias, monitoring, restricted-use, or impact-assessment controls were
disclosed — nine fields in total. Across those nine fields, **75** individual cells on the **58**
disclosed use cases are coded "**unclear**." A full re-check of the reviewer's own notes for every
one of those **75** cells found **zero** with a documented, field-specific rationale — every note
addressed only the separate evidence-strength decision, never the risk or governance field
itself. In practice, this means the "**unclear**" and "**no**" values on these nine fields cannot
be reliably told apart from fields that were simply never actively assessed row by row. This
report therefore does **not** report an aggregate percentage of disclosed use cases that lack a
stated risk or governance control, because that number would not be trustworthy.

Where risk-related detail *is* reported elsewhere in this analysis (for example, the pattern of
human-review and source-citation language observed in high-cost-of-error use cases), it comes
from a direct, individual reading of each quotation's free text, not from these structured
fields — and it describes disclosed design choices, not verified outcomes or an absence of
incidents.

## Results 6. Null results: 49 companies with no qualifying evidence — and no certified non-adopters

**49** of the **87** evidence-based companies (**56.3%** of that group, **49.0%** of the full
population) were fully researched and yielded no qualifying generative-AI disclosure. This is a
substantive finding, not a gap in effort, but it rests on three distinct counts that should not be
collapsed into one: **46** of the **49** have both required annual reports collected and
reviewed (the other **3** — Admiral Group, Melrose Industries, and F&C Investment Trust — each
have at least one annual report not yet collected); separately, **47** of the **49** have the
sustainability-report collection field still stuck at "not started" (the other **2** — Informa and
Whitbread — have it marked collected); and only **44** of the **49** satisfy *both* conditions at
once. **None** of the **49** has been through this project's own strict, human-certified process
for asserting "no disclosure."

The accurate statement for every company in this group is **"no qualifying evidence was
identified in the sources collected and reviewed for this company,"** not **"this company does
not use generative AI."** A company may use generative AI without any disclosure reaching the
source types and channels this project's toolset could reach, or the disclosure may sit in a
source category — a dedicated sustainability report, an investor presentation — that was not
exhaustively pursued for that specific company.

---

# Discussion

*All figures below restate numbers already established and verified in Methodology and Results;
no new statistic is introduced here without a citation back to where it was first derived.*

## Discussion 1. The central finding: what gets disclosed is not evenly distributed across the research question

This report set out to answer a two-part question: how are **FTSE 100** companies implementing
generative AI, and what measurable and unintended consequences has that implementation had? The
Methodology and Results sections answer the first half in real, codable detail, and the second
half barely at all — and that gap, not the adoption number itself, is this report's central
finding.

**Implementation is well documented.** For the **58** disclosed use cases across **38**
companies, this report can state with confidence which business function each use case serves
(**customer_service** and **knowledge_document_work** lead, at **17%** and **16%**), what stage
of deployment it has reached (**86%** already live, `live_limited` or `live_scaled`), who
operates it (**employees**, **55%**, ahead of **customers** at **33%**), and which technology
vendor underpins it (**Microsoft** named in **22%** of use cases, by far the most frequent single
signature). None of this required inference beyond what companies themselves published.

**Measurable consequences are disclosed for a minority, and unevenly even within that minority.**
Only **19%** of disclosed use cases (**11** of **58**) carry any quantified benefit figure at
all, and that **19%** is not one tier of evidence: **8** rest on genuine company-reported
operational data, **1** on a self-reported employee survey, **1** on a single named employee's
account in a vendor's marketing material, and **1** on a vague, unquantified magnitude estimate.
**None** of the **11** — including the strongest **8** — is independently audited.

**Unintended consequences are almost entirely undisclosed, and for two identifiable reasons, not
one.** The corpus was built from **214** sources that are, without meaningful exception, company-
or vendor-authored (only **1** regulatory filing, **zero** earnings-call transcripts); it contains
**no** source oriented toward incidents, complaints, or regulatory scrutiny. Separately, the **9**
structured fields this project's own coding schema built to capture risk and governance controls
cannot support a reliable count at all — of **75** cells coded "unclear" across those fields on
the **58** disclosed rows, **zero** carry a documented rationale distinguishing "not discussed"
from "not assessed."

Read together, these three findings describe a single pattern: **as the research question moves
from "what was deployed" to "did it work" to "what went wrong," the evidence available to answer
it collapses at each step.** That pattern is a finding about what FTSE 100 companies choose to
disclose about generative AI, not a finding about what generative AI has actually done inside
those companies.

## Discussion 2. The evidence-density cascade, stated as a sequence

The scale of the collapse is visible as a single sequence, each step drawn from a different
section of this report. **The first two steps count companies, out of 87; the third counts
individual use cases, out of 58** — a smaller, differently-defined population, not a further
narrowing of the same 87 companies:

1. **74.7%** of the **87** evidence-based companies show *some* AI-related evidence — strategic,
   governance, or operational.
2. **43.7%** (**38** of **87**) clear this report's operational bar — a disclosed, codable use
   case.
3. **19%** of *those* **58** use cases (**11**) carry any quantified benefit figure.
4. An unknown, likely very small, share disclose anything about risk, harm, or unintended
   consequence — "unknown" rather than "zero" or a small percentage, because the fields built to
   measure this cannot be trusted to distinguish absence-of-disclosure from absence-of-assessment
   (§5 of Results).

Each step in this sequence uses a smaller, stricter evidentiary bar than the one before it, and
each step's population shrinks accordingly. This is not surprising in isolation — it would be
unusual for *any* voluntary corporate disclosure regime to report failures as readily as it
reports launches. What this report can add beyond that general expectation is the specific shape
of the collapse in this dataset: it is not a gentle taper but a near-total drop-off between step 3
and step 4, and that drop-off is at least partly an artefact of what this project's sources were
ever capable of showing, not solely a reflection of what companies chose to withhold.

## Discussion 3. A secondary lens: what kind of tasks are being implemented

The preceding two sections describe *how much* is disclosed at each stage. A separate, narrower
question — asked and answered only for the **58** disclosed use cases, and treated here as a
supplementary analytical lens rather than this report's organizing framework — is *what kind* of
task each disclosed use case represents. Three axes were coded for each use case: whether its
input is unstructured natural language or structured/non-language data; whether its output is
genuinely generative and interpretive or leans toward classification; and what the cost of a
wrong output would be (low, medium, or high).

**64%** of disclosed use cases (**37** of **58**) combine unstructured language input,
generative output, and low-or-medium cost of error at once — a pattern this report calls "classic
good fit." This is the modal pattern, but not an overwhelming one: **36%** of disclosed use cases
(**21** of **58**) fall outside it, for one or more of several reasons that are not mutually
exclusive: **8** apply generative techniques to structured or non-language input
(**Rolls-Royce**'s engine-design generation, **Shell**/SparkCognition's seismic-image generation,
**Diageo**'s bottle-personalisation platform, and others); **3** have a mixed input type; **4**
have an output that leans toward classification rather than genuine generation; and **11** carry
a high cost of error if wrong. (This **19%**/**11** figure is coincidentally identical to, but
describes a different set of rows than, the measured-benefit **19%**/**11** figure in Section 1.)
These groups overlap rather than add cleanly to 21: **Shell**'s use case is both structured-input
and high-cost; **HSBC**'s
decision-assistant partnership is mixed-input, mixed-output, *and* high-cost at once;
**Legal & General**'s Copilot rollout is mixed-input and mixed-output; and **BAE Systems**'
drone-command use case is mixed-output and high-cost.

That second group — the **11** high-cost-of-error use cases — is the most analytically interesting
finding this lens produces. It includes **RELX**'s three legal, regulatory, and clinical
products; **Aviva**'s medical-report summarisation for underwriting; **Schroders**' investment-
analyst tool; **Hiscox**'s underwriting-pricing model; **Shell**'s subsurface-exploration imaging;
**HSBC**'s financial-crime-and-decision-assistant partnership; and all three of **BAE Systems**'
defence use cases. Every one of these **11** pairs the generative capability with a disclosed
mitigating control: human review is retained (**Hiscox** drafts a broker email "for underwriter
review"; **Schroders**' tool "assists" analysts who draft the actual summaries), outputs are
source-grounded or cited (**RELX**'s products cite sources; **BAE Systems**' Typhoon assistant
gives "references to exactly where it found the information"), or extensive pre-launch validation
is disclosed (**RELX**'s ClinicalKey AI was "tested by more than 30,000 physicians before
launch").

**This pattern is worth stating plainly, and worth being equally plain about its limits.** It is
observable, disclosed behaviour, not an inference: companies deploying generative AI into
high-stakes tasks consistently describe a specific control alongside the deployment, rather than
describing the deployment alone. But this report cannot say whether that control is effective,
whether it was applied consistently in practice rather than as a one-time launch condition, or
whether it reflects genuine task-sensitive design discipline rather than standard risk-disclosure
language a compliance or communications function would include regardless. **The same
evidentiary collapse described in Sections 1 and 2 applies here too**: this report can describe
what companies say they did to manage a high-stakes deployment far more confidently than it can
say whether that management worked.

## Discussion 4. Why the asymmetry might exist — more than one explanation, none of them provable here

This report can describe the asymmetry precisely. It cannot fully explain it, and more than one
explanation is consistent with the same numbers.

**One explanation is disclosure incentive.** A company has a reputational and competitive reason
to publicise a live generative-AI deployment — it signals technological currency to investors,
customers, and talent. It has correspondingly little reason to volunteer that a deployment cost
more than expected, underperformed, or caused a problem, unless a regulator or journalist forces
disclosure through a channel this project's sources do not include (Methodology §4). This
explanation is consistent with the evidence but not established by it: this report has no way to
distinguish a company that measured a benefit and chose not to publish it from a company that
never measured one at all.

**A second, less cynical explanation is timing.** **86%** of disclosed use cases are already live,
but many are recent: **45%** are `live_limited` rather than `live_scaled`, and a further **14%**
are still at pilot stage. A deployment that went live within the last reporting cycle may simply
not have accumulated enough operating history for a company to have a measured outcome to report,
independent of any reluctance to disclose one.

**A third explanation is that this project's own toolset could not have found consequence
evidence even if a company had published it.** Results §5 already establishes this directly: the
corpus was built from a keyword list and collection guide oriented entirely around generative-AI
product and technology terms, with no term oriented toward incidents, complaints, or regulatory
findings. A negative outcome disclosed through a channel — a regulatory filing, a parliamentary
submission, an investigative news report — this project did not systematically search would not
appear in this dataset regardless of whether it exists.

**This report cannot adjudicate between these three explanations, and does not attempt to.** All
three are consistent with the observed pattern; none is ruled out by it. What can be said with
confidence is narrower and more useful: whatever the cause, the practical effect is the same —
public disclosure from FTSE 100 companies about generative AI is far more informative about what
has been built than about what it has done.

## Discussion 5. What this means: a finding about disclosure, not only about deployment

The thesis this report set out to examine holds, and holds specifically because of the shape of
the evidence rather than despite it: **FTSE 100 companies' public disclosures describe generative-
AI implementation in genuinely codable, comparable detail, but they are structurally asymmetric —
they say far less about whether deployments have worked, and they say almost nothing about what
they may have cost, broken, or endangered.** This is not necessarily a criticism specific to how
FTSE 100 companies disclose generative AI in particular — this report studied only generative AI
and has no comparison group of other technologies to say whether this asymmetry is unusual or
typical — and it is not a claim that no FTSE 100 company has measured an outcome or encountered a
problem. It is a claim about what the public record — the only record this report had access
to — actually contains.

That distinction matters for how this report's findings should be used. This report can support a
claim of the form "**at least 38** FTSE 100 companies have publicly disclosed a specific,
operational generative-AI use case, mostly internal, mostly Microsoft-affiliated, mostly already
live." It cannot support a claim of the form "generative AI is delivering measurable value at
FTSE 100 companies," or a claim of the form "generative AI has caused few problems at FTSE 100
companies" — both would require evidence this dataset does not contain, not merely evidence this
report chose not to report.

## Discussion 6. What the task-suitability lens can and cannot add to that finding

Section 3's task-based classification does not change this conclusion; it sharpens one part of
it. The **64%** "classic good fit" figure and the disclosed-control pattern among the **11**
high-cost-of-error use cases are the most concrete evidence in this dataset that companies think
about task characteristics when deploying generative AI, at least at the point of disclosure. But
that observation sits entirely on the "implementation" side of the asymmetry described above — it
describes *what was built and how it was described*, not *whether building it that way produced a
better outcome than building it otherwise*. This report has no outcome data for any use case,
well-matched or not, so it cannot show that the **37** "classic good fit" use cases are performing
better than the **21** that fall outside that pattern. The task-suitability lens is therefore best
read as a finding about the texture of disclosed implementation — a secondary, descriptive
addition to Sections 1–2 — not as independent evidence that selective task-matching works, which
would be a different, unanswered question.

---

# Conclusion

*Every number below restates a figure already established and verified in the Methodology,
Results, or Discussion sections; nothing new is computed here. One point flagged explicitly below
(population-wide adoption bounds) was deliberately left out because it was never carried into
those three sections, even though it exists in `ANALYSIS_MEMO.md` §8 — including it here would
violate the constraint this section was drafted under.*

This report set out to answer how **FTSE 100** companies are implementing generative AI, and what
measurable and unintended consequences that implementation has had. The answer is not a single
number. As argued in full in Discussion §5, it is a claim about the shape of the evidence
itself — public disclosures describe implementation in reasonably codable detail, but are
structurally asymmetric about whether it worked or what it may have cost, broken, or endangered.
That asymmetry is the finding this report can defend most confidently, precisely because it does
not depend on any single company's disclosure being complete or representative — it holds across
the whole disclosed record.

Four findings support that conclusion, each already established in full in the Results and
Discussion sections. **Adoption is real, but concentrated and shallow at the level of any single
company**: **38** of the **100** FTSE 100 constituents (**38.0%**, or **43.7%** of the **87**
companies this report reached a verdict on) have disclosed at least one qualifying use case, **86%
of** those **58** disclosed use cases are already live rather than merely planned, and yet **68%**
of adopting companies disclose only a single use case each — adoption is broad-based but rarely
deep. **Measurable outcomes are disclosed for a minority of deployments, and that minority is
itself uneven**: only **19%** of disclosed use cases (**11** of **58**) carry any quantified
benefit figure, and of those **11**, only **8** rest on genuine company-wide operational data; the
remaining **3** rest on a single employee survey, a single vendor-sourced anecdote, and a vague
magnitude estimate, one each; **none** of the **11** is independently audited. **Unintended consequences are almost
entirely undisclosed, for two identifiable reasons rather than one**: the evidence base this
report could assemble was never built from sources oriented toward incidents or regulatory
findings, and separately, this project's own structured fields for recording risk and governance
detail proved unable to support a reliable count at all. And **evidence density collapses in
sequence as the research question moves from deployment to outcome to harm**: from **74.7%** of
evidence-based companies showing some AI-related activity, to **43.7%** with a disclosed
operational use case, to **19%** of those use cases with any measured benefit, to a share of
disclosed unintended consequences this report cannot even reliably estimate.

What this dataset cannot answer matters as much as what it can. It cannot say whether the **11**
disclosed measured benefits — or the remaining disclosed use cases, which carry only an expected
or observed-but-unquantified benefit — reflect deployments that are actually delivering value,
because no outcome in this dataset is
independently audited; a company's own claim is the only evidence available, and this report has
been explicit throughout about not treating a claim as a verified result. It cannot say that
generative AI has caused few problems at FTSE 100 companies, because the near-total absence of
unintended-consequence evidence in this dataset is a property of what this project's sources were
built to find, not proof that nothing went wrong. It cannot state a single, settled adoption rate
for the FTSE 100 as a whole, because **13** companies could not be researched to completion and
**49** null-result companies have not been through this project's own certification process for
asserting "no disclosure" — both groups remain genuinely unresolved, not confirmed negatives. And
it cannot say that the **58** disclosed use cases represent the full extent of generative-AI use
inside these companies, because **55%** of them are already internal rather than customer-facing,
and a company has little commercial incentive to publicise a narrow, low-profile internal tool it
has no reason to promote.

Read together, these findings argue for a specific kind of caution that is different from ordinary
scientific humility about sample size or measurement error. The caution this report is arguing for
is about what kind of question public corporate disclosure can answer at all. For a question like
"what has been built," the FTSE 100's public record is a genuinely useful, comparable evidence
base — this report was able to construct one from it. For a question like "did it work" or "what
went wrong," the same record is structurally unsuited to the task, not merely incomplete, because
the sources that make up that record were never written to answer it. A future study of the same
population that wanted a real answer to the second and third questions would need to look
somewhere this report's own sources could not reach: regulatory filings, workforce and union
disclosures, litigation records, or channels this project's toolset was not built to search. Until
then, the honest summary of what FTSE 100 companies' public disclosures show about generative AI
is not "it is working" or "it is safe" — it is that a large share of these companies have told the
public what they built, and almost none of them have told the public whether it was worth
building.
