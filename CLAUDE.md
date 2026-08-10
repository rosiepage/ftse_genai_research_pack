# FTSE 100 Generative AI Research Project

## Project objective
Build a reproducible dataset answering:

**How are FTSE 100 companies using generative AI?**

The unit of analysis is a publicly reported generative-AI use case by a company that was in the FTSE 100 after the 19 June 2026 index changes.

## Core rules
1. Use only evidence contained in files placed in `sources/` or URLs recorded in the source manifest.
2. Never infer that a company uses generative AI merely because it discusses AI generally.
3. Record a use case only where the source explicitly refers to generative AI, large language models, foundation models, copilots, or a clearly identified generative-AI product.
4. Distinguish implemented deployments from pilots, partnerships, plans and general commentary.
5. Every coded row must contain a verbatim supporting quotation, source file, page number where available, publication date and URL.
6. Do not treat a technology supplier's promotional claim as company-confirmed evidence unless this is labelled in `evidence_origin`.
7. Do not merge distinct use cases merely because they occur within the same business function.
8. Preserve uncertainty. Use `unclear` rather than guessing.
9. Write intermediate data to `outputs/intermediate/`. Write final cleaned data to `outputs/final/`.
10. Do not overwrite manually reviewed fields.

## Recommended workflow
1. Read `01_PROJECT_BRIEF.md`.
2. Read `02_DOCUMENT_COLLECTION_GUIDE.md`.
3. Read `03_CODING_MANUAL.md`.
4. Inspect `ftse100_constituents_2026-06-19.csv`.
5. Validate `source_manifest.csv` and report missing documents.
6. Extract candidate passages using the keyword list.
7. Code passages into the schema in `use_case_dataset_template.csv`.
8. Deduplicate candidate use cases.
9. Generate a manual-review sample using `04_VALIDATION_PLAN.md`.
10. Produce summary tables, charts and a methodological audit log.

## Required outputs
- `outputs/final/ftse100_genai_use_cases.csv`
- `outputs/final/company_summary.csv`
- `outputs/final/sector_summary.csv`
- `outputs/final/methodology_log.md`
- `outputs/final/manual_validation_sample.csv`
- `outputs/final/figures/`

## Do not do
- Do not classify ordinary predictive machine learning, automation, robotics or analytics as generative AI.
- Do not use search-result snippets as final evidence.
- Do not invent page numbers, dates, vendors, business benefits or deployment stages.
- Do not count repeated descriptions of the same deployment as separate use cases.
