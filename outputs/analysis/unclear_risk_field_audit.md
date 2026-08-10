# Audit: are "unclear"-coded risk/control fields backed by per-row judgment?

**Prepared:** 2026-08-09
**Scope:** the 58 confirmed operational use cases in `use_case_dataset_template.csv` (the same
strict `confirmed_use_case_count` filter used throughout `ANALYSIS_MEMO.md`).
**Question:** for `risk_or_limitation_discussed` and the eight other risk/control fields
(`human_review`, `privacy_control`, `security_control`, `accuracy_control`,
`bias_fairness_control`, `monitoring_audit`, `restricted_use_control`,
`impact_assessment_control`), when a row is coded `unclear`, does `reviewer_notes` show an
active, field-specific judgment call, or does it only discuss `evidence_strength`/`confidence`?

## Method

For every confirmed row where a given field equals `unclear`, the standard promotion-process
boilerplate ("Promoted from staging... (reviewer_decision=...)", "evidence_strength/confidence
explicitly approved by the human operator: ...") was stripped out of `reviewer_notes`, and the
remaining text was checked for keywords relevant to that specific field (e.g. "risk"/"limitation"
for `risk_or_limitation_discussed`; "privacy" for `privacy_control`; "monitor"/"audit" for
`monitoring_audit`). A hit means the note discusses that field's topic at all, not that it meets
any particular bar of rigor.

Three initial keyword hits (all on `human_review`, all three AstraZeneca rows) were manually
verified by reading the full `reviewer_notes` text and found to be false positives: each note reads
"Approved during the AstraZeneca human-review pass (2026-07-15)," which refers to the human
researcher's review of the *promotion decision itself*, not a stated judgment about the use case's
own human-oversight control. These three are counted as zero-rationale below.

## Finding: the coding manual only defines one of these nine fields

`03_CODING_MANUAL.md` defines `risk_or_limitation_discussed` explicitly (lines 248-251: `yes` =
"the source explicitly discusses a risk, limitation, uncertainty, or potential harm"; `no` = "no
such discussion appears"; `unclear` = "the wording is too vague to classify confidently"). The
other eight fields (`human_review`, `privacy_control`, `security_control`, `accuracy_control`,
`bias_fairness_control`, `monitoring_audit`, `restricted_use_control`,
`impact_assessment_control`) do not appear anywhere in the coding manual — there is no documented
definition of what `yes`/`no`/`unclear` mean for any of them.

## Final counts

| Field | Unclear rows (of 58 confirmed) | Rows with field-specific rationale in reviewer_notes | Rows with zero field-specific rationale |
|---|---:|---:|---:|
| `risk_or_limitation_discussed` | 52 | 0 | 52 |
| `human_review` | 3 | 0 (3 initial hits, all false positives — see Method) | 3 |
| `privacy_control` | 3 | 0 | 3 |
| `security_control` | 3 | 0 | 3 |
| `accuracy_control` | 2 | 0 | 2 |
| `bias_fairness_control` | 3 | 0 | 3 |
| `monitoring_audit` | 3 | 0 | 3 |
| `restricted_use_control` | 3 | 0 | 3 |
| `impact_assessment_control` | 3 | 0 | 3 |
| **TOTAL (cells across all 9 fields)** | **75** | **0** | **75** |

**Zero of the 75 "unclear" cells across these nine fields, on any of the 58 confirmed rows, have
a documented, field-specific rationale in `reviewer_notes`.** Every `reviewer_notes` entry checked
discusses only the `evidence_strength`/`confidence` approval decision, plus (for AstraZeneca's
three rows specifically) one general, non-row-specific remark that these fields as a group were
left unclear because "the source never directly states any control is present or absent"
(`AZN-UC-002`'s note) — itself not a per-row judgment, and not repeated on the other 74 unclear
cells.

## Interpretation

This is consistent with, and sharpens, the concern raised during the earlier reassessment of the
"unintended consequences" research question: for the vast majority of confirmed use cases, these
nine fields read as an unpopulated schema default rather than an actively applied test — even for
`risk_or_limitation_discussed`, the one field the coding manual does define with an explicit
`unclear` = "too vague to classify confidently" test. If that test had genuinely been applied
row-by-row to 52 different pieces of source evidence, some record of the reasoning would be
expected in at least a handful of the 52 `reviewer_notes` entries; none was found.

**Practical consequence for the report:** these fields cannot be used to make any claim of the form
"most confirmed use cases don't disclose a [risk/human-review/privacy/etc.] control" — the `no`
values (55/58 on most fields) cannot be distinguished from "not actively assessed," and the
`unclear` values (75 cells total) show no evidence of having been assessed at all. The only
evidence-based statement this dataset supports is the one already established by reading
`evidence_quotation` text directly (as in `ANALYSIS_MEMO.md` §4): specific, quotable mitigating
language appears in the free-text evidence for particular use cases, on a case-by-case basis — but
the *structured* control fields cannot be summarised into an aggregate count or percentage.

## Files checked

- `use_case_dataset_template.csv` (live root file) — read-only, not modified
- `03_CODING_MANUAL.md` — read-only, not modified
