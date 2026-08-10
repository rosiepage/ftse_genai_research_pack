#!/usr/bin/env python3
"""
06_prepare_staging_candidates.py -- group and provisionally triage a
company's screened candidate passages into reviewable staging files.

Plain-English summary
----------------------
This script reads outputs/intermediate/<slug>_candidate_passages.csv (the
mechanical Stage A/B keyword hits from 05_screen_keywords.py) and
outputs/intermediate/<slug>_source_candidates.csv (source metadata), then
groups and provisionally sorts the evidence into five reviewable staging
files:

  <slug>_operational_candidates_staging.csv
  <slug>_strategic_candidates_staging.csv
  <slug>_governance_candidates_staging.csv
  <slug>_rejected_candidates_staging.csv
  <slug>_duplicate_flags.csv

This script makes NO final judgments. Every "provisional_*" field is a
mechanical suggestion for a human to confirm or overturn. It never writes
reviewed_confirmed, never assigns final evidence_strength/confidence, never
decides is_genai for the record, and never touches use_case_dataset_template.csv
or any other main dataset file -- it only ever writes to outputs/intermediate/.

Generalisation design (company-agnostic engine, company-specific data)
------------------------------------------------------------------------
The routing ENGINE below (boilerplate detection, cluster matching,
same-page/bucket merging, cross-source duplicate detection, schema
writing) contains no company-name branching. Company-specific knowledge --
"this file's passages about X are one consolidated GenAI use case" -- lives
entirely in the CLUSTER_RULES data table, exactly the way GOVERNANCE_/
STRATEGIC_/REJECTED_PHRASE_RULES already worked as generalised-but-content-
specific tables before this change. Adding a new company's known concrete
GenAI initiatives means adding new CLUSTER_RULES rows, not editing the
functions that consume them. A source with no matching CLUSTER_RULES entry
still gets a safe, reasonable default classification via the generic
governance/strategic/rejected/vague phrase-bucket rules -- it just won't be
precisely consolidated into a named operational candidate until a human (or
a future edit) adds a rule for it. This is a deliberate, disclosed
limitation: without an LLM in the loop, precise operational consolidation
for a brand-new company's specific use cases requires a one-time rule
addition, mirroring how this project already works iteratively with human
review at every stage.

Core routing priority (unchanged across all companies):
  1. extraction artefact (from 05_screen_keywords.py's own flag)
  2. qualifying GenAI operational evidence (CLUSTER_RULES match only --
     see "High-precision evidence is not automatically operational
     evidence" below)
  3. AI governance / safeguards / oversight / responsible-use evidence
  4. concrete ordinary/non-generative AI operational task
  5. strategic capability or transformation language with no concrete task
  6. vague, irrelevant or non-substantive reference

High-precision evidence is not automatically operational evidence
---------------------------------------------------------------------
A Stage A keyword hit (e.g. "generative AI", "Copilot", "GenAI") is only a
screening signal. It becomes an operational candidate ONLY when it matches
an explicit CLUSTER_RULES entry describing a concrete company task with a
qualifying generative model/product/technique and enough context to
distinguish it from webpage navigation, vendor marketing or general Board/
risk discussion. A Stage A passage that matches no CLUSTER_RULES entry
falls through to the same generic phrase-bucket classifier as any Stage B
passage -- it is never defaulted to operational just because a high-
precision term matched somewhere nearby.

Webpage boilerplate
--------------------
BOILERPLATE_MARKERS is a generic (non-company-specific) list of substrings
that identify navigation, footers, cookie/accessibility controls, related-
content cards, vendor product menus and repeated CMS/site metadata. Any
passage whose own captured context matches one of these markers is flagged
possible_webpage_boilerplate = yes and routed to rejected staging, and is
excluded from cluster/task consideration -- it is never used as evidence
for an operational, governance or strategic candidate.

Source-level consolidation
----------------------------
Passages are consolidated at two levels:
  - Same-source, same-cluster: every passage (regardless of file) whose
    local context matches a CLUSTER_RULES entry's marker phrases is merged
    into ONE staging row for that cluster (see build_clusters()).
  - Same-page, same-bucket (for passages not claimed by any cluster): the
    unchanged classify_generic_passage() mechanism merges passages sharing
    a page and a governance/strategic/rejected bucket into one row.
Distinct tasks are never merged merely because they appear in the same
document: CLUSTER_RULES entries are matched against a LOCAL text window
around each passage (not the whole file), so two named tasks a paragraph
apart (e.g. BT's Openreach trial and contract-analysis use case, both
under the same "GenAI Gateway" press release) are correctly kept separate.

Cross-source corroboration vs. duplication
---------------------------------------------
A CLUSTER_RULES entry may declare a `primary_filename_hint`. Only the file
matching that hint is promoted to an operational/governance/strategic
staging row; any OTHER file whose local context also matches the cluster's
marker phrases is recorded as a corroborating_source relationship in
duplicate_flags, pointing at the primary row -- it is never turned into a
second, duplicate operational row for the same underlying use case (e.g.
BT's Annual Report 2024 corroborating the Amazon Q Developer case study).

Examples
--------
    python 06_prepare_staging_candidates.py --company Tesco --dry-run
    python 06_prepare_staging_candidates.py --company "BT Group" --dry-run
    python 06_prepare_staging_candidates.py --company "Rolls-Royce Holdings" --dry-run
"""

from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pipeline_common as pc  # noqa: E402

SCRIPT_NAME = "06_prepare_staging_candidates"

# ---------------------------------------------------------------------------
# Controlled vocabularies mirrored from 03_CODING_MANUAL.md.
# ---------------------------------------------------------------------------
DEPLOYMENT_STAGE_VALUES = {
    "live_scaled", "live_limited", "pilot", "planned", "partnership_only",
    "general_ambition", "discontinued", "unclear",
}
USER_GROUP_VALUES = {
    "employees", "customers", "suppliers_or_partners", "developers",
    "regulated_decision_makers", "public", "mixed", "unclear",
}
ORIENTATION_VALUES = {"internal", "customer_facing", "product_embedded", "mixed", "unclear"}
BUSINESS_FUNCTION_VALUES = {
    "customer_service", "software_development_it", "marketing_content", "knowledge_document_work",
    "operations_supply_chain", "risk_legal_compliance", "finance_administration", "human_resources",
    "product_service_innovation", "research_development", "sales", "cybersecurity", "other", "unclear",
}
CLAIMED_BENEFIT_VALUES = {
    "time_saving", "cost_reduction", "productivity", "service_quality", "personalisation",
    "revenue_growth", "innovation", "accuracy", "employee_experience", "risk_reduction",
    "accessibility", "other", "none_stated",
}

