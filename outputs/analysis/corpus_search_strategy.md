# Original corpus search strategy: what was actually queried

**Prepared:** 2026-08-09. Read-only review of the project's own design documents and the
actually-collected source records. No dataset, script, or snapshot file was modified.

## What kind of record exists (and what doesn't)

There is no file anywhere in this project that logs literal, executed search-engine query
strings. `pipeline/scripts/02_validate_source_candidates.py`'s own docstring states the actual
mechanism plainly: *"Claude Code's own source-discovery step (web search / fetch, or a manual
browser check where a site blocks automated access) produces
`outputs/intermediate/<company>_source_candidates.csv`."* In other words, web search and page
fetches were performed live, one company at a time across many sessions, guided by (not
mechanically generated from) the written collection guide below -- the individual query strings
typed into each search were never written to a file. `outputs/intermediate/<company>_source_candidates.csv`
(87 files, one per researched company) has no `search_query` column; its `notes` field
occasionally mentions "located via search this session" in prose but never records the literal
query.

What *does* exist, and is shown in full below, is (1) the written instructions that governed what
to search for, (2) the literal keyword list used to algorithmically screen already-collected
document text, and (3) the empirical record of what source types were actually collected -- the
most reliable evidence of what the corpus-building process actually did, as opposed to what it
was permitted to do.

## 1. `02_DOCUMENT_COLLECTION_GUIDE.md` -- the governing instructions (verbatim, in full)

```
# Documents to collect

Create one folder per company inside `sources/company_documents/`.

## Required documents for every company

### A. Latest annual report
Collect the latest annual report available by 14 July 2026. Prefer the full annual report PDF rather than a webpage summary.
Purpose: official discussion of strategy, operations, risks, investment and material deployments.

### B. Previous annual report
Collect the immediately preceding annual report.
Purpose: identifies changes over time and captures earlier pilots that may have developed into deployments.

### C. Latest sustainability, ESG or responsible-business report
Collect this only where it is a separate substantive report.
Purpose: workforce, responsible-AI, governance, environmental and social disclosures.

## Required web evidence search for every company
Search the official company website for:
generative AI / GenAI / large language model / LLM / foundation model / copilot / ChatGPT /
Claude / Gemini / Microsoft 365 Copilot / GitHub Copilot / Amazon Bedrock / Azure OpenAI /
Google Vertex AI

Collect relevant: company press releases; investor presentations; results presentations;
strategy or technology webpages; official case studies; governance or responsible-AI policies;
speeches or interviews published by the company.

## Partner evidence
Search major technology-provider case-study libraries for the company name. Likely sources
include Microsoft, Google Cloud, AWS, IBM, Salesforce, ServiceNow, Adobe, SAP, Oracle, NVIDIA
and model providers. Code their evidence origin as `technology_partner`, not `company_primary`.

## Optional sources
Use selectively:
- regulatory filings and RNS announcements;
- earnings-call transcripts, where legally accessible;
- parliamentary or regulator evidence submitted by the company;
- reputable interviews quoting a named company executive;
- vendor conference presentations featuring a named company representative.

## Sources not suitable as final evidence
Do not rely on: search snippets; unsourced blogs; generic news summaries; social posts without
substantive detail; automatically generated stock-market pages; Wikipedia as evidence of a use case.
News can help locate a primary source but should usually not be the final citation.
```

Nothing in this guide instructs searching for incidents, complaints, litigation, regulatory
enforcement action, whistleblower material, or union/employee-relations disclosures. "Regulatory
filings and RNS announcements" and "parliamentary or regulator evidence submitted by the
company" are present, but both are explicitly optional ("use selectively"), not required, and
both are framed as company-submitted material (i.e. the company's own filing/evidence), not
independent regulatory scrutiny of the company.

## 2. `05_KEYWORDS.txt` -- the literal keyword list (verbatim, in full)

Used by `pipeline/scripts/05_screen_keywords.py` to algorithmically flag candidate passages
within already-collected document text (not to generate search-engine queries):

```
generative AI, GenAI, gen AI, large language model, large-language model, LLM, foundation model,
copilot, Microsoft 365 Copilot, GitHub Copilot, ChatGPT, OpenAI, Claude, Anthropic, Gemini,
Google Vertex AI, Azure OpenAI, Amazon Bedrock, Bedrock, text generation, content generation,
code generation, synthetic content, retrieval augmented generation, retrieval-augmented
generation, RAG, prompt engineering, AI assistant, AI agent, agentic AI
```

All 30 entries are technology/product-name terms. None reference incidents, harm, complaints,
regulatory enforcement, litigation, redundancy, or industrial relations.

## 3. What was actually collected -- `document_category` across all 214 rows of `source_manifest.csv`

| document_category | Count | Share |
|---|---:|---:|
| annual_report_current | 84 | 39.3% |
| annual_report_previous | 82 | 38.3% |
| press_release | 26 | 12.1% |
| partner_case_study | 10 | 4.7% |
| sustainability_or_esg_report | 5 | 2.3% |
| strategy_or_technology_webpage | 4 | 1.9% |
| results_presentation | 1 | 0.5% |
| regulatory_filing_or_rns | 1 | 0.5% |
| official_case_study | 1 | 0.5% |

## Direct answer: was anything incident/regulatory/complaint/union-oriented ever queried?

- **Incidents:** never mentioned in the guide, the keyword list, or the `document_category`
  controlled vocabulary. No incident-oriented search was ever part of the design or the record.
- **Complaints:** same -- absent from the guide, the keyword list, and every category actually
  used.
- **Union or employee-relations disclosures:** same -- absent throughout. (The dataset does have
  an `employee_training` field, but this records whether a company disclosed *AI training
  provided to* employees, not a grievance, industrial-relations, or workforce-impact source.)
- **Regulatory filings / RNS announcements:** permitted as an optional category, and in practice
  almost never used -- exactly **1 of 214** collected sources (0.5%) is tagged
  `regulatory_filing_or_rns`.
- **Earnings-call transcripts** and **parliamentary/regulator evidence submitted by the
  company:** both explicitly permitted as optional categories in the guide, but **zero** of the
  214 collected sources carry either category -- neither was ever actually used, despite being
  allowed.
- **Everything else actually collected (99.5% of the 214 sources)** is annual reports, press
  releases, partner case studies, sustainability reports, and strategy/technology webpages --
  entirely company-authored or vendor-promotional material. Nothing adversarial, independent, or
  oriented toward surfacing problems, harms, or organised labour perspectives was ever part of
  the corpus in practice, and only one narrow, optional, company-submitted regulatory category
  was used at all, on a single occasion.

## Files reviewed

- `02_DOCUMENT_COLLECTION_GUIDE.md` (read-only)
- `05_KEYWORDS.txt` (read-only)
- `source_manifest.csv` (live root file, read-only)
- `pipeline/scripts/02_validate_source_candidates.py` (read-only, docstring only)
- `outputs/intermediate/aviva_source_candidates.csv` (sampled to confirm no query-log column
  exists in the per-company candidate files; the same column structure is shared across all 87
  `<company>_source_candidates.csv` files)
