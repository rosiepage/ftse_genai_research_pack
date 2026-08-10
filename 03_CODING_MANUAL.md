# Coding manual

## Generative-AI test
Code `is_genai = yes` only if at least one condition is met:
1. The source explicitly says generative AI or GenAI.
2. It explicitly identifies an LLM or foundation model.
3. It names a product whose relevant function is unambiguously generative, such as Microsoft 365 Copilot, GitHub Copilot, ChatGPT, Claude or Gemini.
4. It describes generation of text, code, images, audio or other content through a clearly identified generative model.

Otherwise use `no` or `unclear`.

## Deployment stage
- `live_scaled`: operating in normal business use across a meaningful population.
- `live_limited`: operating in a bounded team, geography or workflow.
- `pilot`: trial, experiment, proof of concept or sandbox.
- `planned`: announced intention with no evidence of active testing.
- `partnership_only`: partnership announced but no use case or stage evidenced.
- `general_ambition`: broad strategic language only.
- `discontinued`: reported as stopped or replaced.
- `unclear`: insufficient evidence.

## User group
- employees
- customers
- suppliers_or_partners
- developers
- regulated_decision_makers
- public
- mixed
- unclear

## Orientation
- `internal`: improves an internal process.
- `customer_facing`: directly interacts with or produces outputs for customers.
- `product_embedded`: incorporated into a product or service sold to clients.
- `mixed`
- `unclear`

## Business function
Choose one primary function and, where useful, one secondary function:
- customer_service
- software_development_it
- marketing_content
- knowledge_document_work
- operations_supply_chain
- risk_legal_compliance
- finance_administration
- human_resources
- product_service_innovation
- research_development
- sales
- cybersecurity
- other
- unclear

## Claimed benefit
Use one or more controlled values:
- time_saving
- cost_reduction
- productivity
- service_quality
- personalisation
- revenue_growth
- innovation
- accuracy
- employee_experience
- risk_reduction
- accessibility
- other
- none_stated

## Evidence strength
- `3_strong`: company primary source identifies a specific use case and deployment stage, with measurable evidence or detailed operational description.
- `2_moderate`: specific use case is clear, but scale, stage or outcomes are incomplete.
- `1_weak`: vendor-led or vague description with limited corroboration.
- `0_not_qualifying`: does not meet inclusion criteria.

## Benefit evidence
- `measured`: quantified outcome with defined metric or comparison.
- `observed_unquantified`: source claims an experienced benefit without a number.
- `expected`: benefit is prospective.
- `none`: no benefit stated.

## Risk and governance fields
Record whether the source describes:
- human review;
- privacy or data protection controls;
- security controls;
- accuracy or hallucination controls;
- bias or fairness controls;
- restricted use cases;
- employee training;
- responsible-AI framework;
- impact assessment;
- monitoring or audit.

Use `yes`, `no` or `unclear`. `No` means the source does not mention the control, not that the company lacks it.

## Quotations
The evidence quotation must contain enough context to justify the coding. Do not exceed a short paragraph. Never paraphrase within the quotation field.

## Duplicates
Treat records as duplicates where company, underlying task, product and user population are substantively the same. Select the strongest primary source as the main record and list additional source IDs in `supporting_source_ids`.

## Document category vocabulary
This is the single, authoritative list of allowed values for the `document_category` column. It is used identically in `source_manifest.csv` and `use_case_dataset_template.csv` — do not create alternate spellings or a second list elsewhere.

- `annual_report_current`
- `annual_report_previous`
- `sustainability_or_esg_report`
- `press_release`
- `investor_presentation`
- `results_presentation`
- `strategy_or_technology_webpage`
- `official_case_study`
- `governance_or_responsible_ai_policy`
- `executive_speech_or_interview`
- `partner_case_study`
- `regulatory_filing_or_rns`
- `earnings_call_transcript`
- `parliamentary_or_regulator_evidence`
- `third_party_interview`
- `vendor_conference_presentation`
- `other`

## Sector lookup rule
`sector` must always be populated by looking up the company in `ftse100_constituents_2026-06-19.csv`. Never type or infer a sector value manually in `source_manifest.csv`, `use_case_dataset_template.csv`, or `company_summary_template.csv`. This prevents sector-label inconsistencies (e.g. "Financial services" vs. "Financial Services") from diverging across files.

## Calculation rules

### provisional_use_case_count
The pre-validation, "appears to qualify" count. For a given company, count rows in `use_case_dataset_template.csv` where:
- `is_genai = yes`; and
- `evidence_strength` is one of `1_weak`, `2_moderate`, `3_strong`; and
- `duplicate_of_record_id` is blank; and
- `review_status` is not `reviewed_excluded`.

This deliberately still includes `1_weak` evidence and rows with `review_status = not_reviewed` — that is the purpose of a provisional count. It excludes only rows a human reviewer has already rejected outright.