PROVISIONAL_IS_GENAI_VALUES = {"yes", "no", "unclear"}
SUGGESTED_DESTINATION_VALUES = {"operational", "strategic", "governance", "rejected", "duplicate_review"}
RELATIONSHIP_TYPE_VALUES = {
    "same_source_consolidation", "likely_duplicate", "corroborating_source",
    "repeated_cross_year_disclosure", "webpage_boilerplate",
}

OPERATIONAL_FIELDS = [
    "staging_id", "company", "ticker", "candidate_title", "local_filename", "source_id",
    "document_category", "evidence_origin", "page_or_section", "matched_keywords", "screening_stages",
    "supporting_passage_count", "supporting_context", "possible_extraction_artifact",
    "possible_webpage_boilerplate",
    "provisional_is_genai", "provisional_primary_business_function", "provisional_secondary_business_function",
    "provisional_user_group", "provisional_orientation", "provisional_deployment_stage",
    "provisional_claimed_benefits", "provisional_quantified_metric", "provisional_risk_or_limitation",
    "provisional_destination_ambiguity",
    "duplicate_group_id", "suggested_destination", "reviewer_decision", "reviewer_notes",
]

PROVISIONAL_DESTINATION_AMBIGUITY_VALUES = {"none", "operational_or_strategic"}

FINDING_FIELDS_BASE = [
    "staging_id", "company", "ticker", "candidate_title", "local_filename", "source_id",
    "document_category", "evidence_origin", "page_or_section", "matched_keywords", "screening_stages",
    "supporting_passage_count", "supporting_context", "possible_extraction_artifact",
    "possible_webpage_boilerplate",
]
STRATEGIC_FIELDS = FINDING_FIELDS_BASE + [
    "provisional_finding_type", "duplicate_group_id", "suggested_destination", "reviewer_decision", "reviewer_notes",
]
GOVERNANCE_FIELDS = FINDING_FIELDS_BASE + [
    "provisional_governance_theme", "duplicate_group_id", "suggested_destination", "reviewer_decision", "reviewer_notes",
]
REJECTED_FIELDS = FINDING_FIELDS_BASE + [
    "provisional_rejection_category", "duplicate_group_id", "suggested_destination", "reviewer_decision", "reviewer_notes",
]
DUPLICATE_FLAGS_FIELDS = [
    "duplicate_group_id", "company", "related_staging_ids", "related_destination_files", "relationship_type",
    "similarity_score", "duplicate_reason", "human_review_required", "reviewer_decision", "reviewer_notes",
]

CONTEXT_SEPARATOR = " ||| "
LOCAL_CONTEXT_WINDOW = 450

# ---------------------------------------------------------------------------
# Generic (non-company-specific) webpage-boilerplate markers.
# Any of these substrings appearing in a passage's own captured context
# marks it as navigation/footer/vendor-menu/CMS-metadata rather than
# substantive page content, regardless of which company or source it is.
# ---------------------------------------------------------------------------
BOILERPLATE_MARKERS = [
    "skip to main content", "skip to primary navigation", "skip to search", "skip to footer",
    "===== html document =====",
    "share on: x share on: facebook", "share on: linkedin",
    "media enquiries", "external communications team",
    "download media kit", "preparing your download",
    "sign in to the", "create an aws account", "download center", "account profile",
    "explore ai solutions", "contact sales", "transform work with microsoft ai",
    "customer stories all stories", "explore related stories", "stories about this customer",
    "databricks platform platform overview", "partner spotlight", "partner program find a partner",
    "cloud providers partner solutions", "ide integrations", "university alliance databricks academy",
    "data + ai summit", "data + ai world tour", "ai blog data brew podcast", "champions of data",
    "lakehouse architecture", "lakehouse in your favorite ide", "free edition learn professional",
    "surface book", "surface pro microsoft copilot", "windows 11 apps", "microsoft advertising",
    "microsoft teams windows 365", "microsoft power platform microsoft teams",
    "azure for students", "support for ai marketplace apps",
    "cookie", "accessibility controls",
]


def is_boilerplate(context: str) -> bool:
    lowered = (context or "").lower()
    return any(marker in lowered for marker in BOILERPLATE_MARKERS)


