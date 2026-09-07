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

# Judgment calls in this draft

Self-tested against the same standard used for the Methodology and Limitations section: for each
choice below, am I stating the fact plainly, or have I chosen a word or structure that manages how
the reader should feel about it? Two failed that test on review and were rewritten before this
draft was shown to you; both are marked as fixed. The rest are structural or emphasis choices, not
severity-management, and are shown as-is for your review.

- **Fixed on self-review: "This is a materially different picture from an earlier mid-project
  estimate of roughly 2%" (Section 4).** My first draft of this sentence said the revision from
  2% to 19% "should be read in context" and "does not change the overall conclusion" — both true,
  but both are reader-management phrases that pre-soften a large, embarrassing-looking revision
  before stating it. Rewritten to state the two numbers plainly (2% → 19%) and let the very next
  sentence — which says 19% is still a minority, still self-reported — carry the qualification,
  the same fix pattern approved for the Methodology section.
- **Fixed on self-review: the unintended-consequences section's opening.** An earlier draft of
  Section 5's opening sentence read "this dataset can say relatively little" about unintended
  consequences. The actual finding is stronger and more useful than "relatively little": the
  dataset can say **almost nothing**, for two identifiable, named reasons. Softening it to
  "relatively little" would have buried the more important, more precise finding underneath a
  vaguer one. Rewritten to state the near-total absence plainly and lead with why.
- **Splitting Section 5 into "two distinct reasons" rather than one combined paragraph.** This is
  a structural choice, not a severity one: the corpus-construction limitation and the
  risk-field-reliability limitation are genuinely different findings from different audits
  (`corpus_search_strategy.md` and `unclear_risk_field_audit.md` respectively), and I judged
  a reader needs to see them as separate claims, each independently checkable, rather than one
  blended "we don't know much about risk" statement. This makes the section longer; I judged the
  precision worth it.
- **Leading Section 4 with the claimed-benefits reliability caveat before presenting the
  claimed-benefits numbers themselves**, rather than presenting the numbers first and caveating
  after. This foregrounds doubt before data — a deliberate choice to stop a reader from anchoring
  on "50% claim productivity" before learning that figure may be partly coder-inferred. An
  equally defensible alternative would present the numbers first and the caveat second, matching
  how §3 of `ANALYSIS_MEMO.md` itself orders it.
- **Describing the AstraZeneca survey figure's own caveat ("explicitly not a company-wide
  measurement, by its own account") inline rather than only in a footnote-style aside.** This is
  presented with the same weight as the headline number itself; an alternative would state the
  92%/1,200 figure and relegate the "not company-wide" caveat to a parenthetical, which would
  read as more impressive and less qualified than the underlying source supports.
- **Choosing not to restate the full [38.0%, 51.0%] blocked-company sensitivity interval from
  `ANALYSIS_MEMO.md` §8 in this Results section.** I judged that bounds-under-uncertainty analysis
  belongs in Discussion (not yet drafted) rather than Results, and mentioned the **13** unresolved
  companies only for denominator clarity in Section 1. If you want the sensitivity table itself
  in Results, that's a straightforward addition.
