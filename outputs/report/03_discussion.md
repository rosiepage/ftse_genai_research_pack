# Discussion

*Draft section — Discussion only, following the approved Methodology, Limitations, and Results
sections. Introduction and Conclusion are not yet drafted. All figures below restate numbers
already established and verified in Methodology and Results; no new statistic is introduced here
without a citation back to where it was first derived.*

## 1. The central finding: what gets disclosed is not evenly distributed across the research question

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

## 2. The evidence-density cascade, stated as a sequence

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

## 3. A secondary lens: what kind of tasks are being implemented

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
have an output that leans toward classification rather than genuine generation; and a **separate
19%** (**11** of **58**) carry a high cost of error if wrong. These groups overlap rather than add
cleanly to 21: **Shell**'s use case is both structured-input and high-cost; **HSBC**'s
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

## 4. Why the asymmetry might exist — more than one explanation, none of them provable here

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

## 5. What this means: a finding about disclosure, not only about deployment

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

## 6. What the task-suitability lens can and cannot add to that finding

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

# Judgment calls in this draft

Self-tested against the same standard as the Methodology, Limitations, and Results
sections: for each choice below, am I stating the fact plainly, or managing how the reader
should feel about it? One item failed on self-review and was rewritten before this draft was
shown to you.

- **Fixed on self-review: Section 4's framing of the disclosure-incentive explanation.** An
  earlier draft stated as fact that "companies disclose successes and suppress failures." That is
  an assertion about company *intent* this dataset cannot support — it describes a plausible
  incentive, not an observed behaviour. Rewritten to state it as one of three explanations this
  report cannot adjudicate between, with the actual limiting fact ("this report has no way to
  distinguish a company that measured a benefit and chose not to publish it from a company that
  never measured one at all") doing the work instead of an unsupported claim about motive.
- **Presenting three explanations in Section 4 with no stated preference among them.** This is a
  deliberate choice, not an oversight: a reader might expect a report to pick the most likely
  explanation. I judged that picking one would overstate what a disclosure-only dataset can
  establish about *why* a pattern exists, as opposed to *that* it exists. An alternative,
  equally defensible approach would rank the three by plausibility even without proof.
- **Leading the Discussion with the asymmetry finding (Sections 1–2) before the task-suitability
  lens (Section 3), rather than the reverse.** This directly follows the brief's instruction that
  the task-suitability framework is secondary, not the organizing thesis — but the ordering
  itself is my implementation choice, not something dictated word-for-word.
- **Describing the high-cost-of-error control pattern (Section 3) as "the most analytically
  interesting finding this lens produces."** This is an editorial judgement about which finding
  matters most within Section 3, not a claim with a number attached — a reasonable alternative
  view would rank the 64%/36% split itself as the more important finding, since it's the
  higher-level pattern.
- **Choosing not to restate the full company list behind the 27 "talk without deployment"
  companies, or the 22 "zero qualifying evidence" companies, in this section.** Both lists exist
  in Results/`ANALYSIS_MEMO.md` §5 already; I judged the Discussion didn't need them repeated
  here, since neither list changes based on anything argued in this section.
- **Fixed on self-review: Section 5 originally claimed that voluntary favourable-framing
  disclosure "is the norm for any technology adoption, not a generative-AI-specific failing."**
  That is an unsupported comparative claim — this report studied only generative AI and has no
  comparison group of other technologies to know whether this asymmetry is typical or unusual.
  I caught this while re-reading my own Judgment Calls list rather than before drafting, which is
  itself worth flagging: I'd initially written the flawed sentence, listed it here as a problem,
  and left the flawed sentence sitting in the body text uncorrected — an inconsistency with how I
  handled the Section 4 issue. Rewritten to state plainly that this report takes no position on
  whether generative-AI disclosure is more or less asymmetric than disclosure of other
  technologies.
