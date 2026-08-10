# How Are FTSE 100 Companies Using Generative AI? A Task-Based Analysis

**Status: FIRST DRAFT — for author review, not a final submission**
**Draft date:** 2026-08-08
**Empirical basis:** `outputs/intermediate/analysis_snapshot_2026-08-08_final_closure/` (read-only snapshot) and `outputs/analysis/ANALYSIS_MEMO.md`
**Table references:** bracketed citations such as [Table 2] refer to the corresponding file in `outputs/analysis/` (a full mapping is given in the Appendix)

---

## 1. Introduction

Generative artificial intelligence — large language models and related systems capable of
producing novel text, code, images or other content in response to a prompt — has moved from
experimental technology to a recurring feature of corporate disclosure in only a few years. Annual
reports, investor presentations and press releases from the largest listed companies in the United
Kingdom now routinely mention "AI," "generative AI," "large language models" or named products such
as Microsoft Copilot, ChatGPT, Claude and Gemini. What is much harder to establish is what these
mentions actually describe: a live, task-specific deployment used by real employees or customers;
a pilot still being tested; a strategic ambition with no working system behind it; or simply
commentary on a technology trend.

This report addresses a single empirical question, adapted from this project's founding brief:

> **How are FTSE 100 companies using generative AI?**

Answering it matters for reasons beyond descriptive interest. Corporate generative-AI adoption is
frequently discussed in the business press, by investors and by policymakers as though it were a
single, homogeneous phenomenon — companies either "have AI" or they do not. This framing obscures
a more important distinction: generative AI is well suited to some business tasks and poorly suited
to others, and a company's disclosure that it "uses AI" says very little on its own about which
kind of task is involved, how the system is deployed, or what happens if it is wrong.

This report is organised around a specific version of that distinction, referred to throughout as
the **central task-based thesis**:

> Companies should deploy large language models and generative AI selectively, according to the
> characteristics of the task in question, rather than assuming that any task involving language is
> automatically suitable for an LLM.

The thesis implies that not every corporate "AI story" is equally credible or equally sound as a
deployment decision. A tool that summarises internal engineering notes for later human review is a
different proposition, in terms of risk and appropriateness, from a tool that drafts insurance
pricing or interprets aircraft maintenance manuals. Sections 2 and 4 make this distinction
operational and apply it to the evidence gathered from all 100 FTSE 100 constituents. Section 5
returns to the thesis directly and asks, honestly, how far the evidence gathered actually supports
it — including the ways in which it does not.

This report draws on a purpose-built dataset assembled over several research sessions: 100 FTSE 100
constituents were researched (87 to a fully evidence-based conclusion, 13 remaining inaccessible to
the automated collection tools used — see Section 3.7 and 4.9), yielding 58 confirmed operational
generative-AI use cases across 38 companies, alongside separate records of strategic ambition and
governance activity that do not themselves constitute deployment. The remainder of this report sets
out the conceptual framework used to interpret that evidence (Section 2), the methodology by which
it was gathered and coded (Section 3), the results in full (Section 4), a discussion of what those
results do and do not establish about the central thesis (Section 5), the limitations of the
exercise (Section 6), and a conclusion (Section 7).

---

## 2. Conceptual framework

### 2.1 What counts as a generative-AI use case

Not every mention of "AI" in a corporate disclosure describes generative AI, and not every mention
of generative AI describes an operational use case. This project defines a qualifying disclosure
(`is_genai = yes`, in the underlying coding scheme) as one that meets at least one of the following:

1. the source explicitly says "generative AI" or "GenAI";
2. it explicitly identifies a large language model (LLM) or foundation model;
3. it names a product whose relevant function is unambiguously generative — for example Microsoft
   365 Copilot, GitHub Copilot, ChatGPT, Claude or Gemini;
4. it describes the generation of text, code, images, audio or other content through a clearly
   identified generative model.

Conventional predictive analytics, classification models, robotics, and vague statements that "AI
is important to our strategy" are explicitly excluded. This bar was applied consistently across the
whole research population, and it is the single most consequential methodological choice in this
project: it is why, for example, a company's predictive-maintenance or fraud-detection AI is not
counted here as generative-AI adoption, however sophisticated it may be.

### 2.2 Task-level, not job-level, analysis

The unit of analysis throughout is a **distinct use case** — one identifiable task, user group,
business process, product or deployment context — rather than a job role, a department, or a
company-wide "AI programme." A company that has deployed Microsoft 365 Copilot to its entire
workforce and separately built a bespoke underwriting-pricing model contributes two distinct use
cases to this dataset, because the task, the user group and the consequences of error are entirely
different in each case, even though both might be described in the same annual report as "our AI
strategy." This distinction is the foundation for the task-based approach that follows: aggregating
to the level of "the company" or "the department" would erase exactly the variation in task
suitability this report is designed to surface.

### 2.3 Three suitability criteria

To assess whether an observed use case represents a *good structural fit* for a large language
model — as distinct from whether it happens to work well in practice, which this dataset generally
cannot establish (Section 2.4) — each confirmed use case in this report was classified against
three criteria, applied as an analytical lens to the dataset during the analysis phase rather than
built into the original coding manual:

- **Unstructured language input.** Does the system take in genuinely unstructured natural language
  — a free-text query, an email, a document, a spoken instruction — or does it operate on
  structured data, design parameters, or another non-language input pressed into a generative
  pipeline?
- **Interpretive or generative output where fluency is valuable.** Is the output itself an act of
  interpretation or generation — drafting, summarising, synthesising, conversing — where natural
  fluency and the ability to handle ambiguity are the point? Or does the underlying task lean
  toward classification, scoring or retrieval, with generation acting mainly as a wrapper around a
  more mechanical process?
