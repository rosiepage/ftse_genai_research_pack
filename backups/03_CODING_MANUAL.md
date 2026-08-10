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