# ---------------------------------------------------------------------------
# CLUSTER_RULES -- company-specific data consumed by a company-agnostic
# engine. Each entry describes ONE concrete initiative that should be
# consolidated into a single staging candidate wherever it is mentioned.
#
# Fields:
#   cluster_key           unique id
#   filename_hint         local_filename must contain this substring (None = any file)
#   primary_filename_hint if set, only this file's matches are promoted to a staging
#                         row; other matching files become corroborating_source flags
#   match_all             list of phrases that must ALL appear in the passage's LOCAL
#                         context window; an EMPTY list means "match every non-
#                         boilerplate/non-artifact passage in this file, provided the
#                         file has at least one Stage A hit" (the Tesco dunnhumby/
#                         Adobe single-topic-page pattern)
#   skip_if_matched       cluster_keys that, if already matched for this passage,
#                         prevent this (broader/catch-all) rule from also claiming it
#   destination           "operational" | "governance" | "strategic"
#   fields                destination-specific provisional field values
#   task_description      human-readable description, used only in reporting
# ---------------------------------------------------------------------------
CLUSTER_RULES = [
    # --- Tesco (unchanged behaviour; preserved for compatibility) ---------
    {
        "cluster_key": "tesco_dunnhumby_creative_studio",
        "filename_hint": "creative-studio", "primary_filename_hint": None,
        "match_all": [], "skip_if_matched": [],
        "destination": "operational",
        "fields": {
            "is_genai": "yes", "primary_business_function": "marketing_content",
            "secondary_business_function": "unclear", "user_group": "suppliers_or_partners",
            "orientation": "product_embedded", "deployment_stage": "live_limited",
            "claimed_benefits": "time_saving;productivity", "quantified_metric": "not_applicable",
            "risk_or_limitation": "unclear", "destination_ambiguity": "none",
        },
        "task_description": "Tesco Media Creative Studio: dunnhumby GenAI ad-creative generation tool.",
    },
    {
        "cluster_key": "tesco_adobe_partnership",
        "filename_hint": "adobe", "primary_filename_hint": None,
        "match_all": [], "skip_if_matched": [],
        "destination": "operational",
        "fields": {
            "is_genai": "yes", "primary_business_function": "marketing_content",
            "secondary_business_function": "unclear", "user_group": "employees",
            "orientation": "mixed", "deployment_stage": "planned",
            "claimed_benefits": "personalisation", "quantified_metric": "not_applicable",
            "risk_or_limitation": "unclear", "destination_ambiguity": "operational_or_strategic",
        },
        "task_description": "Adobe x Tesco AI partnership: planned personalisation via Firefly Foundry/agentic AI.",
    },
    # --- BT Group ----------------------------------------------------------
    {
        "cluster_key": "bt_genai_gateway_openreach_notes",
        "filename_hint": "genai-gateway", "primary_filename_hint": None,
        "match_all": ["openreach", "summaris"], "skip_if_matched": [],
        "destination": "operational",
        "fields": {
            "is_genai": "yes", "primary_business_function": "operations_supply_chain",
            "secondary_business_function": "knowledge_document_work", "user_group": "employees",
            "orientation": "internal", "deployment_stage": "pilot",
            "claimed_benefits": "time_saving;productivity", "quantified_metric": "not_applicable",
            "risk_or_limitation": "unclear", "destination_ambiguity": "none",
            "named_tool_or_model": "GenAI Gateway (Amazon Bedrock-based)", "technology_partner": "AWS",
        },
        "task_description": "GenAI Gateway beta use case: Openreach trial summarising engineering notes on Ethernet/full-fibre jobs.",
    },
    {
        "cluster_key": "bt_genai_gateway_contract_analysis",
        "filename_hint": "genai-gateway", "primary_filename_hint": None,
        "match_all": ["contract analysis"], "skip_if_matched": [],
        "destination": "operational",
        "fields": {
            "is_genai": "yes", "primary_business_function": "risk_legal_compliance",
            "secondary_business_function": "finance_administration", "user_group": "employees",
            "orientation": "internal", "deployment_stage": "live_limited",
            "claimed_benefits": "time_saving", "quantified_metric": "not_applicable",
            "risk_or_limitation": "unclear", "destination_ambiguity": "none",
            "named_tool_or_model": "GenAI Gateway (Amazon Bedrock-based)", "technology_partner": "AWS",
        },
        "task_description": "GenAI Gateway beta use case: contract analysis for BT Group's Business, legal and procurement teams.",
    },
    {
        "cluster_key": "bt_genai_gateway_platform_infrastructure",
        "filename_hint": "genai-gateway", "primary_filename_hint": None,
        "match_all": ["gateway"],
        "skip_if_matched": ["bt_genai_gateway_openreach_notes", "bt_genai_gateway_contract_analysis"],
        "destination": "governance",
        "fields": {"governance_theme": "ai_enablement_platform_and_guardrails"},
        "task_description": "GenAI Gateway itself: centralised, LLM-agnostic enablement infrastructure with guardrails/jailbreak protections -- governance/enablement, not a standalone operational task.",
    },
    {
        "cluster_key": "bt_sprinklr_aimee_customer_service",
        "filename_hint": "leans-on-ai", "primary_filename_hint": None,
        "match_all": ["sprinklr"], "skip_if_matched": [],
        "destination": "operational",
        "fields": {
            "is_genai": "yes", "primary_business_function": "customer_service",
            "secondary_business_function": "unclear", "user_group": "customers",
            "orientation": "customer_facing", "deployment_stage": "live_scaled",
            "claimed_benefits": "service_quality;time_saving", "quantified_metric": "not_applicable",
            "risk_or_limitation": "yes", "destination_ambiguity": "none",
            "named_tool_or_model": "Sprinklr Unified-CXM platform / EE virtual assistant Aimee",
            "technology_partner": "Sprinklr",
        },
        "task_description": "Sprinklr-powered generative-AI customer support via EE's Aimee assistant (~60,000 conversations/week); planned AI-driven interaction summaries are a feature of the same assistant, not a separate task.",
    },
    {
        "cluster_key": "bt_amazon_q_developer",
        "filename_hint": None, "primary_filename_hint": "writing-and-maintaining",
        "match_all": ["amazon q developer"], "skip_if_matched": [],
        "destination": "operational",
        "fields": {
            "is_genai": "yes", "primary_business_function": "software_development_it",
            "secondary_business_function": "unclear", "user_group": "developers",
            "orientation": "internal", "deployment_stage": "live_scaled",
            "claimed_benefits": "productivity;time_saving", "quantified_metric": "not_applicable",
            "risk_or_limitation": "unclear", "destination_ambiguity": "none",
            "named_tool_or_model": "Amazon Q Developer (formerly Amazon CodeWhisperer)",
            "technology_partner": "AWS",
        },
        "task_description": "Amazon Q Developer: code generation, unit-test generation, code transformation and chat assistance for ~2,000 BT developers (consolidated, not split by sub-feature).",
    },
    {
        "cluster_key": "bt_globality_procurement_negotiation",
        "filename_hint": None, "primary_filename_hint": "annual_report_previous",
        "match_all": ["globality"], "skip_if_matched": [],
        "destination": "operational",
        "fields": {
            "is_genai": "yes", "primary_business_function": "operations_supply_chain",
            "secondary_business_function": "finance_administration", "user_group": "employees",
            "orientation": "internal", "deployment_stage": "live_limited",
            "claimed_benefits": "time_saving;productivity", "quantified_metric": "not_applicable",
            "risk_or_limitation": "unclear", "destination_ambiguity": "none",
            "named_tool_or_model": "Globality (autonomous AI-powered negotiation/procurement platform)",
            "technology_partner": "Globality",
        },
        "task_description": "Globality platform: generative-AI features speeding up scoping/negotiation processes; new E-Negotiation and online NDA features (AR2024, no corroborating source found).",
    },
    # --- Rolls-Royce Holdings -----------------------------------------------
    {
        "cluster_key": "rr_databricks_cgan_engine_design",
        "filename_hint": "harnessing-the-power-of-databricks", "primary_filename_hint": None,
        "match_all": ["generative adversarial network"], "skip_if_matched": [],
        "destination": "operational",
        "fields": {
            "is_genai": "yes", "primary_business_function": "research_development",
            "secondary_business_function": "product_service_innovation", "user_group": "employees",
            "orientation": "internal", "deployment_stage": "pilot",
            "claimed_benefits": "time_saving;innovation", "quantified_metric": "not_applicable",
            "risk_or_limitation": "unclear", "destination_ambiguity": "none",
            "named_tool_or_model": "Conditional Generative Adversarial Network (cGAN) via Databricks Data Intelligence Platform",
            "technology_partner": "Databricks",
        },
        "task_description": "Conditional GAN (cGAN) trained on legacy simulation data to generate/validate preliminary aero-engine design concepts; single consolidated candidate despite repeated GenAI/cGAN mentions.",
    },
    {
        "cluster_key": "rr_microsoft_defect_detection_vibration_analysis",
        "filename_hint": "saves-millions-in-cost-avoidance", "primary_filename_hint": None,
        "match_all": ["vibration analysis", "generative ai"], "skip_if_matched": [],
        "destination": "operational",
        "fields": {
            "is_genai": "unclear", "primary_business_function": "operations_supply_chain",
            "secondary_business_function": "product_service_innovation", "user_group": "employees",
            "orientation": "internal", "deployment_stage": "live_limited",
            "claimed_benefits": "accuracy;cost_reduction", "quantified_metric": "not_applicable",
            "risk_or_limitation": "unclear", "destination_ambiguity": "none",
            "named_tool_or_model": "unclear (specific generative technique not named in source)",
            "technology_partner": "Microsoft",
        },
        "task_description": "\"Machine vibration analysis and generative AI have optimized defect detection\" -- explicit 'generative AI' language present, but the described technique reads technically closer to predictive/anomaly-detection AI. provisional_is_genai deliberately set to unclear, not yes -- do not treat as confirmed GenAI.",
    },
    {
        "cluster_key": "rr_microsoft_data_repository_for_genai",
        "filename_hint": "saves-millions-in-cost-avoidance", "primary_filename_hint": None,
        "match_all": ["central data repository"], "skip_if_matched": [],
        "destination": "strategic",
        "fields": {"finding_type": "data_and_ai_capability_building"},
        "task_description": "Building a central data repository/digital thread \"for use by generative AI\" -- enablement/infrastructure and planned capability, not yet a concrete deployed task; routed to strategic, not operational.",
    },
]