- **Acceptable cost of error.** What happens if the output is wrong? This project distinguishes
  low cost of error (internal, human-reviewed, easily corrected), medium (customer-facing or
  process-relevant, but not safety- or financial-critical), and high (financial, legal, medical,
  safety or security stakes).

### 2.4 Why these criteria matter, and what they do not tell us

Large language models are, by construction, probabilistic text generators. Their central strength —
producing fluent, contextually plausible language from an under-specified prompt — is also the
source of their central weakness: they can produce fluent, contextually plausible language that is
wrong. A task that rewards fluency and tolerates occasional error (drafting an internal email,
summarising a document for a human who will still read the source) is a good match for that
profile. A task that requires exactness and where an error is expensive (calculating an insurance
premium, interpreting a safety-critical procedure) is a poor match for the technology on its own
terms — unless it is paired with additional controls that constrain the risk.

This distinction — "language is involved" versus "an LLM is actually the appropriate tool" — is the
analytical core of this report. A company that has "deployed generative AI" in a legal, medical or
financial-advice context has not automatically made a good decision merely by virtue of having
deployed the technology at all; whether it has made a good decision depends on the task
characteristics above and on what controls, if any, accompany the deployment. Conversely, a company
whose "AI" is confined to drafting emails or summarising meeting notes has picked one of the safest
possible applications of the technology, even if the resulting story is less newsworthy.

It is important to state plainly what this framework cannot do. It is a *structural* classification
of the kind of task involved, not a verdict on whether a given deployment is succeeding, failing, or
delivering the benefits claimed for it. Section 4.7 and 4.9 return to this limitation directly: this
project's evidence is much better suited to establishing *what companies say they are doing* than
to establishing *whether it is working*.

---

## 3. Methodology

### 3.1 Population and evidence window

The population is the 100 constituents of the FTSE 100 index following its 19 June 2026
reconstitution (`ftse100_constituents_2026-06-19.csv`). The evidence window runs from 1 January
2023 to 14 July 2026; sources published outside this window were excluded regardless of relevance.
Because index membership changes over time, both the membership date and the evidence window are
stated here explicitly, per this project's founding brief.

### 3.2 Source discovery and inclusion/exclusion criteria

