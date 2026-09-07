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

---

# Judgment calls in this draft

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