def phrases_present(text: str, phrases: list[str]) -> bool:
    lowered = (text or "").lower()
    return all(p in lowered for p in phrases)


def get_local_context(full_text: str, supporting_context: str, window: int = LOCAL_CONTEXT_WINDOW) -> str:
    """Expand a passage's captured 150-char context to a wider local window
    by locating it inside the source's full extracted text. Falls back to
    the original snippet if it cannot be found verbatim (e.g. due to minor
    whitespace differences from CSV round-tripping).
    """
    if not full_text or not supporting_context:
        return supporting_context or ""
    probe = supporting_context.strip()[:60]
    idx = full_text.find(probe) if probe else -1
    if idx == -1:
        return supporting_context
    start = max(0, idx - window)
    end = min(len(full_text), idx + len(supporting_context) + window)
    return full_text[start:end]


def txt_filename_for_source(local_filename: str) -> str:
    name = local_filename
    for ext in (".pdf", ".html", ".htm"):
        if name.lower().endswith(ext):
            return name[: -len(ext)] + ".txt"
    return name + ".txt"


_FULL_TEXT_CACHE: dict[str, str] = {}


def load_full_text(slug: str, local_filename: str) -> str:
    key = f"{slug}/{local_filename}"
    if key in _FULL_TEXT_CACHE:
        return _FULL_TEXT_CACHE[key]
    txt_path = pc.SOURCES_DIR / slug / txt_filename_for_source(local_filename)
    text = ""
    if txt_path.exists():
        text = txt_path.read_text(encoding="utf-8", errors="replace")
    _FULL_TEXT_CACHE[key] = text
    return text


# ---------------------------------------------------------------------------
# Generic phrase-bucket rules for passages NOT claimed by any CLUSTER_RULES
# entry or by boilerplate/artifact detection. Priority within this fallback:
# governance -> rejected (concrete task) -> strategic (capability language) ->
# vague catch-all. General across companies; some entries were first added
# for Tesco and are harmless no-ops for other companies' text.
# ---------------------------------------------------------------------------
GOVERNANCE_PHRASE_RULES = [
    ("governance framework", "ai_governance_framework"),
    ("governance group", "ai_governance_framework"),
    ("ai governance", "ai_governance_framework"),
    ("governance", "ai_governance_framework"),
    ("safeguard", "safeguards_and_responsible_use"),
    ("responsible use", "safeguards_and_responsible_use"),
    ("responsible ai", "safeguards_and_responsible_use"),
    ("responsible tech", "safeguards_and_responsible_use"),
    ("fair, safe, transparent", "safeguards_and_responsible_use"),
    ("ai standard", "safeguards_and_responsible_use"),
    ("ai guidance", "safeguards_and_responsible_use"),
    ("guardrail", "safeguards_and_responsible_use"),
    ("ai ethic", "safeguards_and_responsible_use"),
    ("provided challenge to explore", "board_oversight_of_ai_adoption"),
]
STRATEGIC_PHRASE_RULES = [
    ("embed ai", "embedding_ai_into_operations"),
    ("embedding ai", "embedding_ai_into_operations"),
    ("exploit ai", "embedding_ai_into_operations"),
    ("ai opportunit", "embedding_ai_into_operations"),
    ("ai-enabled enterprise", "digital_transformation"),
    ("digital transformation", "digital_transformation"),
    ("ai foundations", "data_and_ai_capability_building"),
    ("building future ai", "data_and_ai_capability_building"),
    ("data and ai products", "data_and_ai_capability_building"),
    ("data analytics insight", "data_and_ai_capability_building"),
    ("digital thread", "data_and_ai_capability_building"),
    ("evolving ai technology", "technology_strategy"),
    ("ai strategy", "technology_strategy"),
    ("technological change", "technology_strategy"),
    ("ai adoption", "technology_strategy"),
    ("megatrend", "future_strategy"),
    ("future consumer", "future_strategy"),
]
REJECTED_PHRASE_RULES = [
    ("clubcard challenges", "predictive_personalisation"),
    ("optimise the routes", "route_optimisation"),
    ("repurpose heat", "heat_identification_operations"),
    ("heat from refrigeration", "heat_identification_operations"),
    ("workplace adjustment", "insufficient_operational_detail"),
    ("robotic automation", "robotic_automation"),
    ("self-heal", "predictive_automation_network_ops"),
    ("ai ops", "predictive_automation_network_ops"),
    ("predict maintenance", "predictive_maintenance"),
    ("optimise network performance", "predictive_optimisation"),
    ("optimise our network", "predictive_optimisation"),
    ("negotiate autonomously", "predictive_automation_negotiation_agent"),
    ("negotiation strategies and tactics", "predictive_automation_negotiation_agent"),
    ("game theory", "predictive_automation_negotiation_agent"),
    ("edge computing solution", "predictive_optimisation_energy"),
    ("personalised learning", "predictive_personalisation"),
    ("ai-driven learning platform", "predictive_personalisation"),
    ("audit", "audit_analytics"),
    ("machine learning and natural language processing", "audit_analytics"),
    ("personalised offers", "predictive_personalisation"),
    ("demand forecast", "predictive_personalisation"),
    ("automation", "ordinary_automation"),
]