For each company, the project sought the current and previous annual report, a separate
sustainability or ESG report where one exists, an official company-website search for generative-AI
disclosures, and a search for named technology-partner case studies (for example, a vendor's own
published account of a client's deployment). A record qualifies for inclusion when the company or a
named partner explicitly identifies generative AI, an LLM, a foundation model, or a named
generative-AI product, **and** a task, process, product, experiment or intended application is
described. Records are excluded where the source only makes a vague claim that AI is important;
describes predictive AI or conventional machine learning with no generative component; describes
general employee access to a tool with no described task; rests on third-party speculation rather
than company or partner disclosure; duplicates an already-recorded use case; or falls outside the
evidence window.

### 3.3 Evidence classification: operational, strategic, governance, and null result

Every qualifying passage was classified into one of several destinations, kept in separate datasets
so that operational deployment is never conflated with discussion or intention:

- **Operational use case** (`use_case_dataset_template.csv`): a specific, describable deployment
  meeting the inclusion bar above.
- **Strategic capability-building finding** (`strategic_capability_building_findings.csv`):
  discussion of AI strategy, partnerships, acquisitions or capability investment that does not
  itself describe a discrete operational task — for example, a strategic partnership announcement
  with no task, user group or deployment stage evidenced.
- **Governance and enablement finding** (`governance_and_enablement_findings.csv`): disclosure of
  AI governance frameworks, responsible-AI policies, board oversight, or workforce training that is
  not itself an operational deployment.
- **Rejected or aspirational finding** (`rejected_or_aspirational_findings.csv`): passages that
  mention AI but do not meet the inclusion bar (vague general-AI references, ordinary automation,
  or third-party speculation).
- **Null result**: a company for which no qualifying operational use case was found in the sources
  collected and reviewed.

A company can appear in more than one of the non-operational categories, and a company with
strategic or governance evidence is *not* thereby credited with an operational use case — this
separation is maintained throughout Section 4 and is one of the report's central findings in its
own right (Section 4.6).

### 3.4 Evidence-strength and confidence framework

Each candidate use case was rated on a four-point evidence-strength scale: `3_strong` (a
company-primary source identifies a specific use case and deployment stage, with measurable
evidence or a detailed operational description), `2_moderate` (the specific use case is clear, but
scale, stage or outcomes are incomplete), `1_weak` (a vendor-led or vague description with limited
corroboration), or `0_not_qualifying`. Each was also rated for confidence — `high` (directly and
unambiguously supported), `medium` (some inference required but reasonably supported), or `low`
(substantial judgement required or the passage is borderline).

For a use case to count toward this report's headline **confirmed** figures, it must meet a strict
rule: `is_genai = yes`; evidence strength of `2_moderate` or `3_strong` (never `1_weak`); a
review status of `reviewed_confirmed` or `reviewed_corrected` (i.e. it has been through human
review, not left as an unreviewed candidate); and it must not be a duplicate of another record. A
looser **provisional** count additionally includes `1_weak` evidence and not-yet-reviewed
candidates. This report uses the strict, confirmed count throughout unless a table or passage
states otherwise, and always states which count is in use.

### 3.5 Treatment of duplicates

Records are treated as duplicates where the company, underlying task, product and user population
are substantively the same, even if reported in multiple sources (for example, both the current and
prior annual report). The strongest primary source is retained as the main record; other sources are
linked to it rather than counted as separate use cases. This prevents a single deployment mentioned
in two consecutive annual reports from inflating the use-case count.

### 3.6 Treatment of blocked companies

Thirteen companies could not be brought to an evidence-based conclusion because the automated
collection tools available to this project — which do not include a genuine interactive web
browser — were persistently unable to retrieve their primary sources. The blockers fall into three
categories: (a) domain-wide access restrictions (HTTP 403 responses or bot-detection challenges)
that persisted across repeated, independently verified attempts; (b) a persistent connection
timeout (one company); and (c) a document that downloads successfully but is encrypted in a way
this project's text-extraction tools cannot open without installing an additional software
dependency, which was deliberately not done in order to avoid altering the research environment
mid-project. These 13 companies are recorded as `blocked_manual_browser`: their status is
**unresolved**, not negative. They are never counted as null results in this report, and every
adoption statistic that spans the full FTSE 100 states explicitly whether it treats them as unknown
(Section 4.9).

### 3.7 Human-review process

Following this project's validation plan, a sample of coded records was manually reviewed,
including every record initially classed as `unclear`, every record resting only on
technology-partner evidence, a random 20% of included use cases, a random sample of excluded
candidate passages, and a sample of companies for which no use case was found. Reviewers checked
whether each classification was genuinely generative AI, whether the supporting quotation actually
supported the claimed use case, whether the deployment stage and business function were correctly
assigned, and whether citations were accurate. Only use cases that passed this review (`review_status
= reviewed_confirmed` or `reviewed_corrected`) are counted in this report's confirmed figures.

### 3.8 How the final dataset was constructed, and a methodological transparency note

The dataset was built company by company over several research sessions, with each company's
sources collected, extracted, screened for candidate passages, staged, reviewed, and — where
qualifying evidence existed — promoted into the six datasets described above. A session-level
tracking file recorded each company's progress toward a final status. During preparation of the
analysis that underlies this report, a discrepancy was found between that tracking file, which
recorded 47 companies as having reached a "promoted" status, and the authoritative dataset itself
(`company_summary_template.csv`), which shows only 38 companies with at least one confirmed
operational use case. Investigation traced the gap to nine companies whose tracking-file status had
drifted from its own definition over the project's multi-session history — most plausibly because
early sessions used "promoted" loosely to mean "this company's research pipeline completed", rather
than strictly "this company has a confirmed operational use case." Several of these nine are
explicitly recorded elsewhere in the project's own working notes as null results (for example, one
company's own progress note reads: "provisional 0, confirmed 0 — no qualifying GenAI evidence
found"). This report uses the authoritative dataset's figure of **38**, not the tracking file's 47,
throughout. This correction is noted here, once, because it is methodologically relevant to how
confident a reader should be in any single number drawn from this project's history without
independent verification against the underlying dataset — and because a report that quietly used
the more flattering 47 without explanation would misrepresent the project's own evidence.

---

## 4. Results

### 4.1 Coverage and research status [Table 1]

Of the 100 FTSE 100 constituents, 87 were researched to a fully evidence-based final status and 13
remain blocked (Section 3.6). Of the 87, 38 have at least one confirmed operational generative-AI
use case and 49 are null results — meaning no qualifying evidence was found in the sources
collected and reviewed for that company (Section 4.8 discusses what this does and does not mean).

| Status | Companies | % of 100 |
|---|---:|---:|
| Confirmed operational | 38 | 38.0% |
| Completed null result | 49 | 49.0% |
| Blocked (unresolved) | 13 | 13.0% |
| **Total** | **100** | **100.0%** |

This distribution is independently cross-checked against the FTSE 100 constituent list: every
company appears in exactly one of these three categories, with no omissions and no duplicates.

### 4.2 Overall GenAI adoption [Table 2]

Confirmed operational adoption can be stated against two denominators, and this report uses both,
always labelled:

- **Against the full FTSE 100 (n=100):** 38 companies, or **38.0%**.
- **Against the 87 companies with an evidence-based final status (n=87):** 38 companies, or
  **43.7%**.

Neither figure is more "correct" than the other; they answer different questions. The first is the
honest population-level statement, treating the 13 blocked companies as unknown rather than
assuming them into either the adopter or non-adopter category. The second describes adoption only
among the subset of companies this project reached a verdict on. Section 4.9 discusses how much the
13 blocked companies could move the first figure if their status became known.

The 38 confirmed-operational companies collectively account for 58 confirmed use cases (63 if the
looser provisional count, including weaker or not-yet-reviewed evidence, is used instead). Most
adopting companies have a single confirmed use case:

| Confirmed use cases per company | Companies |
|---:|---:|
| 1 | 26 |
| 2 | 6 |
| 3 | 4 |
| 4 | 2 |

Twenty-six of the 38 adopting companies (68%) have exactly one confirmed use case; the total is
disproportionately shaped by a small number of companies with unusually detailed disclosure —
notably RELX (4 use cases), BAE Systems (3), Aviva (3), BT Group (4), and several others with two
each. A handful of well-documented companies therefore contribute a large share of the descriptive
detail in Sections 4.3 and 4.4 below, which should be read with that concentration in mind.

### 4.3 Operational use-case categories [Table 3]

Using the project's own coding categories (no new categories were introduced for this analysis),
the 58 confirmed use cases distribute across business functions as follows:

| Primary business function | n | % |
|---|---:|---:|
| Customer service | 10 | 17.2% |
| Knowledge and document work | 9 | 15.5% |
| Other (general productivity) | 8 | 13.8% |
| Research and development | 6 | 10.3% |
| Risk, legal and compliance | 6 | 10.3% |
| Software development and IT | 5 | 8.6% |
| Product or service innovation | 4 | 6.9% |
| Marketing and content | 3 | 5.2% |
| Operations and supply chain | 2 | 3.4% |
| Cybersecurity | 2 | 3.4% |
| Sales | 2 | 3.4% |
| Human resources | 1 | 1.7% |

The "other" category (8 use cases, 13.8%) is almost entirely composed of general-purpose internal
productivity rollouts — company-wide Copilot-style deployments with no single named business
function — rather than a coding gap; this is itself a meaningful pattern, discussed further below.

By deployment stage, the large majority of confirmed use cases are already live in some form: 26
(44.8%) are `live_limited` (operating in a bounded team, geography or workflow) and 24 (41.4%) are
`live_scaled` (normal business use across a meaningful population), with only 8 (13.8%) still at
pilot stage. Eighty-six percent of confirmed use cases are therefore live rather than merely
planned — a direct consequence of this project's strict evidentiary bar, which requires a detailed
operational description to count as confirmed at all.

By orientation, internal use dominates: 35 of 58 use cases (60.3%) are internally oriented,
compared with 11 customer-facing (19.0%) and 9 product-embedded (15.5%, i.e. built into a product
sold to clients). By user group, employees are the primary beneficiary in 35 cases (60.3%) against
19 for customers (32.8%).

Microsoft is the single most frequently named technology partner, appearing in 13 of 58 confirmed
use cases (22.4%) — chiefly via Microsoft 365 Copilot and GitHub Copilot variants — more than any
other named provider. Twelve use cases (20.7%) name no external technology partner, describing
proprietary or in-house-built systems instead.

Claimed benefits are led by productivity (29 use cases, 50.0%) and time saving (25, 43.1%), with
service quality, personalisation, accuracy, risk reduction and accessibility each appearing in a
smaller minority of cases. Crucially, the *evidence* behind these claims is weak: only 1 of 58
confirmed use cases (1.7%) carries a directly measured, quantified benefit; 32 (55.2%) are merely
"expected" (prospective, not yet observed) and 25 (43.1%) are "observed but unquantified." This
finding is returned to directly in Section 4.7.

### 4.4 Task suitability classification [Table 3b]

Each of the 58 confirmed use cases was individually read and classified against the three criteria
set out in Section 2.3.

| Axis | Result | n | % |
|---|---|---:|---:|
| Input | Unstructured language | 47 | 81.0% |
| Input | Structured or non-language | 8 | 13.8% |
| Input | Mixed | 3 | 5.2% |
| Output | Generative/interpretive | 54 | 93.1% |
| Output | Mixed or classification-leaning | 4 | 6.9% |
| Cost of error | Low | 29 | 50.0% |
| Cost of error | Medium | 18 | 31.0% |
| Cost of error | **High** | **11** | **19.0%** |

Combining all three axes, a "classic good fit" pattern — unstructured language input, generative or
interpretive output, and a low or medium cost of error, simultaneously — describes **37 of 58
confirmed use cases (63.8%)**. This is the modal pattern in the dataset, but it is not close to
universal: more than a third of confirmed use cases sit outside it.

**The high-cost-of-error group (11 use cases, 19.0%) is the most analytically important subset for
the task-suitability question.** It includes three of RELX's legal, regulatory and clinical
information products (Lexis+ with Protege for legal research; PharmaPendium for regulatory
intelligence; ClinicalKey AI for clinical information — domains in which AI hallucination has
caused real, publicised incidents elsewhere in the market); Aviva's generative-AI GP medical-report
summarisation tool used in underwriting; Schroders' GAiiA generative-AI investment analyst; Hiscox's
Gemini-powered lead underwriting model for a sabotage-and-terrorism insurance line; Shell and
SparkCognition's generative-AI subsurface exploration imaging; HSBC and Google Cloud's decision
assistant and financial-crime detection partnership; and all three of BAE Systems' confirmed
defence-sector use cases (an LLM-driven natural-language drone-command capability, a Typhoon
aircraft maintenance assistant, and an operationalised cyber-threat-insight system for customers).

A consistent pattern is observable across this high-stakes group: in every case, the generative
capability is paired with an explicit mitigating control rather than left to operate as an
autonomous decision-maker. Human review is retained — Hiscox's model drafts a broker email "for
underwriter review"; Schroders' tool assists analysts who draft the final summary themselves.
Outputs are grounded in cited sources to reduce the risk of fabricated information — RELX's
PharmaPendium and Lexis+ products both cite sources, and BAE Systems' Typhoon assistant is
described as providing "references to exactly where it found the information." Some deployments
disclose extensive pre-launch validation — RELX's ClinicalKey AI was "tested by more than 30,000
physicians before launch." This is the single clearest piece of evidence in the dataset that
companies deploying generative AI into higher-stakes tasks are not treating "the task involves
language, therefore an LLM is fine" as sufficient justification on its own; the discussion in
Section 5 returns to how much weight this finding can bear.

A further eight use cases (13.8%) apply generative techniques to structured or non-language inputs
rather than natural language — Rolls-Royce and Databricks' generative design of preliminary
aero-engine concepts; Shell and SparkCognition's generation of synthetic subsurface images; two
Diageo consumer-personalisation platforms; Tesco's advertising-creative generator; Auto Trader's
vehicle-description writer; a Synthesia-powered training-video product used by Intertek's clients;
and AstraZeneca's foundation-model analysis of real-world evidence data. These are legitimate,
confirmed generative-AI deployments under this project's inclusion rule, but they sit only partly
within the "unstructured language input" criterion, which is framed around language tasks
specifically. Their existence indicates that real-world generative-AI adoption at FTSE 100
companies is not confined to natural-language-input tasks, a point discussed further in Section 5.

### 4.5 Sector comparison [Table 4]

Sector-level confirmed-adoption rates vary considerably among sectors with at least three
researched companies:

| Sector | Researched | Confirmed operational | Rate |
|---|---:|---:|---:|
| Banks | 4 | 4 | 100% |
| Media | 4 | 3 | 75% |
| Food & drug retailing | 3 | 2 | 67% |
| Support services | 5 | 3 | 60% |
| Multiline utilities | 5 | 3 | 60% |
| Life insurance | 4 | 2 | 50% |
| Aerospace & defence | 4 | 2 | 50% |
| Financial services | 9 | 3 | 33% |
| Travel & leisure | 3 | 1 | 33% |
| Household goods & home construction | 3 | 1 | 33% |
| Real estate investment trusts | 4 | 1 | 25% |
| Mining | 6 | 1 | 17% |

**This variation must be read with considerable caution.** Every sector in this table has between
three and nine researched companies — far too few for any claim of statistical significance — and
the great majority of sector labels in the full dataset (18 of roughly 38 distinct labels) contain
only a single company, precluding any comparison at all for those sectors. No sector ranking in
this report should be read as evidence of a true, generalisable difference in underlying GenAI
adoption between industries; it is at most descriptive of the specific companies researched, and
plausibly reflects differences in public-disclosure culture as much as differences in actual
technology use (Section 6).

It is also worth noting where the 13 blocked companies sit sector-wise, since a gap that happens to
fall inside an already-small or already-high-adoption sector cell has an outsized effect on that
cell's apparent rate. Lloyds Banking Group, a blocked company, sits in the Banks sector, which shows
100% confirmed adoption among the four researched companies — but no independent evidence about
Lloyds' own generative-AI use was obtained, and this figure must not be extrapolated to Lloyds
specifically (Section 4.9).

### 4.6 Operational versus strategic versus governance evidence [Table 5, Table 5b]

A central finding of this project is the gap between companies that *discuss* generative AI at a
strategic or governance level and companies with a *confirmed operational deployment*.

| Group | Companies | % of 87 |
|---|---:|---:|
| Confirmed operational use case | 38 | 43.7% |
| Strategic-capability-building finding present | 33 | 37.9% |
| Governance/enablement finding present | 50 | 57.5% |
| Any of the above three | 65 | 74.7% |
| **Strategic or governance evidence, but no confirmed operational use case** | **27** | **31.0%** |
| No qualifying evidence of any kind | 22 | 25.3% |

Nearly three-quarters of evidence-based companies (74.7%) show *some* form of AI-related disclosure
— strategic, governance, or operational — but fewer than half (43.7%) have a confirmed operational
deployment. Twenty-seven companies, or 31.0% of the evidence-based sample, discuss AI strategy or
governance (board oversight, responsible-AI policies, workforce AI training) with no use case
meeting this project's operational bar. This group includes companies such as 3i, Admiral Group,
Beazley, British American Tobacco, Informa, Prudential plc, and Whitbread, among others (full list
in [Table 5b]).

This finding directly answers a subquestion in this project's founding brief — what proportion of
disclosures describe live deployment versus planned use, pilots, or broad ambition — at the company
level, and it is one of the clearest results in the dataset: **talk about generative AI, at the
level of strategy and governance, substantially outpaces confirmed deployment.**

### 4.7 Evidence quality [Table 6]

| Metric | Value |
|---|---|
| Confirmed use cases at `3_strong` evidence | 27 / 58 (46.6%) |
| Confirmed use cases at `2_moderate` evidence | 31 / 58 (53.4%) |
| Confirmed use cases at `high` confidence | 30 / 58 (51.7%) |
| Confirmed use cases at `medium` confidence | 28 / 58 (48.3%) |
| Confirmed use cases sourced from the company itself | 49 / 58 (84.5%) |
| Confirmed use cases sourced from a technology partner's case study | 9 / 58 (15.5%) |
| Confirmed use cases with a **measured**, quantified benefit | **1 / 58 (1.7%)** |
| Confirmed use cases with an unquantified observed benefit | 25 / 58 (43.1%) |
| Confirmed use cases with only an expected (prospective) benefit | 32 / 58 (55.2%) |

Just over half of the confirmed dataset (53.4%) rests on `2_moderate` evidence, meaning the specific
use case is clear but its scale, deployment stage, or outcomes are incompletely described. This is
expected, given the inclusion rule, but it means readers should not treat "confirmed" as
synonymous with "fully documented" — it means the use case passed a specific evidentiary bar, not
that every detail about it is known.

The benefit-evidence figures are more consequential for what this report can and cannot claim. Only
one use case in the entire confirmed dataset — AstraZeneca's Microsoft Copilot deployment, and even
then only via a survey of a sample of employees, not a company-wide measurement — carries a
genuinely measured, quantified outcome. Every other claimed productivity gain, time saving, or
service-quality improvement in this dataset is either an unquantified observation or a purely
prospective expectation. **This report cannot and does not claim that generative AI is delivering
measurable value at FTSE 100 companies; it can only report what companies themselves say they
expect or have observed.** Any productivity or efficiency language elsewhere in this report should
be read as reporting a company's own claim, not as an independently verified finding.

Fifteen and a half percent of confirmed evidence originates from a technology partner's own case
study (for example, a vendor's published account of a client engagement) rather than the company's
own disclosure. Such evidence is retained and labelled distinctly throughout the underlying dataset,
and this report does the same: partner-sourced claims are not treated as company-confirmed.

### 4.8 Null results and what they mean

Forty-nine companies returned a null result — no qualifying operational use case was found in the
sources collected and reviewed. It is important to state precisely what this does and does not
establish. **None of the 49 null-result companies has reached this project's own strict
certification threshold for asserting that no disclosure exists.** That threshold requires, among
other conditions, that every planned source-collection step be marked complete, unavailable, or
explicitly not applicable — and in the underlying dataset, every one of the 49 null-result companies
remains at a "pending sources" status, not the stricter "no disclosure confirmed" status.

Investigating the cause: for 47 of the 49 null-result companies, both the current and previous
annual report were successfully collected and reviewed — the highest-value sources were genuinely
examined, and no qualifying disclosure was found in them. But for the same 47 companies, a
separate sustainability or ESG report was never formally advanced past "not started," even in cases
where sustainability content is plausibly already integrated into the collected annual report and
could have been marked "not applicable." Five of the 49 also have an incomplete general web search.

The practical reading is a middle ground between two extremes. This is not a case of thin or
absent research — for the great majority of null-result companies, the two most important sources
were genuinely obtained and reviewed. But it is also not the case that every possible avenue of
public disclosure was exhausted for every company. **The correct statement, used throughout this
report, is that no qualifying evidence of generative-AI use was identified in the sources collected
and reviewed for these 49 companies — not that these companies do not use generative AI.** A
company may use generative AI without any public disclosure reaching the specific source
categories, languages, or search paths available to this project.

### 4.9 Sensitivity analysis for blocked companies [Table 7a, Table 7b]

The 13 blocked companies span a range of sectors and blocker types:

| Company | Sector | Blocker type |
|---|---|---|
| Lloyds Banking Group | Banks | Persistent access block |
| BP | Oil & gas producers | Persistent access block |
| Unilever | Personal goods | Persistent access block |
| Sage Group | Software & computer services | Persistent access block |
| Compass Group | Support services | Persistent access block |
| Imperial Brands | Tobacco | Persistent access block |
| Haleon | Pharmaceuticals & biotechnology | Persistent access block |
| Computacenter | Software & computer services | Persistent timeout |
| Associated British Foods | Food & tobacco | Persistent access block |
| Burberry Group | Personal goods | Persistent access block |
| M&G | Financial services | Encrypted document, extraction blocked |
| IMI | Industrial engineering | Persistent access block |
| Coca-Cola HBC | Beverages | Persistent access block |

Given these 13 unresolved companies, this report presents two figures, both derived from the
statistics already given in Section 4.2, and treats neither as an estimate of the true population
value:

- **Floor (observed):** 38 of 100 companies confirmed = **38.0%**.
- **Ceiling (if every blocked company would have qualified):** 51 of 100 = **51.0%**.

There is no basis in this project's evidence for assuming the true figure sits at any particular
point within that range, and there is a specific, documented reason not to assume the 13 blocked
companies simply resemble the 87 researched companies: several of them have named, unverified leads
recorded in the project's own working notes that could plausibly qualify if the company's sources
were ever accessed — for example, a BP disclosure referencing an "automated upstream" tool, and a
Sage Group product explicitly named "Sage Copilot" with an inaccessible anniversary press release.
Neither of these could be independently verified and neither is counted in this report's figures,
but their existence means the blocked group is not evidence-free; it is disproportionately a group
of companies with *some* signal of generative-AI activity that this project's tools could not
confirm to its own evidentiary standard. **The scientifically defensible statement is that the true
FTSE 100 confirmed-adoption rate lies somewhere in the interval [38.0%, 51.0%], and this project's
available tools cannot narrow that interval further.**

---

## 5. Discussion

### 5.1 What the findings suggest about the central thesis

Section 4.4 established that the modal pattern of confirmed generative-AI use at FTSE 100 companies
— accounting for close to two-thirds of confirmed use cases — combines unstructured language input,
generative or interpretive output, and a low or medium cost of error: internal drafting and
summarisation tools, customer-service assistants handling routine enquiries, and similar
applications where fluency is valuable and an occasional error is not consequential. This is
precisely the profile the central thesis would predict companies gravitate toward if they are
genuinely selecting deployments according to task characteristics.

More specifically supportive of the thesis is the pattern found among the smaller, higher-stakes
group of use cases (Section 4.4): every one of the eleven high-cost-of-error deployments identified
in this dataset is disclosed alongside some form of mitigating control — human review retained in
the workflow, source-grounded outputs, or extensive pre-launch validation. Companies deploying
generative AI into legal research, medical-report summarisation, insurance underwriting or defence
applications are not, on the evidence gathered here, treating the mere fact that a task "involves
language" as sufficient justification for an unmitigated LLM deployment. This is the single
strongest piece of disclosed, task-specific evidence in the dataset for the proposition that
companies deploy generative AI selectively rather than indiscriminately.

A further, more circumstantial piece of supporting evidence is the shape of the dataset as a whole:
31.0% of evidence-based companies discuss AI strategy or governance without a confirmed operational
deployment (Section 4.6), and 59% of confirmed use cases remain at a limited or pilot stage rather
than fully scaled (Section 4.3). Read generously, this is consistent with companies being cautious
and deliberate about where and how they deploy the technology, rather than deploying it wherever a
task happens to involve language. Read more conservatively, it may simply reflect the ordinary pace
of enterprise technology adoption, unrelated to any deliberate task-suitability reasoning — the
dataset cannot distinguish between these two readings (Section 5.3).

### 5.2 Which task types appear particularly suitable — and which apparent "AI adoption" should not be treated as operational

The results in Section 4.3 and 4.4 point toward internal productivity work — drafting, summarising,
answering employee questions from internal knowledge bases, code assistance — as the domain where
generative AI is both most commonly deployed and most structurally well-matched to the technology's
strengths. Customer-service applications handling routine, low-stakes enquiries occupy a similar
position, provided (as several confirmed use cases in this dataset show) escalation to a human
remains available for complex or sensitive cases.

At the other end, this report is deliberately cautious about treating every disclosed "AI"
capability as evidence of genuine, well-matched generative-AI deployment. Two patterns identified
during the research process, though not part of the final confirmed count, are worth naming
explicitly because they illustrate the distinction the conceptual framework is designed to draw.
First, several companies' annual reports describe detailed, plausible-sounding AI-powered customer
features — chatbots, engagement tools — using only generic "AI-powered" language, with no explicit
reference to generative AI, large language models, or a named generative product anywhere nearby in
the source text. Under this project's inclusion rule, such disclosures do not qualify as confirmed
generative-AI use cases, however sophisticated the underlying technology plausibly is, because the
public disclosure does not support the classification. Second, a number of disclosures describe
predictive, classification-based, or conventional-automation systems using AI-adjacent language
without any generative component — these were excluded from the outset. Both patterns are a
reminder that "the company mentions AI" and "the company has deployed generative AI for a specific
task" are different claims, and that this report's stricter standard, while it likely undercounts
true adoption to some degree (Section 6), avoids the opposite and arguably more misleading error of
treating every AI-adjacent mention as evidence of generative-AI use.

### 5.3 Complicating evidence

Three findings complicate a simple, unqualified acceptance of the central thesis.

First, more than a third of confirmed use cases (36.2%) fall outside the "classic good fit" pattern
entirely, whether by input type, output type, or cost of error (Section 4.4). If task-suitability
reasoning were being applied strictly and consistently across the FTSE 100, one might expect a
narrower, more homogeneous set of confirmed deployments. Instead, the dataset shows real
heterogeneity, including live, operational deployment in some of the highest-stakes categories
identified — insurance-pricing underwriting and defence applications among them. The thesis
describes a *tendency* observable in the data, not a rule the data uniformly obeys.

Second, the "unstructured language input" criterion, as stated, does not comfortably describe all
confirmed generative-AI use. Eight use cases (13.8%) apply generative techniques to structured data,
design parameters, or guided consumer inputs rather than natural language — generative design of
engineering concepts, synthetic subsurface imaging, personalisation platforms driven by
multiple-choice inputs. These are legitimate generative-AI deployments by this project's own
inclusion rule, and their existence suggests that real-world adoption is not neatly bounded by
whether a task's *input* is language, even where the central thesis's framing emphasises language
tasks specifically.

Third, and most fundamentally, this dataset documents what companies choose to disclose about their
deployments, not how well matched the task actually is in practice, and not whether the deployment
is succeeding. A company that pairs a high-stakes generative-AI use case with language about "human
review" is disclosing an intended control; this project cannot verify whether that control is
genuinely and consistently applied, or whether it is closer to reassuring risk-disclosure language.
The pattern identified in Section 4.4 and Section 5.1 is real and consistent, but it describes
disclosed design choices, not independently audited safety outcomes.

### 5.4 Alternative explanations

The patterns reported above are consistent with genuine, deliberate task-suitability reasoning by
companies, but at least two alternative explanations cannot be ruled out by this dataset. The
observed concentration of confirmed use cases in low-and-medium-stakes internal productivity tasks
may simply reflect which deployments are cheapest, fastest, and least organisationally risky to
build and publicise — independent of any explicit reasoning about task fit. Similarly, the
mitigating controls observed around high-stakes use cases (Section 5.1) may reflect standard
risk-disclosure practice in regulated industries such as insurance, financial services and defence,
rather than a deployment philosophy specific to generative AI. This report cannot distinguish
between "companies are reasoning carefully about task suitability" and "companies are following
pre-existing risk-management conventions that happen to produce a similar pattern," and it does not
attempt to adjudicate between them.

### 5.5 What the dataset can and cannot establish

This dataset can establish, with reasonable confidence, what a substantial and carefully verified
sample of FTSE 100 companies say they are doing with generative AI, in what business functions, at
what disclosed deployment stage, and — for a meaningful subset — with what disclosed controls. It
can establish that talk about AI strategy and governance substantially outpaces confirmed
deployment, and that the pattern of confirmed use skews toward, without being confined to, the
task profile the central thesis identifies as well suited to the technology.

It cannot establish whether generative AI is actually delivering the benefits companies claim for
it (Section 4.7); whether companies that deploy the technology into poorly matched tasks experience
worse outcomes than those that deploy it into well-matched tasks, since no outcome or failure data
exists in this dataset; whether the observed pattern reflects deliberate reasoning or incidental
convenience (Section 5.4); or what the true picture is for the FTSE 100 as a whole, given the 13
companies whose status remains genuinely unknown (Section 4.9) and the absence of certified closure
for any of the 49 null results (Section 4.8).

---

## 6. Limitations

**The 13 blocked companies.** Thirteen FTSE 100 constituents could not be researched to an
evidence-based conclusion because this project's automated collection tools — which do not include
a genuine interactive browser — were persistently unable to access their primary sources. This is a
structural gap, not a random one: several blocked companies have named, unverified leads suggesting
possible generative-AI activity, meaning the blocked group is plausibly not representative of the
"average" unresearched company (Section 4.9).

**Public-source bias.** This project's inclusion rule depends on company-primary disclosure or
named technology-partner case studies. This systematically favours companies with detailed,
English-language, easily discoverable public reporting over companies whose generative-AI use, if
any, is disclosed only through channels this project did not or could not reach — internal
communications, non-English filings, or investor calls without published transcripts.

**Uneven disclosure between companies.** A company that uses generative AI but chooses not to
disclose it publicly is indistinguishable, in this dataset, from a company that does not use it at
all. This project measures *disclosed* adoption, not *actual* adoption, and the gap between the two
is unknown and unmeasurable with the evidence gathered.

**Evidence-quality differences.** Just over half of confirmed use cases rest on the weaker of the
two qualifying evidence-strength ratings, and all but one lack a directly measured, quantified
benefit (Section 4.7). Conclusions about deployment scale or benefit should be read as reflecting
what companies claim, not as independently verified outcomes.

**Small sector samples.** The large majority of sector categories in this dataset contain very few
companies — many contain only one — making sector-level comparison indicative at best and
unreliable as a basis for any claim of a genuine, generalisable sectoral pattern (Section 4.5).

**Difficulty distinguishing current deployment from planned deployment.** While this project's
evidence-strength and deployment-stage coding are designed specifically to guard against this
(only detailed, specifically described use cases are confirmed as operational, and deployment stage
is recorded separately), some genuine ambiguity between an active pilot and a firmly planned but
not-yet-live initiative is unavoidable in disclosures that use inconsistent language across
companies.

**Potential under-reporting of unsuccessful or narrowly scoped internal experiments.** Companies
have limited incentive to publicise internal tools that are small in scale, unsuccessful, or
discontinued. Given that 60% of confirmed use cases are already internally oriented (Section 4.3),
the true incidence of narrow, low-profile internal generative-AI experimentation — both successful
and unsuccessful — is almost certainly higher than what reaches the level of annual-report
disclosure this project draws on.

**Limitations of automated source collection.** This project's toolset — automated document
retrieval and text extraction, without a genuine interactive browser — was sufficient for the great
majority of the population but proved insufficient for 13 companies (Section 3.6) and required
extensive, individually documented manual verification effort for others. A project conducted with
unrestricted, real-time human browser access would very likely resolve at least some of these
gaps, though not necessarily all of them (two of the thirteen blockers, for example, relate to
persistent server-side timeouts and document encryption respectively, which a browser alone would
not necessarily resolve).

---

## 7. Conclusion

**Direct answer to the research question.** Among the 87 FTSE 100 companies that could be
researched to an evidence-based conclusion, 38 (43.7%) have at least one confirmed operational
generative-AI use case, contributing 58 confirmed use cases in total. Against the full 100-company
population, this is 38.0%, with the true figure for the remaining 13 companies genuinely unknown
and bounded, at most, by a ceiling of 51.0% if every blocked company were eventually found to
qualify. Confirmed use is concentrated in internal employee-productivity applications — drafting,
summarising, and general-purpose assistance — with a substantial minority in customer-facing and
product-embedded roles, most frequently built on Microsoft's Copilot family of products. Discussion
of AI strategy and governance is considerably more widespread than confirmed deployment: nearly
three in four evidence-based companies show some form of AI-related disclosure, but fewer than half
have a confirmed use case meeting this project's operational bar.

**Overall assessment of the task-based framework.** The evidence gathered offers genuine, moderate
support for the central thesis that companies should deploy — and to a meaningful extent already do
deploy — generative AI selectively according to task characteristics, rather than assuming any
language-related task is automatically suitable. The clearest support comes not from the overall
adoption rate but from the pattern within it: the modal confirmed use case fits the profile of
unstructured input, generative output, and low-or-medium consequence of error that the framework
identifies as well suited to the technology, and where companies do deploy generative AI into
higher-stakes tasks, they consistently disclose accompanying controls rather than unmitigated
deployment. At the same time, this is a moderate finding, not a decisive one. More than a third of
confirmed use cases sit outside the framework's "good fit" profile, some of the highest-stakes
deployments identified are already live and scaled rather than confined to pilots, and a portion of
confirmed generative-AI use falls outside the framework's language-centred scope entirely.

**What the evidence supports.** That FTSE 100 generative-AI adoption, where it exists and is
disclosed, skews toward — without being confined to — tasks matching the profile the task-based
framework identifies as well suited; that strategic and governance discussion of AI substantially
outpaces confirmed operational deployment; and that where higher-stakes deployments do occur, they
are disclosed alongside identifiable mitigating controls rather than presented as autonomous,
unsupervised systems.

**What remains uncertain.** Whether generative AI is actually delivering the benefits claimed for
it; whether the observed deployment pattern reflects deliberate task-suitability reasoning or
simply reflects which applications are easiest and least risky to build and disclose; and what the
true adoption picture looks like across the 13 companies this project could not resolve, and among
the 49 null-result companies for which the project's own methodology has not yet certified an
exhaustive search.

**Implications.** For readers seeking to understand corporate generative-AI adoption, the central
lesson of this project is not a simple adoption percentage but a warning against treating "the
company uses AI" as a single, homogeneous fact. The same label — generative AI — covers an internal
email-drafting assistant and a defence-sector drone-command capability, an unmitigated experiment
and a system layered with human review and source grounding, a live deployment serving thousands of
employees and a single, cautious pilot. Any assessment of whether a given deployment is a *good* use
of the technology has to be made at the level of the individual task, not at the level of "does this
company have AI" — which is precisely the distinction this report's conceptual framework, and the
central thesis it was built to test, insist upon.

---

## Appendix: table reference key

| In-text citation | File |
|---|---|
| [Table 1] | `outputs/analysis/table_1_coverage.csv` |
| [Table 2] | `outputs/analysis/table_2_adoption.csv` |
| [Table 3] | `outputs/analysis/table_3_use_case_categories.csv` |
| [Table 3b] | `outputs/analysis/table_3b_task_suitability_detail.csv` |
| [Table 4] | `outputs/analysis/table_4_sector_comparison.csv` |
| [Table 5] | `outputs/analysis/table_5_strategic_governance_vs_operational.csv` |
| [Table 5b] | `outputs/analysis/table_5b_company_lists.csv` |
| [Table 6] | `outputs/analysis/table_6_evidence_quality.csv` |
| [Table 7a] | `outputs/analysis/table_7a_blocked_companies.csv` |
| [Table 7b] | `outputs/analysis/table_7b_blocked_sensitivity_bounds.csv` |

All figures in this report were independently verified against `company_summary_template.csv`,
`use_case_dataset_template.csv`, `strategic_capability_building_findings.csv`,
`governance_and_enablement_findings.csv`, and `manual_browser_resolution_queue_controller.csv` in
`outputs/intermediate/analysis_snapshot_2026-08-08_final_closure/` before inclusion in this draft.
No file in that snapshot, nor any of the project's underlying coding or pipeline scripts, was
modified in the preparation of this report.
