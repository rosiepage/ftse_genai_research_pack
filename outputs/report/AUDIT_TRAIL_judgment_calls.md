# Audit trail: Judgment Calls across all five report sections

This file collects every "Judgment Calls" self-review appendix from the five drafted report
sections, in one place, for reference. It is not part of the reader-facing report
(`FTSE100_GenAI_Report_FINAL.md`); it exists so the reasoning behind every wording, emphasis, or
framing choice made while drafting is preserved and checkable, without requiring a reader of the
final report to read past it.

## From `04_introduction.md`

Self-tested against the same standard as the preceding sections: for each choice below, am I
stating the fact plainly, or managing how the reader should feel about it?

- **The claim that FTSE 100 companies are "a natural population for this question" because they
  are "under continuous pressure... to describe their use of new technology."** This is a
  reasonable, conventional justification for the population choice, but it is not itself a
  finding this dataset establishes — it is scene-setting, stated with appropriate hedging ("if any
  set of companies were going to leave a detailed... record, it would be this one") rather than as
  a proven claim. I judged this acceptable framing for an Introduction, but it is closer to
  argument than to fact, and I want that visible rather than smoothed over.
- **Not stating the central thesis in full, quoted form, in the Introduction**, reserving the full
  argument for the Discussion section. An equally defensible alternative would state the complete
  thesis sentence here too, so a reader who stops after the Introduction still gets the whole
  claim rather than a preview of it.
- **Describing the report's contribution as "the asymmetry — not the adoption figure on its own"**
  without yet stating the adoption figure's actual value (38.0%/43.7%) in the Introduction body
  text. This is a deliberate choice to keep the Introduction free of the detailed headline
  statistics (which appear in Results), but it means a reader relying only on the Introduction
  would not learn the adoption rate itself — only that it exists and is not the main point.

---

## From `01_methodology_and_limitations.md`

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

---

## From `02_results.md`

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

---

## From `03_discussion.md`

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

---

## From `05_conclusion.md`

Self-tested against the same standard as the preceding sections: for each choice below, am I
stating the fact plainly, or managing how the reader should feel about it?

- **Omitting the [38.0%, 51.0%] population-wide sensitivity interval for the 13 blocked
  companies.** This number exists, correctly computed, in `ANALYSIS_MEMO.md` §8, but it was never
  carried into Methodology, Results, or Discussion, and this section was drafted under a hard
  constraint not to introduce anything not already established in those three files. I judged
  that omitting it here — rather than quietly introducing it for the first time in the
  Conclusion — was the correct call under that constraint, even though it means the Conclusion's
  treatment of "the true adoption rate is unresolved" is less quantified than it could be. If you
  want this interval in the report at all, it needs to be added to Results or Discussion first,
  not slipped into the Conclusion.
- **The closing sentence's framing ("a large share of these companies have told the public what
  they built, and almost none of them have told the public whether it was worth building").**
  "Large share" and "almost none" are prose restatements of **43.7%** and **19%**-of-a-minority
  respectively (both already stated earlier in this section with their exact figures) — this is a
  rhetorical closing line, not a place where a new, unsupported characterisation is smuggled in,
  but it is doing more persuasive work than a plain restatement of the numbers would. An
  alternative, flatter closing would repeat the exact percentages one final time instead.
- **Choosing to end on a normative note** ("a future study... would need to look somewhere this
  report's own sources could not reach") **rather than a purely descriptive one.** This is
  argumentative — it recommends a research direction rather than only summarising findings. It
  follows directly from the Limitations and Discussion sections' own content (the specific source
  types named — regulatory filings, workforce/union disclosures, litigation records — are the same
  ones named in Methodology and Discussion as absent from this project's corpus), so it does not
  introduce a new factual claim, but it is more prescriptive than a strictly neutral conclusion
  would be.
- **Restating all four central findings from Results/Discussion in one dense paragraph**, rather
  than as a shorter list or with fewer of them emphasised equally. I judged that a genuine closing
  argument needed all four to make the "evidence collapses in sequence" case convincingly, but a
  shorter conclusion emphasising only the single strongest finding (the evidentiary cascade) would
  also be defensible and more concise.