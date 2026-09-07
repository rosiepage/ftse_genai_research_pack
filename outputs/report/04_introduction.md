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

# Judgment calls in this draft

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