### confirmed_use_case_count
The strict, validated count. For a given company, count rows in `use_case_dataset_template.csv` where:
- `is_genai = yes`; and
- `evidence_strength` is one of `2_moderate`, `3_strong` (never `1_weak`); and
- `review_status` is one of `reviewed_confirmed`, `reviewed_corrected`; and
- `duplicate_of_record_id` is blank.

`1_weak` evidence, `unclear`/`no` values of `is_genai`, unreviewed rows, excluded rows, and duplicate supporting rows must never be counted here. Weak-evidence rows remain in the dataset for transparency but are never reported as confirmed use cases.

### no_disclosure_confirmed
Tracked per company in `company_summary_template.csv`, with four allowed values:
- `not_yet_assessed` — default, before sourcing begins.
- `pending_sources` — set while any of the five collection/search fields is still `not_started`, or while any document marked `collected` has a corresponding `source_manifest.csv` row still at `document_review_status = not_yet_reviewed`.
- `disclosure_found` — set as soon as `confirmed_use_case_count >= 1`, even if other sourcing for the company is not yet finished.
- `no_disclosure_confirmed` — set only manually by a human reviewer, and only once all of the following hold:
  1. `annual_report_latest_collected`, `annual_report_previous_collected`, and `separate_sustainability_report_collected` are each `collected`, `unavailable`, or `not_applicable` (none left at `not_started`);
  2. `official_web_search_completed` and `partner_search_completed` are both `complete` (not `incomplete`);
  3. every document actually marked `collected` has a manifest row with `document_review_status` not equal to `not_yet_reviewed`;
  4. any `unavailable` or `not_applicable` sources are explicitly recorded as such, not left blank;
  5. `confirmed_use_case_count = 0`.

A source marked `unavailable` or `not_applicable` is not required to show `reviewed_no_relevant_evidence` — it was never reviewable, so it is excluded from that check rather than treated as a gap.

## Controlled field definitions

### 1. confidence
- `high`: the classification is directly and unambiguously supported by the source.
- `medium`: some inference is required, but the classification is still reasonably supported.
- `low`: substantial judgment is required or the passage is borderline.

### 2. review_status
- `not_reviewed`: no human validation has taken place.
- `reviewed_confirmed`: the human reviewer agrees with the coded record.
- `reviewed_corrected`: the human reviewer changed one or more fields.
- `reviewed_excluded`: the human reviewer determined that the record should not qualify.

### 3. page_or_section
Allow:
- a single page number;
- a page range;
- a named section;
- a webpage paragraph reference;
- `not_applicable`.

Examples:
```
42
42–43
Risk management section
Webpage, paragraph 6
not_applicable
```

### 4. quantified_metric
Populate only where `benefit_evidence = measured`. It must include:
- the numerical value;
- the unit;
- what the metric measures;
- the relevant timeframe where stated.

Do not infer or calculate metrics that are not explicitly supported by the source. Use `not_applicable` where `benefit_evidence` is not `measured`.

### 5. logged_by
Allowed values:
- `claude_code`
- `human`

### 6. coded_by
Allowed values:
- `claude_code`
- `human`

### 7. model_version
Populate only when the current environment can verify the model identifier. Otherwise leave blank.

### 8. supporting_source_ids
Use a semicolon-separated list of source IDs.

Example:
```
AZN-001;AZN-004;AZN-007
```

Leave blank where there are no additional supporting sources.

### 9. evidence_origin
- `company_primary`
- `technology_partner`
- `third_party_named_executive`
- `other`

### 10. document_review_status
- `not_yet_reviewed`
- `reviewed_evidence_found`
- `reviewed_no_relevant_evidence`

## Remaining controlled field definitions

### 1. download_status
- `not_downloaded`: the source has been identified but no local copy has been saved.
- `downloaded`: the source has been successfully saved locally.
- `unavailable`: the source could not be accessed or downloaded.

### 2. text_extraction_status
- `not_extracted`: no text extraction has been attempted.
- `extracted`: usable text has been extracted.
- `extraction_failed`: extraction was attempted but did not produce usable text.

### 3. risk_or_limitation_discussed
- `yes`: the source explicitly discusses a risk, limitation, uncertainty, or potential harm connected to the use case.
- `no`: no such discussion appears in the cited evidence.
- `unclear`: the wording is too vague to classify confidently.

### 4. duplicate_of_record_id
- Leave blank when the record is the main standalone use-case record.
- Otherwise enter the `record_id` of the main record into which this duplicate was merged.
- Never delete duplicate rows silently.

### 5. annual_report_latest_collected
### 6. annual_report_previous_collected
### 7. separate_sustainability_report_collected
Allowed values for each:
- `not_started`
- `collected`
- `unavailable`
- `not_applicable`

For `separate_sustainability_report_collected`, use `not_applicable` where sustainability reporting is integrated into another collected report.

### 8. official_web_search_completed
### 9. partner_search_completed
Allowed values:
- `not_started`
- `complete`
- `incomplete`

### 10. manual_review_status
- `not_sampled`: the company was not selected for manual validation.
- `pending_review`: selected for validation but not yet completed.
- `review_complete`: manual validation has been completed.