def classify_generic_passage(context: str) -> tuple[str, str]:
    """Fallback classifier for any passage not claimed by boilerplate,
    extraction-artefact detection or a CLUSTER_RULES entry. Never returns
    'operational' -- see module docstring, "High-precision evidence is not
    automatically operational evidence".
    """
    lowered = (context or "").lower()
    for phrase, category in GOVERNANCE_PHRASE_RULES:
        if phrase in lowered:
            return "governance", category
    for phrase, category in REJECTED_PHRASE_RULES:
        if phrase in lowered:
            return "rejected", category
    for phrase, category in STRATEGIC_PHRASE_RULES:
        if phrase in lowered:
            return "strategic", category
    return "rejected", "vague_general_ai_reference"


def page_sort_key(page_or_section: str) -> tuple[int, str]:
    m = re.match(r"p\.(\d+)", page_or_section or "")
    if m:
        return (0, int(m.group(1)))
    return (1, page_or_section or "")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Group and provisionally triage a company's screened candidate passages "
            "(outputs/intermediate/<slug>_candidate_passages.csv) into reviewable staging files: "
            "operational, strategic, governance, rejected, and duplicate flags. Company-agnostic "
            "engine; company-specific consolidation rules live in CLUSTER_RULES. Makes no final "
            "judgments -- never sets reviewed_confirmed, never assigns final evidence_strength/"
            "confidence, never decides is_genai for the record, and never writes to any main dataset."
        ),
    )
    parser.add_argument("--company", required=True, help="Company name or ticker exactly as in pilot_companies.csv.")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Report proposed staging counts and groupings without writing any staging file or checkpoint.",
    )
    return parser.parse_args(argv)


# ---------------------------------------------------------------------------
# Source-candidate metadata association (unchanged from prior version)
# ---------------------------------------------------------------------------
def build_expected_local_filename(ticker: str, evidence_origin: str, document_category: str,
                                   candidate_title: str, publication_date_candidate: str,
                                   financial_year_covered: str, extension: str) -> str:
    origin_prefix = "partner" if evidence_origin == "technology_partner" else "company"
    category_slug = (document_category or "uncategorised").strip()
    fy = (financial_year_covered or "").strip()
    if fy and fy.lower() not in ("not_applicable", "unknown"):
        title_or_fy = pc.slugify(fy)
    else:
        title_or_fy = pc.slugify(candidate_title)[:60].strip("-") or "untitled"
    parts = [ticker.strip(), origin_prefix, category_slug, title_or_fy]
    date_slug = (publication_date_candidate or "").strip()
    if date_slug and date_slug.lower() != "unknown":
        parts.append(date_slug)
    base = "_".join(p for p in parts if p)
    ext = extension if extension.startswith(".") else f".{extension}"
    name = base
    while name.lower().endswith(ext.lower()):
        name = name[: -len(ext)]
    return f"{name}{ext}"


def load_source_metadata(slug: str, ticker: str) -> dict[str, dict]:
    path = pc.INTERMEDIATE_DIR / f"{slug}_source_candidates.csv"
    fieldnames, rows = pc.read_csv_rows(path)
    lookup: dict[str, dict] = {}
    if not fieldnames:
        return lookup
    for r in rows:
        if (r.get("approval_status") or "").strip() != "approved":
            continue
        candidate_title = (r.get("candidate_title") or "").strip()
        document_category = (r.get("document_category") or "").strip()
        evidence_origin = (r.get("evidence_origin") or "").strip()
        publication_date_candidate = (r.get("publication_date_candidate") or "").strip()
        financial_year_covered = (r.get("financial_year_covered") or "").strip()
        meta = {
            "candidate_title": candidate_title, "document_category": document_category,
            "evidence_origin": evidence_origin, "publication_date_candidate": publication_date_candidate,
        }
        for ext in (".pdf", ".html"):
            filename = build_expected_local_filename(
                ticker, evidence_origin, document_category, candidate_title,
                publication_date_candidate, financial_year_covered, ext,
            )
            lookup[filename] = meta
    return lookup


def load_manifest_lookup() -> dict[str, str]:
    fieldnames, rows = pc.read_csv_rows(pc.SOURCE_MANIFEST_CSV)
    lookup: dict[str, str] = {}
    if not fieldnames:
        return lookup
    for r in rows:
        local_filename = (r.get("local_filename") or "").strip()
        if not local_filename:
            continue
        base = local_filename
        while base.lower().endswith(".pdf"):
            base = base[:-4]
        lookup[base.lower()] = (r.get("source_id") or "").strip()
    return lookup


