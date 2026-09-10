# Uncommitted Candidate Rows

Fully-drafted use-case rows that were identified and coded but deliberately **not** added to
`use_case_dataset_template.csv`, so the current n=58 dataset and every dependent report figure
remain unchanged. Preserved here so the work is not lost and can be incorporated in a future
dataset revision, along with the reasoning and any unresolved judgment calls.

## VOD-UC-003 (candidate, not added)

Identified 2026-09-07 during a post-finalization spot-check of Vodafone Group's recorded use
cases. Full detail and rationale: `outputs/KNOWN_GAPS.md`.

| Field | Proposed value |
|---|---|
| `record_id` | VOD-UC-003 |
| `company` | Vodafone Group |
| `ticker` | VOD |
| `sector` | Mobile telecommunications |
| `source_id` | VOD-002 |
| `document_title` | Meet SuperTOBi -- Vodafone's new Generative AI virtual assistant now serving customers in multiple countries |
| `document_category` | press_release |
| `evidence_origin` | company_primary |
| `publication_date` | 2024-07-04 |
| `url` | https://www.vodafone.com/news/newsroom/technology/meet-super-tobi-vodafone-s-new-generative-ai-virtual-assistant-now-serving-customers-in-multiple-countries |
| `local_filename` | VOD_company_press_release_meet-supertobi-vodafone-s-new-generative-ai-virtual-assistan_2024-07-04.html |
| `page_or_section` | not_applicable |
| `evidence_quotation` | "Based on Microsoft Azure OpenAI's Agent Copilot solution, SuperAgent helps human agents to quickly search and locate answers to complex queries or multiple questions. In Ireland, SuperAgent is assisting agents by sending a summary of its online customer conversation to the agent, so customers don't need to repeat themselves." |
| `is_genai` | yes |
| `use_case_name` | SuperAgent generative-AI agent-assist tool for customer care employees |
| `use_case_description` | SuperAgent, an internal bot assistant for Vodafone's own customer care employees, built on Microsoft Azure OpenAI's Agent Copilot solution. Helps human agents quickly search and locate answers to complex or multi-part customer queries, drawing only on Vodafone's internal knowledge base. In Ireland, SuperAgent generates a summary of the customer's prior online conversation for the agent, so the customer does not have to repeat themselves. |
| `primary_business_function` | customer_service |
| `secondary_business_function` | knowledge_document_work *(judgment call)* |
| `user_group` | employees |
| `orientation` | internal |
| `deployment_stage` | live_limited |
| `named_tool_or_model` | SuperAgent (built on Microsoft Azure OpenAI's Agent Copilot) |
| `technology_partner` | Microsoft (Azure OpenAI) |
| `claimed_benefits` | productivity;service_quality *(judgment call)* |
| `benefit_evidence` | observed_unquantified *(judgment call)* |
| `quantified_metric` | not_applicable |
| `risk_or_limitation_discussed` | unclear |
| `human_review` | no |
| `privacy_control` | no |
| `security_control` | no |
| `accuracy_control` | no |
| `bias_fairness_control` | no |
| `employee_training` | no |
| `responsible_ai_framework` | no |
| `monitoring_audit` | no |
| `restricted_use_control` | no *(judgment call — see below)* |
| `impact_assessment_control` | no |
| `evidence_strength` | 2_moderate |
| `confidence` | medium |
| `review_status` | not_reviewed |
| `reviewer_notes` | Proposed 2026-09-07: same source press release as VOD-UC-001 (VOD-002/SuperTOBi), which names three products — SuperTOBi, SuperAgent, SuperSearch — but only SuperTOBi was originally coded. SuperAgent meets is_genai bar (named product built on Microsoft Azure OpenAI's Agent Copilot solution; describes a generative search/summarization function for internal customer-care agents). SuperSearch checked and excluded: no generative-AI signal given in source. Row identified and drafted by Claude Code; not yet human-reviewed. |
| `supporting_source_ids` | *(blank)* |
| `duplicate_of_record_id` | *(blank)* |
| `coded_by` | claude_code |
| `model_version` | claude-sonnet-5 |
| `coded_date` | 2026-09-07 |

### Unresolved judgment calls on this row

1. **`restricted_use_control`** — the passage states SuperAgent "only uses information from
   Vodafone's companywide and private knowledge database, ensuring that the information is more
   reliable than public sources." This could plausibly count as a disclosed restricted-use
   control (grounding the model to internal data only) rather than "no." Defaulted to "no" to
   match VOD-UC-001's pattern; needs checking against the coding manual's exact definition of this
   field before this row is ever promoted.
2. **`benefit_evidence`** — coded `observed_unquantified` because "is assisting agents" is
   present-tense/live rather than a future promise, but there is no quantified figure. Given this
   project's own history of `measured`/`expected`/`observed_unquantified` miscoding (see
   Methodology §6), this specific call should be independently re-checked, not taken on trust.
3. **`secondary_business_function`** and **`claimed_benefits`** — reasonable readings of the
   text, not the only defensible ones.

## NWG-UC-002 (candidate, not added)

Identified 2026-09-10 during an annual-report extension of the same check (covering all 72
collected annual reports for the 38 companies with at least one disclosed use case). Full detail
and rationale: `outputs/KNOWN_GAPS.md`.

| Field | Proposed value |
|---|---|
| `record_id` | NWG-UC-002 |
| `company` | NatWest Group |
| `ticker` | NWG |
| `sector` | Banks |
| `source_id` | NWG-002 |
| `document_title` | NatWest Group plc 2024 Annual Report and Accounts |
| `document_category` | annual_report_previous |
| `evidence_origin` | company_primary |
| `publication_date` | 2025-03 |
| `url` | https://investors.natwestgroup.com/~/media/Files/R/RBS-IR-V2/results-center/14022025/nwg-annual-report-and-accounts-accessible-11032025.pdf |
| `local_filename` | NWG_company_annual_report_previous_fy2024_2025-03.pdf |
| `page_or_section` | not_applicable |
| `evidence_quotation` | "We also introduced Cora+, an enhancement to our AI virtual assistant, which uses generative AI to deliver responsive answers within the mobile app and e-banking platforms. This advanced solution offers our customers expert support on mortgages, credit cards, loans, and overdrafts in a natural, conversational style." |
| `is_genai` | yes |
| `use_case_name` | Cora+ generative-AI customer virtual assistant enhancement |
| `use_case_description` | Cora+, an enhancement to NatWest Group's existing "Cora" AI virtual assistant, using generative AI to deliver responsive, conversational answers within NatWest's mobile app and e-banking platforms. Provides customers with support on mortgages, credit cards, loans, and overdrafts. |
| `primary_business_function` | customer_service |
| `secondary_business_function` | unclear |
| `user_group` | customers |
| `orientation` | customer_facing |
| `deployment_stage` | live_limited *(judgment call — could arguably be live_scaled; no explicit scale/quantification given)* |
| `named_tool_or_model` | Cora+ (enhancement to NatWest's existing "Cora" virtual assistant) |
| `technology_partner` | unclear |
| `claimed_benefits` | service_quality *(judgment call)* |
| `benefit_evidence` | observed_unquantified *(judgment call)* |
| `quantified_metric` | not_applicable |
| `risk_or_limitation_discussed` | unclear |
| `human_review` | no |
| `privacy_control` | no |
| `security_control` | no |
| `accuracy_control` | no |
| `bias_fairness_control` | no |
| `employee_training` | no |
| `responsible_ai_framework` | no |
| `monitoring_audit` | no |
| `restricted_use_control` | no |
| `impact_assessment_control` | no |
| `evidence_strength` | 2_moderate |
| `confidence` | medium |
| `review_status` | not_reviewed |
| `reviewer_notes` | Proposed 2026-09-10: found during an annual-report scan extending the SuperAgent check. Cora+ is named and described in NatWest's previous-year annual report (NWG-002), a source already marked reviewed_evidence_found in source_manifest.csv, but whose notes record no operational use case pulled from it; the only currently-coded NatWest row (NWG-UC-001) was sourced from a separate press release (NWG-003) describing a different, internal-facing tool (AI Digital Enabler + Microsoft Copilot Chat, for colleagues). Cora+ is customer-facing and distinct in product, user group, and orientation. A second passage in the same paragraph ("call summarisation technology... used by Private Banking colleagues") was also checked and NOT added as a separate candidate: it gives no distinct product name and plausibly describes the same Copilot Chat/AI Digital Enabler rollout already coded, applied to one business unit — ambiguous rather than confirmed. Row identified and drafted by Claude Code; not yet human-reviewed. |
| `supporting_source_ids` | *(blank)* |
| `duplicate_of_record_id` | *(blank)* |
| `coded_by` | claude_code |
| `model_version` | claude-sonnet-5 |
| `coded_date` | 2026-09-10 |

### Unresolved judgment calls on this row

1. **`deployment_stage`** — coded `live_limited` conservatively; the passage gives no scale
   language (no country count, no customer count, no percentage), unlike SuperTOBi's explicit
   multi-country rollout, but it also gives no reason to think it's narrower than a full,
   bank-wide channel rollout (mobile app + e-banking platforms). Could reasonably be `live_scaled`.
2. **`benefit_evidence`, `claimed_benefits`, `secondary_business_function`, `technology_partner`**
   — reasonable readings of a passage that describes function without a named vendor or a
   quantified outcome; not independently verified beyond this quotation.
3. **A second candidate from the same paragraph was explicitly considered and not drafted**: "We
   also deployed generative AI internally to support our workforce. For example, call
   summarisation technology is now being used by Private Banking colleagues to capture key facts
   more efficiently during customer conversations." No distinct product name is given, and this
   plausibly describes the same Copilot Chat / AI Digital Enabler rollout already coded as
   NWG-UC-001, applied to one business unit — not confirmed as a separate use case, and therefore
   not drafted as a row here.

## REL-UC-005 (candidate, not added)

Identified 2026-09-10 during the same annual-report extension. Full detail and rationale:
`outputs/KNOWN_GAPS.md`.

| Field | Proposed value |
|---|---|
| `record_id` | REL-UC-005 |
| `company` | RELX |
| `ticker` | REL |
| `sector` | Media |
| `source_id` | REL-001 |
| `document_title` | RELX 2025 Annual Report |
| `document_category` | annual_report_current |
| `evidence_origin` | company_primary |
| `publication_date` | *(blank — no on-page date confirmed, matching REL-001's manifest row)* |
| `url` | https://www.relx.com/~/media/Files/R/RELX-Group/documents/reports/annual-reports/relx-2025-annual-report.pdf |
| `local_filename` | REL_company_annual_report_current_fy2025.pdf |
| `page_or_section` | not_applicable |
| `evidence_quotation` | "New EmbaseAI, the generative AI-powered version of Embase, the leading biomedical database, allows users to pose queries in natural language and receive a summarised response with inline citations to ensure transparency." |
| `is_genai` | yes |
| `use_case_name` | EmbaseAI generative-AI biomedical literature search and summarization assistant |
| `use_case_description` | EmbaseAI, the generative-AI-powered version of RELX/Elsevier's Embase biomedical database. Allows users (biomedical researchers, pharmacovigilance and life-sciences professionals) to pose queries in natural language and receive a summarised response with inline citations to the underlying literature. |
| `primary_business_function` | research_development |
| `secondary_business_function` | knowledge_document_work *(judgment call)* |
| `user_group` | customers |
| `orientation` | product_embedded |
| `deployment_stage` | live_limited |
| `named_tool_or_model` | EmbaseAI |
| `technology_partner` | not_applicable (no external partner named) |
| `claimed_benefits` | accuracy *(judgment call — "inline citations to ensure transparency" supports accuracy; a time_saving reading is inferred, not stated, and was deliberately not added, per Limitations item 11's own caution about coder-inferred benefits)* |
| `benefit_evidence` | observed_unquantified |
| `quantified_metric` | not_applicable |
| `risk_or_limitation_discussed` | unclear |
| `human_review` | no |
| `privacy_control` | no |
| `security_control` | no |
| `accuracy_control` | no |
| `bias_fairness_control` | no |
| `employee_training` | no |
| `responsible_ai_framework` | no |
| `monitoring_audit` | no |
| `restricted_use_control` | no |
| `impact_assessment_control` | no |
| `evidence_strength` | 2_moderate |
| `confidence` | medium |
| `review_status` | not_reviewed |
| `reviewer_notes` | Proposed 2026-09-10: found in the same paragraph of RELX's 2025 Annual Report (REL-001) as "Reaxys AI Search," which was checked and NOT added: its own description ("using natural language discovery") gives no explicit generative-AI/LLM/foundation-model signal, either here or on RELX's dedicated generative-AI strategy webpage (REL-003), which also describes Reaxys only as "AI search and retrosynthesis tools" — an "AI-powered" framing Methodology 3 requires to be excluded absent a specific generative signal. EmbaseAI's own sentence, by contrast, explicitly says "the generative AI-powered version of Embase," meeting the bar directly. Distinct from all four already-coded RELX rows (Lexis+/Protege=legal, PharmaPendium AI=regulatory, ClinicalKey AI=clinical, Ask ICIS=energy/commodities) — Embase is a separate biomedical-literature database. Row identified and drafted by Claude Code; not yet human-reviewed. |
| `supporting_source_ids` | *(blank)* |
| `duplicate_of_record_id` | *(blank)* |
| `coded_by` | claude_code |
| `model_version` | claude-sonnet-5 |
| `coded_date` | 2026-09-10 |

### Unresolved judgment calls on this row

1. **`claimed_benefits`** — coded `accuracy` on the strength of "inline citations to ensure
   transparency"; a `time_saving` reading (getting a summarised answer instead of manually
   searching) is plausible but not explicitly stated by the source, and was deliberately left out
   rather than inferred, per this project's own documented caution about coder-inferred benefits
   (Limitations item 11).
2. **`secondary_business_function`, `deployment_stage`, `user_group`, `orientation`** — coded by
   direct analogy to the three already-confirmed sibling RELX rows (PharmaPendium AI, ClinicalKey
   AI, Ask ICIS), which share the same "AI-powered upgrade to an existing professional database"
   shape; not independently verified beyond that analogy.
3. **Reaxys AI Search, named in the same sentence, was deliberately excluded, not drafted as a
   row** — see reviewer_notes above and `outputs/KNOWN_GAPS.md` for the full reasoning.
