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

# Judgment calls in this draft

A short list of the choices in the text above that were not dictated directly by a source file,
for your review:

- **How much of the corpus-construction finding to state as a limitation versus as neutral
  methodology.** I put the "no incident/complaint/regulatory source types were ever queried"
  finding in both the Methodology narrative (Section 4) and as the lead item in Limitations (item
  1), rather than confining it to one place. That's a deliberate emphasis choice — it's arguably
  the single most consequential fact for how a reader should weight the eventual Results section,
  and I chose to repeat it rather than risk it being read once and forgotten.
- **Leading Limitations with source-type dependence rather than the blocked-company gap.** Both are
  defensible as the "most important" limitation. I ordered by what most directly shapes the
  Results section's *content* (what kinds of findings are even possible from this corpus) ahead of
  what shapes its *coverage* (which companies are missing).
- **This item is resolved, not a live judgment call — noted for the record.** The Lloyds/Sage
  blocker-type discrepancy flagged in an earlier version of this draft turned out to be a real
  error in `reachability_audit_blocked_and_null.md` (built by concatenating a raw field rather
  than reading the underlying notes), not a defensible alternative reading. `ANALYSIS_MEMO.md`'s
  original "Cloudflare block" description for Lloyds was correct; Sage Group has been moved back
  into the plain-HTTP-403 group. Both source files and this draft now agree.
- **Resolved.** The spot-check's 14/20 finding now reads "a majority of cases — 70%" instead of "a
  meaningful minority of cases." The original phrasing was a case of managing how alarmed the
  reader should feel about a plain fact, not stating it — flagged and fixed on review.
- **Resolved.** Section 6 originally described the orientation/user_group reverse pattern as "a
  parallel, opposite-direction pattern" without stating how many rows or which ones — an omission
  that failed the plain-fact test the same way the 14/20 phrasing did, just by leaving a number out
  entirely rather than softening it. Now names both rows explicitly: **HSBA-UC-001** (**HSBC**)
  and **BA-UC-002** (**BAE Systems**). The fuller epistemic-asymmetry reasoning for why they
  weren't corrected still lives in `disclosed_use_case_spot_check.md`, not reproduced in full here.
- **Whether to state the checkpoint discrepancy (47 vs. 38) as "an earlier project tracking file"
  without naming `master_controller_checkpoint.json` or the session/pipeline structure behind it.**
  I kept this deliberately generic for a reader who has never seen the pipeline, on the view that
  naming internal file structures belongs in an appendix rather than the Limitations prose — but
  this trades away some transparency for readability, and could go the other way.