# ---------------------------------------------------------------------------
# Main processing
# ---------------------------------------------------------------------------
def process_company(company: str, ticker: str, slug: str) -> dict:
    passages_path = pc.INTERMEDIATE_DIR / f"{slug}_candidate_passages.csv"
    fieldnames, passages = pc.read_csv_rows(passages_path)
    if fieldnames is None:
        raise FileNotFoundError(f"{passages_path} does not exist -- run 05_screen_keywords.py first.")

    source_meta = load_source_metadata(slug, ticker)
    manifest_lookup = load_manifest_lookup()
    id_prefix = ticker.split(".")[0]  # e.g. "BT.A" -> "BT"; "TSCO"/"RR"/"AZN" unchanged

    by_file: dict[str, list[dict]] = {}
    for p in passages:
        by_file.setdefault(p["local_filename"], []).append(p)

    operational_rows: list[dict] = []
    strategic_rows: list[dict] = []
    governance_rows: list[dict] = []
    rejected_rows: list[dict] = []
    duplicate_groups: list[dict] = []

    counters = {"operational": 0, "strategic": 0, "governance": 0, "rejected": 0}
    dup_counter = 0
    total_raw_passages = len(passages)

    def next_id(bucket: str) -> str:
        counters[bucket] += 1
        prefix = {"operational": "OP", "strategic": "STR", "governance": "GOV", "rejected": "REJ"}[bucket]
        return f"{id_prefix}-{prefix}-{counters[bucket]:03d}"

    def next_dup_id() -> str:
        nonlocal dup_counter
        dup_counter += 1
        return f"DUPG-{dup_counter:03d}"

    # ---- Pass 1: artefact + boilerplate routing; compute per-row cluster matches
    artifact_rows: list[dict] = []
    boilerplate_rows: list[dict] = []
    remaining_rows: list[dict] = []  # each augmented with local_ctx, cluster_keys

    for local_filename in sorted(by_file.keys()):
        file_passages = by_file[local_filename]
        file_has_stage_a = any(p["stage"] == "A" for p in file_passages)
        full_text = load_full_text(slug, local_filename)
        for p in file_passages:
            if (p.get("possible_extraction_artifact") or "").strip().lower() == "yes":
                artifact_rows.append(p)
                continue
            if is_boilerplate(p["surrounding_context"]):
                boilerplate_rows.append(p)
                continue
            local_ctx = get_local_context(full_text, p["surrounding_context"])
            matched: list[str] = []
            for rule in CLUSTER_RULES:
                if any(k in matched for k in rule["skip_if_matched"]):
                    continue
                hint = rule["filename_hint"]
                if hint and hint.lower() not in local_filename.lower():
                    continue
                if not rule["match_all"]:
                    if file_has_stage_a:
                        matched.append(rule["cluster_key"])
                elif phrases_present(local_ctx, rule["match_all"]):
                    matched.append(rule["cluster_key"])
            p = dict(p)
            p["_local_ctx"] = local_ctx
            p["_cluster_keys"] = matched
            remaining_rows.append(p)

    def meta_for(local_filename: str) -> tuple[str, str, str, str]:
        meta = source_meta.get(local_filename, {})
        source_id = manifest_lookup.get(Path(local_filename).stem.lower(), "")
        return (meta.get("candidate_title", ""), meta.get("document_category", ""),
                meta.get("evidence_origin", ""), source_id)

    # ---- Artefact rows: one rejected row each (unchanged behaviour) ----
    for p in artifact_rows:
        candidate_title, document_category, evidence_origin, source_id = meta_for(p["local_filename"])
        staging_id = next_id("rejected")
        rejected_rows.append({
            "staging_id": staging_id, "company": company, "ticker": ticker,
            "candidate_title": candidate_title, "local_filename": p["local_filename"],
            "source_id": source_id, "document_category": document_category, "evidence_origin": evidence_origin,
            "page_or_section": p["page_or_section"], "matched_keywords": p["matched_keyword"],
            "screening_stages": p["stage"], "supporting_passage_count": 1,
            "supporting_context": p["surrounding_context"], "possible_extraction_artifact": "yes",
            "possible_webpage_boilerplate": "no", "provisional_rejection_category": "extraction_artifact",
            "duplicate_group_id": "", "suggested_destination": "rejected", "reviewer_decision": "", "reviewer_notes": "",
        })

    # ---- Boilerplate rows: merge by (file, page) into rejected rows ----
    bp_groups: dict[tuple, list] = {}
    bp_order: list[tuple] = []
    for p in boilerplate_rows:
        key = (p["local_filename"], p["page_or_section"])
        if key not in bp_groups:
            bp_groups[key] = []
            bp_order.append(key)
        bp_groups[key].append(p)
    for key in bp_order:
        local_filename, page_or_section = key
        group = bp_groups[key]
        candidate_title, document_category, evidence_origin, source_id = meta_for(local_filename)
        keywords = sorted({p["matched_keyword"] for p in group})
        stages_present = sorted({p["stage"] for p in group})
        supporting_context = CONTEXT_SEPARATOR.join(p["surrounding_context"] for p in group)
        staging_id = next_id("rejected")
        row = {
            "staging_id": staging_id, "company": company, "ticker": ticker,
            "candidate_title": candidate_title, "local_filename": local_filename,
            "source_id": source_id, "document_category": document_category, "evidence_origin": evidence_origin,
            "page_or_section": page_or_section, "matched_keywords": ";".join(keywords),
            "screening_stages": ";".join(stages_present), "supporting_passage_count": len(group),
            "supporting_context": supporting_context, "possible_extraction_artifact": "no",
            "possible_webpage_boilerplate": "yes", "provisional_rejection_category": "webpage_boilerplate",
            "duplicate_group_id": "", "suggested_destination": "rejected", "reviewer_decision": "", "reviewer_notes": "",
        }
        if len(group) > 1:
            group_id = next_dup_id()
            row["duplicate_group_id"] = group_id
            duplicate_groups.append({
                "duplicate_group_id": group_id, "company": company, "related_staging_ids": staging_id,
                "related_destination_files": "rejected_candidates_staging", "relationship_type": "webpage_boilerplate",
                "similarity_score": "not_applicable",
                "duplicate_reason": f"{len(group)} webpage-boilerplate passages on the same page/section of {local_filename} consolidated into one rejected row.",
                "human_review_required": "yes", "reviewer_decision": "", "reviewer_notes": "",
            })
        rejected_rows.append(row)

    # ---- Cluster rows: build one row per cluster_key that has primary-file matches
    cluster_rule_by_key = {r["cluster_key"]: r for r in CLUSTER_RULES}
    rows_by_cluster: dict[str, list[dict]] = {}
    consumed_row_ids: set[int] = set()
    for idx, p in enumerate(remaining_rows):
        for ck in p["_cluster_keys"]:
            rows_by_cluster.setdefault(ck, []).append((idx, p))
            consumed_row_ids.add(idx)

    cluster_staging_id: dict[str, str] = {}
    corroboration_candidates: list[dict] = []

    for rule in CLUSTER_RULES:
        ck = rule["cluster_key"]
        entries = rows_by_cluster.get(ck, [])
        if not entries:
            continue
        primary_hint = rule["primary_filename_hint"]
        if primary_hint:
            primary_entries = [(i, p) for i, p in entries if primary_hint.lower() in p["local_filename"].lower()]
            other_entries = [(i, p) for i, p in entries if primary_hint.lower() not in p["local_filename"].lower()]
        else:
            primary_entries = entries
            other_entries = []

        if primary_entries:
            local_filename = primary_entries[0][1]["local_filename"]
            candidate_title, document_category, evidence_origin, source_id = meta_for(local_filename)
            keywords = sorted({p["matched_keyword"] for _, p in primary_entries})
            stages_present = sorted({p["stage"] for _, p in primary_entries})
            pages = sorted({p["page_or_section"] for _, p in primary_entries}, key=page_sort_key)
            page_or_section = ";".join(pages) if len(pages) > 1 else (pages[0] if pages else "not_applicable")
            supporting_context = CONTEXT_SEPARATOR.join(
                p["_local_ctx"].strip() for _, p in primary_entries
            )
            dest = rule["destination"]
            f = rule["fields"]
            staging_id = next_id(dest)
            cluster_staging_id[ck] = staging_id
            base = {
                "staging_id": staging_id, "company": company, "ticker": ticker,
                "candidate_title": candidate_title, "local_filename": local_filename,
                "source_id": source_id, "document_category": document_category, "evidence_origin": evidence_origin,
                "page_or_section": page_or_section, "matched_keywords": ";".join(keywords),
                "screening_stages": ";".join(stages_present), "supporting_passage_count": len(primary_entries),
                "supporting_context": supporting_context, "possible_extraction_artifact": "no",
                "possible_webpage_boilerplate": "no",
                "duplicate_group_id": "", "suggested_destination": dest, "reviewer_decision": "", "reviewer_notes": "",
            }
            if dest == "operational":
                base.update({
                    "provisional_is_genai": f["is_genai"],
                    "provisional_primary_business_function": f["primary_business_function"],
                    "provisional_secondary_business_function": f["secondary_business_function"],
                    "provisional_user_group": f["user_group"],
                    "provisional_orientation": f["orientation"],
                    "provisional_deployment_stage": f["deployment_stage"],
                    "provisional_claimed_benefits": f["claimed_benefits"],
                    "provisional_quantified_metric": f["quantified_metric"],
                    "provisional_risk_or_limitation": f["risk_or_limitation"],
                    "provisional_destination_ambiguity": f["destination_ambiguity"],
                })
                operational_rows.append(base)
            elif dest == "governance":
                base["provisional_governance_theme"] = f["governance_theme"]
                governance_rows.append(base)
            else:
                base["provisional_finding_type"] = f["finding_type"]
                strategic_rows.append(base)

            if len(primary_entries) > 1:
                group_id = next_dup_id()
                base["duplicate_group_id"] = group_id
                duplicate_groups.append({
                    "duplicate_group_id": group_id, "company": company, "related_staging_ids": staging_id,
                    "related_destination_files": f"{dest}_candidates_staging",
                    "relationship_type": "same_source_consolidation", "similarity_score": "not_applicable",
                    "duplicate_reason": f"{len(primary_entries)} passages from {local_filename} describing the same initiative ({ck}) were consolidated into one row.",
                    "human_review_required": "yes", "reviewer_decision": "", "reviewer_notes": "",
                })

        for _, p in other_entries:
            corroboration_candidates.append({"cluster_key": ck, "row": p})

    # ---- Remaining (non-clustered) rows: generic per-page/bucket classifier
    remaining_unclustered = [p for idx, p in enumerate(remaining_rows) if idx not in consumed_row_ids]
    by_file_remaining: dict[str, list[dict]] = {}
    for p in remaining_unclustered:
        by_file_remaining.setdefault(p["local_filename"], []).append(p)

    for local_filename in sorted(by_file_remaining.keys()):
        file_passages = by_file_remaining[local_filename]
        candidate_title, document_category, evidence_origin, source_id = meta_for(local_filename)
        classified = [(p, *classify_generic_passage(p["surrounding_context"])) for p in file_passages]
        merge_groups: dict[tuple, list] = {}
        merge_order: list[tuple] = []
        for p, bucket, sub_category in classified:
            key = (p["page_or_section"], bucket, sub_category)
            if key not in merge_groups:
                merge_groups[key] = []
                merge_order.append(key)
            merge_groups[key].append(p)

        for key in sorted(merge_order, key=lambda k: (page_sort_key(k[0]), k[1], k[2])):
            page_or_section, bucket, sub_category = key
            group_passages = merge_groups[key]
            keywords = sorted({p["matched_keyword"] for p in group_passages})
            stages_present = sorted({p["stage"] for p in group_passages})
            supporting_context = CONTEXT_SEPARATOR.join(p["surrounding_context"] for p in group_passages)
            staging_id = next_id(bucket)
            base_row = {
                "staging_id": staging_id, "company": company, "ticker": ticker,
                "candidate_title": candidate_title, "local_filename": local_filename,
                "source_id": source_id, "document_category": document_category, "evidence_origin": evidence_origin,
                "page_or_section": page_or_section, "matched_keywords": ";".join(keywords),
                "screening_stages": ";".join(stages_present), "supporting_passage_count": len(group_passages),
                "supporting_context": supporting_context, "possible_extraction_artifact": "no",
                "possible_webpage_boilerplate": "no",
                "duplicate_group_id": "", "suggested_destination": bucket, "reviewer_decision": "", "reviewer_notes": "",
            }
            if bucket == "strategic":
                base_row["provisional_finding_type"] = sub_category
                strategic_rows.append(base_row)
            elif bucket == "governance":
                base_row["provisional_governance_theme"] = sub_category
                governance_rows.append(base_row)
            else:
                base_row["provisional_rejection_category"] = sub_category
                rejected_rows.append(base_row)

            if len(group_passages) > 1:
                group_id = next_dup_id()
                base_row["duplicate_group_id"] = group_id
                duplicate_groups.append({
                    "duplicate_group_id": group_id, "company": company, "related_staging_ids": staging_id,
                    "related_destination_files": f"{bucket}_candidates_staging",
                    "relationship_type": "same_source_consolidation", "similarity_score": "not_applicable",
                    "duplicate_reason": (
                        f"{len(group_passages)} passages on the same page ({page_or_section}) of "
                        f"{local_filename} describe the same {sub_category.replace('_', ' ')} theme and "
                        "were consolidated into one row."
                    ),
                    "human_review_required": "yes", "reviewer_decision": "", "reviewer_notes": "",
                })

    # ---- Corroboration flags: non-primary files matching a cluster -------
    for entry in corroboration_candidates:
        ck = entry["cluster_key"]
        p = entry["row"]
        primary_id = cluster_staging_id.get(ck)
        if not primary_id:
            continue  # cluster had no primary row (unexpected; skip rather than invent one)
        group_id = next_dup_id()
        duplicate_groups.append({
            "duplicate_group_id": group_id, "company": company, "related_staging_ids": primary_id,
            "related_destination_files": f"{cluster_rule_by_key[ck]['destination']}_candidates_staging",
            "relationship_type": "corroborating_source", "similarity_score": "not_applicable",
            "duplicate_reason": (
                f"{p['local_filename']} p.{p['page_or_section']} corroborates the same use case as {primary_id} "
                f"({cluster_rule_by_key[ck]['task_description']}) but is not promoted as a separate operational row."
            ),
            "human_review_required": "yes", "reviewer_decision": "", "reviewer_notes": "",
        })

    # ---- Cross-destination near-duplicate detection (difflib), unchanged
    # mechanism, with relationship_type now inferred from document_category.
    all_rows_for_dedup = operational_rows + strategic_rows + governance_rows + rejected_rows
    for i in range(len(all_rows_for_dedup)):
        for j in range(i + 1, len(all_rows_for_dedup)):
            row_a, row_b = all_rows_for_dedup[i], all_rows_for_dedup[j]
            if row_a["local_filename"] == row_b["local_filename"]:
                continue
            ratio = difflib.SequenceMatcher(
                None, row_a["supporting_context"].lower(), row_b["supporting_context"].lower()
            ).ratio()
            if ratio >= 0.5:
                group_id = next_dup_id()
                if not row_a["duplicate_group_id"]:
                    row_a["duplicate_group_id"] = group_id
                if not row_b["duplicate_group_id"]:
                    row_b["duplicate_group_id"] = group_id
                cats = {row_a["document_category"], row_b["document_category"]}
                if cats == {"annual_report_current", "annual_report_previous"}:
                    relationship_type = "repeated_cross_year_disclosure"
                else:
                    relationship_type = "likely_duplicate"
                duplicate_groups.append({
                    "duplicate_group_id": group_id, "company": company,
                    "related_staging_ids": f"{row_a['staging_id']};{row_b['staging_id']}",
                    "related_destination_files": (
                        f"{row_a['suggested_destination']}_candidates_staging;"
                        f"{row_b['suggested_destination']}_candidates_staging"
                    ),
                    "relationship_type": relationship_type, "similarity_score": f"{ratio:.2f}",
                    "duplicate_reason": (
                        f"Passages in {row_a['local_filename']} and {row_b['local_filename']} are "
                        f"textually very similar (difflib ratio {ratio:.2f})."
                    ),
                    "human_review_required": "yes", "reviewer_decision": "", "reviewer_notes": "",
                })

    return {
        "operational_rows": operational_rows, "strategic_rows": strategic_rows,
        "governance_rows": governance_rows, "rejected_rows": rejected_rows,
        "duplicate_groups": duplicate_groups, "total_raw_passages": total_raw_passages,
        "total_staging_rows": len(operational_rows) + len(strategic_rows) + len(governance_rows) + len(rejected_rows),
        "artifact_count": len(artifact_rows), "boilerplate_count": len(boilerplate_rows),
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    row = pc.find_company_row(args.company)
    if row is None:
        print(f"ERROR: '{args.company}' was not found in pilot_companies.csv.")
        return 1
    company, ticker = row["company"], row["ticker"]
    slug = pc.slugify(company)
    pc.report(f"Company: {company} ({ticker})  ->  slug: {slug}")

    try:
        result = process_company(company, ticker, slug)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}")
        return 1

    passages_grouped = result["total_raw_passages"] - result["total_staging_rows"]
    pc.report(f"Raw candidate passages read: {result['total_raw_passages']}")
    pc.report(f"Proposed operational candidates: {len(result['operational_rows'])}")
    pc.report(f"Proposed strategic candidates: {len(result['strategic_rows'])}")
    pc.report(f"Proposed governance candidates: {len(result['governance_rows'])}")
    pc.report(f"Proposed rejected candidates: {len(result['rejected_rows'])}")
    pc.report(f"Total staging rows: {result['total_staging_rows']}")
    pc.report(f"Passages consolidated via grouping: {passages_grouped}")
    pc.report(f"Extraction-artifact rows: {result['artifact_count']}")
    pc.report(f"Webpage-boilerplate passages: {result['boilerplate_count']}")
    pc.report(f"Duplicate/corroboration groups flagged: {len(result['duplicate_groups'])}")

    if args.dry_run:
        pc.report("[dry-run] Proposed operational candidates:")
        for r in result["operational_rows"]:
            pc.report(f"  {r['staging_id']} | {r['candidate_title']} | page={r['page_or_section']} | "
                      f"is_genai={r['provisional_is_genai']} | deployment_stage={r['provisional_deployment_stage']} | "
                      f"passages={r['supporting_passage_count']}")
        pc.report("[dry-run] Proposed governance candidates:")
        for r in result["governance_rows"]:
            pc.report(f"  {r['staging_id']} | {r['provisional_governance_theme']} | page={r['page_or_section']} | passages={r['supporting_passage_count']}")
        pc.report("[dry-run] Proposed strategic candidates:")
        for r in result["strategic_rows"]:
            pc.report(f"  {r['staging_id']} | {r['provisional_finding_type']} | page={r['page_or_section']} | passages={r['supporting_passage_count']}")
        pc.report("[dry-run] Rejected-category counts:")
        rej_counts: dict[str, int] = {}
        for r in result["rejected_rows"]:
            cat = r["provisional_rejection_category"]
            rej_counts[cat] = rej_counts.get(cat, 0) + 1
        for cat, count in sorted(rej_counts.items()):
            pc.report(f"  {cat}: {count}")
        pc.report("[dry-run] Duplicate/corroboration relationships:")
        for d in result["duplicate_groups"]:
            pc.report(f"  {d['duplicate_group_id']} | {d['relationship_type']} | {d['related_staging_ids']} | score={d['similarity_score']}")
        pc.report("[dry-run] No staging file written. No checkpoint updated.")
        return 0

    output_paths = {
        "operational": pc.INTERMEDIATE_DIR / f"{slug}_operational_candidates_staging.csv",
        "strategic": pc.INTERMEDIATE_DIR / f"{slug}_strategic_candidates_staging.csv",
        "governance": pc.INTERMEDIATE_DIR / f"{slug}_governance_candidates_staging.csv",
        "rejected": pc.INTERMEDIATE_DIR / f"{slug}_rejected_candidates_staging.csv",
        "duplicates": pc.INTERMEDIATE_DIR / f"{slug}_duplicate_flags.csv",
    }

    def write_safely(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
        tmp_path = path.with_name(path.name + ".partial")
        pc.write_csv_rows(tmp_path, fieldnames, rows)
        _, written = pc.read_csv_rows(tmp_path)
        if len(written) != len(rows):
            raise RuntimeError(f"validation failed writing {path.name}: wrote {len(rows)} but re-read {len(written)}")
        tmp_path.replace(path)

    write_safely(output_paths["operational"], OPERATIONAL_FIELDS, result["operational_rows"])
    write_safely(output_paths["strategic"], STRATEGIC_FIELDS, result["strategic_rows"])
    write_safely(output_paths["governance"], GOVERNANCE_FIELDS, result["governance_rows"])
    write_safely(output_paths["rejected"], REJECTED_FIELDS, result["rejected_rows"])
    write_safely(output_paths["duplicates"], DUPLICATE_FLAGS_FIELDS, result["duplicate_groups"])

    pc.report("Staging files written:")
    for key, path in output_paths.items():
        pc.report(f"  {path}")

    pc.save_checkpoint(slug, "prepare_staging_candidates", {
        "status": "complete",
        "operational_candidates": len(result["operational_rows"]),
        "strategic_candidates": len(result["strategic_rows"]),
        "governance_candidates": len(result["governance_rows"]),
        "rejected_candidates": len(result["rejected_rows"]),
        "duplicate_groups": len(result["duplicate_groups"]),
        "passages_grouped": passages_grouped,
    }, dry_run=False)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
