#!/usr/bin/env python3
"""
07_promote_reviewed_staging.py -- promote human-reviewed staging rows into
the project's main datasets.

Plain-English summary
----------------------
This is the ONLY script allowed to write to source_manifest.csv,
use_case_dataset_template.csv, strategic_capability_building_findings.csv,
governance_and_enablement_findings.csv, rejected_or_aspirational_findings.csv,
or company_summary_template.csv. It reads a company's five staging files
(written by 06_prepare_staging_candidates.py and then hand-reviewed by a
human, who applied reviewer_decision/reviewer_notes to every row) and
proposes exactly what would be promoted, mapped into each main dataset's
real schema using the controlled vocabulary in 03_CODING_MANUAL.md.

It never invents a required value. No staging file carries evidence_strength
or confidence -- 03_CODING_MANUAL.md reserves that judgment for a human/
coding decision -- so each operational override below states a proposed
value with an explicit reason. Until a human operator has explicitly
reviewed and approved a given row's evidence_strength/confidence, its
review_status stays `not_reviewed`, and promoting the row's other fields
does not by itself constitute that sign-off. Once a human operator has
explicitly approved a row's proposed evidence_strength/confidence (as
Tesco's two operational rows now are, in build_operational_proposal),
review_status becomes `reviewed_confirmed` and the confirmed_use_case_count
formula in compute_use_case_counts applies normally -- a reviewed row may
still carry evidence_strength = 1_weak and simply not qualify for the
confirmed count.

Promotion eligibility, per staging file:
  - operational / strategic / governance: reviewer_decision == accept.
    (`correct` is accepted too, since a human has still endorsed the row;
    `reject`, `needs_more_evidence`, `merge`, `keep_separate` alone are not
    promotion signals for these three files.)
  - rejected: reviewer_decision == accept (the human confirmed this really
    is non-qualifying evidence worth logging for methodological transparency,
    matching the existing AstraZeneca rows in rejected_or_aspirational_findings.csv).

Idempotency: before assigning a new ID, the script checks whether a row
already carries a "Promoted from staging <staging_id>" marker in the
corresponding main dataset's notes/reviewer_notes column, and skips it if so.

Examples
--------
    python 07_promote_reviewed_staging.py --company Tesco --dry-run
    python 07_promote_reviewed_staging.py --company Tesco
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pipeline_common as pc  # noqa: E402

SCRIPT_NAME = "07_promote_reviewed_staging"

# ---------------------------------------------------------------------------
# Controlled vocabularies (re-checked against 03_CODING_MANUAL.md this run)
# ---------------------------------------------------------------------------
REVIEWER_DECISION_VALUES = {
    "accept", "reject", "correct", "needs_more_evidence",  # staging-row decisions
    "merge", "keep_separate", "corroborating", "reject_flag",  # duplicate_flags-row decisions
}
DOCUMENT_CATEGORY_VALUES = pc.DOCUMENT_CATEGORY_VALUES
EVIDENCE_ORIGIN_VALUES = pc.EVIDENCE_ORIGIN_VALUES
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
EVIDENCE_STRENGTH_VALUES = {"3_strong", "2_moderate", "1_weak", "0_not_qualifying"}
BENEFIT_EVIDENCE_VALUES = {"measured", "observed_unquantified", "expected", "none"}
CONFIDENCE_VALUES = {"high", "medium", "low"}
REVIEW_STATUS_VALUES = {"not_reviewed", "reviewed_confirmed", "reviewed_corrected", "reviewed_excluded"}
CODED_BY_VALUES = {"claude_code", "human"}  # 03_CODING_MANUAL.md field 6 -- NOT "human_reviewed_pipeline"
LOGGED_BY_VALUES = {"claude_code", "human"}  # 03_CODING_MANUAL.md field 5
DOCUMENT_REVIEW_STATUS_VALUES = {"not_yet_reviewed", "reviewed_evidence_found", "reviewed_no_relevant_evidence"}
DOWNLOAD_STATUS_VALUES = {"not_downloaded", "downloaded", "unavailable"}
TEXT_EXTRACTION_STATUS_VALUES = {"not_extracted", "extracted", "extraction_failed"}
RISK_YES_NO_UNCLEAR = {"yes", "no", "unclear"}
COLLECTED_FIELD_VALUES = {"not_started", "collected", "unavailable", "not_applicable"}
SEARCH_FIELD_VALUES = {"not_started", "complete", "incomplete"}
NO_DISCLOSURE_CONFIRMED_VALUES = {"not_yet_assessed", "pending_sources", "disclosure_found", "no_disclosure_confirmed"}
MANUAL_REVIEW_STATUS_VALUES = {"not_sampled", "pending_review", "review_complete"}

OPERATIONAL_PROMOTABLE_DECISIONS = {"accept", "correct"}
STRATEGIC_PROMOTABLE_DECISIONS = {"accept", "correct"}
GOVERNANCE_PROMOTABLE_DECISIONS = {"accept", "correct"}
# NOTE: "correct" on a REJECTED-staging row means "this does not belong in
# rejected staging at all -- it belongs in operational/strategic/governance
# instead" (see the rejected-staging review standard). It is therefore the
# opposite signal from "correct" on an operational/strategic/governance row
# (where it means "stays in this bucket, a field was corrected"). A rejected
# row marked `correct` must never be promoted into
# rejected_or_aspirational_findings.csv -- only `accept` ("the rejection
# itself was confirmed") is a promotion signal here.
REJECTED_PROMOTABLE_DECISIONS = {"accept"}

# Exact schemas of the main datasets, restated here only for validation --
# the authoritative source of truth at run time is always the live CSV
# header actually read from disk (see load_main_csv below), never this list.
USE_CASE_FIELDS = [
    "record_id", "company", "ticker", "sector", "source_id", "document_title", "document_category",
    "evidence_origin", "publication_date", "url", "local_filename", "page_or_section", "evidence_quotation",
    "is_genai", "use_case_name", "use_case_description", "primary_business_function", "secondary_business_function",
    "user_group", "orientation", "deployment_stage", "named_tool_or_model", "technology_partner",
    "claimed_benefits", "benefit_evidence", "quantified_metric", "risk_or_limitation_discussed", "human_review",
    "privacy_control", "security_control", "accuracy_control", "bias_fairness_control", "employee_training",
    "responsible_ai_framework", "monitoring_audit", "restricted_use_control", "impact_assessment_control",
    "evidence_strength", "confidence", "review_status", "reviewer_notes", "supporting_source_ids",
    "duplicate_of_record_id", "coded_by", "model_version", "coded_date",
]
SOURCE_MANIFEST_FIELDS = [
    "source_id", "company", "ticker", "sector", "document_category", "document_title", "financial_year_covered",
    "publication_date", "url", "local_filename", "evidence_origin", "download_status", "text_extraction_status",
    "document_review_status", "logged_by", "model_version", "logged_date", "notes",
]
STRATEGIC_FINDING_FIELDS = [
    "finding_id", "company", "ticker", "sector", "source_id", "finding_name", "finding_type",
    "evidence_quotation", "page_or_section", "evidence_strength", "confidence",
    "reason_excluded_from_operational_count", "coded_by", "coded_date", "notes",
]
GOVERNANCE_FINDING_FIELDS = [
    "finding_id", "company", "ticker", "sector", "source_ids", "finding_name", "finding_type",
    "evidence_quotation_or_summary", "page_or_section", "employee_training", "responsible_ai_framework",
    "human_involvement_discussed", "privacy_discussed", "accuracy_or_hallucination_discussed",
    "environmental_limitation_discussed", "reason_excluded_from_operational_count", "coded_by", "coded_date", "notes",
]
REJECTED_FINDING_FIELDS = [
    "finding_id", "company", "ticker", "sector", "source_id", "item_name", "evidence_quotation",
    "page_or_section", "rejection_category", "reason_rejected", "coded_by", "coded_date", "notes",
]
COMPANY_SUMMARY_FIELDS = [
    "company", "ticker", "sector", "annual_report_latest_collected", "annual_report_previous_collected",
    "separate_sustainability_report_collected", "official_web_search_completed", "partner_search_completed",
    "provisional_use_case_count", "confirmed_use_case_count", "no_disclosure_confirmed", "manual_review_status",
    "notes", "last_updated_date",
]

REJECTION_CATEGORY_LABELS = {
    "predictive_personalisation": "predictive_ml_not_genai",
    "route_optimisation": "predictive_ml_not_genai",
    "heat_identification_operations": "predictive_ml_not_genai",
    "ordinary_automation": "ordinary_automation_not_genai",
    "robotic_automation": "ordinary_automation_not_genai",
    "audit_analytics": "general_ai_not_genai",
    "vague_general_ai_reference": "general_ai_not_genai",
    "extraction_artifact": "extraction_artifact_not_a_genuine_mention",
    "webpage_boilerplate": "webpage_boilerplate_not_evidence",
    "predictive_optimisation": "predictive_ml_not_genai",
    "predictive_automation_network_ops": "ordinary_automation_not_genai",
    "insufficient_operational_detail": "insufficient_operational_detail",
    "predictive_automation_negotiation_agent": "predictive_ml_not_genai",
    "predictive_optimisation_energy": "predictive_ml_not_genai",
}
REJECTION_ITEM_LABELS = {
    "predictive_personalisation": "Predictive/personalisation AI feature",
    "route_optimisation": "Delivery route optimisation AI",
    "heat_identification_operations": "Predictive refrigeration heat-identification tool",
    "ordinary_automation": "Ordinary automation tool/process",
    "robotic_automation": "Robotic process automation",
    "audit_analytics": "Audit/risk analytics and machine learning",
    "vague_general_ai_reference": "Vague, unqualified 'AI' reference",
    "extraction_artifact": "PDF extraction artefact (not a genuine AI mention)",
    "webpage_boilerplate": "Website navigation/footer/CMS boilerplate",
    "predictive_optimisation": "Predictive/optimisation AI (network performance/maintenance)",
    "predictive_automation_network_ops": "AI Ops network self-healing automation",
    "insufficient_operational_detail": "Named GenAI product with no concrete qualifying task described",
    "predictive_automation_negotiation_agent": "Game-theory/negotiation automation agent",
    "predictive_optimisation_energy": "AI-powered energy-optimisation solution",
}


def today_date() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Promote human-reviewed rows from a company's five staging files "
            "(outputs/intermediate/<company>_*_staging.csv) into the project's main datasets: "
            "source_manifest.csv, use_case_dataset_template.csv, strategic_capability_building_findings.csv, "
            "governance_and_enablement_findings.csv, rejected_or_aspirational_findings.csv and "
            "company_summary_template.csv. Only rows with an eligible reviewer_decision are promoted. "
            "evidence_strength/confidence are PROPOSED with reasons, never invented -- real promotion leaves "
            "review_status = not_reviewed until a human explicitly approves those proposed values."
        ),
    )
    parser.add_argument("--company", required=True, help="Company name or ticker exactly as in pilot_companies.csv.")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Report the full promotion proposal without writing any main dataset file or checkpoint.",
    )
    return parser.parse_args(argv)


# ---------------------------------------------------------------------------
# Loading staging + main dataset files
# ---------------------------------------------------------------------------

def load_staging(slug: str, name: str) -> tuple[list[str] | None, list[dict]]:
    path = pc.INTERMEDIATE_DIR / f"{slug}_{name}_staging.csv" if name != "duplicate_flags" else \
        pc.INTERMEDIATE_DIR / f"{slug}_duplicate_flags.csv"
    return pc.read_csv_rows(path)


def load_main_csv(path: Path) -> tuple[list[str], list[dict]]:
    """Read a main dataset CSV, using its OWN on-disk header as the
    authoritative field list/order -- never a hardcoded constant -- so
    column order is always preserved exactly as found.
    """
    fieldnames, rows = pc.read_csv_rows(path)
    if fieldnames is None:
        raise FileNotFoundError(f"{path} does not exist.")
    return fieldnames, rows


def sector_lookup(company: str) -> str:
    """03_CODING_MANUAL.md's 'Sector lookup rule': sector must come from
    ftse100_constituents_2026-06-19.csv, never typed manually elsewhere.
    """
    fieldnames, rows = pc.read_csv_rows(pc.FTSE_CONSTITUENTS_CSV)
    if fieldnames is None:
        raise FileNotFoundError(f"{pc.FTSE_CONSTITUENTS_CSV} does not exist.")
    for r in rows:
        if (r.get("company") or "").strip().lower() == company.strip().lower():
            return (r.get("sector") or "").strip()
    raise ValueError(f"'{company}' not found in {pc.FTSE_CONSTITUENTS_CSV.name} -- cannot populate sector.")


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def check_reviewer_decisions(all_staging_rows: list[dict], problems: list[str]) -> None:
    for r in all_staging_rows:
        decision = (r.get("reviewer_decision") or "").strip()
        if decision and decision not in REVIEWER_DECISION_VALUES:
            problems.append(
                f"BLOCKED {r.get('staging_id', r.get('duplicate_group_id', '?'))}: "
                f"invalid reviewer_decision '{decision}'"
            )


def already_promoted(staging_id: str, existing_rows: list[dict], note_field: str) -> bool:
    marker = f"Promoted from staging {staging_id}"
    return any(marker in (r.get(note_field) or "") for r in existing_rows)


# ---------------------------------------------------------------------------
# Tesco-specific source-manifest field overrides
# ---------------------------------------------------------------------------
# Mechanical fields (financial_year_covered, evidence_origin, document_category,
# candidate_title) come straight from tesco_source_candidates.csv. The fields
# below require a judgment call the source-candidates file cannot mechanically
# resolve, so they are stated explicitly here with a reason -- mirroring the
# AZN-004 "title discrepancy" precedent already logged in source_manifest.csv.
SOURCE_MANIFEST_OVERRIDES = {
    "TSCO_company_annual_report_current_fy2025.pdf": {
        # direct_download_url from tesco_source_candidates.csv -- the actual PDF location, not the landing page.
        "url": "https://www.tescoplc.com/media/ky0bfwpo/tesco_ar25_interactive.pdf",
        "publication_date": "",  # no publication/board-approval date directly confirmed on the extracted pages; left blank, not inferred
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the verified direct_download_url; the landing page is "
            "https://www.tescoplc.com/investors/reports-results-and-presentations/annual-report-2025 . "
            "No publication/board-approval date is directly confirmed on the extracted pages (checked pages 1-5); "
            "publication_date left blank rather than inferred. Report covers the 52-week period ended 22 February "
            "2025 (a reporting period, not a publication date). Yielded governance findings (AI governance group/"
            "committee, safeguards) and strategic findings (embedding AI into operations); no operational GenAI "
            "use case found in this document itself."
        ),
    },
    "TSCO_company_annual_report_previous_fy2024.pdf": {
        "url": "https://www.tescoplc.com/media/zgvhd0dn/tescos_ar24.pdf",
        "publication_date": "",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the verified direct_download_url; the landing page is "
            "https://www.tescoplc.com/investors/reports-results-and-presentations/annual-report-2024 . "
            "No publication date is directly confirmed on the extracted pages (checked pages 1-5); left blank "
            "rather than inferred. Report covers the year ended 24 February 2024. Contains a confirmed pypdf "
            "extraction artefact ('Ai ming' -> 'Aiming', p.17) correctly excluded, not coded as a genuine AI "
            "mention. Yielded governance and strategic findings, cross-year duplicates of the FY2025 report's "
            "equivalent disclosures."
        ),
    },
    "TSCO_company_sustainability_or_esg_report_fy2024-25.pdf": {
        "url": "https://www.tescoplc.com/media/wvkj1yic/tesco-sustainability-report-2025.pdf",
        # Extracted page 1 directly states "Tesco PLC Sustainability Report 2024/25 / May 2025" -- a genuine
        # on-page confirmation, at month-level precision only (matching the AZN-003 sustainability-report
        # precedent of "2025-05"). Not converting to an invented exact day.
        "publication_date": "2025-05",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the verified direct_download_url; the landing page is "
            "https://www.tescoplc.com/sustainability-report-2025 . publication_date '2025-05' is directly "
            "confirmed on extracted page 1 ('May 2025'), at month precision only -- no exact day is stated "
            "anywhere on the page, so none is invented. Yielded one governance finding (AI governance framework), "
            "consistent with the equivalent annual-report disclosures."
        ),
    },
    "TSCO_partner_press_release_tesco-media-creative-studio-ai-powered-ad-creation-tool-for_2025-10-09.html": {
        # final_redirected_url from tesco_download_log.csv -- the actual page fetched and verified (HTTP 200);
        # the originally-recorded landing_page_url redirects to this URL.
        "url": "https://www.dunnhumby.com/news/tesco-media-upfront-redefining-retail-media/",
        "publication_date": "2025-10-09",
        "document_review_status": "reviewed_evidence_found",
        "document_title": "Tesco Media Upfront 2025: The Future of Retail Media",
        "notes": (
            "url is the verified final_redirected_url actually fetched (HTTP 200); the originally-recorded "
            "landing_page_url https://www.dunnhumby.com/about-us/news/tesco-media-upfront-redefining-retail-media/ "
            "redirects to this address. Title discrepancy: source-candidate checklist title was 'Tesco Media "
            "Creative Studio (AI-powered ad creation tool for brands)'; actual saved page title (from the HTML "
            "<title> tag) is 'Tesco Media Upfront 2025: The Future of Retail Media | dunnhumby' -- site-name suffix "
            "dropped. dunnhumby is a distinct company managing Tesco Media's technology infrastructure (historically "
            "a Tesco-owned data-science arm), not Tesco plc itself -- evidence_origin recorded as technology_partner "
            "accordingly. Explicit quote: 'Powered by GenAI, it automatically generates compliant ads in all the "
            "formats brands need.' Yielded one operational use case (TSCO-UC-002)."
        ),
    },
    "TSCO_partner_press_release_adobe-tesco-enter-strategic-ai-partnership-to-personalise-ex_2026-04-13.html": {
        "url": "https://news.adobe.com/en/gb/news/2026/04/adobe-tesco-enter-strategic-ai-partnership",
        "publication_date": "2026-04-13",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the verified official Adobe newsroom address (landing_page_url, direct_download_url and "
            "final_redirected_url are all identical for this source -- no redirect occurred). Official Adobe "
            "newsroom release (technology_partner; Adobe's own publication, not Tesco's). Explicit quote: 'Using "
            "technology like Adobe's agentic AI capabilities and Adobe Firefly Foundry, Tesco's personalisation and "
            "AI teams will be able to...'. Describes a planned/early-stage partnership (Tesco x Adobe Innovation "
            "Lab), not a live deployment. Yielded one operational use case (TSCO-UC-001)."
        ),
    },
    # --- BT Group ------------------------------------------------------------
    "BT.A_company_annual_report_current_fy2025.pdf": {
        "url": "https://www.bt.com/bt-plc/assets/documents/investors/financial-reporting-and-news/annual-reports/2025/2025-bt-group-plc-annual-report.pdf",
        "publication_date": "",  # not directly confirmed on the extracted pages this session; left blank, not inferred
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct_download_url from bt-group_source_candidates.csv; the landing page is "
            "https://www.bt.com/about/investors/financial-reporting-and-news/annual-reports (shared with the "
            "FY2024 report -- both years still downloaded as separate PDFs). No publication/board-approval date "
            "confirmed on-page; left blank rather than inferred. Yielded governance and strategic findings; the "
            "AR2025 Copilot/workplace-adjustment mention was assessed and correctly kept out of operational "
            "staging (no concrete qualifying task described)."
        ),
    },
    "BT.A_company_annual_report_previous_fy2024.pdf": {
        "url": "https://www.bt.com/bt-plc/assets/documents/investors/financial-reporting-and-news/annual-reports/2024/2024-bt-group-plc-annual-report.pdf",
        "publication_date": "",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct_download_url; landing page shared with the FY2025 report (see above). No "
            "publication date confirmed on-page; left blank. Contains the Globality negotiation-platform mention "
            "(operational, needs_more_evidence pending confirmation of generative-AI status) and corroborating "
            "Amazon Q Developer language (not promoted as a second operational row)."
        ),
    },
    "BT.A_company_sustainability_or_esg_report_fy2025.pdf": {
        "url": "https://www.bt.com/bt-plc/assets/documents/digital-impact-and-sustainability/our-report/report-archive/2025/2025-bt-group-plc-esg-addendum.pdf",
        "publication_date": "",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct_download_url; landing page is "
            "https://www.bt.com/about/digital-impact-and-sustainability/our-approach . No publication date "
            "confirmed on-page. Contains only a single generic 'Internet of Things and AI' mention, correctly "
            "rejected as vague/non-qualifying -- yielded no operational, strategic or governance finding."
        ),
    },
    "BT.A_company_press_release_bt-group-s-digital-unit-launches-genai-gateway-platform-powe_2024-09-24.html": {
        "url": "https://newsroom.bt.com/bt-groups-digital-unit-launches-genai-gateway-platform-powered-by-aws-accelerating-the-companys-safe-adoption-of-generative-ai-at-scale/",
        "publication_date": "2024-09-24",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the landing_page_url (no direct_download_url recorded; no redirect observed during download). "
            "Company-primary press release (evidence_origin=company_primary; AWS is the named infrastructure "
            "partner but this is BT's own newsroom publication). Yielded two distinct operational use cases "
            "(Openreach engineering-note summarisation; contract analysis for Business/legal/procurement) plus a "
            "governance finding for the Gateway's enablement/guardrails infrastructure itself."
        ),
    },
    "BT.A_company_press_release_bt-group-leans-on-ai-to-transform-customer-service-experienc_2024-12-12.html": {
        "url": "https://newsroom.bt.com/bt-group-leans-on-ai-to-transform-customer-service-experience/",
        "publication_date": "2024-12-12",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the landing_page_url (no redirect observed). Company-primary press release describing the "
            "Sprinklr-powered EE virtual assistant Aimee. Yielded one consolidated operational use case "
            "(BT-OP-003) plus a governance finding (ethical guardrails/private-cloud hosting)."
        ),
    },
    "BT.A_partner_partner_case_study_writing-and-maintaining-2-million-lines-a-year-using-amazon.html": {
        "url": "https://aws.amazon.com/solutions/case-studies/bt-group-case-study/",
        "publication_date": "",  # no publication date shown on the AWS case-study page
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the landing_page_url (no redirect observed). AWS-authored technology-partner case study "
            "(evidence_origin=technology_partner) -- no publication date shown on the page. Yielded one "
            "consolidated operational use case (Amazon Q Developer, BT-OP-004), corroborated (not duplicated) by "
            "a brief AR2024 mention of the same tool."
        ),
    },
    # --- Rolls-Royce Holdings --------------------------------------------------
    "RR_company_annual_report_current_fy2025.pdf": {
        "url": "https://www.rolls-royce.com/~/media/Files/R/Rolls-Royce/documents/annual-report/2026/2025-annual-report-interactive.pdf",
        "publication_date": "",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct_download_url (interactive PDF) from rolls-royce-holdings_source_candidates.csv; "
            "landing page is https://www.rolls-royce.com/investors/results-reports-and-presentations/annual-report-2025.aspx . "
            "No publication date confirmed on-page; left blank. Zero Stage A (high-precision GenAI) hits -- "
            "yielded only governance and strategic findings, no operational candidate from this document."
        ),
    },
    "RR_company_annual_report_previous_fy2024.pdf": {
        "url": "https://www.rolls-royce.com/~/media/Files/R/Rolls-Royce/documents/annual-report/2025/2024-annual-report.pdf",
        "publication_date": "",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct_download_url; landing page is "
            "https://www.rolls-royce.com/investors/results-reports-and-presentations/annual-report-2024.aspx . No "
            "publication date confirmed on-page. Zero Stage A hits; contains the AI-workforce-readiness passages "
            "corrected into strategic staging (RR-STR-005/RR-STR-006)."
        ),
    },
    "RR_partner_partner_case_study_rolls-royce-harnessing-the-power-of-databricks-for-image-gen_2024-08-08.html": {
        "url": "https://www.databricks.com/blog/rolls-royce-mosaic-ai",
        "publication_date": "2024-08-08",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the landing_page_url (no redirect observed). Databricks-authored technology-partner blog "
            "post, co-authored by five named Rolls-Royce engineers. Yielded one consolidated operational use case "
            "(conditional GAN for preliminary aero-engine design, RR-OP-001); additional cGAN-mentioning passages "
            "correctly treated as corroborating evidence for the same finding, not a second candidate."
        ),
    },
    "RR_partner_partner_case_study_rolls-royce-saves-millions-in-cost-avoidance-with-microsoft_2025-04-01.html": {
        "url": "https://www.microsoft.com/en/customers/story/23201-rolls-royce-azure-databricks",
        "publication_date": "2025-04-01",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the landing_page_url (no redirect observed). Microsoft-authored technology-partner case "
            "study. Yielded one operational candidate held at needs_more_evidence (vibration-analysis defect "
            "detection, RR-OP-002 -- provisional_is_genai=unclear) and one strategic finding (central data "
            "repository built 'for use by generative AI', RR-STR-001, enablement/infrastructure not yet a "
            "concrete task)."
        ),
    },
    # --- Experian (Batch 1) --------------------------------------------------
    "EXPN_company_annual_report_current_fy2026.pdf": {
        "url": "https://www.experianplc.com/content/dam/marketing/global/plc/en/assets/documents/reports/2026/experian-annual-report-2026.pdf",
        "publication_date": "",  # not directly confirmed on the extracted pages this session; left blank, not inferred
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the verified direct_download_url; landing page is https://www.experianplc.com/investors/ . "
            "No on-page publication date confirmed; left blank rather than inferred. Experian's fiscal year ends "
            "31 March, so this FY2026 report (year ended 31 March 2026) is the current latest annual report. "
            "Reviewed passages did not yield a promotable operational/strategic/governance finding from this "
            "document itself this round."
        ),
    },
    "EXPN_company_press_release_experian-accelerates-migration-to-aws-to-drive-innovation-wi_2025-06-19.html": {
        "url": "https://www.experianplc.com/newsroom/press-releases/2025/experian-accelerates-migration-to-aws-to-drive-innovation-with-g",
        "publication_date": "2025-06-19",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the effective_download_url (landing page and direct URL are identical; no redirect "
            "occurred). Company-primary newsroom release. Explicit 'generative AI' language ('developing more "
            "than 100 generative AI use-cases'; GenAI-driven database-migration streamlining), but no individual "
            "task meets the full operational bar (no named user group; the quantified 60% figure is attributed "
            "to the broader AWS migration, not isolated to the GenAI mechanism) -- retained as strategic "
            "capability-building evidence (EXPN-STR-012), not promoted to operational."
        ),
    },
    "EXPN_company_press_release_new-ai-powered-experian-assistant-for-model-risk-management_2025-07-31.html": {
        "url": "https://www.experianplc.com/newsroom/press-releases/2025/new-ai-powered-experian-assistant-for-model-risk-management-stre",
        "publication_date": "2025-07-31",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the effective_download_url (no redirect occurred). Company-primary newsroom release. "
            "Explicit 'GenAI capabilities'/'GenAI-enabled capabilities' language describing the Experian "
            "Assistant for Model Risk Management -- a concrete documentation/governance-automation task for "
            "financial-institution clients. Yielded one operational use case (EXPN-OP-001), consolidated from "
            "staging rows originally split across governance (EXPN-GOV-014) and rejected (EXPN-REJ-068)."
        ),
    },
    "EXPN_company_press_release_experian-brings-trusted-agentic-ai-to-financial-services-wit_2026-06-02.html": {
        "url": "https://www.experianplc.com/newsroom/press-releases/2026/experian-brings-trusted-agentic-ai-to-financial-services-with-th",
        "publication_date": "2026-06-02",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the effective_download_url (no redirect occurred). Company-primary newsroom release "
            "describing the Agent Operating System (agentic AI layer within the Experian Ascend Platform). "
            "Concrete lending-workflow tasks are named (fraud checks, loan approvals) but deployment is "
            "explicitly planned/future ('will be available to early adopters later this year') -- does not meet "
            "the operational bar. Retained as a governance finding (EXPN-GOV-013), consolidated from staging rows "
            "originally split across governance and rejected (EXPN-REJ-065, EXPN-REJ-066)."
        ),
    },
    # --- Rio Tinto (Batch 1) ---------------------------------------------------
    "RIO_company_annual_report_current_fy2025.pdf": {
        "url": "https://cdn-rio.dataweavers.io/-/media/content/documents/invest/reports/annual-reports/2025-annual-report.pdf?rev=928756ce35df4757be31105d2665bd55",
        "publication_date": "",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the effective_download_url, extracted from the official riotinto.com landing page "
            "(https://www.riotinto.com/en/invest/reports/annual-report) and served via Rio Tinto's own asset "
            "CDN (cdn-rio.dataweavers.io), not a third-party mirror. No on-page publication date confirmed; left "
            "blank. Contains only a generic risk-factor mention of generative AI (principal-risks section, "
            "p.92) -- correctly rejected as vague_general_ai_reference (RIO-REJ-004), not connected to RIO-OP-001."
        ),
    },
    "RIO_company_annual_report_previous_fy2024.pdf": {
        "url": "https://www.riotinto.com/-/media/content/documents/invest/reports/annual-reports/2024-annual-report.pdf",
        "publication_date": "",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the effective_download_url (riotinto.com-hosted, not a third-party mirror). No on-page "
            "publication date confirmed; left blank. Reviewed passages did not yield a promotable operational/"
            "strategic/governance finding from this document itself this round (6 rejected-staging rows remain "
            "unreviewed, reviewer_decision blank)."
        ),
    },
    "RIO_company_strategy_or_technology_webpage_using-artificial-intelligence-and-data-science-for-better-op_2024-07-25.html": {
        "url": "https://www.riotinto.com/en/news/stories/using-ai-data-science-for-better-operations",
        "publication_date": "2024-07-25",  # page shows "Last updated: 25 July 2024" -- recorded as such, not assumed to be the original publish date
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the effective_download_url (no redirect occurred). Official riotinto.com story page "
            "(company_primary). Explicit 'Generative AI and Large Language Models (LLMs)' and 'Generative "
            "Pre-Trained Transformer (GPT) like' language describing a knowledge agent built by the internal "
            "data science team for the Annual Planning Review workshop. Yielded one operational use case "
            "(RIO-OP-001), promoted from rejected staging (RIO-REJ-015)."
        ),
    },
    # --- Admiral Group (Batch 1) -------------------------------------------------
    "ADM_partner_partner_case_study_admiral-selects-google-cloud-to-accelerate-innovative-custom_2024-02-14.html": {
        "url": "https://www.prnewswire.com/news-releases/admiral-selects-google-cloud-to-accelerate-innovative-customer-experiences-302061528.html",
        "publication_date": "2024-02-14",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the effective_download_url (no redirect occurred). Google Cloud-authored technology-partner "
            "release (evidence_origin=technology_partner) issued via PR Newswire. Explicit 'generative AI' "
            "language ('leverage Google Cloud's...generative AI capabilities to strategically enable data-driven "
            "decision making') but no concrete task, user group or deployment stage is described -- does not meet "
            "the operational bar. Retained as strategic technology-partnership evidence (ADM-STR-001), promoted "
            "from rejected staging (ADM-REJ-002)."
        ),
    },
    # --- Informa (Batch 1) ----------------------------------------------------
    "INF_company_annual_report_current_fy2025.pdf": {
        "url": "https://www.informa.com/globalassets/documents/investor-relations/2026/2025-informa-annual-report.pdf",
        "publication_date": "",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the effective_download_url (no redirect occurred); landing page is "
            "https://www.informa.com/investors/ . No on-page publication date confirmed; left blank. Contains an "
            "explicit reference to a board-approved 'Generative AI Use Policy' and 'AI Governance Charter' "
            "(p.55) -- yielded one governance finding (INF-GOV-007), confirmed as governance oversight evidence, "
            "not an operational use case. Other passages from this document remain unreviewed this round "
            "(reviewer_decision blank)."
        ),
    },
    "INF_company_annual_report_previous_fy2024.pdf": {
        "url": "https://www.informa.com/globalassets/documents/investor-relations/2025/2024-informa-annual-report.pdf",
        "publication_date": "",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the effective_download_url (no redirect occurred); landing page is "
            "https://www.informa.com/investors/ . No on-page publication date confirmed; left blank. Reviewed "
            "passages did not yield a promotable finding from this document this round (all staging rows remain "
            "reviewer_decision blank)."
        ),
    },
    "INF_company_sustainability_or_esg_report_fy2025.pdf": {
        "url": "https://www.informa.com/globalassets/documents/sustainability/reporting/2026/2025-informa-sustainability-report.pdf",
        "publication_date": "",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the effective_download_url (no redirect occurred); landing page is "
            "https://www.informa.com/sustainability/ . No on-page publication date confirmed; left blank. "
            "Genuinely separate sustainability report, distinct from the Annual Report. Reviewed passages did "
            "not yield a promotable finding from this document this round (all staging rows remain "
            "reviewer_decision blank)."
        ),
    },
    # --- Diageo (scale-up batch loop 2) ---------------------------------------
    "DGE_company_annual_report_current_fy2025.pdf": {
        "url": "https://www.diageo.com/~/media/Files/D/Diageo-V2/Diageo-Corp/investors/results-reports-and-events/annual-reports/2025/annual-report-2025.pdf",
        "publication_date": "",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the effective_download_url (no redirect occurred); landing page is "
            "https://www.diageo.com/en/investors . Report covers the year ended 30 June 2025. No on-page "
            "publication date confirmed; left blank. Yielded two operational use cases (DGE-OP-002 generative-AI "
            "cybersecurity chatbot; contributes to the Diageo-wide review), plus rejected general-AI-strategy "
            "commentary."
        ),
    },
    "DGE_company_annual_report_previous_fy2024.pdf": {
        "url": "https://www.diageo.com/~/media/Files/D/Diageo-V2/Diageo-Corp/investors/results-reports-and-events/annual-reports/diageo-annual-report-2024.pdf",
        "publication_date": "",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the effective_download_url (no redirect occurred). No on-page publication date confirmed; "
            "left blank. Yielded one operational use case (DGE-OP-003, 'What's Your Cocktail?' generative-AI "
            "food-pairing platform)."
        ),
    },
    "DGE_company_press_release_diageo-unveils-its-first-bottle-personalisation-experience-f_2024-07-23.html": {
        "url": "https://www.diageo.com/en/news-and-media/press-releases/2024/diageo-unveils-its-first-bottle-personalisation-experience-fuelled-by-generative-ai",
        "publication_date": "2024-07-23",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the effective_download_url (no redirect occurred). Company-primary newsroom release. "
            "Publication date confirmed directly on-page as 2024-07-23 (a WebSearch summary this session had "
            "incorrectly suggested 2026 -- the direct-fetch date is authoritative). Yielded one operational use "
            "case (DGE-OP-001, Generative-AI bottle/label personalisation pilot, Amazon Titan Bedrock model)."
        ),
    },
    # --- National Grid plc (scale-up batch loop 2) ----------------------------
    "NG_company_annual_report_current_fy2025-26.pdf": {
        "url": "https://www.nationalgrid.com/document/579676/download",
        "publication_date": "",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the effective_download_url (no redirect occurred); landing page is "
            "https://www.nationalgrid.com/investors . No on-page publication date confirmed; left blank. "
            "Reviewed passages did not yield a promotable finding from this document this round."
        ),
    },
    "NG_company_annual_report_previous_fy2024-25.pdf": {
        "url": "https://www.nationalgrid.com/document/560311/download",
        "publication_date": "",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the effective_download_url (no redirect occurred). No on-page publication date confirmed; "
            "left blank. All 4 Stage-A ('likely_genai') passages reviewed and confirmed correctly rejected -- "
            "generic industry-trend/board-agenda/strategic-ambition commentary with no concrete National Grid "
            "task, user group or deployment described (yielded rejected findings NG-REJ-027, NG-REJ-031, "
            "NG-REJ-035, NG-REJ-036)."
        ),
    },
    # --- Shell plc (scale-up loop 3, Track B unblocked) -----------------------
    "SHEL_company_annual_report_current_fy2025_2026-03-12.pdf": {
        "url": "https://www.shell.com/investors/results-and-reporting/annual-report/_jcr_content/root/main/section/promo.multi.stream/1779352356739/36306d968747b6079d3f800b2b1552a033856b5d/shell-integrated-annual-and-sustainability-report.pdf",
        "publication_date": "2026-03-12",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the effective_download_url; landing page is "
            "https://www.shell.com/investors/results-and-reporting/annual-report.html . Integrated annual and "
            "sustainability report; submitted to the UK National Storage Mechanism and Dutch AFM on 2026-03-12 "
            "per prior-session search results. Reviewed passages did not yield a promotable finding from this "
            "document itself this round (generic generative-AI risk-factor mentions correctly rejected)."
        ),
    },
    "SHEL_company_annual_report_previous_fy2024.pdf": {
        "url": "https://www.shell.com/investors/results-and-reporting/annual-report-archive/_jcr_content/root/main/section_812377294/tabs/tab_copy/text.multi.stream/1751445525195/e136de58f65e2a30bc91aa5f2d7c6833e4e060b3/shell-annual-report-and-accounts-and-form-20-f-2024.pdf",
        "publication_date": "",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the corrected direct_download_url (the originally recorded URL returned a genuine HTTP 404 "
            "on repeated retries across sessions -- confirmed via direct HEAD request; this replacement URL was "
            "located via search and HEAD-verified as HTTP 200 during Track B resolution). Landing page is "
            "https://www.shell.com/investors/results-and-reporting/annual-report-archive.html . No on-page "
            "publication date confirmed; left blank."
        ),
    },
    "SHEL_partner_partner_case_study_sparkcognition-and-shell-announce-a-technology-collaboration_2023-05-17.html": {
        "url": "https://www.prnewswire.com/news-releases/sparkcognition-and-shell-announce-a-technology-collaboration-aimed-at-accelerating-the-pace-of-exploration-through-the-use-of-generative-ai-301826717.html",
        "publication_date": "2023-05-17",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the effective_download_url (no redirect occurred). Technology_partner (SparkCognition) "
            "release via PR Newswire. Yielded one operational use case (SHEL-OP-001, generative-AI subsurface "
            "exploration imaging)."
        ),
    },
    # --- HSBC (scale-up loop 3, Track B unblocked) ----------------------------
    "HSBA_company_annual_report_current_fy2025.pdf": {
        "url": "https://www.hsbc.com/-/files/hsbc/investors/hsbc-results/2025/annual/pdfs/hsbc-holdings-plc/260225-annual-report-and-accounts-2025.pdf",
        "publication_date": "",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the effective_download_url (no redirect occurred); landing page is "
            "https://www.hsbc.com/investors . No on-page publication date confirmed; left blank. Reviewed "
            "passages did not yield a promotable finding from this document itself this round."
        ),
    },
    "HSBA_company_annual_report_previous_fy2024.pdf": {
        "url": "https://www.hsbc.com/-/files/hsbc/investors/hsbc-results/2024/annual/pdfs/hsbc-holdings-plc/250219-annual-report-and-accounts-2024.pdf",
        "publication_date": "",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the effective_download_url (no redirect occurred). No on-page publication date confirmed; "
            "left blank."
        ),
    },
    "HSBA_company_press_release_hsbc-and-google-cloud-announce-transformative-ai-banking-par_2026-06-17.html": {
        "url": "https://www.hsbc.com/news-and-views/news/media-releases/2026/hsbc-and-google-cloud-announce-transformative-ai-banking-partnership",
        "publication_date": "2026-06-17",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the effective_download_url (no redirect occurred). Company-primary newsroom release. "
            "Yielded one operational use case (HSBA-OP-001, Google Cloud/Gemini partnership)."
        ),
    },
    "HSBA_company_press_release_hsbc-and-mistral-ai-join-forces-to-accelerate-ai-adoption-ac_2025-12-01.html": {
        "url": "https://www.hsbc.com/news-and-views/news/media-releases/2025/hsbc-and-mistral-ai-join-forces-to-accelerate-ai-adoption-across-global-bank",
        "publication_date": "2025-12-01",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the effective_download_url (no redirect occurred). Company-primary newsroom release. "
            "Yielded one operational use case (HSBA-OP-002, Mistral AI foundational-model productivity platform)."
        ),
    },
    # --- GSK plc (scale-up loop 3) ---------------------------------------------
    "GSK_company_annual_report_current_fy2025.pdf": {
        "url": "https://www.gsk.com/media/kn0bknmd/annual-report-2025.pdf",
        "publication_date": "",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the corrected direct_download_url (the originally recorded assets.gskstatic.com URL "
            "returned a genuine HTTP 404; this www.gsk.com-hosted equivalent, same asset ID, was located and "
            "HEAD-verified as HTTP 200). Landing page is "
            "https://www.gsk.com/en-gb/investors/financial-reports/annual-report-2025/ . No on-page publication "
            "date confirmed; left blank. Yielded one operational use case (GSK-OP-001)."
        ),
    },
    "GSK_company_annual_report_previous_fy2024.pdf": {
        "url": "https://www.gsk.com/media/wrvfwob1/annual-report-2024.pdf",
        "publication_date": "",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the effective_download_url (no redirect occurred). No on-page publication date confirmed; "
            "left blank. Reviewed passages did not yield a promotable finding from this document itself this "
            "round."
        ),
    },
    # --- RELX (scale-up loop 3) -------------------------------------------------
    "REL_company_annual_report_current_fy2025.pdf": {
        "url": "https://www.relx.com/~/media/Files/R/RELX-Group/documents/reports/annual-reports/relx-2025-annual-report.pdf",
        "publication_date": "",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the effective_download_url (no redirect occurred); landing page is "
            "https://www.relx.com/investors/annual-reports . No on-page publication date confirmed; left blank."
        ),
    },
    "REL_company_annual_report_previous_fy2024.pdf": {
        "url": "https://www.relx.com/~/media/Files/R/RELX-Group/documents/reports/annual-reports/relx-2024-annual-report.pdf",
        "publication_date": "",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the effective_download_url (no redirect occurred). No on-page publication date confirmed; "
            "left blank."
        ),
    },
    "REL_company_strategy_or_technology_webpage_how-relx-is-adopting-generative-ai_2026-03.html": {
        "url": "https://stories.relx.com/generative-ai/index.html",
        "publication_date": "",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the effective_download_url (no redirect occurred). Official RELX corporate storytelling "
            "page (company_primary), dated March 2026 on-page (no exact day given). Describes numerous "
            "commercially-available generative-AI products; yielded four operational use cases (REL-OP-001 "
            "through REL-OP-004) -- a representative, non-exhaustive selection; several further named products "
            "on this page were not separately coded this round due to scope."
        ),
    },
    # --- Next plc (scale-up loop 3) ---------------------------------------------
    "NXT_company_annual_report_current_fy2025-26.pdf": {
        "url": "https://www.nextplc.co.uk/~/media/Files/N/next-plc-v4/about-next/annual-report-and-accounts-jan-2026.pdf",
        "publication_date": "",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the effective_download_url (no redirect occurred); landing page is "
            "https://www.nextplc.co.uk/investors . Next's fiscal year ends in late January, so this is the "
            "current latest report. No on-page publication date confirmed; left blank. Reviewed passages did "
            "not yield a promotable operational finding -- AI/agentic-AI/LLM mentions are blended within a "
            "broad general-AI strategy narrative without an isolated, quantified generative-AI task."
        ),
    },
    "NXT_company_annual_report_previous_fy2024-25.pdf": {
        "url": "https://www.nextplc.co.uk/~/media/Files/N/next-plc-v4/about-next/annual-report-and-accounts-jan-2025.pdf",
        "publication_date": "",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the effective_download_url (no redirect occurred). No on-page publication date confirmed; "
            "left blank."
        ),
    },
    # --- Vodafone Group (scale-up batch loop 2) -------------------------------
    "VOD_company_annual_report_current_fy2025.pdf": {
        "url": "https://investors.vodafone.com/~/media/Files/V/Vodafone-IR/documents/performance/financial-results/2025/form-20-f-2025.pdf",
        "publication_date": "",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the effective_download_url (no redirect occurred); landing page is "
            "https://investors.vodafone.com/performance/annual-reporting . Vodafone files its comprehensive "
            "annual disclosure as a Form 20-F. No on-page publication date confirmed; left blank. Yielded one "
            "operational use case (VOD-OP-002, Copilot for Microsoft 365 employee rollout)."
        ),
    },
    "VOD_company_press_release_meet-supertobi-vodafone-s-new-generative-ai-virtual-assistan_2024-07-04.html": {
        "url": "https://www.vodafone.com/news/newsroom/technology/meet-super-tobi-vodafone-s-new-generative-ai-virtual-assistant-now-serving-customers-in-multiple-countries",
        "publication_date": "2024-07-04",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the effective_download_url (no redirect occurred). Company-primary newsroom release. "
            "Yielded one operational use case (VOD-OP-001, SuperTOBi generative-AI virtual assistant)."
        ),
    },
    # --- Legal & General (scale-up batch loop 2) ------------------------------
    "LGEN_company_annual_report_current_fy2025.pdf": {
        "url": "https://group.legalandgeneral.com/asset/49512b/globalassets/group/reporting-hub/reports/2026/annual-report-and-accounts-2025/annual-reports-and-accounts-2025.pdf",
        "publication_date": "",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the effective_download_url (no redirect occurred); landing page is "
            "https://group.legalandgeneral.com/en/investors . No on-page publication date confirmed; left blank. "
            "Reviewed passages did not yield a promotable finding from this document itself this round."
        ),
    },
    "LGEN_company_annual_report_previous_fy2024.pdf": {
        "url": "https://group.legalandgeneral.com/asset/492cb6/globalassets/group/about-us/our-purpose/l-g-annual-report-and-accounts-2024.pdf",
        "publication_date": "",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the effective_download_url (no redirect occurred). No on-page publication date confirmed; "
            "left blank. Reviewed passages did not yield a promotable finding from this document itself this "
            "round."
        ),
    },
    "LGEN_company_press_release_l-g-expands-microsoft-collaboration-to-accelerate-ai-enablem_2026-06-16.html": {
        "url": "https://group.legalandgeneral.com/newsroom/press-releases/2026/6/lg-expands-microsoft-collaboration-to-accelerate-ai-enablement-and-transform-customer-experience/",
        "publication_date": "2026-06-16",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the effective_download_url (no redirect occurred). Company-primary newsroom release. "
            "Yielded one operational use case (LGEN-OP-001, Copilot for Microsoft 365 employee rollout + "
            "already-live Retail-business customer-facing AI tool), consolidated from staging rows originally "
            "split across strategic (LGEN-STR-001) and rejected (LGEN-REJ-023)."
        ),
    },
    # --- Reckitt (scale-up batch loop 2) ---------------------------------------
    "RKT_company_annual_report_current_fy2025.pdf": {
        "url": "https://eu-assets.contentstack.com/v3/assets/blt93c8bc7a598af9f0/blt3a6f2cd6ab14bf47/69c2b35aa17ac75c0a18f6f2/Reckitt_Annual_Report_and_Accounts_2025_(2).pdf",
        "publication_date": "",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the effective_download_url, served via Reckitt's official Contentstack CDN (linked from "
            "reckitt.com's own investor pages, not a third-party mirror). No on-page publication date "
            "confirmed; left blank. Reviewed passages did not yield a promotable finding from this document "
            "itself this round (the operational finding came from the separate press release)."
        ),
    },
    "RKT_company_press_release_reckitt-s-first-genai-results-demonstrate-changing-face-of-m_2024-06-21.html": {
        "url": "https://www.reckitt.com/news/reckitt-s-first-genai-results-demonstrate-changing-face-of-marketing-during-cannes-lions-international-festival-of-creativity/",
        "publication_date": "2024-06-21",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the effective_download_url (no redirect occurred). Company-primary newsroom release. "
            "Yielded one operational use case (RKT-OP-001, GenAI marketing pilots -- Gaviscon, Finish)."
        ),
    },
    # --- Croda International (scale-up batch loop 2) --------------------------
    "CRDA_company_annual_report_current_fy2025.pdf": {
        "url": "https://www.croda.com/mediaassets/files/corporate/annual-report-2025/croda-annual-report-2025.pdf",
        "publication_date": "",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the effective_download_url (no redirect occurred); landing page is "
            "https://www.croda.com/en-gb/investors . No on-page publication date confirmed; left blank. Zero "
            "Stage A (high-precision GenAI) hits -- no explicit generative-AI evidence found in this document; "
            "only general AI/data-analytics/machine-learning language, correctly not coded as GenAI per Core "
            "Rule 2."
        ),
    },
    "CRDA_company_annual_report_previous_fy2024.pdf": {
        "url": "https://www.croda.com/mediaassets/files/corporate/reporting-hub-2024/annual-report/annual-report-2024.pdf",
        "publication_date": "",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the effective_download_url (no redirect occurred). No on-page publication date confirmed; "
            "left blank. Zero Stage A hits -- no explicit generative-AI evidence found in this document."
        ),
    },

    # --- Whitbread (scale-up loop 4) ----------------------------------------
    "WTB_company_annual_report_current_fy2024-25_2025-05.pdf": {
        "url": "https://cdn.whitbread.co.uk/media/2025/05/Whitbread-PLC-Annual-Report-and-Accounts-2024-25.pdf",
        "publication_date": "2025-05",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct_download_url (official cdn.whitbread.co.uk). Yielded one thin but genuine "
            "strategic finding (Generative AI as a named Board briefing topic); one governance-staged row "
            "(AI-enabled food waste detection) rejected as general-AI-only, not generative AI."
        ),
    },
    "WTB_company_annual_report_previous_fy2023-24_2024-05.pdf": {
        "url": "https://cdn.whitbread.co.uk/media/2024/05/Whitbread-PLC-Annual-Report-and-Accounts-2023_Single_pages-1.pdf",
        "publication_date": "2024-05",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct_download_url (official cdn.whitbread.co.uk). Source of WTB-STR-001 (Generative AI "
            "Board briefing topic, p.117)."
        ),
    },
    "WTB_company_sustainability_or_esg_report_fy2024-25_2025-05.pdf": {
        "url": "https://cdn.whitbread.co.uk/media/2025/05/Whitbread-PLC-Environmental-Social-and-Governance-Report-2024-25.pdf",
        "publication_date": "2025-05",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct_download_url (official cdn.whitbread.co.uk). Source of the AI-enabled food waste "
            "detection (Winnow) mention, correctly rejected as general-AI-only."
        ),
    },

    # --- Barratt Redrow (scale-up loop 4) -----------------------------------
    "BTRW_company_annual_report_current_fy2025_2025.pdf": {
        "url": "https://www.barrattredrow.co.uk/~/media/Files/B/Barratt-Developments-V2/documents/annual-report-2025/strategic-report-barratt-redrow-plc-annual-report-and-accounts-2025.pdf",
        "publication_date": "",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct_download_url. Fetched and read directly this session with no generative-AI/LLM/"
            "copilot language found anywhere; zero screening hits at all. No on-page publication date confirmed; "
            "left blank."
        ),
    },
    "BTRW_company_annual_report_previous_fy2024_2024.pdf": {
        "url": "https://www.barrattredrow.co.uk/~/media/Files/B/Barratt-Developments-V2/documents/reports-and-presentation/2024/report/barratt-ar2024.pdf",
        "publication_date": "",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct_download_url. Sole finding (BTRW-REJ-001) is a general 'artificial intelligence' "
            "telehandler proximity-detection trial -- general-AI-only, not generative AI. No on-page publication "
            "date confirmed; left blank."
        ),
    },

    # --- London Stock Exchange Group (scale-up loop 4) ----------------------
    "LSEG_company_annual_report_current_fy2025_2026-02.pdf": {
        "url": "https://www.lseg.com/content/dam/lseg/en_us/documents/investor-relations/annual-reports/lseg-annual-report-2025.pdf",
        "publication_date": "2026-02",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct_download_url (official lseg.com). Extensive AI-strategy ('LSEG Everywhere') and "
            "governance disclosure; no operational-qualifying generative-AI deployment found in this specific "
            "document (the AI-powered Question and Answer Service (QAS) mention on p.14 does not use explicit "
            "generative-AI/LLM language, so is correctly excluded from the operational count)."
        ),
    },
    "LSEG_company_annual_report_previous_fy2024_2025-04.pdf": {
        "url": "https://www.lseg.com/content/dam/lseg/en_us/documents/investor-relations/annual-reports/lseg-annual-report-2024.pdf",
        "publication_date": "2025-04",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct_download_url (official lseg.com). Source of both confirmed operational findings: "
            "Financial Meeting Prep (explicitly 'generally available'/launched by end of 2024) and AI Insights "
            "API, both explicitly named 'Gen AI' products (p.8, corroborated at p.43 and in the remuneration "
            "committee report)."
        ),
    },
    "LSEG_company_press_release_n-a_2025-10-13.html": {
        "url": "https://www.lseg.com/en/media-centre/press-releases/2025/lseg-and-microsoft-transform-access-to-ai-ready-financial-data-in-customer-workflows",
        "publication_date": "2025-10-13",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct press-release URL (official lseg.com), fetch-verified this session. Describes the "
            "LSEG/Microsoft Copilot Studio and MCP-server partnership -- a platform enabling customers to build "
            "unspecified AI agents, correctly coded as strategic technology enablement, not a specific "
            "operational task."
        ),
    },
    "LSEG_company_press_release_n-a_2025-12.html": {
        "url": "https://www.lseg.com/en/media-centre/press-releases/2025/lseg-announces-new-collaboration-with-openai",
        "publication_date": "2025-12",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct press-release URL (official lseg.com), fetch-verified this session. Describes the "
            "ChatGPT/MCP connector and the planned 4,000-employee ChatGPT Enterprise rollout -- both explicitly "
            "future-tense/planned in this document, coded as strategic (LSEG-STR-015, LSEG-STR-016) rather than "
            "operational, per this loop's rule against classifying planned deployments as operational."
        ),
    },
    "LSEG_company_official_case_study_n-a.html": {
        "url": "https://www.lseg.com/en/insights/from-interoperability-to-agents-powering-financial-workflows-with-ai",
        "publication_date": "",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct page URL (official lseg.com), fetch-verified this session. Describes LSEG "
            "Workspace 'agentic workflows (currently in pilot)' -- explicitly a pilot, not live; contributed "
            "governance content (LSEG-GOV-006) on AI interaction governance/auditability. No on-page publication "
            "date found; left blank."
        ),
    },

    # --- Smiths Group (scale-up loop 4) -------------------------------------
    "SMIN_company_annual_report_current_fy2025_2025-09.pdf": {
        "url": "https://www.smiths.com/media/uwkpyowa/smiths-annual-report-2025.pdf",
        "publication_date": "2025-09",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct_download_url (official smiths.com). 'GenAI' named as one of several technology "
            "megatrends (p.14, thin strategic finding); a general 'artificial intelligence' adoption-risk mention "
            "(p.30) correctly rejected as general-AI-only, not generative AI. Note: Smiths Detection (predictive/"
            "classification AI for CT threat detection) is being divested from Smiths Group (sale agreed 2025, "
            "expected completion H2 2026) and in any case does not involve generative AI."
        ),
    },
    "SMIN_company_annual_report_previous_fy2024_2024-09.pdf": {
        "url": "https://www.smiths.com/media/qlyomwgz/smiths-annual-report-2024-overview-and-strategic-report.pdf",
        "publication_date": "2024-09",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct_download_url (official smiths.com). No generative-AI-qualifying evidence found; "
            "only ordinary automation/capex language."
        ),
    },

    # --- British Land (scale-up loop 4) -------------------------------------
    "BLND_company_annual_report_current_fy2025-26_2026-05.pdf": {
        "url": "https://www.britishland.com/media/nq2p0biq/british-land_ara26.pdf",
        "publication_date": "2026-05",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct_download_url (official britishland.com). Fetched and read directly this session: "
            "no generative-AI/LLM/copilot language describing British Land's own use found anywhere; the only "
            "AI-related content is tenant/office-demand commentary naming AI-sector occupiers (e.g. Anthropic, "
            "Synthesia), which does not describe British Land's own deployment and is correctly rejected."
        ),
    },
    "BLND_company_annual_report_previous_fy2024-25_2025-05.pdf": {
        "url": "https://www.britishland.com/media/oxffzaui/bl_ar25_int_strategic-report.pdf",
        "publication_date": "2025-05",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct_download_url (official britishland.com). Sole governance-staged row (ERP 'AI "
            "Automation') rejected as general-AI-only, not generative AI; sole generative-AI-labelled mention "
            "(Synthesia, a tenant) correctly rejected as tenant/market commentary, not British Land's own use."
        ),
    },

    # --- Barclays (scale-up batch 1) ----------------------------------------
    "BARC_company_annual_report_current_fy2025_2025.pdf": {
        "url": "https://home.barclays/content/dam/home-barclays/documents/investor-relations/reports-and-events/annual-reports/2025/Barclays-PLC-Annual-Report-2025.pdf",
        "publication_date": "2025",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct_download_url (official home.barclays PDF). Yielded one operational use case "
            "(BARC-OP-001, Microsoft 365 Copilot rollout, c.100,000 licences)."
        ),
    },
    "BARC_company_annual_report_previous_fy2024_2024.pdf": {
        "url": "https://home.barclays/content/dam/home-barclays/documents/investor-relations/reports-and-events/annual-reports/2024/Barclays-PLC-Annual-Report-2024.pdf",
        "publication_date": "2024",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official home.barclays PDF). Corroborating/background source; no distinct operational finding sourced from this report specifically.",
    },

    # --- Aviva (scale-up batch 1) -------------------------------------------
    "AV_company_annual_report_current_fy2025_2026-03.pdf": {
        "url": "https://static.aviva.io/content/dam/aviva-corporate/documents/investors/pdfs/reports/2025/annual-report-and-accounts-2025.pdf",
        "publication_date": "2026-03",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct_download_url (official static.aviva.io PDF). Yielded two operational use cases: "
            "AV-OP-001 (GenAI claims summarisation tool, 500+ handlers) and AV-OP-002 (generative-AI GP-medical-"
            "report summarisation tool for underwriters)."
        ),
    },
    "AV_company_annual_report_previous_fy2024_2025.pdf": {
        "url": "https://static.aviva.io/content/dam/aviva-corporate/documents/investors/pdfs/reports/2024/aviva-plc-annual-report-and-accounts-2024.pdf",
        "publication_date": "2025",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct_download_url (official static.aviva.io PDF). Yielded one operational use case "
            "(AV-OP-003, Microsoft 365 Copilot Chat for all colleagues / GitHub Copilot for all developers)."
        ),
    },

    # --- Halma plc (scale-up batch 1) ---------------------------------------
    "HLMA_company_annual_report_current_fy2025_2025.pdf": {
        "url": "https://www.halma.com/~/media/Files/H/Halma/Corp-V2/reports-and-presentations/reports/2025/halma-fy25-report.pdf",
        "publication_date": "2025",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official halma.com PDF). No qualifying generative-AI evidence found; PeriGen's predictive/clinical-decision-support AI is general-AI-only, not generative AI.",
    },
    "HLMA_company_annual_report_previous_fy2024_2024.pdf": {
        "url": "https://www.halma.com/~/media/Files/H/Halma/Corp-V2/reports-and-presentations/reports/2024/ara/halma-annual-report-and-accounts-2024.pdf",
        "publication_date": "2024",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official halma.com PDF). No qualifying generative-AI evidence found.",
    },

    # --- Severn Trent (scale-up batch 1) ------------------------------------
    "SVT_company_annual_report_current_fy2025_2025.pdf": {
        "url": "https://www.severntrent.com/content/dam/stw-plc/Severn_Trent_AR25_Strategic_Report.pdf",
        "publication_date": "2025",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official severntrent.com PDF, strategic-report component). No GenAI-specific evidence found in this year's report (the Copilot/GPT-4 disclosure is in the AR2024 only).",
    },
    "SVT_company_annual_report_previous_fy2024_2024.pdf": {
        "url": "https://www.severntrent.com/content/dam/stw-plc/shareholder-resources/2024-reports/severn-trent-ara-2024-bookmarked-web-full-report.pdf",
        "publication_date": "2024",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct_download_url (official severntrent.com PDF). Yielded one operational use case "
            "(SVT-OP-001, Copilot with 'the capabilities of GPT-4' for colleagues)."
        ),
    },

    # --- Marks & Spencer (scale-up batch 2) ---------------------------------
    "MKS_company_annual_report_current_fy2024-25_2025-05.pdf": {
        "url": "https://corporate.marksandspencer.com/sites/marksandspencer/files/2025-05/Marks-and-Spencer-Group-plc-Annual-Report-and-Financial-Statements-2025_INTERACTIVE_FINAL.pdf",
        "publication_date": "2025-05",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official corporate.marksandspencer.com PDF). Background/corroborating source; the operational finding was sourced from the March 2026 press release instead.",
    },
    "MKS_company_annual_report_previous_fy2023-24_2024-06.pdf": {
        "url": "https://corporate.marksandspencer.com/sites/marksandspencer/files/2024-06/M-and-S-2024-Annual-Report.pdf",
        "publication_date": "2024-06",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official corporate.marksandspencer.com PDF). Background/corroborating source.",
    },
    "MKS_company_press_release_n-a_2026-03-25.html": {
        "url": "https://corporate.marksandspencer.com/newsroom/press-releases/ms-gives-every-store-manager-and-every-store-support-centre-colleague",
        "publication_date": "2026-03-25",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct press-release URL (official corporate.marksandspencer.com), fetch-verified this "
            "session. Yielded one operational use case (MKS-OP-001, Microsoft 365 Copilot for store managers "
            "and support-centre colleagues)."
        ),
    },

    # --- Standard Chartered (scale-up batch 2) ------------------------------
    "STAN_company_annual_report_current_fy2025_2026-02.pdf": {
        "url": "https://www.sc.com/en/uploads/sites/66/content/docs/standard-chartered-plc-2025-annual-report.pdf",
        "publication_date": "2026-02",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official sc.com PDF). Background/corroborating source; the two operational findings were sourced from the official AI innovation webpage instead.",
    },
    "STAN_company_annual_report_previous_fy2024_2025-02.pdf": {
        "url": "https://www.sc.com/uk/uploads/sites/66/content/docs/annual-report-2024-strategic-report.pdf",
        "publication_date": "2025-02",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official sc.com PDF). Background/corroborating source.",
    },
    "STAN_company_strategy_or_technology_webpage_n-a.html": {
        "url": "https://www.sc.com/en/about/innovation/artificial-intelligence/",
        "publication_date": "",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct page URL (official sc.com), fetch-verified this session. Yielded two "
            "operational use cases: STAN-OP-001 (SC GPT, in-house LLM, 70,000+ employees) and STAN-OP-002 "
            "(GitHub Copilot for developers). No on-page publication date found; left blank."
        ),
    },

    # --- Prudential plc (scale-up batch 2) ----------------------------------
    "PRU_company_annual_report_current_fy2025_2026-03.pdf": {
        "url": "https://www.prudentialplc.com/content/dam/prudential-plc/investor/results-and-reports/lastest-annual-report/prudential-plc-ar-2025.pdf",
        "publication_date": "2026-03",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official prudentialplc.com PDF). Background/corroborating source.",
    },
    "PRU_company_annual_report_previous_fy2024_2025.pdf": {
        "url": "https://www.prudentialplc.com/content/dam/prudential-plc/investor/results-and-reports/all-reports/2024/prudential-plc-ar-2024.pdf",
        "publication_date": "2025",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct_download_url (official prudentialplc.com PDF). Source of PRU-STR-003 (MedLM "
            "pilot for medical-claims analysis, coded strategic not operational -- explicitly a pilot)."
        ),
    },
    "PRU_company_press_release_n-a_2024-10-24.html": {
        "url": "https://www.prudentialplc.com/en/news-and-insights/all-news/news-releases/2024/24-10-2024",
        "publication_date": "2024-10-24",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct press-release URL (official prudentialplc.com), fetch-verified this session. Corroborates PRU-STR-003 (MedLM pilot); explicitly describes a bounded 3-4 month pilot, not a production deployment.",
    },

    # --- International Airlines Group (scale-up batch 2) --------------------
    "IAG_company_annual_report_current_fy2025_2025.pdf": {
        "url": "https://www.iairgroup.com/media/ktnlp1jx/iag-annual-report-and-accounts-2025.pdf",
        "publication_date": "2025",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official iairgroup.com PDF). No qualifying generative-AI evidence found -- only general AI risk-factor/opportunity-identification language.",
    },
    "IAG_company_annual_report_previous_fy2024_2024.pdf": {
        "url": "https://www.iairgroup.com/media/4qxgaavc/iag-annual-report-and-accounts-2024.pdf",
        "publication_date": "2024",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official iairgroup.com PDF). No qualifying generative-AI evidence found.",
    },

    # --- NatWest Group (scale-up batch 3) -----------------------------------
    "NWG_company_annual_report_current_fy2025_2026-02.pdf": {
        "url": "https://investors.natwestgroup.com/~/media/Files/R/RBS-IR-V2/results-center/13022026/nwg-annual-report-and-accounts-2025.pdf",
        "publication_date": "2026-02",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official investors.natwestgroup.com PDF). Background/corroborating source; the operational finding was sourced from the April 2025 press release instead.",
    },
    "NWG_company_annual_report_previous_fy2024_2025-03.pdf": {
        "url": "https://investors.natwestgroup.com/~/media/Files/R/RBS-IR-V2/results-center/14022025/nwg-annual-report-and-accounts-accessible-11032025.pdf",
        "publication_date": "2025-03",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official investors.natwestgroup.com PDF). Background/corroborating source.",
    },
    "NWG_company_press_release_n-a_2025-04.html": {
        "url": "https://www.natwestgroup.com/news-and-insights/latest-stories/ai-and-data/2025/apr/deploying-new-generative-ai-technology-to-support-our-colleagues.html",
        "publication_date": "2025-04",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct press-release URL (official natwestgroup.com), fetch-verified this session. "
            "Yielded one operational use case (NWG-OP-001, AI Digital Enabler + Microsoft Copilot Chat, "
            "rolled out to 99% of colleagues)."
        ),
    },

    # --- Persimmon (scale-up batch 3) ---------------------------------------
    "PSN_company_annual_report_current_fy2025_2025.pdf": {
        "url": "https://www.persimmonhomes.com/corporate/media/t2ejxi3y/persimmon-plc-annual-report-2025.pdf",
        "publication_date": "2025",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official persimmonhomes.com PDF). No qualifying generative-AI evidence found -- only general AI governance/pilot-academy language.",
    },
    "PSN_company_annual_report_previous_fy2024_2024.pdf": {
        "url": "https://www.persimmonhomes.com/corporate/media/pg0jl11j/persimmon-plc-annual-report-2024.pdf",
        "publication_date": "2024",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official persimmonhomes.com PDF). No qualifying generative-AI evidence found.",
    },

    # --- SSE plc (scale-up batch 3) ------------------------------------------
    "SSE_company_annual_report_current_fy2025_2025-06.pdf": {
        "url": "https://www.sse.com/media/blhnuywb/sse-full-annual-report.pdf",
        "publication_date": "2025-06",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official sse.com PDF). Background/corroborating source; the operational finding was sourced from the Microsoft technology-partner case study instead.",
    },
    "SSE_company_annual_report_previous_fy2024_2024.pdf": {
        "url": "https://www.sse.com/media/0aibgke4/sse_ar24_interactive.pdf",
        "publication_date": "2024",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official sse.com PDF). Background/corroborating source.",
    },
    "SSE_partner_partner_case_study_n-a.html": {
        "url": "https://www.microsoft.com/en/customers/story/24657-sse-microsoft-copilot-studio",
        "publication_date": "",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct page URL (official microsoft.com), fetch-verified this session. Yielded one "
            "operational use case (SSE-OP-001, Nero virtual assistant, Azure OpenAI + Copilot Studio, "
            "evidence_origin=technology_partner). No on-page publication date found; left blank."
        ),
    },

    # --- Auto Trader Group (scale-up batch 3) --------------------------------
    "AUTO_company_annual_report_current_fy2025_2025-05.pdf": {
        "url": "https://plc.autotrader.co.uk/media/ujinai40/at-ar25-web.pdf",
        "publication_date": "2025-05",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct_download_url (official plc.autotrader.co.uk PDF). Yielded one operational use "
            "case (AUTO-OP-001, Co-Driver/AI Generated Descriptions, LLM-based, live per the Board's own risk "
            "disclosure)."
        ),
    },
    "AUTO_company_annual_report_previous_fy2024_2024-07.pdf": {
        "url": "https://plc.autotrader.co.uk/media/rrqk35uy/at-ar24-web-final.pdf",
        "publication_date": "2024-07",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official plc.autotrader.co.uk PDF). Background/corroborating source.",
    },

    # --- Intertek (scale-up batch 3) ------------------------------------------
    "ITRK_company_annual_report_current_fy2025_2026.pdf": {
        "url": "https://www.intertek.com/siteassets/investors/2026/ara/intertek-annual-report--accounts-2025-combined.pdf",
        "publication_date": "2026",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct_download_url (official intertek.com PDF). Yielded one operational use case "
            "(ITRK-OP-001, Synthesia-powered generative-AI training-video product for People Assurance "
            "clients), distinct from Intertek's separate general-AI assurance/certification service line "
            "(correctly excluded as not generative AI)."
        ),
    },
    "ITRK_company_annual_report_previous_fy2024_2024.pdf": {
        "url": "https://www.intertek.com/siteassets/investors/2024/intertek-annual-report-2024.pdf",
        "publication_date": "2024",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official intertek.com PDF). Background/corroborating source.",
    },

    # --- Anglo American plc (scale-up batch 4) --------------------------------
    "AAL_company_annual_report_current_fy2025_2026-03.pdf": {
        "url": "https://www.angloamerican.com/~/media/Files/A/Anglo-American-Group-v9/PLC/investors/annual-reporting/2025/aa-annual-report-full-2025.pdf",
        "publication_date": "2026-03",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct_download_url (official angloamerican.com PDF). Yielded one strategic finding "
            "(AAL-STR-002, generative AI for internal knowledge stores/analytical acceleration) -- not coded "
            "operational as no specific named tool, user group or deployment stage is confirmed."
        ),
    },
    "AAL_company_annual_report_previous_fy2024_2025-03.pdf": {
        "url": "https://www.angloamerican.com/~/media/Files/A/Anglo-American-Group-v9/PLC/investors/annual-reporting/2024/aa-annual-report-full-2024.pdf",
        "publication_date": "2025-03",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official angloamerican.com PDF). Background/corroborating source.",
    },

    # --- Convatec (scale-up batch 4) ------------------------------------------
    "CTEC_company_annual_report_current_fy2025_2026.pdf": {
        "url": "https://www.convatecgroup.com/siteassets/investors/ec1372707_convatec-ar-2025_aw_interactive.pdf",
        "publication_date": "2026",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct_download_url (official convatecgroup.com PDF). Yielded one operational use case "
            "(CTEC-OP-001, Microsoft Copilot and Synthesia, enterprise-scale deployment)."
        ),
    },
    "CTEC_company_annual_report_previous_fy2024_2025.pdf": {
        "url": "https://www.convatecgroup.com/siteassets/convatec-ara-2024.pdf",
        "publication_date": "2025",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official convatecgroup.com PDF). Background/corroborating source.",
    },

    # --- Bunzl (scale-up batch 4) ---------------------------------------------
    "BNZL_company_annual_report_current_fy2025_2025.pdf": {
        "url": "https://www.bunzl.com/media/px0hi0zf/bunzl_ar25_interactive.pdf",
        "publication_date": "2025",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official bunzl.com PDF). No qualifying operational generative-AI evidence found -- only a thin GenAI-tool-use governance policy mention.",
    },
    "BNZL_company_annual_report_previous_fy2023_2023.pdf": {
        "url": "https://www.bunzl.com/media/0aljxph1/annual-report-2023.pdf",
        "publication_date": "2023",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official bunzl.com PDF). No qualifying generative-AI evidence found.",
    },

    # --- Entain (scale-up batch 4) ---------------------------------------------
    "ENT_company_annual_report_current_fy2025_2026-03-20.pdf": {
        "url": "https://www.entaingroup.com/media/by4fdoyj/entain-annual-report-2025.pdf",
        "publication_date": "2026-03-20",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct_download_url (official entaingroup.com PDF). Yielded one operational use case "
            "(ENT-OP-001, SportingBOT generative-AI chatbot, 65,000+ users in Brazil)."
        ),
    },
    "ENT_company_annual_report_previous_fy2024_2025-03-21.pdf": {
        "url": "https://www.entaingroup.com/AnnualReport2024/documents/Entain_Annual_Report_2024.pdf",
        "publication_date": "2025-03-21",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official entaingroup.com PDF). Background/corroborating source (GenAI Blackbelt Programme, strategic capability-building only).",
    },

    # --- Schroders (scale-up batch 4) -------------------------------------------
    "SDR_company_annual_report_current_fy2025_2026-02.html": {
        "url": "https://www.schroders.com/en/global/individual/corporate-transparency/reporting/annual-report-and-accounts-2025/",
        "publication_date": "2026-02",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": (
            "url is the landing-page URL (official schroders.com); no distinct downloadable PDF was confidently "
            "isolated this session -- this page resolved to a JavaScript-rendered document-viewer shell "
            "(confirmed identical extracted content to the previous-year row, zero screening hits in both), "
            "so it does not represent genuine distinct report content. Both operational findings for this "
            "company were sourced from the separately fetch-verified press release instead."
        ),
    },
    "SDR_company_annual_report_previous_fy2024_2025-03.html": {
        "url": "https://www.schroders.com/en/global/individual/corporate-transparency/reporting/annual-report-and-accounts-2024/",
        "publication_date": "2025-03",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the landing-page URL (official schroders.com); same document-viewer-shell limitation as the current-year row -- zero screening hits, no genuine distinct content extracted.",
    },
    "SDR_company_press_release_n-a_2024-07.html": {
        "url": "https://www.schroders.com/en-us/us/institutional/media-center/schroders-capital-launches-ai-analyst-for-private-equity/",
        "publication_date": "2024-07",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct press-release URL (official schroders.com), fetch-verified this session. "
            "Yielded two operational use cases: SDR-OP-001 (GAiiA, Generative AI Investment Analyst for "
            "private equity) and SDR-OP-002 (Genie, GPT-based internal assistant for 1,000+ colleagues daily)."
        ),
    },

    # --- Sainsbury's (scale-up batch 5) -----------------------------------------
    "SBRY_company_annual_report_current_fy2024-25_2025.pdf": {
        "url": "https://corporate.sainsburys.co.uk/media/e1lfnybd/sainsbury-annual-report-and-financial-statements-2025.pdf",
        "publication_date": "2025",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": (
            "url is the direct_download_url (official corporate.sainsburys.co.uk PDF). Screened with zero "
            "Stage A hits; only ordinary automation/machine-learning-forecasting and vague unqualified 'AI' "
            "language found (including two board-level 'generative artificial intelligence' training-session "
            "mentions with no operational deployment described) -- genuine null result, not a blocker."
        ),
    },
    "SBRY_company_annual_report_previous_fy2023-24_2024.pdf": {
        "url": "https://corporate.sainsburys.co.uk/media/n3bdgevz/sainsbury-annual-report-and-financial-statements-2024.pdf",
        "publication_date": "2024",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official corporate.sainsburys.co.uk PDF). Same genuine null result as the current-year row -- ordinary automation/ML-forecasting language only, zero Stage A hits.",
    },

    # --- Pearson plc (scale-up batch 5) ------------------------------------------
    "PSON_company_annual_report_current_fy2025_2026.pdf": {
        "url": "https://plc.pearson.com/sites/pearson-corp/files/annual-reports/2025/pearson-annual-report-2025.pdf",
        "publication_date": "2026",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct_download_url (official plc.pearson.com PDF). Yielded one operational use case "
            "(PSON-OP-001, Claude and Claude Code deployment across engineering and business functions, split "
            "out from over-consolidated staging row PSON-STR-004) plus multiple genuine strategic/governance "
            "findings (AI Centre for Enablement, Responsible AI framework, digital-transformation partnerships)."
        ),
    },
    "PSON_company_annual_report_previous_fy2024_2025.pdf": {
        "url": "https://plc.pearson.com/sites/pearson-corp/files/pearson/annual-report-2024/strategic-report-2024.pdf",
        "publication_date": "2025",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct_download_url (official plc.pearson.com strategic-report PDF component). Yielded "
            "strategic findings only (Generative AI Foundations certification -- a training/certification "
            "product about GenAI topics, not an application of GenAI to a task, so coded strategic/capability-"
            "building rather than operational)."
        ),
    },
    "PSON_company_press_release_n-a.html": {
        "url": "https://plc.pearson.com/en-GB/news-and-insights/news/pearson-and-microsoft-announce-multi-year-partnership-transform-future",
        "publication_date": "unknown",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct press-release URL (official plc.pearson.com), fetch-verified this session. Yielded strategic findings (Generative AI Foundations certification launch, Microsoft partnership).",
    },

    # --- Smith & Nephew (scale-up batch 5) ---------------------------------------
    "SN_company_annual_report_current_fy2025_2026-03.html": {
        "url": "https://www.smith-nephew.com/en/who-we-are/investors/annual-report-2025",
        "publication_date": "2026-03",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": (
            "url is the landing-page URL (official smith-nephew.com); no static PDF was isolated, but this "
            "page DID extract genuine narrative annual-report content (57,169 characters, directly verified "
            "by reading the extracted text), screened and searched for GenAI keywords -- only general AI/ML/"
            "ERP language found ('leverage analytics and artificial intelligence', 'employ AI, machine "
            "learning and data analytics'), no explicit generative-AI/LLM/Copilot terms. Genuine null result."
        ),
    },
    "SN_company_annual_report_previous_fy2024_2025.html": {
        "url": "https://www.smith-nephew.com/en/who-we-are/investors/reports-and-presentations",
        "publication_date": "2025",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": (
            "url is the landing-page URL (official smith-nephew.com); this row resolved to pure website-"
            "navigation/product-listing boilerplate with no annual-report narrative content at all (confirmed "
            "by directly reading the full 472-line extracted text) -- not treated as a hard blocker because "
            "the current-year row separately provided genuine, substantively-screened narrative content."
        ),
    },

    # --- Centrica (scale-up batch 5) ---------------------------------------------
    "CNA_company_annual_report_current_fy2025_2026-02.pdf": {
        "url": "https://www.centrica.com/media/ckfb0qxj/annual-report-and-accounts-2025-untagged.pdf",
        "publication_date": "2026-02",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official centrica.com PDF). Screened with 16 Stage A hits; contributed governance/AI-oversight findings (no operational use case sourced from this document itself -- see the Microsoft partner case study for the operational finding).",
    },
    "CNA_company_annual_report_previous_fy2024_2024.pdf": {
        "url": "https://www.centrica.com/media/2pjoazw0/annual-report-and-accounts-2024-untagged.pdf",
        "publication_date": "2024",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official centrica.com PDF). No qualifying GenAI-specific evidence found in this document.",
    },
    "CNA_partner_partner_case_study_n-a.html": {
        "url": "https://www.microsoft.com/en/customers/story/26768-centrica-microsoft-power-platform",
        "publication_date": "unknown",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct case-study URL (official microsoft.com), fetch-verified this session, naming "
            "Centrica specifically. Yielded one operational use case (CNA-OP-001, Microsoft 365 Copilot Agent "
            "Builder email-compliance agent, split out from over-consolidated staging row CNA-REJ-028) plus "
            "governance findings; two further agents described in the same source (Employee Self-Service, "
            "career-development recommendations) were explicitly still in development/being customised and "
            "are NOT included in the operational finding."
        ),
    },

    # --- Babcock International (scale-up batch 7) ---------------------------------
    "BAB_company_annual_report_current_fy2025_2025-07.pdf": {
        "url": "https://www.babcockinternational.com/wp-content/uploads/2025/07/Babcock-Annual-Report-and-Financial-Statements-2025.pdf",
        "publication_date": "2025-07",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": (
            "url is the direct_download_url (official babcockinternational.com PDF). Only general AI-ethics "
            "governance discussion and a predictive/ML 'Risk Resilience' supply-chain monitoring tool "
            "(not generative) found -- no operational generative-AI use case. Genuine null result."
        ),
    },
    "BAB_company_annual_report_previous_fy2024_2024-07.pdf": {
        "url": "https://www.babcockinternational.com/wp-content/uploads/2025/06/Babcock-Annual-Report-2024-Strategic-Report.pdf",
        "publication_date": "2024-07",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": (
            "url is the direct_download_url (official babcockinternational.com PDF, Strategic Report section "
            "-- the 2024 report is split into sectioned PDFs rather than one combined file). Same genuine "
            "null result as the current-year row."
        ),
    },

    # --- Rentokil Initial (scale-up batch 7) ---------------------------------------
    "RTO_company_annual_report_current_fy2025_2026-03.pdf": {
        "url": "https://www.rentokil-initial.com/~/media/Files/R/Rentokil/documents/annual-reports/rentokil-ar25.pdf",
        "publication_date": "2026-03",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct_download_url (official rentokil-initial.com PDF). Yielded one operational use "
            "case (RTO-OP-001, Google Gemini AI for Google Workspace rolled out to the entire global "
            "workforce) split out from an over-consolidated staging row, plus a strategic finding for the "
            "not-yet-live in-house 'AI Portal'/RatGPT agent platform and 3 governance findings."
        ),
    },
    "RTO_company_annual_report_previous_fy2024_2025-03.pdf": {
        "url": "https://www.rentokil-initial.com/~/media/Files/R/Rentokil/documents/annual-reports/250317_RIAR24_FINAL.pdf",
        "publication_date": "2025-03",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official rentokil-initial.com PDF). Only a single passing 'generative AI advancements' mention with no operational detail -- no qualifying evidence in this document on its own.",
    },

    # --- JD Sports (scale-up batch 8) --------------------------------------------
    "JD_company_annual_report_current_fy2025_2025-05.pdf": {
        "url": "https://s204.q4cdn.com/980191062/files/doc_downloads/results_centre/2025/05/24467_JD_Sports_AR25_Web.pdf",
        "publication_date": "2025-05",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official jdplc.com IR content domain, q4cdn.com). Only vague general-AI/cyber-risk language found within this document itself -- the qualifying GenAI evidence came from a separate press release.",
    },
    "JD_company_annual_report_previous_fy2024_2024-06.pdf": {
        "url": "https://s204.q4cdn.com/980191062/files/doc_financials/2024/ar/jd-sports-fashion-annual-report-and-accounts-2024.pdf",
        "publication_date": "2024-06",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official jdplc.com IR content domain). Only a vague, non-GenAI 'AI Support' customer-service tool mention found -- no explicit generative-AI/LLM language in this document.",
    },
    "JD_company_press_release_n-a_2026-01-12.pdf": {
        "url": "https://s204.q4cdn.com/980191062/files/doc_news/JD-deploys-cutting-edge-technology-to-enable-direct-purchases-through-AI-platforms-2026.pdf",
        "publication_date": "2026-01-12",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct press-release URL (official jdplc.com IR content domain). Yielded one strategic finding (JD-STR-001, a planned/not-yet-live one-click AI-commerce rollout via Copilot/Gemini/ChatGPT) -- not operational, since explicitly future-tense throughout.",
    },

    # --- Coca-Cola Europacific Partners (scale-up batch 8) -----------------------
    "CCEP_company_annual_report_current_fy2025_2026-03.pdf": {
        "url": "https://www.cocacolaep.com/assets/Download-centre/CCEP-Annual-Report-and-Form-20-F-2025.pdf",
        "publication_date": "2026-03",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": (
            "url is the direct_download_url (official cocacolaep.com PDF). Only predictive/IoT AI (smart "
            "coolers), predictive agricultural-science AI (Avalo crop development) and general Responsible-AI "
            "governance language found -- no explicit generative-AI use case. A third-party trade-media claim "
            "about a CCEP/Bureau Works AI translation 'Language Portal' was checked directly against this "
            "text and NOT found -- not used as evidence. Genuine null result."
        ),
    },
    "CCEP_company_annual_report_previous_fy2024_2025-03.pdf": {
        "url": "https://www.cocacolaep.com/assets/Global/Investors/2024-Annual-Report/2024-CCEP-Annual-Report_2025.03.20_Interactive.pdf",
        "publication_date": "2025-03",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official cocacolaep.com PDF). Same genuine null result as the current-year row.",
    },

    # --- Hiscox (scale-up batch 8) ------------------------------------------------
    "HSX_company_annual_report_current_fy2025_2026-03.pdf": {
        "url": "https://www.hiscoxgroup.com/sites/group/files/documents/2026-03/Hiscox%20Ltd%20Report%20and%20Accounts%202025.pdf",
        "publication_date": "2026-03",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official hiscoxgroup.com PDF). Contributed strategic/governance findings on AI adoption and AI governance framework (no distinct operational finding sourced from this document itself -- see the separate press release and Microsoft case study for the two operational findings).",
    },
    "HSX_company_annual_report_previous_fy2024_2025-03.html": {
        "url": "https://www.hiscoxgroup.com/investors/report-and-accounts-2024",
        "publication_date": "2025-03",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": (
            "url is the landing-page URL (official hiscoxgroup.com); this page resolved to the CURRENT (2025) "
            "results landing page rather than genuine FY2024 report content, and even that page is a thin "
            "navigation/summary shell (confirmed by directly reading the extracted text) -- not treated as a "
            "hard blocker because the current-year AR plus the separately-sourced press release and Microsoft "
            "case study together provide substantial, well-corroborated coverage for this company."
        ),
    },
    "HSX_company_press_release_n-a_2024-08-12.html": {
        "url": "https://www.hiscoxgroup.com/news/press-releases/2024/12-08-24",
        "publication_date": "2024-08-12",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct press-release URL (official hiscoxgroup.com), fetch-verified this session. Yielded one operational use case (HSX-OP-001, Gemini-powered lead underwriting model for the sabotage/terrorism line, submission-to-quote cut from 3 days to 3 minutes).",
    },
    "HSX_partner_partner_case_study_n-a.html": {
        "url": "https://ukstories.microsoft.com/features/how-ai-is-supercharging-hiscox-employees-to-do-what-theyre-great-at/",
        "publication_date": "unknown",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct case-study URL (official ukstories.microsoft.com), fetch-verified this session, naming Hiscox specifically. Yielded one operational use case (HSX-OP-002, Microsoft 365 Copilot for claims handling, rolled out to 3,000+ employees across 14 countries).",
    },

    # --- Games Workshop (scale-up batch 8) ---------------------------------------
    "GAW_company_annual_report_current_fy2024-25_2025-07-29.pdf": {
        "url": "https://assets.ctfassets.net/ost7hseic9hc/3kXsoA4jSOmOj6BLZ7bV7F/c34a5f56769e8be055c19b8e1ccc5526/Accounts_2024-25_FINAL.pdf",
        "publication_date": "2025-07-29",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": (
            "url is the direct_download_url (official games-workshop.com/ctfassets-hosted PDF). Only a "
            "coincidental 'bedrock' keyword match (unrelated to AI) and a predictive/rules-based ML fraud-"
            "scoring mention found -- no generative-AI evidence. Prior search found third-party media "
            "reporting that Games Workshop's CEO stated (in a half-yearly report, a document type not in this "
            "company's required source set) that the company has adopted a policy barring generative AI from "
            "design/creative processes; this specific statement was not located in either of the two full "
            "annual reports collected and is not coded as a finding, but is a plausible contributing "
            "explanation for the genuine null result found here."
        ),
    },
    "GAW_company_annual_report_previous_fy2023-24_2024-07.pdf": {
        "url": "https://assets.ctfassets.net/ost7hseic9hc/6nhjgj1BVPlaTocG6L4IbS/e42b72a50979ca58769b9e85e04ae79a/2023-24_accounts_-_final.pdf",
        "publication_date": "2024-07",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official games-workshop.com/ctfassets-hosted PDF). Same genuine null result as the current-year row.",
    },

    # --- British American Tobacco (scale-up batch 6) -----------------------------
    "BATS_company_annual_report_current_fy2025_2026-02.pdf": {
        "url": "https://www.bat.com/content/dam/batcom/global/main-nav/investors-and-reporting/reporting/combined-annual-and-sustainability-report/BAT_Annual_Report_2025.pdf",
        "publication_date": "2026-02",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": (
            "url is the direct_download_url (official bat.com PDF). Screened; only general AI/ML governance, "
            "risk-framework, agricultural-prediction and portfolio-investment mentions found -- no operational "
            "generative-AI use case. Genuine null result."
        ),
    },
    "BATS_company_annual_report_previous_fy2024_2025-02.pdf": {
        "url": "https://www.bat.com/content/dam/batcom/global/main-nav/investors-and-reporting/reporting/combined-annual-and-sustainability-report/BAT_Annual_Report_Form_on_20-F_2024.pdf",
        "publication_date": "2025-02",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official bat.com PDF). Same genuine null result as the current-year row.",
    },

    # --- IHG Hotels & Resorts (scale-up batch 6) ---------------------------------
    "IHG_company_annual_report_current_fy2025_2026-02.pdf": {
        "url": "https://www.ihgplc.com/~/media/Files/I/Ihg-Plc/investors/annual-report/2025/ihg-ar25-interactive.pdf",
        "publication_date": "2026-02",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official ihgplc.com PDF). Only general 'AI-powered technology'/embedding-AI strategic language found -- no explicit generative-AI/LLM/named-product use case within the AR itself.",
    },
    "IHG_company_annual_report_previous_fy2024_2025-02.pdf": {
        "url": "https://www.ihgplc.com/~/media/Files/I/Ihg-Plc/investors/annual-report/2024/ihg-ar-2024.pdf",
        "publication_date": "2025-02",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official ihgplc.com PDF). Same genuine null result as the current-year row.",
    },
    "IHG_company_press_release_n-a_2026-07-28.html": {
        "url": "https://www.ihgplc.com/en/news-and-media/news-releases/2026/ihg-hotels-and-resorts-launches-ai-conversational-search-across-its-digital-channels-transforming-the-guest-experience",
        "publication_date": "2026-07-28",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": (
            "url is the direct press-release URL (official ihgplc.com), fetch-verified this session. Describes "
            "a detailed, live/beta-stage 'AI Conversational Search' feature (natural-language trip planning) "
            "but never uses explicit generative-AI/LLM/foundation-model language for it -- only generic 'AI-"
            "powered'/'AI search' terminology, so it does not meet the project's explicit-GenAI-language "
            "requirement despite the feature's substance. Separately names a live, launched 'IHG app in "
            "ChatGPT' (a clearly identified generative-AI product per the project's naming test) but gives no "
            "concrete task/functionality description for it beyond context -- matches the "
            "'insufficient_operational_detail' rejection category (named GenAI product, no concrete qualifying "
            "task described). Neither element alone satisfies both the explicit-GenAI-language and concrete-"
            "task requirements together, so this is coded a genuine null result rather than operational, "
            "consistent with the project's precedent (e.g. Anglo American plc, Session 1) of not promoting "
            "thin/close-but-not-qualifying evidence."
        ),
    },

    # --- Glencore (scale-up batch 6) ---------------------------------------------
    "GLEN_company_annual_report_current_fy2025_2026-02.pdf": {
        "url": "https://www.glencore.com/.rest/api/v1/documents/static/9b103e11-72e7-40bf-ae7c-eabe57361522/GLEN-2025-Annual-Report.pdf",
        "publication_date": "2026-02",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": (
            "url is the direct_download_url (official glencore.com PDF). Every AI mention discusses AI only "
            "as an external commodity-demand driver (data-centre/energy buildout) or a generic cyber-security/"
            "deepfake risk -- no mention of Glencore's own operational GenAI use anywhere in either report. "
            "Genuine null result."
        ),
    },
    "GLEN_company_annual_report_previous_fy2024_2025-02.pdf": {
        "url": "https://www.glencore.com/.rest/api/v1/documents/static/7a4295e4-3674-45e9-94c4-7d7fb285faff/GLEN-2024-Annual-Report.pdf",
        "publication_date": "2025-02",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": (
            "CORRECTED URL: the initial news-page URL resolved to a 94KB HTML news article, not the report "
            "itself; the genuine direct static PDF was located via a follow-up WebFetch of glencore.com/"
            "publications this session. Same genuine null result as the current-year row."
        ),
    },

    # --- Kingfisher plc (scale-up batch 6) ---------------------------------------
    "KGF_company_annual_report_current_fy2024-25_2025-03.pdf": {
        "url": "https://www.kingfisher.com/~/media/Files/K/Kingfisher-Plc/Universal/investors/result-reports-presentation/2025/Kingfisher-Annual-Report-2024-25.pdf",
        "publication_date": "2025-03",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct_download_url (official kingfisher.com PDF). Corroborates KGF-OP-001 with a "
            "quantified figure ('c. 500k interactions with Hello Casto since launch in 2023') but this AR "
            "passage itself bundles Hello Casto with several unrelated non-GenAI initiatives, so is not the "
            "primary promoted source for the operational finding."
        ),
    },
    "KGF_company_annual_report_previous_fy2023-24_2024-03.pdf": {
        "url": "https://www.kingfisher.com/~/media/Files/K/Kingfisher-Plc/Universal/investors/result-reports-presentation/2024/kingfisher-annual-report-202324-pdf.pdf",
        "publication_date": "2024-03",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official kingfisher.com PDF). Only vague general-AI/governance language found in this report on its own -- no explicit GenAI use case in this document independent of the press release.",
    },
    "KGF_company_press_release_n-a_2023-11.html": {
        "url": "https://www.kingfisher.com/media/news/2023/kingfisher-launches-ai-powered-diy-assistant",
        "publication_date": "2023-11",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct press-release URL (official kingfisher.com), fetch-verified this session. "
            "Yielded one operational use case (KGF-OP-001, Hello Casto/Athena generative-AI DIY assistant), "
            "split out from a staging row that the automated engine mis-routed to rejected as webpage "
            "boilerplate."
        ),
    },

    # --- Airtel Africa (scale-up batch 9) -----------------------------------------
    "AAF_company_annual_report_current_fy2024-25_2025.pdf": {
        "url": "https://cdn-webportal.airtelstream.net/website/investor/main/pdf/AR2025/Airtel-Africa-plc-Annual-Report-and-Accounts-2025.pdf",
        "publication_date": "2025",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": (
            "url is the direct_download_url (official airtelstream.net PDF, Airtel Africa's own IR content "
            "domain). The 'Airtel AI Spam Alert Service' (SMS spam filtering, 1.5bn messages processed) is a "
            "predictive/classification AI system, not generative -- no explicit generative-AI/LLM language "
            "anywhere in the document. Genuine null result."
        ),
    },
    "AAF_company_annual_report_previous_fy2023-24_2024.pdf": {
        "url": "https://cdn-webportal.airtelstream.net/website/investor/main/pdf/annual-report/Annual-Report-and-Accounts-2024_FINAL.pdf",
        "publication_date": "2024",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official airtelstream.net PDF). Same genuine null result as the current-year row.",
    },

    # --- Beazley (scale-up batch 9) ------------------------------------------------
    "BEZ_company_annual_report_current_fy2025_2026-03.pdf": {
        "url": "https://www.beazley.com/globalassets/ir-documents/annual-reports/annual-report-2025/annual-report-and-accounts.pdf",
        "publication_date": "2026-03",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": (
            "CORRECTED URL: the initial guessed filename resolved to a 374KB HTML redirect page, not the "
            "report; the genuine direct PDF was located via a follow-up WebFetch this session. Only AI "
            "governance/risk-oversight discussion found (AI Steering Committee, AI Governance & Controls "
            "Committee) -- no concrete operational task/tool/user-group evidence. Genuine null result."
        ),
    },
    "BEZ_company_annual_report_previous_fy2024_2025-03.pdf": {
        "url": "https://www.beazley.com/globalassets/ir-documents/annual-reports/annual-report-2024/annual-report-2024.pdf",
        "publication_date": "2025-03",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official beazley.com PDF). Same genuine null result as the current-year row.",
    },

    # --- Howdens Joinery (scale-up batch 9) -----------------------------------------
    "HWDN_company_annual_report_current_fy2025_2026-02.pdf": {
        "url": "https://www.howdenjoinerygroupplc.com/docs/librariesprovider25/archives/annual-reports/2025-annual-report.pdf",
        "publication_date": "2026-02",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official howdenjoinerygroupplc.com PDF). Only AGM Q&A and risk-register mentions of AI/cyber found -- no operational GenAI evidence. Genuine null result.",
    },
    "HWDN_company_annual_report_previous_fy2024_2025-02.pdf": {
        "url": "https://www.howdenjoinerygroupplc.com/docs/librariesprovider25/archives/annual-reports/2024-annual-report.pdf",
        "publication_date": "2025-02",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official howdenjoinerygroupplc.com PDF). Same genuine null result as the current-year row.",
    },

    # --- Weir Group (scale-up batch 9) -----------------------------------------------
    "WEIR_company_annual_report_current_fy2025_2026-03.pdf": {
        "url": "https://www.global.weir/globalassets/investors/reporting-centre/2026/annual-report/weir-2025-annual-report.pdf",
        "publication_date": "2026-03",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": (
            "url is the direct_download_url (official global.weir PDF). One passage states 'Generative AI "
            "initiatives accelerated' but with no named tool, task, or user group -- confirmed via direct grep "
            "this is the only such mention in the document, insufficient to qualify as operational. References "
            "to Weir's Motion Metrics/SentianAI investees describe predictive/computer-vision process-"
            "optimisation AI, not generative. Genuine null result."
        ),
    },
    "WEIR_company_annual_report_previous_fy2024_2025-03.pdf": {
        "url": "https://www.global.weir/globalassets/investors/reporting-centre/2025/annual-report/weir-2024-annual-report.pdf",
        "publication_date": "2025-03",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official global.weir PDF). Same genuine null result as the current-year row.",
    },

    # --- Antofagasta plc (scale-up batch 10) ---------------------------------------
    "ANTO_company_annual_report_current_fy2025_2026-03.pdf": {
        "url": "https://www.antofagasta.co.uk/media/4905/49913-antofagasta-ar25-web-ready.pdf",
        "publication_date": "2026-03",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": (
            "url is the direct_download_url (official antofagasta.co.uk PDF). All AI mentions are predictive/"
            "classification/optimisation systems (SIRO grinding optimisation, Machine Vision equipment "
            "monitoring, desalination-plant scheduling) -- not generative. One passage mentions 'considering "
            "the progressive incorporation of generative artificial intelligence for operational support' but "
            "this is explicitly future/planned with no named tool or concrete task. Genuine null result."
        ),
    },
    "ANTO_company_annual_report_previous_fy2024_2025-03.pdf": {
        "url": "https://www.antofagasta.co.uk/media/4803/antofagasta-annual-report-2024-web-version-26-march-compressed_1.pdf",
        "publication_date": "2025-03",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official antofagasta.co.uk PDF). Same genuine null result as the current-year row.",
    },

    # --- DCC plc (scale-up batch 10) -------------------------------------------------
    "DCC_company_annual_report_current_fy2024-25_2025-05.pdf": {
        "url": "https://www.dcc.ie/~/media/Files/D/Dcc-Corp-v3/documents/investors/annual-and-sustainability-reports/2025/annual-report-2025.pdf",
        "publication_date": "2025-05",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct_download_url (official dcc.ie PDF). Yielded one governance finding (DCC-GOV-001, "
            "an 'Acceptable Use of Generative AI applications' employee policy) split out from an "
            "over-consolidated rejected row. No operational finding -- DCC's own AR explicitly states its "
            "internal AI platform favours 'practical, actionable AI solutions...rather than exploratory or "
            "generative AI technologies'."
        ),
    },
    "DCC_company_annual_report_previous_fy2023-24_2024-05.pdf": {
        "url": "https://www.dccenergy.com/~/media/Files/D/Dcc-Corp-v3/documents/investors/annual-and-sustainability-reports/2024/annual-report-2024.pdf",
        "publication_date": "2024-05",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official dccenergy.com PDF, a DCC plc-branded domain). Yielded one strategic finding (DCC-STR-001, the company's non-generative internal AI platform strategy).",
    },

    # --- Diploma (scale-up batch 10) -------------------------------------------------
    "DPLM_company_annual_report_current_fy2025_2025-11.pdf": {
        "url": "https://www.diplomaplc.com/media/5s3fi0yk/diploma-plc-annual-report-and-accounts-2025.pdf",
        "publication_date": "2025-11",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official diplomaplc.com PDF). Yielded one vague strategic finding (DPLM-STR-001, generic 'AI opportunities' mention) -- no operational GenAI evidence.",
    },
    "DPLM_company_annual_report_previous_fy2024_2024-11.pdf": {
        "url": "https://www.diplomaplc.com/media/vdyeuqza/diploma-2024-annual-report.pdf",
        "publication_date": "2024-11",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official diplomaplc.com PDF). Only a vague governance-adjacent mention found (DPLM-GOV-001) -- no operational GenAI evidence.",
    },

    # --- Investec (scale-up batch 10) -------------------------------------------------
    "INVP_company_annual_report_previous_fy2023-24_2024-07.pdf": {
        "url": "https://www.investec.com/content/dam/investor-relations/financial-information/group-financial-results/2024/Investec-plc-annual-report-March-2024.pdf",
        "publication_date": "2024-07",
        "document_review_status": "reviewed_evidence_found",
        "notes": (
            "url is the direct_download_url (official investec.com PDF). Only general AI/cyber risk mentions "
            "found in this document itself -- the qualifying GenAI evidence came from the separately-sourced "
            "Microsoft technology-partner case study. The FY2025 current-year AR could not be located (the "
            "URL pattern matching the FY2024 report returned HTTP 404, and a follow-up WebFetch to the "
            "investec.com landing page to find the exact filename returned HTTP 403); this single source row "
            "is marked manual_collection_required in the source-candidates file but does not block the "
            "company, since the FY2024 AR plus the Microsoft case study together provide substantial evidence."
        ),
    },
    "INVP_partner_partner_case_study_n-a.html": {
        "url": "https://www.microsoft.com/en/customers/story/1777785808385732889-investec-microsoft-teams-banking-and-capital-markets-en-united-kingdom",
        "publication_date": "unknown",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct case-study URL (official microsoft.com domain), fetch-verified this session, naming Investec specifically. Yielded one operational use case (INVP-OP-001, Microsoft Copilot for Sales, 900 UK bankers plus a rollout to 700 South African bankers, ~200 hours/year saved) split out from an over-consolidated staging row.",
    },

    # --- United Utilities (scale-up batch 10) -----------------------------------------
    "UU_company_annual_report_current_fy2024-25_2025-05.pdf": {
        "url": "https://www.unitedutilities.com/globalassets/documents/corporate-documents/united-utilites-plc-mar-25-v1.0-final---signed.pdf",
        "publication_date": "2025-05",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": (
            "url is the direct_download_url (official unitedutilities.com PDF). All AI mentions describe "
            "predictive/ML systems (Dynamic Network Management, leak-detection sensors) -- not generative. "
            "Genuine null result."
        ),
    },
    "UU_company_annual_report_previous_fy2023-24_2024-05.pdf": {
        "url": "https://www.unitedutilities.com/globalassets/documents/corporate-documents/31404-united-utilities-ar-2024.pdf",
        "publication_date": "2024-05",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": (
            "CORRECTED URL: the initial guessed path (missing a 'corporate-documents' segment) returned HTTP "
            "404; the genuine direct PDF was located via a follow-up search this session. Same genuine null "
            "result as the current-year row."
        ),
    },

    # --- Melrose Industries (scale-up batch 11) ---------------------------------------
    "MRO_company_annual_report_previous_fy2024_2025-03.pdf": {
        "url": "https://www.melroseplc.net/media/i32ndact/melrose_ar24.pdf",
        "publication_date": "2025-03",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": (
            "Current-year (FY2025) AR could not be located (404 on guessed path, 403 on landing page, only "
            "PDF found was a 41.7KB RNS notice, not the full report) and is left approval_status=pending in "
            "melrose-industries_source_candidates.csv -- not treated as a company blocker. All AI mentions in "
            "this previous-year AR are ordinary automation/robotics. Genuine null result."
        ),
    },

    # --- Spirax Group (scale-up batch 11) ----------------------------------------------
    "SPX_company_annual_report_current_fy2025_2026-03.pdf": {
        "url": "https://content.spiraxgroup.com/-/media/engineering/documents/results-and-agm-notices/2025/ara/spirax-group-plc-annual-report-2025.ashx?rev=4264817ad6cb42e7b009ed3640dc1b22",
        "publication_date": "2026-03",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official content.spiraxgroup.com PDF). Yielded one operational use case (SPX-OP-001, proprietary large-language-model tool 'MiM' for sales-engineer training/productivity, piloted with 200 then rolled out to 1,000+ sales colleagues).",
    },
    "SPX_company_annual_report_previous_fy2024_2025-03.pdf": {
        "url": "https://content.spiraxgroup.com/-/media/engineering/documents/results-and-agm-notices/2024/results/spirax-group-plc-annual-report-2024.ashx?rev=b72cd41f0c424b658d5fa502324b7dc2",
        "publication_date": "2025-03",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official content.spiraxgroup.com PDF). Corroborates SPX-OP-001 -- MiM described here as first developed in early 2024.",
    },

    # --- 3i (scale-up batch 11) --------------------------------------------------------
    "III_company_annual_report_previous_fy2023-24_2024-05.pdf": {
        "url": "https://www.3i.com/media/nnrkjwke/annual_report_and_accounts_2024.pdf",
        "publication_date": "2024-05",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": (
            "url is the direct_download_url (official 3i.com PDF). Yielded one strategic-capability-building "
            "finding (III-STR-001, CTO Forum session on enabling generative AI adoption in portfolio "
            "companies) but no operational GenAI deployment by 3i itself. Genuine null result for the "
            "operational dataset."
        ),
    },
    "III_company_annual_report_current_fy2024-25_2025-05.pdf": {
        "url": "https://www.3i.com/media/cxwbwcdw/3i-group-annual-report-2025-interactive.pdf",
        "publication_date": "2025-05",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official 3i.com PDF). All GenAI mentions here are governance/oversight-level (Group AI policy, AI steering group, Board/CTO GenAI briefings) -- no operational deployment. Genuine null result.",
    },

    # --- IG Group (scale-up batch 11) --------------------------------------------------
    "IGG_company_annual_report_current_fy2025-year-ended-31-dec-2025_2026.pdf": {
        "url": "https://www.iggroup.com/~/media/Files/I/IG-Group/documents/investors/financial-results/results-reports-and-presentations/2026/annual-report-31-December-2025.pdf",
        "publication_date": "2026",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": (
            "url is the direct_download_url (official iggroup.com PDF). Describes a live customer-facing 'AI "
            "chatbot' and an 'AI-powered engagement tool', but neither is described using generative-AI/LLM/"
            "named-product language anywhere nearby (confirmed via direct grep of source text) -- matches the "
            "IHG Hotels & Resorts precedent (batch 6) and does not meet Core Rule 3. Genuine null result for "
            "the operational dataset; yielded governance (AI Governance Committee) and strategic "
            "(AI-powered threat detection) findings instead."
        ),
    },
    "IGG_company_annual_report_previous_fy2024-year-ended-31-may-2024_2024.pdf": {
        "url": "https://www.iggroup.com/~/media/Files/I/IG-Group/documents/investors/financial-results/results-reports-and-presentations/2024/ig-group-annual-report-2024.pdf",
        "publication_date": "2024",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official iggroup.com PDF). All AI mentions here are governance/oversight-level (Board AI training, AI/ML risk-register entries). Genuine null result.",
    },

    # --- Fresnillo plc (scale-up batch 11) ---------------------------------------------
    "FRES_company_annual_report_current_fy2025_2026-03.pdf": {
        "url": "https://www.fresnilloplc.com/media/jwggz1pk/fresnillo-annual-report-2025-web.pdf",
        "publication_date": "2026-03",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": (
            "url is the direct_download_url (official fresnilloplc.com PDF). All AI mentions are vague general "
            "AI references (AI-driven datacentre demand commentary, computer-vision driver-fatigue detection, "
            "cybersecurity AI/ML monitoring, and a forward-looking risk-register mention of 'Generative "
            "Artificial Intelligence' as a named risk/opportunity category, not a deployed tool) or ordinary "
            "automation. Genuine null result."
        ),
    },
    "FRES_company_annual_report_previous_fy2024_2025-03.pdf": {
        "url": "https://www.fresnilloplc.com/media/gf3fqvci/fresnillo-financial-statements-ar24-web.pdf",
        "publication_date": "2025-03",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": (
            "url is the direct_download_url (official fresnilloplc.com PDF). Only the 'Financial Statements' "
            "sectioned component of the FY2024 report could be located (no single combined AR file found), "
            "same sectioning limitation as Babcock/Howdens in earlier batches. Genuine null result."
        ),
    },

    # --- Aberdeen Group (scale-up batch 12) --------------------------------------------
    "ABDN_company_annual_report_current_fy2025_2026-03.pdf": {
        "url": "https://www.aberdeeninvestments.com/docs?documentid=AA-110326-205370-24",
        "publication_date": "2026-03",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is a document-viewer gateway URL (official aberdeeninvestments.com); downloaded successfully despite WebFetch returning HTTP 500 on the same URL (a rendered-fetch limitation, not a bad link). All AI mentions are vague/general (predictive email filtering, AI-related market commentary, ordinary automation, AI risk/governance oversight). Genuine null result.",
    },
    "ABDN_company_annual_report_previous_fy2024_2025-03.pdf": {
        "url": "https://www.aberdeenplc.com/docs?documentid=AA-040325-190118-23",
        "publication_date": "2025-03",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is a document-viewer gateway URL (official aberdeenplc.com); downloaded successfully. Same genuine null result as the current-year row.",
    },

    # --- St. James's Place (scale-up batch 12) -----------------------------------------
    "STJ_company_annual_report_current_fy2025_2026.pdf": {
        "url": "https://www.sjp.co.uk/sites/sjp-corp/files/SJP/shareholders/reports-presentations-webcasts/2026/SJP_AR_2025.pdf",
        "publication_date": "2026",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official sjp.co.uk PDF). Describes 'AI tools' that 'respond to questions on our advice framework' for advisers, but never uses generative-AI/LLM/named-product language anywhere nearby -- matches the IHG Hotels & Resorts (batch 6) / IG Group (batch 11) precedent. Genuine null result.",
    },
    "STJ_company_annual_report_previous_fy2024_2025.pdf": {
        "url": "https://www.sjp.co.uk/sites/sjp-corp/files/SJP/shareholders/2024-in-review/SJP_AR_2024_Strategic_Report.pdf",
        "publication_date": "2025",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official sjp.co.uk PDF). Only the 'Strategic Report' sectioned component of the FY2024 report could be located (no single combined AR file found, unlike FY2025), same sectioning limitation as Fresnillo/Babcock/Howdens in earlier batches. Same genuine null result as the current-year row.",
    },

    # --- Land Securities (scale-up batch 12) -------------------------------------------
    "LAND_company_annual_report_current_fy2024-25_2025.pdf": {
        "url": "https://content.landsec.com/media/0ilhb1mo/annual_report_2025_interactive_0_0.pdf",
        "publication_date": "2025",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official content.landsec.com PDF). The one named AI product (Brainbox AI, a 12-month HVAC-control trial) is predictive building-control, not generative. Genuine null result.",
    },
    "LAND_company_annual_report_previous_fy2023-24_2024.pdf": {
        "url": "https://content.landsec.com/media/ayijkjmt/landsec_ar2024_interactive_final_0.pdf",
        "publication_date": "2024",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official content.landsec.com PDF). Same genuine null result as the current-year row.",
    },

    # --- Endeavour Mining (scale-up batch 12) ------------------------------------------
    "EDV_company_annual_report_current_fy2025_2026-03-05.pdf": {
        "url": "https://edv-14806-s3.s3.eu-west-2.amazonaws.com/files/7017/7306/8914/EDV_-_2025_Annual_Report.pdf",
        "publication_date": "2026-03-05",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official endeavourmining.com S3-hosted PDF). AI mentions describe predictive exploration-targeting tools, not generative. Genuine null result.",
    },
    "EDV_company_annual_report_previous_fy2024_2025-03-06.pdf": {
        "url": "https://edv-14806-s3.s3.eu-west-2.amazonaws.com/files/7617/4124/4823/EDV_AnnualReport2024_Website.pdf",
        "publication_date": "2025-03-06",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official endeavourmining.com S3-hosted PDF). One 'generative AI'/'foundation models' mention describes a Non-Executive Director's own outside company (Earth Dynamics.ai), not Endeavour Mining's own use -- excluded per Core Rule 1. Genuine null result.",
    },

    # --- Metlen Energy & Metals (scale-up batch 12) ------------------------------------
    "MTLN_company_annual_report_current_fy2025_2026.pdf": {
        "url": "https://www.metlen.com/media/jf0azh1w/metlen_iar25-signed.pdf",
        "publication_date": "2026",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official metlen.com PDF). Yielded one operational use case (MTLN-OP-001, 'Avokado CORTEX', a named GenAI digital assistant for B2B customers, offered by METLEN's own technology subsidiary Avokado).",
    },
    "MTLN_company_annual_report_previous_fy2024_2025.pdf": {
        "url": "https://www.metlen.com/media/pooiu4em/iar_2024_metlen_en.pdf",
        "publication_date": "2025",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official metlen.com PDF). Corroborates MTLN-OP-001 -- Avokado CORTEX described identically here as in the FY2025 report.",
    },

    # --- Alliance Witan (session 4) -----------------------------------------------------
    "ALW_company_annual_report_current_fy2025_2026-03.pdf": {
        "url": "https://www.alliancewitan.com/api/document/zhcddtp5/4041-alliance-witan-annual-report_interactive.pdf",
        "publication_date": "2026-03",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official alliancewitan.com PDF). All AI mentions are investment commentary on the AI theme in markets/portfolio holdings, not the Trust's own use. Genuine null result.",
    },
    "ALW_company_annual_report_previous_fy2024_2025-03.pdf": {
        "url": "https://www.alliancewitan.com/api/document/nouk0hpg/3510-alliance-witan-annual-report_interactive_opens-full-screen.pdf",
        "publication_date": "2025-03",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official alliancewitan.com PDF). Same genuine null result as the current-year row.",
    },

    # --- F&C Investment Trust (session 4) -----------------------------------------------
    "FCIT_company_annual_report_current_fy2025_2026-03.pdf": {
        "url": "https://docs.columbiathreadneedle.com/documents/FandC%20-%20Annual%20Report%20and%20Accounts.pdf",
        "publication_date": "2026-03",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official docs.columbiathreadneedle.com PDF). All AI mentions are investment commentary on the AI theme or stewardship engagement with portfolio companies (e.g. Microsoft) about their AI governance -- not F&C's own use. Genuine null result.",
    },

    # --- Intermediate Capital Group (session 4) -----------------------------------------
    "ICG_company_annual_report_current_fy2024-25_2025-06.pdf": {
        "url": "https://www.icgam.com/wp-content/uploads/2025/06/ICG_AR2025_Interactive_Final.pdf",
        "publication_date": "2025-06",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official icgam.com PDF). Yielded one governance finding (ICG-GOV-001, the Risk Committee's own governance focus on generative AI); no operational deployment described. Genuine null result for the operational dataset.",
    },
    "ICG_company_annual_report_previous_fy2023-24_2024-06.pdf": {
        "url": "https://www.icgam.com/wp-content/uploads/2024/06/icg-annual-report-and-accounts-2024.pdf",
        "publication_date": "2024-06",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official icgam.com PDF). All AI mentions are vague governance/risk-oversight discussion or a NED's outside AI-related directorships. Genuine null result.",
    },

    # --- Lion Finance Group (session 4) -------------------------------------------------
    "BGEO_company_annual_report_current_fy2025_2026-02.pdf": {
        "url": "https://ramad.bog.ge/s3/BogGroup/49872-Lion-Finance-Group-AR-25.pdf",
        "publication_date": "2026-02",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official ramad.bog.ge, Bank of Georgia Group infrastructure). Yielded two operational use cases (BGEO-OP-001, Georgian-language Generative AI customer chatbot; BGEO-OP-002, enterprise AI platform for employee-built custom AI assistants), one new governance finding (BGEO-GOV-007, a named Generative AI policy), and multiple existing governance/strategic findings.",
    },
    "BGEO_company_annual_report_previous_fy2024_2025-04.pdf": {
        "url": "https://ramad.bog.ge/s3/BogGroup/Lion-Finance-Group-PLC-Annual-Report-2024.pdf",
        "publication_date": "2025-04",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official ramad.bog.ge PDF). Corroborates both BGEO-OP-001 and BGEO-OP-002 -- describes the prior-generation chatbot and the 'Strategic GenAI Initiatives for 2025' that were realised in the current-year report.",
    },

    # --- LondonMetric Property (session 4) ----------------------------------------------
    "LMP_company_annual_report_current_fy2024-25_2025-06.pdf": {
        "url": "https://www.londonmetric.com/~/media/Files/L/londonmetric/results-and-presentations/report/lmp-annual-report-2025.pdf",
        "publication_date": "2025-06",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official londonmetric.com PDF). All AI mentions are vague Board-strategy-day/cyber-risk references. Genuine null result.",
    },
    "LMP_company_annual_report_previous_fy2023-24_2024-06.pdf": {
        "url": "https://www.londonmetric.com/~/media/Files/L/londonmetric/results-and-presentations/report/london-metric-annual-report-2024.pdf",
        "publication_date": "2024-06",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official londonmetric.com PDF). Same genuine null result as the current-year row.",
    },

    # --- Pershing Square Holdings (session 4) -------------------------------------------
    "PSH_company_annual_report_current_fy2025_2026-02.pdf": {
        "url": "https://assets.pershingsquareholdings.com/wp-content/uploads/2026/02/18175039/Pershing-Square-Holdings-Ltd.-2025-Annual-Report.pdf",
        "publication_date": "2026-02",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official pershingsquareholdings.com PDF). All AI mentions are investment commentary about portfolio holdings (AWS) or governance-committee engagement with portfolio companies' AI ethics -- not PSH's own use. Genuine null result.",
    },
    "PSH_company_annual_report_previous_fy2024_2025-03.pdf": {
        "url": "https://pershingsquareholdings.com/wp-content/uploads/2025/07/Pershing-Square-Holdings-Ltd.-2024-Annual-Report-1.pdf",
        "publication_date": "2025-03",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official pershingsquareholdings.com PDF). Same genuine null result as the current-year row.",
    },

    # --- Polar Capital Technology Trust (session 4) -------------------------------------
    "PCT_company_annual_report_current_fy-ended-2026-04-30_2026-07.pdf": {
        "url": "https://www.polarcapitaltechnologytrust.co.uk/static/literature/PCTT_Annual_Report_2026.pdf",
        "publication_date": "2026-07",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official polarcapitaltechnologytrust.co.uk PDF). Extremely AI-keyword-dense (a technology-sector investment trust) but every passage is the Investment Manager's market analysis/investment thesis about the AI sector -- not PCT's own operational or governance use. Genuine null result.",
    },
    "PCT_company_annual_report_previous_fy-ended-2025-04-30_2025-07.pdf": {
        "url": "https://www.pctannualhighlights.co.uk/static/literature/PCTT_Annual_Report_2025.pdf",
        "publication_date": "2025-07",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official pctannualhighlights.co.uk PDF). Same genuine null result as the current-year row.",
    },

    # --- Scottish Mortgage Investment Trust (session 4) ---------------------------------
    "SMT_company_annual_report_current_fy-ended-2025-03-31_2025-05.pdf": {
        "url": "https://media.bailliegifford.com/mws/qhzbpw0h/20250529152947_scottish-mortgage-ar-2025-interactive-final.pdf",
        "publication_date": "2025-05",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official media.bailliegifford.com PDF). All AI mentions describe portfolio holdings (Meta, Cloudflare, the 'Global AI Opportunities Fund') and their own AI adoption -- not Scottish Mortgage's own use. Genuine null result.",
    },
    "SMT_company_annual_report_previous_fy-ended-2024-03-31_2024-06.pdf": {
        "url": "https://media.bailliegifford.com/mws/jhkjrkq4/20240603113752_scottish-mortgage-annual-report-310324.pdf",
        "publication_date": "2024-06",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official media.bailliegifford.com PDF). Same genuine null result as the current-year row.",
    },

    # --- Segro (session 4) ---------------------------------------------------------------
    "SGRO_company_annual_report_current_fy2025_2026-02.pdf": {
        "url": "https://www.segro.com/media/kbshtxbq/segro_annual-report-accounts-2025.pdf",
        "publication_date": "2026-02",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official segro.com PDF). Yielded one operational use case (SGRO-OP-001, Microsoft Copilot rolled out to all employees).",
    },
    "SGRO_company_annual_report_previous_fy2024_2025-02.pdf": {
        "url": "https://www.segro.com/media/1h4c1331/segro_ar24_interactive.pdf",
        "publication_date": "2025-02",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official segro.com PDF). The Copilot rollout is not mentioned in this earlier report -- a FY2025 initiative only.",
    },

    # --- Standard Life (session 4) --------------------------------------------------------
    "SDLF_company_annual_report_current_fy2025_2026-03-16.pdf": {
        "url": "https://library.standardlife.co.uk/annual-report-and-accounts-2025-spread.pdf",
        "publication_date": "2026-03-16",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official library.standardlife.co.uk PDF). Yielded strategic (Board's own AI-strategy oversight) and governance (Internal Audit's own AI-strategy focus) findings; no operational deployment described. Genuine null result for the operational dataset.",
    },
    "SDLF_company_annual_report_previous_fy2024_2025-03.pdf": {
        "url": "https://www.thephoenixgroup.com/media/lhih1hpj/phoenix_group_annual_report_and_accounts_2024.pdf",
        "publication_date": "2025-03",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official thephoenixgroup.com PDF, published under the company's former name Phoenix Group Holdings plc). Corroborates SDLF-GOV-002 -- Internal Audit's AI-strategy focus described identically here as in the FY2025 report.",
    },

    # --- Tritax Big Box REIT (session 4) --------------------------------------------------
    "BBOX_company_annual_report_current_fy2025_2026-02.pdf": {
        "url": "https://www.tritaxbigbox.co.uk/media/4n0brecg/tritax-big-box-reit-plc-annual-report-2025.pdf",
        "publication_date": "2026-02",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official tritaxbigbox.co.uk PDF). Yielded one governance finding (BBOX-GOV-001, the Board's own risk-oversight of AI/robotics impact on logistics); no operational deployment described. Genuine null result for the operational dataset.",
    },
    "BBOX_company_annual_report_previous_fy2024_2025-02.pdf": {
        "url": "https://www.tritaxbigbox.co.uk/media/cv0lcio0/tritax-big-box-reit-plc-annual-report-2024.pdf",
        "publication_date": "2025-02",
        "document_review_status": "reviewed_no_relevant_evidence",
        "notes": "url is the direct_download_url (official tritaxbigbox.co.uk PDF). All AI mentions are ordinary automation (warehouse/robotics), no distinct governance content this year.",
    },

    # --- BAE Systems (manual-browser resolution pass) -----------------------------------
    "BA_company_annual_report_current_fy2025.pdf": {
        "url": "https://investors.baesystems.com/dam/jcr:105fe9f2-cff7-4960-9d99-956aba996540/BAE-Systems-Annual-Report-2025.2026-03-24-10-33-48.pdf",
        "publication_date": "2026-03-24",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official investors.baesystems.com PDF). Previously blocked_manual_browser (Incapsula bot protection); resolved this pass -- the same URL downloaded a genuine, correctly-sized 11.5MB PDF via 03_download_sources.py (the site's protection status appears to have changed, or the prior block was intermittent). Yielded one operational use case (BA-OP-001, LLM/generative-AI natural-language drone command and self-reconfiguration).",
    },
    "BA_company_annual_report_previous_fy2024.pdf": {
        "url": "https://investors.baesystems.com/dam/jcr:f57706a5-0a28-441a-8829-0e0c213436c1/BAE-Systems-Annual-Report-2024.2025-04-29-16-28-37.pdf",
        "publication_date": "2025-04-29",
        "document_review_status": "reviewed_evidence_found",
        "notes": "url is the direct_download_url (official investors.baesystems.com PDF). Resolved this pass alongside the current-year report. Yielded two further operational use cases (BA-OP-002, Typhoon AI maintenance assistant; BA-OP-003, operationalised AI cyber-threat-insight system for customers) and one governance finding.",
    },
}

SOURCE_CANDIDATE_TO_FILENAME = {
    "Tesco PLC Annual Report and Financial Statements 2025": "TSCO_company_annual_report_current_fy2025.pdf",
    "Tesco PLC Annual Report and Financial Statements 2024": "TSCO_company_annual_report_previous_fy2024.pdf",
    "Making a positive impact: Tesco PLC Sustainability Report 2024/25":
        "TSCO_company_sustainability_or_esg_report_fy2024-25.pdf",
    "Tesco Media Creative Studio (AI-powered ad creation tool for brands)":
        "TSCO_partner_press_release_tesco-media-creative-studio-ai-powered-ad-creation-tool-for_2025-10-09.html",
    "Adobe & Tesco enter strategic AI partnership to personalise experiences and reward loyalty for Tesco's customers":
        "TSCO_partner_press_release_adobe-tesco-enter-strategic-ai-partnership-to-personalise-ex_2026-04-13.html",
    "BT Group plc Annual Report 2025": "BT.A_company_annual_report_current_fy2025.pdf",
    "BT Group plc Annual Report 2024": "BT.A_company_annual_report_previous_fy2024.pdf",
    "ESG Addendum to the BT Group plc Annual Report 2025": "BT.A_company_sustainability_or_esg_report_fy2025.pdf",
    "BT Group's Digital Unit launches 'GenAI Gateway' platform, powered by AWS, accelerating the company's safe adoption of generative AI at scale":
        "BT.A_company_press_release_bt-group-s-digital-unit-launches-genai-gateway-platform-powe_2024-09-24.html",
    "BT Group leans on AI to transform customer service experience":
        "BT.A_company_press_release_bt-group-leans-on-ai-to-transform-customer-service-experienc_2024-12-12.html",
    "Writing and Maintaining 2 Million Lines a Year Using Amazon Q Developer with BT Group":
        "BT.A_partner_partner_case_study_writing-and-maintaining-2-million-lines-a-year-using-amazon.html",
    "Rolls-Royce Holdings plc Annual Report 2025": "RR_company_annual_report_current_fy2025.pdf",
    "Rolls-Royce Holdings plc Annual Report 2024": "RR_company_annual_report_previous_fy2024.pdf",
    "Rolls-Royce: Harnessing the Power of Databricks for Image Generation":
        "RR_partner_partner_case_study_rolls-royce-harnessing-the-power-of-databricks-for-image-gen_2024-08-08.html",
    "Rolls-Royce saves millions in cost avoidance with Microsoft Cloud for Manufacturing":
        "RR_partner_partner_case_study_rolls-royce-saves-millions-in-cost-avoidance-with-microsoft_2025-04-01.html",
    # --- Experian (Batch 1) --------------------------------------------------
    "Experian Annual Report 2026 (year ended 31 March 2026)": "EXPN_company_annual_report_current_fy2026.pdf",
    "Experian Accelerates Migration to AWS to Drive Innovation with Generative AI":
        "EXPN_company_press_release_experian-accelerates-migration-to-aws-to-drive-innovation-wi_2025-06-19.html",
    "New AI-Powered Experian Assistant for Model Risk Management Streamlines and Accelerates Governance Processes":
        "EXPN_company_press_release_new-ai-powered-experian-assistant-for-model-risk-management_2025-07-31.html",
    "Experian brings trusted agentic AI to financial services with the launch of Agent Operating System (TM)":
        "EXPN_company_press_release_experian-brings-trusted-agentic-ai-to-financial-services-wit_2026-06-02.html",
    # --- Rio Tinto (Batch 1) ---------------------------------------------------
    "Rio Tinto 2025 Annual Report": "RIO_company_annual_report_current_fy2025.pdf",
    "Rio Tinto 2024 Annual Report": "RIO_company_annual_report_previous_fy2024.pdf",
    "Using Artificial Intelligence and data science for better operations":
        "RIO_company_strategy_or_technology_webpage_using-artificial-intelligence-and-data-science-for-better-op_2024-07-25.html",
    # --- Admiral Group (Batch 1) -------------------------------------------------
    "Admiral Selects Google Cloud to Accelerate Innovative Customer Experiences":
        "ADM_partner_partner_case_study_admiral-selects-google-cloud-to-accelerate-innovative-custom_2024-02-14.html",
    # --- Informa (Batch 1) ----------------------------------------------------
    "Informa Annual Report 2025": "INF_company_annual_report_current_fy2025.pdf",
    "Informa Annual Report 2024": "INF_company_annual_report_previous_fy2024.pdf",
    "Informa Sustainability Report 2025": "INF_company_sustainability_or_esg_report_fy2025.pdf",
    # --- Diageo (scale-up batch loop 2) ---------------------------------------
    "Diageo Annual Report 2025": "DGE_company_annual_report_current_fy2025.pdf",
    "Diageo Annual Report 2024": "DGE_company_annual_report_previous_fy2024.pdf",
    "Diageo unveils its First Bottle Personalisation Experience Fuelled by Generative AI":
        "DGE_company_press_release_diageo-unveils-its-first-bottle-personalisation-experience-f_2024-07-23.html",
    # --- National Grid plc (scale-up batch loop 2) ----------------------------
    "National Grid plc Annual Report and Accounts 2025/26": "NG_company_annual_report_current_fy2025-26.pdf",
    "National Grid plc Annual Report and Accounts 2024/25": "NG_company_annual_report_previous_fy2024-25.pdf",
    # --- Shell plc (scale-up loop 3, Track B unblocked) -----------------------
    "Shell plc Annual Report and Accounts 2025": "SHEL_company_annual_report_current_fy2025_2026-03-12.pdf",
    "Shell plc Annual Report and Accounts 2024": "SHEL_company_annual_report_previous_fy2024.pdf",
    "SparkCognition and Shell Announce a Technology Collaboration Aimed at Accelerating the Pace of Exploration Through the Use of Generative AI":
        "SHEL_partner_partner_case_study_sparkcognition-and-shell-announce-a-technology-collaboration_2023-05-17.html",
    # --- HSBC (scale-up loop 3, Track B unblocked) ----------------------------
    "HSBC Holdings plc Annual Report and Accounts 2025": "HSBA_company_annual_report_current_fy2025.pdf",
    "HSBC Holdings plc Annual Report and Accounts 2024": "HSBA_company_annual_report_previous_fy2024.pdf",
    "HSBC and Google Cloud announce transformative AI banking partnership":
        "HSBA_company_press_release_hsbc-and-google-cloud-announce-transformative-ai-banking-par_2026-06-17.html",
    "HSBC and Mistral AI join forces to accelerate AI adoption across global bank":
        "HSBA_company_press_release_hsbc-and-mistral-ai-join-forces-to-accelerate-ai-adoption-ac_2025-12-01.html",
    # --- GSK plc (scale-up loop 3) ---------------------------------------------
    "GSK Annual Report 2025": "GSK_company_annual_report_current_fy2025.pdf",
    "GSK Annual Report 2024": "GSK_company_annual_report_previous_fy2024.pdf",
    # --- RELX (scale-up loop 3) -------------------------------------------------
    "RELX 2025 Annual Report": "REL_company_annual_report_current_fy2025.pdf",
    "RELX 2024 Annual Report": "REL_company_annual_report_previous_fy2024.pdf",
    "How RELX is adopting generative AI":
        "REL_company_strategy_or_technology_webpage_how-relx-is-adopting-generative-ai_2026-03.html",
    # --- Next plc (scale-up loop 3) ---------------------------------------------
    "Next plc Annual Report & Accounts January 2026": "NXT_company_annual_report_current_fy2025-26.pdf",
    "Next plc Annual Report & Accounts January 2025": "NXT_company_annual_report_previous_fy2024-25.pdf",
    # --- Vodafone Group (scale-up batch loop 2) -------------------------------
    "Vodafone Group Plc Annual Report on Form 20-F 2025": "VOD_company_annual_report_current_fy2025.pdf",
    "Meet SuperTOBi -- Vodafone's new Generative AI virtual assistant now serving customers in multiple countries":
        "VOD_company_press_release_meet-supertobi-vodafone-s-new-generative-ai-virtual-assistan_2024-07-04.html",
    # --- Legal & General (scale-up batch loop 2) ------------------------------
    "Legal & General Group Plc Annual Report and Accounts 2025": "LGEN_company_annual_report_current_fy2025.pdf",
    "Legal & General Group Plc Annual Report and Accounts 2024": "LGEN_company_annual_report_previous_fy2024.pdf",
    "L&G expands Microsoft collaboration to accelerate AI enablement and transform customer experience":
        "LGEN_company_press_release_l-g-expands-microsoft-collaboration-to-accelerate-ai-enablem_2026-06-16.html",
    # --- Reckitt (scale-up batch loop 2) ---------------------------------------
    "Reckitt Annual Report and Accounts 2025": "RKT_company_annual_report_current_fy2025.pdf",
    "Reckitt's First GenAI Results Demonstrate Changing Face of Marketing During Cannes Lions International Festival of Creativity":
        "RKT_company_press_release_reckitt-s-first-genai-results-demonstrate-changing-face-of-m_2024-06-21.html",
    # --- Croda International (scale-up batch loop 2) --------------------------
    "Croda Annual Report 2025": "CRDA_company_annual_report_current_fy2025.pdf",
    "Croda Annual Report & Accounts 2024": "CRDA_company_annual_report_previous_fy2024.pdf",

    # --- Whitbread (scale-up loop 4) ----------------------------------------
    "Whitbread PLC Annual Report and Accounts 2024/25": "WTB_company_annual_report_current_fy2024-25_2025-05.pdf",
    "Whitbread PLC Annual Report and Accounts 2023/24": "WTB_company_annual_report_previous_fy2023-24_2024-05.pdf",
    "Whitbread PLC Environmental, Social and Governance Report 2024/25 (Force for Good)":
        "WTB_company_sustainability_or_esg_report_fy2024-25_2025-05.pdf",

    # --- Barratt Redrow (scale-up loop 4) -----------------------------------
    "Barratt Redrow plc Annual Report and Accounts 2025": "BTRW_company_annual_report_current_fy2025_2025.pdf",
    "Barratt Redrow plc (Barratt Developments plc) Annual Report and Accounts 2024":
        "BTRW_company_annual_report_previous_fy2024_2024.pdf",

    # --- London Stock Exchange Group (scale-up loop 4) ----------------------
    "London Stock Exchange Group plc Annual Report 2025": "LSEG_company_annual_report_current_fy2025_2026-02.pdf",
    "London Stock Exchange Group plc Annual Report 2024": "LSEG_company_annual_report_previous_fy2024_2025-04.pdf",
    "LSEG and Microsoft transform access to AI-ready financial data in customer workflows":
        "LSEG_company_press_release_n-a_2025-10-13.html",
    "LSEG announces new collaboration with OpenAI": "LSEG_company_press_release_n-a_2025-12.html",
    "From interoperability to agents: Powering financial workflows with AI":
        "LSEG_company_official_case_study_n-a.html",

    # --- Smiths Group (scale-up loop 4) -------------------------------------
    "Smiths Group plc Annual Report & Accounts FY2025": "SMIN_company_annual_report_current_fy2025_2025-09.pdf",
    "Smiths Group plc Annual Report FY2024 -- Overview and Strategic Report":
        "SMIN_company_annual_report_previous_fy2024_2024-09.pdf",

    # --- British Land (scale-up loop 4) -------------------------------------
    "British Land Annual Report and Accounts 2026": "BLND_company_annual_report_current_fy2025-26_2026-05.pdf",
    "British Land Annual Report and Accounts 2025 (Strategic Report)":
        "BLND_company_annual_report_previous_fy2024-25_2025-05.pdf",

    # --- Barclays (scale-up batch 1) ----------------------------------------
    "Barclays PLC Annual Report 2025": "BARC_company_annual_report_current_fy2025_2025.pdf",
    "Barclays PLC Annual Report 2024": "BARC_company_annual_report_previous_fy2024_2024.pdf",

    # --- Aviva (scale-up batch 1) -------------------------------------------
    "Aviva plc Annual Report and Accounts 2025": "AV_company_annual_report_current_fy2025_2026-03.pdf",
    "Aviva plc Annual Report and Accounts 2024": "AV_company_annual_report_previous_fy2024_2025.pdf",

    # --- Halma plc (scale-up batch 1) ---------------------------------------
    "Halma plc Annual Report and Accounts 2025": "HLMA_company_annual_report_current_fy2025_2025.pdf",
    "Halma plc Annual Report and Accounts 2024": "HLMA_company_annual_report_previous_fy2024_2024.pdf",

    # --- Severn Trent (scale-up batch 1) ------------------------------------
    "Severn Trent Plc Annual Report and Accounts 2025 (Strategic Report)":
        "SVT_company_annual_report_current_fy2025_2025.pdf",
    "Severn Trent Plc Annual Report and Accounts 2024": "SVT_company_annual_report_previous_fy2024_2024.pdf",

    # --- Marks & Spencer (scale-up batch 2) ---------------------------------
    "M&S Annual Report and Financial Statements 2025": "MKS_company_annual_report_current_fy2024-25_2025-05.pdf",
    "M&S Annual Report 2024": "MKS_company_annual_report_previous_fy2023-24_2024-06.pdf",
    "M&S gives every Store Manager and every Store Support Centre colleague latest AI tools with 11,000 Microsoft 365 Copilot licenses":
        "MKS_company_press_release_n-a_2026-03-25.html",

    # --- Standard Chartered (scale-up batch 2) ------------------------------
    "Standard Chartered PLC Annual Report 2025": "STAN_company_annual_report_current_fy2025_2026-02.pdf",
    "Standard Chartered PLC Annual Report 2024": "STAN_company_annual_report_previous_fy2024_2025-02.pdf",
    "Artificial intelligence | Standard Chartered": "STAN_company_strategy_or_technology_webpage_n-a.html",

    # --- Prudential plc (scale-up batch 2) ----------------------------------
    "Prudential plc Annual Report 2025": "PRU_company_annual_report_current_fy2025_2026-03.pdf",
    "Prudential plc Annual Report 2024": "PRU_company_annual_report_previous_fy2024_2025.pdf",
    "Prudential Pioneers Use of Generative AI for Faster and More Frictionless Medical Claims, in Global-first Partnership with Google Cloud":
        "PRU_company_press_release_n-a_2024-10-24.html",

    # --- International Airlines Group (scale-up batch 2) --------------------
    "IAG Annual Report and Accounts 2025": "IAG_company_annual_report_current_fy2025_2025.pdf",
    "IAG Annual Report and Accounts 2024": "IAG_company_annual_report_previous_fy2024_2024.pdf",

    # --- NatWest Group (scale-up batch 3) -----------------------------------
    "NatWest Group plc 2025 Annual Report and Accounts": "NWG_company_annual_report_current_fy2025_2026-02.pdf",
    "NatWest Group plc 2024 Annual Report and Accounts": "NWG_company_annual_report_previous_fy2024_2025-03.pdf",
    "Deploying new generative AI technology to support our colleagues | NatWest Group":
        "NWG_company_press_release_n-a_2025-04.html",

    # --- Persimmon (scale-up batch 3) ---------------------------------------
    "Persimmon Plc Annual Report 2025": "PSN_company_annual_report_current_fy2025_2025.pdf",
    "Persimmon Plc Annual Report 2024": "PSN_company_annual_report_previous_fy2024_2024.pdf",

    # --- SSE plc (scale-up batch 3) ------------------------------------------
    "SSE plc Annual Report 2025": "SSE_company_annual_report_current_fy2025_2025-06.pdf",
    "SSE plc Annual Report 2024": "SSE_company_annual_report_previous_fy2024_2024.pdf",
    "SSE creates a compliant, nuanced virtual assistant using Microsoft Copilot Studio and Azure OpenAI | Microsoft Customer Stories":
        "SSE_partner_partner_case_study_n-a.html",

    # --- Auto Trader Group (scale-up batch 3) --------------------------------
    "Auto Trader Group plc Annual Report 2025": "AUTO_company_annual_report_current_fy2025_2025-05.pdf",
    "Auto Trader Group plc Annual Report and Financial Statements 2024":
        "AUTO_company_annual_report_previous_fy2024_2024-07.pdf",

    # --- Intertek (scale-up batch 3) ------------------------------------------
    "Intertek Annual Report & Accounts 2025 (Strategic Report, Combined)":
        "ITRK_company_annual_report_current_fy2025_2026.pdf",
    "Intertek Annual Report & Accounts 2024 (Strategic Report)":
        "ITRK_company_annual_report_previous_fy2024_2024.pdf",

    # --- Anglo American plc (scale-up batch 4) --------------------------------
    "Anglo American plc Integrated Annual Report 2025": "AAL_company_annual_report_current_fy2025_2026-03.pdf",
    "Anglo American plc Integrated Annual Report 2024": "AAL_company_annual_report_previous_fy2024_2025-03.pdf",

    # --- Convatec (scale-up batch 4) ------------------------------------------
    "Convatec Group Plc Annual Report and Accounts 2025": "CTEC_company_annual_report_current_fy2025_2026.pdf",
    "Convatec Group Plc Annual Report and Accounts 2024": "CTEC_company_annual_report_previous_fy2024_2025.pdf",

    # --- Bunzl (scale-up batch 4) ---------------------------------------------
    "Bunzl plc Annual Report 2025": "BNZL_company_annual_report_current_fy2025_2025.pdf",
    "Bunzl plc Annual Report 2023": "BNZL_company_annual_report_previous_fy2023_2023.pdf",

    # --- Entain (scale-up batch 4) ---------------------------------------------
    "Entain Annual Report 2025": "ENT_company_annual_report_current_fy2025_2026-03-20.pdf",
    "Entain Annual Report 2024": "ENT_company_annual_report_previous_fy2024_2025-03-21.pdf",

    # --- Schroders (scale-up batch 4) -------------------------------------------
    "Schroders plc Annual Report and Accounts 2025": "SDR_company_annual_report_current_fy2025_2026-02.html",
    "Schroders plc Annual Report and Accounts 2024": "SDR_company_annual_report_previous_fy2024_2025-03.html",
    "Schroders Capital launches AI analyst for private equity": "SDR_company_press_release_n-a_2024-07.html",

    # --- Sainsbury's (scale-up batch 5) -----------------------------------------
    "J Sainsbury plc Annual Report and Financial Statements 2025": "SBRY_company_annual_report_current_fy2024-25_2025.pdf",
    "J Sainsbury plc Annual Report and Financial Statements 2024": "SBRY_company_annual_report_previous_fy2023-24_2024.pdf",

    # --- Pearson plc (scale-up batch 5) ------------------------------------------
    "Pearson plc Annual Report and Accounts 2025": "PSON_company_annual_report_current_fy2025_2026.pdf",
    "Pearson plc Annual Report and Accounts 2024": "PSON_company_annual_report_previous_fy2024_2025.pdf",
    "Pearson and Microsoft Announce Multi-Year Partnership to Transform the Future of Learning and Work with AI":
        "PSON_company_press_release_n-a.html",

    # --- Smith & Nephew (scale-up batch 5) ---------------------------------------
    "Smith+Nephew Annual Report 2025": "SN_company_annual_report_current_fy2025_2026-03.html",
    "Smith+Nephew Annual Report and Reports and Presentations (previous years)": "SN_company_annual_report_previous_fy2024_2025.html",

    # --- Centrica (scale-up batch 5) ---------------------------------------------
    "Centrica plc Annual Report and Accounts 2025": "CNA_company_annual_report_current_fy2025_2026-02.pdf",
    "Centrica plc Annual Report and Accounts 2024": "CNA_company_annual_report_previous_fy2024_2024.pdf",
    "Centrica drives a new wave of Power Platform innovation with Managed Environments and Copilot Studio | Microsoft Customer Stories":
        "CNA_partner_partner_case_study_n-a.html",

    # --- British American Tobacco (scale-up batch 6) -----------------------------
    "Combined Annual and Sustainability Report 2025 -- British American Tobacco": "BATS_company_annual_report_current_fy2025_2026-02.pdf",
    "Annual Report and Form 20-F 2024 -- British American Tobacco": "BATS_company_annual_report_previous_fy2024_2025-02.pdf",

    # --- IHG Hotels & Resorts (scale-up batch 6) ---------------------------------
    "Annual Report and Form 20-F 2025 -- IHG Hotels & Resorts": "IHG_company_annual_report_current_fy2025_2026-02.pdf",
    "Annual Report and Form 20-F 2024 -- IHG Hotels & Resorts": "IHG_company_annual_report_previous_fy2024_2025-02.pdf",
    "IHG Hotels & Resorts Launches AI Conversational Search Across its Digital Channels, Transforming the Guest Experience":
        "IHG_company_press_release_n-a_2026-07-28.html",

    # --- Glencore (scale-up batch 6) ---------------------------------------------
    "Glencore 2025 Annual Report -- Energising today, Advancing tomorrow": "GLEN_company_annual_report_current_fy2025_2026-02.pdf",
    "Glencore 2024 Annual Report": "GLEN_company_annual_report_previous_fy2024_2025-02.pdf",

    # --- Kingfisher plc (scale-up batch 6) ---------------------------------------
    "Kingfisher plc Annual Report and Accounts 2024/25": "KGF_company_annual_report_current_fy2024-25_2025-03.pdf",
    "Kingfisher plc Annual Report and Accounts 2023/24": "KGF_company_annual_report_previous_fy2023-24_2024-03.pdf",
    "Kingfisher launches AI-powered DIY assistant": "KGF_company_press_release_n-a_2023-11.html",

    # --- Babcock International (scale-up batch 7) --------------------------------
    "Babcock International Annual Report and Financial Statements 2025": "BAB_company_annual_report_current_fy2025_2025-07.pdf",
    "Babcock International Annual Report 2024 -- Strategic Report": "BAB_company_annual_report_previous_fy2024_2024-07.pdf",

    # --- Rentokil Initial (scale-up batch 7) --------------------------------------
    "Rentokil Initial Annual Report 2025": "RTO_company_annual_report_current_fy2025_2026-03.pdf",
    "Rentokil Initial Annual Report 2024": "RTO_company_annual_report_previous_fy2024_2025-03.pdf",

    # --- JD Sports (scale-up batch 8) --------------------------------------------
    "JD Sports Fashion Plc Annual Report & Accounts 2025": "JD_company_annual_report_current_fy2025_2025-05.pdf",
    "JD Sports Fashion Plc Annual Report & Accounts 2024": "JD_company_annual_report_previous_fy2024_2024-06.pdf",
    "JD deploys cutting edge technology to enable direct purchases through AI platforms":
        "JD_company_press_release_n-a_2026-01-12.pdf",

    # --- Coca-Cola Europacific Partners (scale-up batch 8) -----------------------
    "Coca-Cola Europacific Partners Annual Report and Form 20-F 2025": "CCEP_company_annual_report_current_fy2025_2026-03.pdf",
    "Coca-Cola Europacific Partners 2024 Annual Report": "CCEP_company_annual_report_previous_fy2024_2025-03.pdf",

    # --- Hiscox (scale-up batch 8) ------------------------------------------------
    "Hiscox Ltd Report and Accounts 2025": "HSX_company_annual_report_current_fy2025_2026-03.pdf",
    "Hiscox Ltd Report and Accounts 2024": "HSX_company_annual_report_previous_fy2024_2025-03.html",
    "Hiscox's generative AI-enhanced lead underwriting model enabled by Google Cloud goes live":
        "HSX_company_press_release_n-a_2024-08-12.html",
    "How AI is 'supercharging' Hiscox employees to do what they're great at":
        "HSX_partner_partner_case_study_n-a.html",

    # --- Games Workshop (scale-up batch 8) ---------------------------------------
    "Games Workshop Group PLC Annual Report 2024-25": "GAW_company_annual_report_current_fy2024-25_2025-07-29.pdf",
    "Games Workshop Group PLC Annual Report 2023-24": "GAW_company_annual_report_previous_fy2023-24_2024-07.pdf",

    # --- Airtel Africa (scale-up batch 9) -----------------------------------------
    "Airtel Africa plc Annual Report and Accounts 2025": "AAF_company_annual_report_current_fy2024-25_2025.pdf",
    "Airtel Africa plc Annual Report and Accounts 2024": "AAF_company_annual_report_previous_fy2023-24_2024.pdf",

    # --- Beazley (scale-up batch 9) ------------------------------------------------
    "Beazley plc Annual Report and Accounts 2025": "BEZ_company_annual_report_current_fy2025_2026-03.pdf",
    "Beazley plc Annual Report and Accounts 2024": "BEZ_company_annual_report_previous_fy2024_2025-03.pdf",

    # --- Howdens Joinery (scale-up batch 9) -----------------------------------------
    "Howden Joinery Group Plc Annual Report and Accounts 2025": "HWDN_company_annual_report_current_fy2025_2026-02.pdf",
    "Howden Joinery Group Plc Annual Report and Accounts 2024": "HWDN_company_annual_report_previous_fy2024_2025-02.pdf",

    # --- Weir Group (scale-up batch 9) -----------------------------------------------
    "Weir Group plc Annual Report 2025": "WEIR_company_annual_report_current_fy2025_2026-03.pdf",
    "Weir Group plc Annual Report 2024": "WEIR_company_annual_report_previous_fy2024_2025-03.pdf",

    # --- Antofagasta plc (scale-up batch 10) ---------------------------------------
    "Antofagasta plc Annual Report and Financial Statements 2025": "ANTO_company_annual_report_current_fy2025_2026-03.pdf",
    "Antofagasta plc Annual Report and Financial Statements 2024": "ANTO_company_annual_report_previous_fy2024_2025-03.pdf",

    # --- DCC plc (scale-up batch 10) -------------------------------------------------
    "DCC plc Annual Report and Accounts 2025": "DCC_company_annual_report_current_fy2024-25_2025-05.pdf",
    "DCC plc Annual Report and Accounts 2024": "DCC_company_annual_report_previous_fy2023-24_2024-05.pdf",

    # --- Diploma (scale-up batch 10) -------------------------------------------------
    "Diploma PLC Annual Report and Accounts 2025": "DPLM_company_annual_report_current_fy2025_2025-11.pdf",
    "Diploma PLC Annual Report and Accounts 2024": "DPLM_company_annual_report_previous_fy2024_2024-11.pdf",

    # --- Investec (scale-up batch 10) -------------------------------------------------
    "Investec plc Annual Report 2024": "INVP_company_annual_report_previous_fy2023-24_2024-07.pdf",
    "Investec yields high productivity returns with Microsoft Copilot for Sales | Microsoft Customer Stories":
        "INVP_partner_partner_case_study_n-a.html",

    # --- United Utilities (scale-up batch 10) -----------------------------------------
    "United Utilities Group PLC Integrated Annual Report 2025": "UU_company_annual_report_current_fy2024-25_2025-05.pdf",
    "United Utilities Group PLC Integrated Annual Report 2024": "UU_company_annual_report_previous_fy2023-24_2024-05.pdf",

    # --- Melrose Industries (scale-up batch 11) ---------------------------------------
    "Melrose Industries PLC Annual Report 2024": "MRO_company_annual_report_previous_fy2024_2025-03.pdf",

    # --- Spirax Group (scale-up batch 11) ----------------------------------------------
    "Spirax Group plc Annual Report 2025": "SPX_company_annual_report_current_fy2025_2026-03.pdf",
    "Spirax Group plc Annual Report 2024": "SPX_company_annual_report_previous_fy2024_2025-03.pdf",

    # --- 3i (scale-up batch 11) --------------------------------------------------------
    "3i Group plc Annual Report 2025": "III_company_annual_report_current_fy2024-25_2025-05.pdf",
    "3i Group plc Annual Report 2024": "III_company_annual_report_previous_fy2023-24_2024-05.pdf",

    # --- IG Group (scale-up batch 11) --------------------------------------------------
    "IG Group Holdings plc Annual Report 31 December 2025": "IGG_company_annual_report_current_fy2025-year-ended-31-dec-2025_2026.pdf",
    "IG Group Holdings plc Annual Report 2024": "IGG_company_annual_report_previous_fy2024-year-ended-31-may-2024_2024.pdf",

    # --- Fresnillo plc (scale-up batch 11) ---------------------------------------------
    "Fresnillo plc Annual Report 2025": "FRES_company_annual_report_current_fy2025_2026-03.pdf",
    "Fresnillo plc Annual Report and Accounts 2024 (Financial Statements component)": "FRES_company_annual_report_previous_fy2024_2025-03.pdf",

    # --- Aberdeen Group (scale-up batch 12) --------------------------------------------
    "Aberdeen Group plc Annual Report and Accounts 2025": "ABDN_company_annual_report_current_fy2025_2026-03.pdf",
    "Aberdeen Group plc Annual Report and Accounts 2024": "ABDN_company_annual_report_previous_fy2024_2025-03.pdf",

    # --- St. James's Place (scale-up batch 12) -----------------------------------------
    "St. James's Place Annual Report and Accounts 2025": "STJ_company_annual_report_current_fy2025_2026.pdf",
    "St. James's Place Annual Report and Accounts 2024 (Strategic Report component)": "STJ_company_annual_report_previous_fy2024_2025.pdf",

    # --- Land Securities (scale-up batch 12) -------------------------------------------
    "Landsec Annual Report 2025": "LAND_company_annual_report_current_fy2024-25_2025.pdf",
    "Landsec Annual Report 2024": "LAND_company_annual_report_previous_fy2023-24_2024.pdf",

    # --- Endeavour Mining (scale-up batch 12) ------------------------------------------
    "Endeavour Mining plc Annual Report 2025": "EDV_company_annual_report_current_fy2025_2026-03-05.pdf",
    "Endeavour Mining plc Annual Report 2024": "EDV_company_annual_report_previous_fy2024_2025-03-06.pdf",

    # --- Metlen Energy & Metals (scale-up batch 12) ------------------------------------
    "Metlen Energy & Metals Integrated Annual Report 2025": "MTLN_company_annual_report_current_fy2025_2026.pdf",
    "Metlen Energy & Metals Integrated Annual Report 2024": "MTLN_company_annual_report_previous_fy2024_2025.pdf",

    # --- Alliance Witan (session 4) -----------------------------------------------------
    "Alliance Witan PLC Annual Report 2025": "ALW_company_annual_report_current_fy2025_2026-03.pdf",
    "Alliance Witan PLC Annual Report 2024": "ALW_company_annual_report_previous_fy2024_2025-03.pdf",

    # --- F&C Investment Trust (session 4) -----------------------------------------------
    "F&C Investment Trust plc Annual Report and Accounts 2025": "FCIT_company_annual_report_current_fy2025_2026-03.pdf",

    # --- Intermediate Capital Group (session 4) -----------------------------------------
    "Intermediate Capital Group plc Annual Report and Accounts 2025": "ICG_company_annual_report_current_fy2024-25_2025-06.pdf",
    "Intermediate Capital Group plc Annual Report and Accounts 2024": "ICG_company_annual_report_previous_fy2023-24_2024-06.pdf",

    # --- Lion Finance Group (session 4) -------------------------------------------------
    "Lion Finance Group PLC Annual Report 2025": "BGEO_company_annual_report_current_fy2025_2026-02.pdf",
    "Lion Finance Group PLC Annual Report 2024": "BGEO_company_annual_report_previous_fy2024_2025-04.pdf",

    # --- LondonMetric Property (session 4) ----------------------------------------------
    "LondonMetric Property Plc Annual Report 2025": "LMP_company_annual_report_current_fy2024-25_2025-06.pdf",
    "LondonMetric Property Plc Annual Report 2024": "LMP_company_annual_report_previous_fy2023-24_2024-06.pdf",

    # --- Pershing Square Holdings (session 4) -------------------------------------------
    "Pershing Square Holdings Ltd. 2025 Annual Report": "PSH_company_annual_report_current_fy2025_2026-02.pdf",
    "Pershing Square Holdings Ltd. 2024 Annual Report": "PSH_company_annual_report_previous_fy2024_2025-03.pdf",

    # --- Polar Capital Technology Trust (session 4) -------------------------------------
    "Polar Capital Technology Trust plc Annual Report 2026": "PCT_company_annual_report_current_fy-ended-2026-04-30_2026-07.pdf",
    "Polar Capital Technology Trust plc Annual Report 2025": "PCT_company_annual_report_previous_fy-ended-2025-04-30_2025-07.pdf",

    # --- Scottish Mortgage Investment Trust (session 4) ---------------------------------
    "Scottish Mortgage Investment Trust plc Annual Report and Financial Statements 2025": "SMT_company_annual_report_current_fy-ended-2025-03-31_2025-05.pdf",
    "Scottish Mortgage Investment Trust plc Annual Report and Financial Statements 2024": "SMT_company_annual_report_previous_fy-ended-2024-03-31_2024-06.pdf",

    # --- Segro (session 4) ---------------------------------------------------------------
    "SEGRO plc Annual Report and Accounts 2025": "SGRO_company_annual_report_current_fy2025_2026-02.pdf",
    "SEGRO plc Annual Report and Accounts 2024": "SGRO_company_annual_report_previous_fy2024_2025-02.pdf",

    # --- Standard Life (session 4) --------------------------------------------------------
    "Standard Life plc Annual Report and Accounts 2025": "SDLF_company_annual_report_current_fy2025_2026-03-16.pdf",
    "Phoenix Group Holdings plc Annual Report and Accounts 2024": "SDLF_company_annual_report_previous_fy2024_2025-03.pdf",

    # --- Tritax Big Box REIT (session 4) --------------------------------------------------
    "Tritax Big Box REIT plc Annual Report 2025": "BBOX_company_annual_report_current_fy2025_2026-02.pdf",
    "Tritax Big Box REIT plc Annual Report 2024": "BBOX_company_annual_report_previous_fy2024_2025-02.pdf",

    # --- BAE Systems (manual-browser resolution pass) -----------------------------------
    "BAE Systems Annual Report 2025": "BA_company_annual_report_current_fy2025.pdf",
    "BAE Systems Annual Report 2024": "BA_company_annual_report_previous_fy2024.pdf",
}


def build_source_manifest_proposal(slug: str, ticker: str, company: str, sector: str,
                                    existing_manifest_rows: list[dict], problems: list[str]) -> list[dict]:
    fieldnames, candidates = pc.read_csv_rows(pc.INTERMEDIATE_DIR / f"{slug}_source_candidates.csv")
    if fieldnames is None:
        problems.append(f"BLOCKED: {slug}_source_candidates.csv not found.")
        return []

    existing_by_filename = {(r.get("local_filename") or "").strip(): r for r in existing_manifest_rows}
    existing_ids = {(r.get("source_id") or "").strip() for r in existing_manifest_rows}
    existing_urls = {(r.get("url") or "").strip() for r in existing_manifest_rows if (r.get("url") or "").strip()}
    id_prefix = ticker.split(".")[0]  # e.g. "BT.A" -> "BT"; the ticker field itself keeps the full value

    next_num = 1
    while f"{id_prefix}-{next_num:03d}" in existing_ids:
        next_num += 1

    proposed_rows: list[dict] = []
    for c in candidates:
        if (c.get("approval_status") or "").strip() != "approved":
            continue
        candidate_title = (c.get("candidate_title") or "").strip()
        local_filename = SOURCE_CANDIDATE_TO_FILENAME.get(candidate_title)
        if local_filename is None:
            problems.append(f"BLOCKED: approved candidate '{candidate_title}' has no known downloaded filename mapping.")
            continue

        if local_filename in existing_by_filename:
            pc.report(f"  [idempotent] {local_filename} already in source_manifest.csv as "
                      f"{existing_by_filename[local_filename].get('source_id')} -- not re-proposed.")
            continue

        override = SOURCE_MANIFEST_OVERRIDES.get(local_filename, {})
        if not override:
            problems.append(f"BLOCKED: no manifest override defined for approved source '{local_filename}'.")
            continue

        document_category = (c.get("document_category") or "").strip()
        evidence_origin = (c.get("evidence_origin") or "").strip()
        financial_year_covered = (c.get("financial_year_covered") or "").strip() or "not_applicable"
        if document_category not in DOCUMENT_CATEGORY_VALUES:
            problems.append(f"BLOCKED {local_filename}: document_category '{document_category}' not in controlled vocabulary.")
            continue
        if evidence_origin not in EVIDENCE_ORIGIN_VALUES:
            problems.append(f"BLOCKED {local_filename}: evidence_origin '{evidence_origin}' not in controlled vocabulary.")
            continue

        source_id = f"{id_prefix}-{next_num:03d}"
        next_num += 1
        while f"{id_prefix}-{next_num:03d}" in existing_ids:
            next_num += 1

        url = override.get("url", "")
        if url and url in existing_urls:
            problems.append(f"BLOCKED {local_filename}: proposed url '{url}' collides with an existing manifest row.")
            continue

        row = {
            "source_id": source_id,
            "company": company,
            "ticker": ticker,
            "sector": sector,
            "document_category": document_category,
            "document_title": override.get("document_title", candidate_title),
            "financial_year_covered": financial_year_covered,
            "publication_date": override["publication_date"],
            "url": url,
            "local_filename": local_filename,
            "evidence_origin": evidence_origin,
            "download_status": "downloaded",
            "text_extraction_status": "extracted",
            "document_review_status": override["document_review_status"],
            "logged_by": "claude_code",
            "model_version": "",
            "logged_date": today_date(),
            "notes": override["notes"],
        }
        if row["document_review_status"] not in DOCUMENT_REVIEW_STATUS_VALUES:
            problems.append(f"BLOCKED {local_filename}: document_review_status invalid.")
            continue
        proposed_rows.append(row)

    return proposed_rows


def manifest_source_id_for(local_filename: str, proposed_manifest_rows: list[dict]) -> str:
    for r in proposed_manifest_rows:
        if r["local_filename"] == local_filename:
            return r["source_id"]
    return ""


# ---------------------------------------------------------------------------
# Operational -> use_case_dataset_template.csv
# ---------------------------------------------------------------------------
# evidence_strength/confidence were proposed with explicit reasons in the
# prior dry-run report and have now been explicitly approved by the human
# operator (see the "Operational evidence decisions" instruction), along
# with review_status = reviewed_confirmed for both rows. A human-reviewed
# row may legitimately carry evidence_strength = 1_weak (Adobe) -- the
# review_status records that the classification itself was reviewed; the
# confirmed_use_case_count formula separately determines whether a row's
# evidence_strength qualifies it for the confirmed count (see
# compute_use_case_counts below).
OPERATIONAL_OVERRIDES = {
    "TSCO-OP-001": {  # Adobe
        "evidence_quotation": (
            "Tesco plans to use Adobe AI and agentic AI capabilities to better interpret and anticipate "
            "customers’ needs for an even more personalised and helpful shopping experience"
        ),
        "use_case_name": "Adobe x Tesco AI-powered personalisation partnership (Tesco x Adobe Innovation Lab)",
        "use_case_description": (
            "Tesco and Adobe announced a strategic AI partnership under which Tesco's personalisation and AI teams "
            "plan to use Adobe's agentic AI capabilities and Adobe Firefly Foundry, via a new 'Tesco x Adobe "
            "Innovation Lab', to generate personalised content, offers and experiences for customers. Described as "
            "planned/early-stage; not yet live."
        ),
        "named_tool_or_model": "Adobe Firefly Foundry; Adobe agentic AI capabilities",
        "technology_partner": "Adobe",
        "proposed_evidence_strength": "1_weak",
        "evidence_strength_reason": (
            "Vendor-authored (Adobe's own newsroom, technology_partner) announcement of a planned partnership with "
            "no independent Tesco-primary corroboration found this session and no active deployment evidenced -- "
            "matches the manual's 1_weak definition ('vendor-led or vague description with limited corroboration')."
        ),
        "proposed_confidence": "medium",
        "confidence_reason": (
            "The generative-AI classification itself is unambiguous (explicit 'Adobe Firefly Foundry' and 'agentic "
            "AI' naming), but several supporting fields required judgment calls already flagged as unclear at "
            "staging (secondary_business_function, risk_or_limitation, destination_ambiguity) -- matches the "
            "manual's medium definition."
        ),
    },
    "TSCO-OP-002": {  # dunnhumby
        "evidence_quotation": (
            "Powered by GenAI, it automatically generates compliant ads in all the formats brands need, across "
            "both onsite and offsite."
        ),
        "use_case_name": "Tesco Media Creative Studio -- GenAI ad-creative generation tool",
        "use_case_description": (
            "Tesco Media's 'Creative Studio' tool, described by dunnhumby (which manages Tesco Media's technology "
            "infrastructure) as powered by generative AI, automatically generates compliant advertising creative in "
            "the formats needed across onsite and offsite channels for brands advertising with Tesco Media. "
            "Reported as a live, launched tool as of October 2025."
        ),
        "named_tool_or_model": "Creative Studio (underlying model/provider not named in source)",
        "technology_partner": "dunnhumby",
        "proposed_evidence_strength": "2_moderate",
        "evidence_strength_reason": (
            "The use case is specific and clearly described (a live, launched, named tool with a stated generative "
            "function), which exceeds the manual's 1_weak bar -- but it is vendor-authored (dunnhumby, technology_"
            "partner, not a Tesco-primary statement) with no quantified scale or outcome, so it falls short of "
            "3_strong. Approved as 2_moderate ('specific use case is clear, but scale, stage or outcomes are "
            "incomplete') despite the vendor-origin tension with 1_weak, since the tool is confirmed live and "
            "named, unlike Adobe's planned-stage announcement."
        ),
        "proposed_confidence": "medium",
        "confidence_reason": (
            "Classification as genuine GenAI is directly supported by explicit 'Powered by GenAI' language, but "
            "dunnhumby's distinct-from-Tesco corporate status (flagged at staging) and the technology_partner "
            "origin mean some judgment is still required -- matches the manual's medium definition."
        ),
    },
    "BT-OP-001": {  # GenAI Gateway: Openreach engineering-note summarisation
        "evidence_quotation": (
            "A trial in Openreach is summarising engineering notes on Ethernet and full fibre jobs, helping to "
            "simplify processes and boost productivity for its teams and Communications Provider customers."
        ),
        "use_case_name": "GenAI Gateway: Openreach engineering-note summarisation",
        "use_case_description": (
            "BT's GenAI Gateway (built on Amazon Bedrock) is being trialled in Openreach to automatically "
            "summarise engineering notes on Ethernet and full-fibre jobs, intended to simplify processes and "
            "boost productivity for Openreach teams and Communications Provider customers."
        ),
        "named_tool_or_model": "GenAI Gateway (Amazon Bedrock-based)",
        "technology_partner": "AWS",
        "proposed_evidence_strength": "2_moderate",
        "evidence_strength_reason": (
            "Company-primary source names a specific pilot task (Openreach engineering-note summarisation) with "
            "a stated purpose, but no quantified outcome or scale is given -- matches 2_moderate ('specific use "
            "case is clear, but scale, stage or outcomes are incomplete')."
        ),
        "proposed_confidence": "medium",
        "confidence_reason": (
            "Classification as genuine GenAI is clear given the explicit GenAI Gateway/Bedrock framing, but "
            "pilot-stage status with limited operational detail leaves some judgment required."
        ),
    },
    "BT-OP-002": {  # GenAI Gateway: contract analysis
        "evidence_quotation": (
            "A second use case, supporting contract analysis for the Group's Business, legal and procurement "
            "teams, is also live."
        ),
        "use_case_name": "GenAI Gateway: contract analysis for Business/legal/procurement",
        "use_case_description": (
            "BT's GenAI Gateway supports a live contract-analysis use case for the Group's Business, legal and "
            "procurement teams."
        ),
        "named_tool_or_model": "GenAI Gateway (Amazon Bedrock-based)",
        "technology_partner": "AWS",
        "proposed_evidence_strength": "2_moderate",
        "evidence_strength_reason": (
            "Specific, named, live use case with a defined user group, but no quantified scale or outcome is "
            "given -- matches 2_moderate."
        ),
        "proposed_confidence": "medium",
        "confidence_reason": "Genuine GenAI Gateway use case is clearly stated, but operational detail beyond 'is also live' is limited.",
    },
    "BT-OP-003": {  # Sprinklr/Aimee customer service
        "evidence_quotation": (
            "The platform enables BT Group to use generative AI to support various customer experiences, for "
            "sales and support for both EE and BT customers."
        ),
        "use_case_name": "Sprinklr/Aimee generative-AI customer service",
        "use_case_description": (
            "BT Group uses generative AI via Sprinklr's Unified-CXM platform, powering EE's virtual assistant "
            "Aimee, to support sales and customer-service experiences; explicit examples include generative-AI "
            "travel-preparation support (roughly halving the need for online support) and generative-AI billing-"
            "charge explanations, with continuing use at meaningful scale (tens of thousands of conversations "
            "per week)."
        ),
        "named_tool_or_model": "Sprinklr Unified-CXM platform / EE virtual assistant Aimee",
        "technology_partner": "Sprinklr",
        "proposed_evidence_strength": "3_strong",
        "evidence_strength_reason": (
            "Matches 3_strong on all four supporting elements: (1) BT-primary evidence -- this is BT Group's own "
            "newsroom announcement (evidence_origin=company_primary), not a vendor case study; (2) explicit "
            "generative-AI language -- the source states BT Group 'use[s] generative AI to support various "
            "customer experiences' and names the underlying LLM-agnostic architecture; (3) a concrete, deployed "
            "customer-service function -- generative-AI travel-preparation support and generative-AI billing-"
            "charge explanations, both live within the Aimee assistant; (4) quantified usage/scale evidence -- "
            "tens of thousands of weekly conversations handled, with described week-on-week growth."
        ),
        "proposed_confidence": "high",
        "confidence_reason": "Explicit, detailed, company-primary description with concrete named functions and quantified scale leaves little ambiguity.",
    },
    "BT-OP-004": {  # Amazon Q Developer
        "evidence_quotation": (
            "Amazon Q Developer generates over 2 million lines of code per year for BT Group, compared with "
            "2.5-3 million lines of code that developers previously produced annually."
        ),
        "use_case_name": "Amazon Q Developer for code generation, testing and transformation",
        "use_case_description": (
            "BT Group's approximately 2,000 developers use Amazon Q Developer (formerly Amazon CodeWhisperer) for "
            "code generation, unit-test generation, code transformation between language versions, and console/"
            "in-line chat assistance."
        ),
        "named_tool_or_model": "Amazon Q Developer (formerly Amazon CodeWhisperer)",
        "technology_partner": "AWS",
        "proposed_evidence_strength": "2_moderate",
        "evidence_strength_reason": (
            "Vendor-authored (AWS, technology_partner) case study with a specific, quantified use case (~2,000 "
            "users, 2M+ lines/year) -- exceeds 1_weak's 'vague description', but the vendor origin, without "
            "independent BT-primary corroboration beyond a brief AR2024 mention, keeps it short of 3_strong."
        ),
        "proposed_confidence": "medium",
        "confidence_reason": "Genuine, specific GenAI coding-assistant use case, but vendor authorship requires some judgment.",
    },
    "RR-OP-001": {  # Databricks cGAN aero-engine design generation
        "evidence_quotation": (
            "Rolls-Royce has witnessed the transformative power of the Databricks Data Intelligence Platform in "
            "various AI projects. One example is a collaboration between Rolls-Royce and Databricks, focused on "
            "optimizing conditional Generative Adversarial Network (cGAN)"
        ),
        "use_case_name": "Databricks cGAN for preliminary aero-engine design generation",
        "use_case_description": (
            "Rolls-Royce and Databricks collaborated on training a conditional Generative Adversarial Network "
            "(cGAN), reusing legacy simulation data, to generate and validate preliminary aero-engine design "
            "concepts; co-authored by five named Rolls-Royce engineers."
        ),
        "named_tool_or_model": "Conditional Generative Adversarial Network (cGAN) via Databricks Data Intelligence Platform",
        "technology_partner": "Databricks",
        "proposed_evidence_strength": "2_moderate",
        "evidence_strength_reason": (
            "Vendor-published (Databricks) but co-authored by five named Rolls-Royce engineers, strengthening "
            "credibility; describes a specific, named generative technique (cGAN) and task (design-concept "
            "generation), but no quantified benefit is given (only qualitative claims), and Rolls-Royce has not "
            "independently published corroboration -- matches 2_moderate."
        ),
        "proposed_confidence": "medium",
        "confidence_reason": "The generative technique (cGAN) is unambiguous, but vendor origin and lack of independent RR corroboration require some judgment.",
    },
    "EXPN-OP-001": {  # Experian Assistant for Model Risk Management
        "evidence_quotation": (
            "This launch further strengthens the award-winning Experian Assistant product family, extending "
            "trusted automation and GenAI capabilities from model development into model governance."
        ),
        "use_case_name": "Experian Assistant for Model Risk Management -- GenAI-enabled documentation and governance automation",
        "use_case_description": (
            "A GenAI-enabled capability within the Experian Assistant product family, launched for financial-"
            "institution clients to simplify model documentation efforts via automation and guided workflows, "
            "extending automation from model development into model governance for model risk management. "
            "Follows the earlier introduction of the award-winning Experian Assistant and its AI-enabled model-"
            "lifecycle features."
        ),
        "named_tool_or_model": "Experian Assistant for Model Risk Management (part of the Experian Ascend Platform; built with ValidMind technology)",
        "technology_partner": "ValidMind",
        "proposed_evidence_strength": "2_moderate",
        "evidence_strength_reason": (
            "Company-primary launch announcement (Experian's own newsroom) with an explicit, concrete task "
            "(simplifying model documentation via automation and guided workflows) and a named client user group "
            "(financial institutions), but no quantified adoption/outcome metric is given -- matches 2_moderate "
            "('specific use case is clear, but scale, stage or outcomes are incomplete')."
        ),
        "proposed_confidence": "medium",
        "confidence_reason": (
            "The GenAI classification is clearly and explicitly stated ('GenAI capabilities', 'GenAI-enabled "
            "capabilities'), but the precise user_group (customers vs. regulated_decision_makers) and deployment "
            "scale required some judgment at staging -- matches medium."
        ),
    },
    "RIO-OP-001": {  # GPT-like knowledge agent for the Annual Planning Review workshop
        "evidence_quotation": (
            "a Generative Pre-Trained Transformer (GPT) like knowledge agent for the Annual Planning Review "
            "workshop. We leveraged cutting-edge technology such as Generative AI and Large Language Models "
            "(LLMs) and collaborated across different teams to ensure timely delivery in only 3 weeks."
        ),
        "use_case_name": "GPT-like knowledge agent for the Annual Planning Review workshop",
        "use_case_description": (
            "Rio Tinto's internal Data & Analytics team built a Generative Pre-Trained Transformer (GPT)-like "
            "knowledge agent, using generative AI and large language models, to support the Annual Planning "
            "Review workshop -- delivered by the internal data science team in three weeks."
        ),
        "named_tool_or_model": "GPT-like knowledge agent (internally built; no named vendor model)",
        "technology_partner": "not_applicable (internally built by Rio Tinto's own Data & Analytics team)",
        "proposed_evidence_strength": "2_moderate",
        "evidence_strength_reason": (
            "Company-primary source (official riotinto.com story page) explicitly names a specific delivered "
            "task (a GPT-like knowledge agent for the Annual Planning Review workshop, built by the internal "
            "Data & Analytics team in 3 weeks), but no quantified usage outcome or ongoing-scale evidence is "
            "given beyond the one named workshop -- matches 2_moderate ('specific use case is clear, but scale, "
            "stage or outcomes are incomplete')."
        ),
        "proposed_confidence": "medium",
        "confidence_reason": (
            "The generative AI/LLM/GPT classification is unambiguous and explicit, but whether the tool "
            "continues in use beyond the named workshop is not confirmed, requiring some judgment on "
            "deployment_stage -- matches medium."
        ),
    },
    "DGE-OP-001": {  # Bottle/label personalisation pilot (Johnnie Walker x Scott Naismith)
        "evidence_quotation": (
            "The technology, powered by Generative AI, empowers consumers to co-create designs on Diageo "
            "products in a way that is bespoke to them and relevant to the worlds they are passionate about. "
            "Diageo has leveraged the latest developments in Generative AI through Amazon's Titan bedrock model."
        ),
        "use_case_name": "Johnnie Walker x Scott Naismith generative-AI bottle/label personalisation pilot",
        "use_case_description": (
            "A Generative AI-powered experience, built on Amazon's Titan Bedrock model, allowing guests at "
            "Johnnie Walker Princes Street (Edinburgh) to co-design a personalised Johnnie Walker Blue Label "
            "bottle/label with artist Scott Naismith. Guests answer three questions that influence artistic "
            "themes; explicitly described in-source as 'the first pilot in a wider platform'. Ran 1-31 August "
            "2024 at a single venue."
        ),
        "named_tool_or_model": "Amazon Titan Bedrock model",
        "technology_partner": "Amazon AWS (also named: Phantom, Hybrid Software, GMG, Roland DG)",
        "proposed_evidence_strength": "2_moderate",
        "evidence_strength_reason": (
            "Company-primary source names a specific generative-AI model (Amazon Titan Bedrock) and a concrete "
            "task (bottle-label co-creation), but the deployment is explicitly a time- and venue-limited pilot "
            "with no quantified usage/outcome metric -- matches 2_moderate."
        ),
        "proposed_confidence": "medium",
        "confidence_reason": "GenAI classification is explicit and unambiguous, but the one-month/single-venue pilot scope requires judgment on how to weight deployment_stage.",
    },
    "DGE-OP-002": {  # Generative-AI cybersecurity chatbot
        "evidence_quotation": (
            "We utilise a generative AI-chatbot for real-time learning, revised ransomware response protocols "
            "and improved phishing simulation outcomes."
        ),
        "use_case_name": "Generative-AI chatbot for cybersecurity training and phishing simulation",
        "use_case_description": (
            "Diageo's internal security function uses a generative-AI chatbot to support real-time learning, "
            "revised ransomware-response protocols, and improved phishing-simulation outcomes, disclosed as a "
            "current risk-mitigation measure in the FY2025 Annual Report."
        ),
        "named_tool_or_model": "Generative AI chatbot (no vendor/model named in source)",
        "technology_partner": "not_applicable (no technology partner named)",
        "proposed_evidence_strength": "2_moderate",
        "evidence_strength_reason": (
            "Company-primary Annual Report disclosure names a specific, concrete task (phishing-simulation/"
            "security-awareness chatbot) as a current mitigation, but no vendor/model or adoption-scale figures "
            "are given -- matches 2_moderate."
        ),
        "proposed_confidence": "medium",
        "confidence_reason": "Explicit generative-AI language is clear, but the brief risk-register framing leaves deployment scale and tooling unconfirmed.",
    },
    "DGE-OP-003": {  # "What's Your Cocktail?" generative-AI food-pairing platform
        "evidence_quotation": (
            "In May, we launched 'What's Your Cocktail?', a generative AI-driven digital platform to recommend "
            "cocktail pairings with individual food preferences."
        ),
        "use_case_name": "'What's Your Cocktail?' generative-AI food-pairing recommendation platform",
        "use_case_description": (
            "A generative AI-driven digital platform, launched by Diageo in May [2024], that recommends "
            "cocktail-and-food pairings tailored to individual consumer food preferences, helping consumers "
            "'demystify cocktails'."
        ),
        "named_tool_or_model": "'What's Your Cocktail?' platform (underlying model/vendor not named in source)",
        "technology_partner": "not_applicable (no technology partner named)",
        "proposed_evidence_strength": "2_moderate",
        "evidence_strength_reason": (
            "Company-primary Annual Report disclosure describing a named, launched, live consumer-facing "
            "platform with an explicit generative-AI function, but no adoption-scale or outcome metric is "
            "given -- matches 2_moderate."
        ),
        "proposed_confidence": "medium",
        "confidence_reason": "GenAI classification and task are clearly stated, but the one-paragraph Annual Report disclosure leaves scale/vendor detail unconfirmed.",
    },
    "VOD-OP-001": {  # SuperTOBi generative-AI virtual assistant
        "evidence_quotation": (
            "Vodafone today announced that SuperTOBi, its new customer-focussed Generative AI (GenAI) driven "
            "virtual assistant, is being rolled out across Europe. SuperTOBi, powered by Microsoft Azure "
            "OpenAI, can understand and respond faster."
        ),
        "use_case_name": "SuperTOBi generative-AI customer virtual assistant",
        "use_case_description": (
            "SuperTOBi, Vodafone's customer-focused Generative AI virtual assistant, powered by Microsoft Azure "
            "OpenAI, understands and responds to complex customer enquiries (interpreting full sentences/"
            "phrases rather than keywords) better than traditional chatbots. Rolled out in Italy and Portugal, "
            "expanding to Germany and Turkey and other markets. In Portugal, first-time resolution rose from "
            "15% to 60% and online NPS improved by 14 points to 64."
        ),
        "named_tool_or_model": "SuperTOBi (built on Microsoft Azure OpenAI)",
        "technology_partner": "Microsoft (Azure OpenAI)",
        "proposed_evidence_strength": "3_strong",
        "evidence_strength_reason": (
            "Company-primary announcement naming a specific tool and underlying platform (Azure OpenAI), a "
            "concrete customer-service task, a multi-country live deployment, and quantified outcome metrics "
            "(first-time resolution 15%->60%, NPS +14 points) -- matches 3_strong (concrete deployed function, "
            "quantified scale/outcome, company-primary)."
        ),
        "proposed_confidence": "high",
        "confidence_reason": "Explicit, detailed, company-primary description with concrete named function, named underlying platform, and quantified outcomes leaves little ambiguity.",
    },
    "VOD-OP-002": {  # Copilot for Microsoft 365 employee rollout
        "evidence_quotation": (
            "In November 2024 we started a global market-by-market rollout of Copilot for Microsoft 365. This "
            "tool uses GenAI to make daily tasks such as drafting emails, creating presentations and "
            "summarising meetings easier, boosting productivity. By January 2025, over 50,000 colleagues had "
            "access to Copilot."
        ),
        "use_case_name": "Copilot for Microsoft 365 employee productivity rollout",
        "use_case_description": (
            "Vodafone's global rollout of Copilot for Microsoft 365 (from November 2024), which 'uses GenAI to "
            "make daily tasks such as drafting emails, creating presentations and summarising meetings easier'. "
            "By January 2025, over 50,000 colleagues had access; 20 skill labs on prompt engineering were "
            "delivered to 13,000 colleagues. A foundational 'GenAI Empowering You' training campaign was "
            "completed by 40,000 colleagues."
        ),
        "named_tool_or_model": "Copilot for Microsoft 365",
        "technology_partner": "Microsoft",
        "proposed_evidence_strength": "3_strong",
        "evidence_strength_reason": (
            "Company-primary Annual Report disclosure naming a specific tool, concrete tasks (drafting emails/"
            "presentations/meeting summaries), and a quantified, large-scale deployment (50,000+ employees, "
            "13,000 in skill labs, 40,000 in foundational training) -- matches 3_strong."
        ),
        "proposed_confidence": "high",
        "confidence_reason": "Explicit GenAI language, named tool, and detailed quantified adoption figures leave little ambiguity.",
    },
    "LGEN-OP-001": {  # Copilot rollout + live Retail AI tool
        "evidence_quotation": (
            "L&G will continue to deploy Microsoft 365 Copilot to all 10,000 employees globally. This will "
            "embed generative AI into everyday tools to reduce administrative tasks, accelerate insight "
            "generation and enable colleagues to focus on supporting customers."
        ),
        "use_case_name": "Microsoft 365 Copilot rollout and Retail-business customer-service AI tool",
        "use_case_description": (
            "L&G's collaboration with Microsoft to deploy Microsoft 365 Copilot to all ~10,000 employees "
            "globally, embedding generative AI into everyday tools to reduce administrative tasks and "
            "accelerate insight generation. Builds on an existing, already-live Retail-business AI deployment "
            "giving service teams a real-time view of customer interactions, which has already delivered an "
            "eight-point year-on-year Net Promoter Score increase (Q1, DC & Workplace Savings) and serves more "
            "than 12 million L&G customers."
        ),
        "named_tool_or_model": "Microsoft 365 Copilot; Microsoft Azure",
        "technology_partner": "Microsoft",
        "proposed_evidence_strength": "3_strong",
        "evidence_strength_reason": (
            "Company-primary newsroom release naming specific tools (Copilot, Azure), concrete tasks "
            "(administrative-task reduction, real-time customer-interaction view), a large deployment scale "
            "(10,000 employees; 12+ million customers already served) and a quantified outcome (8-point NPS "
            "increase) -- matches 3_strong."
        ),
        "proposed_confidence": "high",
        "confidence_reason": "Explicit generative-AI language, named tools, and a quantified, already-achieved outcome leave little ambiguity.",
    },
    "RKT-OP-001": {  # GenAI marketing pilots (Gaviscon, Finish)
        "evidence_quotation": (
            "Reckitt undertook a series of pilots across Gaviscon, Finish and the company's overall marketing "
            "function... using a suite of tools that were tailored to Reckitt's needs. These included "
            "custom-built GPTs trained on Reckitt data and expertise, multi-modal GenAI tools for content "
            "adaptation and localisation, and an interactive interface to create, test, and refine new product "
            "concepts from consumer insights data."
        ),
        "use_case_name": "GenAI marketing pilots for concept development and content localisation (Gaviscon, Finish)",
        "use_case_description": (
            "Reckitt's marketing function, in partnership with Boston Consulting Group, ran GenAI pilots across "
            "the Gaviscon and Finish brands using custom-built GPTs trained on Reckitt data, multi-modal GenAI "
            "content-adaptation/localisation tools, and an interactive product-concept creation interface. "
            "Results: up to 60% faster concept development, ~30% faster ad adaptation/localisation, and "
            "post-campaign media analysis time reduced up to 90% with a two-fold quality improvement. Explicitly "
            "described as pilots, with the company 'moving to scaling up'."
        ),
        "named_tool_or_model": "Custom-built GPTs (no specific vendor model named)",
        "technology_partner": "Boston Consulting Group (delivery partner, not a named AI vendor)",
        "proposed_evidence_strength": "3_strong",
        "evidence_strength_reason": (
            "Company-primary press release naming specific tools (custom GPTs, multi-modal content tools), "
            "named brands/teams (Gaviscon, Finish, marketing function), and multiple quantified outcomes (60% "
            "faster concept development, ~30% faster localisation, up to 90% faster media analysis) -- matches "
            "3_strong despite pilot-stage deployment, since the manual's 3_strong bar is about evidence "
            "specificity/quantification, not deployment maturity."
        ),
        "proposed_confidence": "high",
        "confidence_reason": "Explicit, detailed, company-primary description with named tools, named brands, and multiple quantified outcomes leaves little ambiguity about the GenAI classification itself.",
    },
    "SHEL-OP-001": {  # SparkCognition subsurface-imaging generative AI
        "evidence_quotation": (
            "The proprietary generative AI approach being developed by Shell and SparkCognition uses deep "
            "learning to generate reliable subsurface images using far fewer seismic shots -- as little as 1% "
            "in completed field trials -- than traditionally necessary."
        ),
        "use_case_name": "SparkCognition/Shell generative-AI subsurface exploration imaging",
        "use_case_description": (
            "Shell and SparkCognition developed a proprietary generative-AI approach using deep learning to "
            "generate reliable subsurface images for oil and gas exploration, using as little as 1% of the "
            "seismic shots traditionally required, per completed field trials."
        ),
        "named_tool_or_model": "Proprietary generative-AI/deep-learning approach (no specific model architecture named)",
        "technology_partner": "SparkCognition",
        "proposed_evidence_strength": "2_moderate",
        "evidence_strength_reason": (
            "Technology-partner press release naming a specific task (subsurface seismic imaging) with a "
            "quantified field-trial result (1% of shots needed), but no independent Shell-primary corroboration "
            "and deployment described as field trials/pilot rather than scaled production -- matches "
            "2_moderate."
        ),
        "proposed_confidence": "medium",
        "confidence_reason": "Genuine generative-AI classification is explicit, but vendor origin and pilot-stage framing require some judgment.",
    },
    "HSBA-OP-001": {  # Google Cloud/Gemini partnership
        "evidence_quotation": (
            "AI-empowered teams: HSBC will supercharge its frontline staff and relationship managers with the "
            "expansion of an AI-powered decision assistant that is already reducing admin and client meeting "
            "prep time from hours to minutes for thousands of users."
        ),
        "use_case_name": "HSBC/Google Cloud Gemini-powered decision assistant and AI banking partnership",
        "use_case_description": (
            "HSBC and Google Cloud's multi-year partnership to build and deploy AI capabilities across HSBC's "
            "operations globally, focused on hyper-personalised wealth-management support, financial-crime risk "
            "detection using generative and agentic AI, and an AI-powered decision assistant already reducing "
            "admin/client-meeting-prep time from hours to minutes for thousands of relationship managers. Uses "
            "Gemini models and the Gemini Enterprise Agent Platform."
        ),
        "named_tool_or_model": "Gemini models; Gemini Enterprise Agent Platform",
        "technology_partner": "Google Cloud (including Google DeepMind)",
        "proposed_evidence_strength": "3_strong",
        "evidence_strength_reason": (
            "Company-primary newsroom release naming specific products (Gemini, Gemini Enterprise Agent "
            "Platform), a concrete already-live task (decision assistant reducing prep time from hours to "
            "minutes) with an explicit user-scale claim (thousands of users), plus quantified future-value "
            "figures (200+ use cases, $100m+ initiatives) -- matches 3_strong."
        ),
        "proposed_confidence": "high",
        "confidence_reason": "Explicit, detailed, company-primary description with named products and a concrete already-live component leaves little ambiguity.",
    },
    "HSBA-OP-002": {  # Mistral AI productivity platform
        "evidence_quotation": (
            "This will enable HSBC to enhance current AI initiatives through self-hosted AI models that operate "
            "on HSBC's internal technology systems ... an AI-powered platform used by HSBC colleagues globally "
            "to help with productivity tasks."
        ),
        "use_case_name": "HSBC/Mistral AI self-hosted generative-AI productivity platform",
        "use_case_description": (
            "HSBC's strategic partnership with Mistral AI to deploy self-hosted generative-AI/foundational "
            "models on HSBC's internal systems, powering an AI-powered productivity platform used by HSBC "
            "colleagues globally for tasks including client-communication drafting, hyper-personalised "
            "marketing, procurement analysis, complex financial-document analysis, multilingual translation, "
            "and accelerated prototyping of new processes/features."
        ),
        "named_tool_or_model": "Mistral AI commercial/foundational models (self-hosted)",
        "technology_partner": "Mistral AI",
        "proposed_evidence_strength": "2_moderate",
        "evidence_strength_reason": (
            "Company-primary newsroom release naming a specific technology partner and foundational-model "
            "approach, with four concrete task areas described, but no adoption-scale or quantified-outcome "
            "figure is given (unlike HSBA-OP-001's 'thousands of users') -- matches 2_moderate."
        ),
        "proposed_confidence": "medium",
        "confidence_reason": "Explicit generative-AI/LLM classification is clear, but the lack of quantified scale/outcome leaves some judgment required.",
    },
    "GSK-OP-001": {  # Generative AI for investigation-data review at 20+ sites
        "evidence_quotation": (
            "Generative AI has been implemented at over 20 sites to review historical investigation data and "
            "identify trends for improvement."
        ),
        "use_case_name": "Generative AI for manufacturing investigation-data review across 20+ sites",
        "use_case_description": (
            "GSK has implemented generative AI at over 20 manufacturing/operational sites to review historical "
            "investigation data and identify trends for improvement, alongside other data-technology "
            "applications such as predictive maintenance and environmental monitoring."
        ),
        "named_tool_or_model": "Generative AI (no specific vendor/model named in source)",
        "technology_partner": "not_applicable (no technology partner named)",
        "proposed_evidence_strength": "2_moderate",
        "evidence_strength_reason": (
            "Company-primary Annual Report disclosure with a concrete task and a quantified deployment scale "
            "(20+ sites), but no vendor/model named and no outcome metric beyond 'identify trends for "
            "improvement' -- matches 2_moderate."
        ),
        "proposed_confidence": "medium",
        "confidence_reason": "Explicit generative-AI classification and quantified site count are clear, but the brief disclosure leaves tooling and precise outcome unconfirmed.",
    },
    "REL-OP-001": {  # Lexis+ with Protege
        "evidence_quotation": (
            "Lexis+ with Protege delivers purpose-built, end-to-end legal AI workflows with a new user "
            "interface designed to make trusted legal work possible with one prompt."
        ),
        "use_case_name": "Lexis+ with Protege -- generative-AI legal research and drafting platform",
        "use_case_description": (
            "RELX's flagship legal-AI product (formerly Lexis+ AI), providing conversational legal research, "
            "personalised drafting, document analysis, summarisation and citation checking for legal "
            "professionals, grounded in 200 billion documents and general AI models from Anthropic, Google and "
            "OpenAI. At general availability, replacing the prior Lexis+ AI product."
        ),
        "named_tool_or_model": "Lexis+ with Protege (built on models from Anthropic, Google, OpenAI)",
        "technology_partner": "Anthropic; Google; OpenAI (underlying model providers)",
        "proposed_evidence_strength": "3_strong",
        "evidence_strength_reason": (
            "Company-primary corporate page describing a named, flagship, generally-available product with "
            "concrete tasks and named underlying models, plus a quantified content scale (200bn documents) -- "
            "matches 3_strong."
        ),
        "proposed_confidence": "high",
        "confidence_reason": "Explicit, detailed, company-primary description of a live commercial product leaves little ambiguity.",
    },
    "REL-OP-002": {  # PharmaPendium AI
        "evidence_quotation": (
            "PharmaPendium AI is a generative AI assistant for regulatory intelligence in drug development ... "
            "Early access users reported time savings of up to 66 percent per search and review session."
        ),
        "use_case_name": "PharmaPendium AI -- generative-AI regulatory intelligence assistant",
        "use_case_description": (
            "A generative-AI assistant layered on RELX's PharmaPendium regulatory tool, using retrieval-"
            "augmented generation to deliver citation-backed answers to regulatory questions for pharmaceutical "
            "regulatory-affairs professionals and researchers, drawing on FDA/EMA documents."
        ),
        "named_tool_or_model": "PharmaPendium AI (retrieval-augmented generation)",
        "technology_partner": "not_applicable (no external technology partner named)",
        "proposed_evidence_strength": "3_strong",
        "evidence_strength_reason": (
            "Company-primary description of a named product with a concrete task and a quantified outcome "
            "(up to 66% time savings for early-access users) -- matches 3_strong."
        ),
        "proposed_confidence": "high",
        "confidence_reason": "Explicit generative-AI/RAG classification with a quantified outcome leaves little ambiguity.",
    },
    "REL-OP-003": {  # ClinicalKey AI
        "evidence_quotation": (
            "ClinicalKey AI combines trusted, evidence-based clinical content with conversational search powered "
            "by generative AI to support clinicians in delivering high-quality patient care."
        ),
        "use_case_name": "ClinicalKey AI -- generative-AI clinical information assistant",
        "use_case_description": (
            "A generative-AI-powered conversational search tool over Elsevier's clinical content (medical "
            "textbooks, journals, reference content) to help clinicians find accurate clinical information at "
            "the point of care; tested by more than 30,000 physicians before launch and available in many "
            "markets."
        ),
        "named_tool_or_model": "ClinicalKey AI",
        "technology_partner": "OpenEvidence (co-development partner)",
        "proposed_evidence_strength": "3_strong",
        "evidence_strength_reason": (
            "Company-primary description of a named, launched product available in many markets, with a "
            "quantified pre-launch testing scale (30,000+ physicians) -- matches 3_strong."
        ),
        "proposed_confidence": "high",
        "confidence_reason": "Explicit generative-AI classification, named product, and quantified testing scale leave little ambiguity.",
    },
    "REL-OP-004": {  # Ask ICIS
        "evidence_quotation": (
            "Launched in 2024, Ask ICIS is ICIS' first of its kind generative AI assistant that delivers "
            "subscribers an unparalleled access to standout energy and chemicals market intelligence."
        ),
        "use_case_name": "Ask ICIS -- generative-AI commodities/energy market-intelligence assistant",
        "use_case_description": (
            "ICIS's (a RELX business) generative-AI assistant delivering energy and chemicals market "
            "intelligence to subscribers, leveraging over 500 million data points and available in 50+ "
            "languages, launched in 2024."
        ),
        "named_tool_or_model": "Ask ICIS",
        "technology_partner": "not_applicable (no external technology partner named)",
        "proposed_evidence_strength": "3_strong",
        "evidence_strength_reason": (
            "Company-primary description of a named, launched (2024) product with a quantified data scale "
            "(500m+ data points) and language coverage (50+ languages) -- matches 3_strong."
        ),
        "proposed_confidence": "high",
        "confidence_reason": "Explicit generative-AI classification, named product, explicit launch year and quantified scale leave little ambiguity.",
    },
    "LSEG-OP-001": {  # Financial Meeting Prep
        "evidence_quotation": (
            "This interoperability has facilitated the launch of Financial Meeting Prep, an application that "
            "uses Gen AI and data from LSEG Workspace to produce insightful briefing reports for meetings"
        ),
        "use_case_name": "Financial Meeting Prep -- Gen AI meeting-briefing report generator",
        "use_case_description": (
            "A Microsoft Teams application, developed via the LSEG/Microsoft partnership, that uses generative "
            "AI together with LSEG's licensed financial data and news to automatically generate briefing "
            "reports about public companies ahead of client meetings. Explicitly confirmed as generally "
            "available/launched by the end of 2024 in three separate passages within the AR2024."
        ),
        "named_tool_or_model": "Financial Meeting Prep (Microsoft Teams application)",
        "technology_partner": "Microsoft",
        "proposed_evidence_strength": "2_moderate",
        "evidence_strength_reason": (
            "Named, launched product with explicit 'Gen AI' language, confirmed general availability/launch by "
            "end of 2024 in three separate passages, concrete task (generate meeting-briefing reports) and "
            "identifiable user group (LSEG customers via Microsoft Teams) -- matches 2_moderate (no quantified "
            "adoption/usage metric, which would be required for 3_strong)."
        ),
        "proposed_confidence": "medium",
        "confidence_reason": (
            "Explicit generative-AI classification and launch confirmation are unambiguous, but no usage-scale "
            "metric is given -- matches medium."
        ),
    },
    "LSEG-OP-002": {  # AI Insights API
        "evidence_quotation": (
            "AI Insights API, which leverages LSEG's proprietary data and analytics to summarise large volumes "
            "of information using natural language prompts"
        ),
        "use_case_name": "AI Insights API -- Gen AI document/data summarisation",
        "use_case_description": (
            "An API product, named by LSEG as one of two examples of 'Gen AI in our offering', that uses "
            "LSEG's proprietary data and analytics to summarise large volumes of information in response to "
            "natural language prompts."
        ),
        "named_tool_or_model": "AI Insights API",
        "technology_partner": "not_applicable (no external technology partner named)",
        "proposed_evidence_strength": "1_weak",
        "evidence_strength_reason": (
            "Named product with explicit 'Gen AI' language and a concrete task (summarise large volumes of "
            "information via natural language prompts), but deployment-stage evidence is only present-tense "
            "('in our offering') rather than an explicit launch/GA date like Financial Meeting Prep -- matches "
            "1_weak."
        ),
        "proposed_confidence": "medium",
        "confidence_reason": (
            "Generative-AI classification and task are clear, but deployment-stage/scale evidence is thinner "
            "than Financial Meeting Prep -- matches medium."
        ),
    },
    "BARC-OP-001": {  # Microsoft 365 Copilot
        "evidence_quotation": (
            "M365 Copilot is Microsoft's AI-powered assistant and we have c.100,000 licences for colleagues "
            "across the bank to help improve productivity and encourage innovation."
        ),
        "use_case_name": "Microsoft 365 Copilot -- bank-wide colleague productivity assistant",
        "use_case_description": (
            "Barclays has deployed Microsoft 365 Copilot to approximately 100,000 colleague licences across "
            "the bank, described as an AI-powered assistant to help colleagues make better decisions, "
            "collaborate and focus on higher-value activities."
        ),
        "named_tool_or_model": "Microsoft 365 Copilot",
        "technology_partner": "Microsoft",
        "proposed_evidence_strength": "3_strong",
        "evidence_strength_reason": (
            "Named, live, bank-wide product deployment with an explicit, large quantified licence count "
            "(c.100,000) -- matches 3_strong."
        ),
        "proposed_confidence": "high",
        "confidence_reason": "Explicit product name, explicit scale, unambiguous live deployment.",
    },
    "AV-OP-001": {  # GenAI claims summarisation tool
        "evidence_quotation": (
            "We're deploying technology and AI at scale. For example, our GenAI claims summarisation tool is "
            "used by over 500 handlers and has halved the time that customers are on hold."
        ),
        "use_case_name": "GenAI claims summarisation tool -- UK General Insurance",
        "use_case_description": (
            "A generative-AI tool used by over 500 claims handlers in Aviva's UK General Insurance business "
            "to summarise claims, which has halved the time customers spend on hold."
        ),
        "named_tool_or_model": "GenAI claims summarisation tool (unnamed proprietary product)",
        "technology_partner": "not_applicable (no external technology partner named)",
        "proposed_evidence_strength": "3_strong",
        "evidence_strength_reason": (
            "Named task, quantified user base (500+ handlers) and quantified benefit (halved hold time), "
            "cross-year corroborated in the AR2024 -- matches 3_strong."
        ),
        "proposed_confidence": "high",
        "confidence_reason": "Explicit GenAI classification, quantified scale and quantified benefit leave little ambiguity.",
    },
    "AV-OP-002": {  # Generative AI underwriting / GP medical report summarisation
        "evidence_quotation": (
            "This year, we launched a new generative AI tool that enables our underwriters to analyse and "
            "summarise GP medical reports significantly faster, whilst maintaining the highest standards of "
            "accuracy and customer care."
        ),
        "use_case_name": "Generative-AI GP medical report summarisation tool for underwriting",
        "use_case_description": (
            "A generative-AI tool, launched in 2025, that enables Aviva's Protection-division underwriters to "
            "analyse and summarise GP medical reports faster; described elsewhere in the same report as an "
            "'industry-first AI-powered medical report summarisation tool that converts GP reports into "
            "decision-ready insights', already improving turnaround times."
        ),
        "named_tool_or_model": "Generative AI medical report summarisation tool (unnamed proprietary product)",
        "technology_partner": "not_applicable (no external technology partner named)",
        "proposed_evidence_strength": "2_moderate",
        "evidence_strength_reason": (
            "Named task, launched (live) deployment, explicit generative-AI language, but no user-count or "
            "percentage metric given (only a qualitative turnaround-time improvement claim) -- matches "
            "2_moderate."
        ),
        "proposed_confidence": "medium",
        "confidence_reason": "Explicit generative-AI classification and launch confirmation are unambiguous, but no quantified scale is given.",
    },
    "AV-OP-003": {  # Microsoft 365 Copilot Chat / GitHub Copilot
        "evidence_quotation": (
            "For example, all Aviva colleagues have Microsoft 365 Copilot Chat, and we're rolling out GitHub "
            "Copilot to all developers."
        ),
        "use_case_name": "Microsoft 365 Copilot Chat and GitHub Copilot -- company-wide colleague/developer rollout",
        "use_case_description": (
            "All Aviva colleagues have been given Microsoft 365 Copilot Chat for general productivity, and "
            "GitHub Copilot is being rolled out to all developers, as part of an identified pipeline of over "
            "150 GenAI use cases focused on process enhancements and workforce productivity."
        ),
        "named_tool_or_model": "Microsoft 365 Copilot Chat; GitHub Copilot",
        "technology_partner": "Microsoft; GitHub",
        "proposed_evidence_strength": "3_strong",
        "evidence_strength_reason": (
            "Named products, company-wide 'all colleagues'/'all developers' deployment scale, live -- matches "
            "3_strong."
        ),
        "proposed_confidence": "high",
        "confidence_reason": "Explicit product names and explicit company-wide scale leave little ambiguity.",
    },
    "SVT-OP-001": {  # Copilot / GPT-4
        "evidence_quotation": (
            "Our colleagues now have access to Copilot, which offers the capabilities of GPT-4, with "
            "commercial data protection from Microsoft."
        ),
        "use_case_name": "Copilot (GPT-4) -- colleague productivity assistant",
        "use_case_description": (
            "Severn Trent colleagues have access to Microsoft Copilot, explicitly described as offering "
            "the capabilities of GPT-4, with commercial data protection."
        ),
        "named_tool_or_model": "Microsoft Copilot (GPT-4)",
        "technology_partner": "Microsoft",
        "proposed_evidence_strength": "2_moderate",
        "evidence_strength_reason": (
            "Named product with explicit GPT-4 attribution and live deployment ('now have access'), but no "
            "quantified colleague count or usage metric is given -- matches 2_moderate."
        ),
        "proposed_confidence": "medium",
        "confidence_reason": "Explicit generative-AI/GPT-4 classification is unambiguous, but no quantified scale is given.",
    },
    "MKS-OP-001": {  # Microsoft 365 Copilot for store managers
        "evidence_quotation": (
            "I already love using AI in my daily tasks. Every morning I ask Copilot to pull together my "
            "morning huddle and shift handover notes."
        ),
        "use_case_name": "Microsoft 365 Copilot -- store manager productivity assistant",
        "use_case_description": (
            "M&S is purchasing 11,000 Microsoft 365 Copilot licences for store managers and Store Support "
            "Centre colleagues, who use it for tasks such as compiling meeting notes, sales insights, rotas "
            "and shift handovers; at least one named store manager confirmed already using it daily."
        ),
        "named_tool_or_model": "Microsoft 365 Copilot",
        "technology_partner": "Microsoft",
        "proposed_evidence_strength": "2_moderate",
        "evidence_strength_reason": (
            "Named, quantified licence purchase (11,000) with a concrete task and confirmed daily live use by "
            "at least one named early-adopter colleague, but the broader rollout is still described in "
            "future/in-progress language rather than confirmed complete -- matches 2_moderate rather than "
            "3_strong."
        ),
        "proposed_confidence": "medium",
        "confidence_reason": "Explicit product name and quantified licence count are unambiguous, but the mixed live/in-progress tense in the source introduces some deployment-stage uncertainty.",
    },
    "STAN-OP-001": {  # SC GPT
        "evidence_quotation": (
            "Our bespoke, secure SC GPT has been rolled out to support over 70,000 employees across 41 "
            "markets."
        ),
        "use_case_name": "SC GPT -- bespoke in-house LLM for employees",
        "use_case_description": (
            "Standard Chartered's own bespoke, secure large language model, SC GPT, rolled out to support "
            "over 70,000 employees across 41 markets, combined with enterprise software subscriptions for "
            "colleague workflows."
        ),
        "named_tool_or_model": "SC GPT",
        "technology_partner": "not_applicable (in-house LLM)",
        "proposed_evidence_strength": "3_strong",
        "evidence_strength_reason": (
            "Named, in-house LLM with an explicit, large quantified rollout figure (70,000+ employees across "
            "41 markets), live deployment ('has been rolled out') -- matches 3_strong."
        ),
        "proposed_confidence": "high",
        "confidence_reason": "Explicit named in-house LLM, explicit large-scale quantified rollout, unambiguous live language.",
    },
    "STAN-OP-002": {  # GitHub Copilot
        "evidence_quotation": (
            "GitHub Copilot, powered by advanced Anthropic models, assists developers in coding, testing, and "
            "documentation, allowing teams to focus more on solving complex problems and developing richer "
            "features."
        ),
        "use_case_name": "GitHub Copilot -- developer coding assistant",
        "use_case_description": (
            "Standard Chartered engineers use GitHub Copilot, powered by Anthropic models, to assist with "
            "coding, testing and documentation."
        ),
        "named_tool_or_model": "GitHub Copilot (Anthropic models)",
        "technology_partner": "GitHub; Anthropic",
        "proposed_evidence_strength": "2_moderate",
        "evidence_strength_reason": (
            "Named product with a concrete task (coding, testing, documentation) and live deployment language, "
            "but no quantified developer headcount is given -- matches 2_moderate."
        ),
        "proposed_confidence": "medium",
        "confidence_reason": "Explicit product name and task are unambiguous, but no quantified scale is given.",
    },
    "NWG-OP-001": {  # AI Digital Enabler + Microsoft Copilot Chat
        "evidence_quotation": (
            "We're rolling out two new internal GenAI tools to 99% of our colleagues across NatWest Group... "
            "the AI Digital Enabler for NatWest... We're also rolling out Microsoft Copilot Chat, a GenAI "
            "tool that uses smart AI to answer questions, generate content and find information our "
            "colleagues need quickly."
        ),
        "use_case_name": "AI Digital Enabler and Microsoft Copilot Chat -- colleague GenAI rollout",
        "use_case_description": (
            "NatWest Group rolled out two internal generative-AI tools to 99% of colleagues: the AI Digital "
            "Enabler, an internal ChatGPT-like platform for document summarisation, problem-solving, content "
            "drafting and brainstorming, and Microsoft Copilot Chat for answering questions, generating "
            "content and finding information."
        ),
        "named_tool_or_model": "AI Digital Enabler; Microsoft Copilot Chat",
        "technology_partner": "Microsoft",
        "proposed_evidence_strength": "3_strong",
        "evidence_strength_reason": (
            "Named tools with an explicit, large quantified rollout figure (99% of colleagues), live "
            "deployment ('rolling out'), explicit GenAI language throughout -- matches 3_strong."
        ),
        "proposed_confidence": "high",
        "confidence_reason": "Explicit named tools, explicit large-scale quantified rollout, unambiguous live language.",
    },
    "SSE-OP-001": {  # Nero virtual assistant
        "evidence_quotation": (
            "Nero, SSE's new virtual assistant, is now embedded in the SSE website... Available 24/7, Nero "
            "currently handles around 280 customer conversations each day."
        ),
        "use_case_name": "Nero -- generative-AI customer virtual assistant",
        "use_case_description": (
            "SSE's customer-facing virtual assistant, Nero, built on Microsoft Copilot Studio and Azure "
            "OpenAI with retrieval-augmented generation, helps customers view and pay bills and answer "
            "queries; available 24/7 and handling around 280 customer conversations per day, with a 53% "
            "increase in positive customer reactions since launch."
        ),
        "named_tool_or_model": "Nero (Microsoft Copilot Studio + Azure OpenAI)",
        "technology_partner": "Microsoft",
        "proposed_evidence_strength": "3_strong",
        "evidence_strength_reason": (
            "Named product, explicit generative-AI language ('using the generative AI to drive the "
            "interaction'), live deployment with a specific daily-volume quantified metric (280 conversations/"
            "day) and quantified outcome (53% increase in positive reactions) -- matches 3_strong."
        ),
        "proposed_confidence": "high",
        "confidence_reason": "Named product, explicit GenAI/RAG technical detail, quantified live usage and outcome all leave little ambiguity, though sourced from a technology-partner case study rather than SSE's own annual report.",
    },
    "AUTO-OP-001": {  # Co-Driver / AI Generated Descriptions
        "evidence_quotation": (
            "Co-Driver is an umbrella brand for a range of AI-enabled products... The first three products "
            "include Smart Image Management, AI Generated Descriptions and Vehicle Highlights, all of which "
            "assist retailers in getting an advert live quickly and accurately."
        ),
        "use_case_name": "Co-Driver (AI Generated Descriptions) -- generative-AI vehicle-listing assistant",
        "use_case_description": (
            "Auto Trader's Co-Driver suite of AI-enabled retailer tools, including AI Generated Descriptions "
            "(which uses large language models to write vehicle descriptions) and Smart Image Management; the "
            "Board's own risk disclosure confirms LLMs are used 'in real-time' with mitigations already in "
            "place."
        ),
        "named_tool_or_model": "Co-Driver; AI Generated Descriptions (unnamed LLM)",
        "technology_partner": "not_applicable (no external technology partner named)",
        "proposed_evidence_strength": "2_moderate",
        "evidence_strength_reason": (
            "Named product suite with a concrete task and the company's own Board-level confirmation of "
            "real-time LLM use with mitigations in place (not merely planned), but no retailer-count or "
            "advert-count metric is confirmed within the approved sources this session -- matches 2_moderate."
        ),
        "proposed_confidence": "medium",
        "confidence_reason": "Explicit LLM classification and live/real-time deployment are confirmed by the Board's own language, but no quantified usage scale is given in the approved sources.",
    },
    "ITRK-OP-001": {  # Synthesia-powered training video product
        "evidence_quotation": (
            "Intertek People Assurance has partnered with Synthesia, the UK's largest generative AI media "
            "company, to deliver consistent, high-quality training content across our global frontline teams. "
            "By integrating advanced AI-powered video technology into our products, Intertek's People "
            "Assurance clients can scale dynamic, multi-lingual, branded training videos to local teams at "
            "speed and with lower production costs."
        ),
        "use_case_name": "Synthesia-powered generative-AI training-video product (Intertek People Assurance)",
        "use_case_description": (
            "Intertek's People Assurance business line has partnered with Synthesia, a generative-AI video "
            "platform, to let its clients create multi-lingual, branded training videos for frontline teams "
            "at speed and lower cost."
        ),
        "named_tool_or_model": "Synthesia",
        "technology_partner": "Synthesia",
        "proposed_evidence_strength": "2_moderate",
        "evidence_strength_reason": (
            "Named generative-AI technology partner (Synthesia) integrated into a live, named product line "
            "with a concrete task (multi-lingual training-video generation) and identifiable user group "
            "(People Assurance clients), but no usage-scale metric (number of clients/videos) is given -- "
            "matches 2_moderate."
        ),
        "proposed_confidence": "medium",
        "confidence_reason": "Explicit named generative-AI partner and concrete task are unambiguous, but no quantified scale is given and this is a customer-facing product rather than internal use, requiring a small amount of interpretive judgement consistent with the RELX precedent.",
    },
    "CTEC-OP-001": {  # Microsoft Copilot + Synthesia
        "evidence_quotation": (
            "Deploying enterprise-scale AI solutions such as Microsoft Copilot, SmartCat (a translation and "
            "localisation platform) and Synthesia (a video generation platform) and expanding the deployment "
            "of AI-powered tools like Talkdesk in customer interaction centres."
        ),
        "use_case_name": "Microsoft Copilot and Synthesia -- enterprise-scale generative-AI deployment",
        "use_case_description": (
            "Convatec is deploying enterprise-scale generative-AI solutions including Microsoft Copilot (for "
            "general employee productivity) and Synthesia (for AI-generated video content), as part of its "
            "digital transformation and AI adoption programme."
        ),
        "named_tool_or_model": "Microsoft Copilot; Synthesia",
        "technology_partner": "Microsoft; Synthesia",
        "proposed_evidence_strength": "2_moderate",
        "evidence_strength_reason": (
            "Two named, live, enterprise-scale generative-AI products, but no specific user-count or task-"
            "outcome metric is given (only 'enterprise-scale' qualitatively) -- matches 2_moderate."
        ),
        "proposed_confidence": "medium",
        "confidence_reason": "Explicit named products and live/enterprise-scale deployment language are unambiguous, but no quantified scale is given.",
    },
    "ENT-OP-001": {  # SportingBOT
        "evidence_quotation": (
            "SportingBOT is a generative AI chatbot that serves as a personalised betting assistant... The AI "
            "chatbot reached over 65,000 users."
        ),
        "use_case_name": "SportingBOT -- generative-AI personalised betting assistant",
        "use_case_description": (
            "Entain's Sportingbet Brazil business launched SportingBOT, a generative-AI chatbot that acts as a "
            "personalised betting assistant, integrating live odds pricing, real-time match data and "
            "Sportingbet promotions/T&Cs to answer customer questions conversationally; reached over 65,000 "
            "users, with plans to expand to Spain and build a dedicated Customer Service version."
        ),
        "named_tool_or_model": "SportingBOT",
        "technology_partner": "not_applicable (Sportsradar named as a real-time data provider, not the GenAI technology partner)",
        "proposed_evidence_strength": "3_strong",
        "evidence_strength_reason": (
            "Named, live generative-AI product with a concrete task, quantified real-world user base (65,000+ "
            "users) and quantified engagement metrics (6x targeted visits, 40% visitor engagement) -- matches "
            "3_strong despite being framed as an initial single-market rollout within a broader pilot-then-"
            "scale strategy."
        ),
        "proposed_confidence": "high",
        "confidence_reason": "Explicit generative-AI classification, named product and quantified real-world usage leave little ambiguity.",
    },
    "SDR-OP-001": {  # GAiiA
        "evidence_quotation": (
            "Schroders Capital...today unveils its Generative AI Investment Analyst (GAiiA) platform. This "
            "innovation is designed to speed up the analysis of large volumes of data, enabling our private "
            "equity investment [professionals]... GAiiA already assisted in more than 40 investment cases."
        ),
        "use_case_name": "GAiiA -- Generative AI Investment Analyst",
        "use_case_description": (
            "Schroders Capital's proprietary Generative AI Investment Analyst (GAiiA), used by private equity "
            "investment professionals to screen large volumes of data and help draft investment summaries; "
            "assisted in more than 40 investment cases since launch."
        ),
        "named_tool_or_model": "GAiiA (Generative AI Investment Analyst)",
        "technology_partner": "not_applicable (proprietary/internal platform)",
        "proposed_evidence_strength": "3_strong",
        "evidence_strength_reason": (
            "Named, launched, proprietary generative-AI product with a concrete task, identifiable user group "
            "and a quantified usage figure (40+ investment cases) -- matches 3_strong."
        ),
        "proposed_confidence": "high",
        "confidence_reason": "Explicit generative-AI classification, named product, launch confirmation and quantified usage leave little ambiguity.",
    },
    "SDR-OP-002": {  # Genie
        "evidence_quotation": (
            "Schroders has made its internal-only AI assistant, Genie, available to all employees globally. "
            "Leveraging the latest GPT models, Genie is now used by over 1,000 colleagues across the firm "
            "each day."
        ),
        "use_case_name": "Genie -- GPT-based internal colleague assistant",
        "use_case_description": (
            "Schroders' internal-only AI assistant, Genie, built on the latest GPT models and available to "
            "all employees globally; used by over 1,000 colleagues across the firm each day."
        ),
        "named_tool_or_model": "Genie (GPT-based)",
        "technology_partner": "not_applicable (proprietary/internal platform, built on third-party GPT models)",
        "proposed_evidence_strength": "3_strong",
        "evidence_strength_reason": (
            "Named, live, globally-available generative-AI assistant with an explicit large quantified daily-"
            "usage figure (1,000+ colleagues/day) -- matches 3_strong."
        ),
        "proposed_confidence": "high",
        "confidence_reason": "Explicit GPT-based classification, named product, global availability and quantified daily usage leave little ambiguity.",
    },
    "PSON-OP-001": {  # Claude / Claude Code
        "evidence_quotation": (
            "we are also deploying Claude and Claude Code across engineering and business functions to "
            "accelerate development and enhance productivity and quality"
        ),
        "use_case_name": "Claude and Claude Code -- engineering and business-function deployment",
        "use_case_description": (
            "Pearson is deploying Anthropic's Claude and Claude Code across engineering and business functions "
            "to accelerate software development and enhance productivity and quality. Split out from the "
            "over-consolidated strategic staging row PSON-STR-004, which bundled this concrete, named-tool "
            "deployment with vaguer strategic AI-adoption language and a forward-looking, not-yet-live "
            "'transformative knowledge agent' mention."
        ),
        "named_tool_or_model": "Claude; Claude Code",
        "technology_partner": "Anthropic",
        "proposed_evidence_strength": "2_moderate",
        "evidence_strength_reason": (
            "Named, live generative-AI tools (Claude, Claude Code) deployed across a specific function "
            "(engineering) with a stated task (development acceleration) and productivity/quality benefit "
            "claimed, but no quantified usage figure or user count given -- matches 2_moderate."
        ),
        "proposed_confidence": "high",
        "confidence_reason": "Explicit named tools and present-tense live-deployment language ('are also deploying') leave little ambiguity about GenAI classification and live status, even without a quantified metric.",
    },
    "CNA-OP-001": {  # Microsoft 365 Copilot Agent Builder -- email compliance agent
        "evidence_quotation": (
            "The company started by enabling all employees to build simple AI agents directly inside "
            "Microsoft 365 Copilot using Agent Builder...One agent, for example, checks email content to "
            "ensure compliance with company policies, saving employees hundreds of hours a year."
        ),
        "use_case_name": "Microsoft 365 Copilot Agent Builder -- email compliance-checking agent",
        "use_case_description": (
            "Centrica enabled all employees to build simple AI agents inside Microsoft 365 Copilot using "
            "Agent Builder; one live agent checks email content for compliance with company policy, saving "
            "employees hundreds of hours a year. Split out from the over-consolidated rejected-staging row "
            "CNA-REJ-028, which bundled this live agent with two further agents (an Employee Self-Service "
            "agent and a career-development-recommendation agent) that the same source explicitly describes "
            "as still being customised/in development -- those two are NOT included in this finding."
        ),
        "named_tool_or_model": "Microsoft 365 Copilot Agent Builder",
        "technology_partner": "Microsoft",
        "proposed_evidence_strength": "2_moderate",
        "evidence_strength_reason": (
            "Company-wide live deployment ('all employees') of a named generative-AI tool for a specific "
            "compliance-checking task, with a quantified qualitative benefit claim ('hundreds of hours a "
            "year') but no precise numeric hours or adoption-rate figure, and sourced from an official "
            "technology-partner case study rather than a company-primary document -- matches 2_moderate."
        ),
        "proposed_confidence": "medium",
        "confidence_reason": "Official Microsoft technology-partner case study naming Centrica specifically and describing a live, specific deployment, but evidence_origin=technology_partner (not company-confirmed) warrants medium rather than high confidence.",
    },
    "KGF-OP-001": {  # Hello Casto / Athena
        "evidence_quotation": (
            "Kingfisher has launched the first AI-powered assistant in the home improvement sector, harnessing "
            "the capability of generative AI to support customers with their DIY projects...the virtual "
            "assistant answers customers' DIY queries and provides step-by-step advice on a range of home "
            "improvement projects, as well as tailored product recommendations...Kingfisher's data team has "
            "developed a proprietary AI orchestration framework, named Athena. This will manage prompting and "
            "interaction with a range of large language models."
        ),
        "use_case_name": "Hello Casto -- generative-AI DIY assistant (built on the Athena framework)",
        "use_case_description": (
            "Kingfisher launched Hello Casto, a generative-AI-powered virtual assistant for DIY customers, "
            "initially at Castorama France; it answers customer DIY queries and gives step-by-step project "
            "advice and tailored product recommendations. It runs on Kingfisher's proprietary Athena "
            "orchestration framework, which manages prompting and interaction with a range of large language "
            "models. The FY2024-25 Annual Report corroborates continued live status two years on, citing "
            "c. 500,000 interactions with Hello Casto since its 2023 launch."
        ),
        "named_tool_or_model": "Hello Casto (built on Athena, Kingfisher's proprietary multi-LLM orchestration framework)",
        "technology_partner": "not_applicable (proprietary in-house framework spanning multiple third-party LLMs, none individually named)",
        "proposed_evidence_strength": "3_strong",
        "evidence_strength_reason": (
            "Named, live generative-AI product with a concrete task (DIY query answering, project advice, "
            "product recommendations), an identifiable user group (customers) and a quantified usage figure "
            "corroborated two years post-launch (c. 500,000 interactions) -- matches 3_strong."
        ),
        "proposed_confidence": "high",
        "confidence_reason": "Explicit generative-AI/LLM classification, named product, and a quantified usage figure independently corroborated in a later company-primary annual report leave little ambiguity.",
    },
    "RTO-OP-001": {  # Google Gemini AI for Google Workspace
        "evidence_quotation": (
            "We launched Google Gemini AI as an integrated tool within email and documents, and as a "
            "standalone app to enable further efficiencies. By the end of 2025, all colleagues worldwide had "
            "access to Gemini AI, demonstrating a strong commitment to digital transformation...In just six "
            "months, colleagues used Gemini AI on over one million occasions to support their work."
        ),
        "use_case_name": "Google Gemini AI -- company-wide Workspace productivity assistant",
        "use_case_description": (
            "Rentokil Initial rolled out Google Gemini AI as an integrated generative-AI tool within email "
            "and documents (and as a standalone app) across its entire c.63,400-strong global workforce; by "
            "the end of 2025 all colleagues worldwide had access, with over one million uses recorded in the "
            "first six months."
        ),
        "named_tool_or_model": "Google Gemini AI (Gemini for Google Workspace)",
        "technology_partner": "Google",
        "proposed_evidence_strength": "3_strong",
        "evidence_strength_reason": (
            "Named, live generative-AI product rolled out company-wide to the entire global workforce with a "
            "large quantified usage figure (1,000,000+ uses in six months) -- matches 3_strong."
        ),
        "proposed_confidence": "high",
        "confidence_reason": "Explicit named product, company-wide live deployment and a specific quantified usage figure leave little ambiguity.",
    },
    "HSX-OP-001": {  # Gemini-powered lead underwriting model
        "evidence_quotation": (
            "Hiscox has now gone live with the London insurance market's first lead underwriting model "
            "enhanced by generative AI...Risks that are in scope are assessed using Google Cloud's Gemini "
            "large language model, and the process generates an email for the broker with pricing and other "
            "data already completed, ready for underwriter review. As a result, Hiscox can provide a broker "
            "with an insurance quote in a matter of minutes."
        ),
        "use_case_name": "Gemini-powered lead underwriting model (sabotage and terrorism line)",
        "use_case_description": (
            "Hiscox, combining its proprietary Hiscox AI Laboratories (Hailo) framework with Google Cloud's "
            "Gemini large language model, launched the London insurance market's first generative-AI-enhanced "
            "lead underwriting model, initially for the sabotage and terrorism line of business (US/Canada "
            "renewals, excluding NY/Chicago metro areas). Risks in scope are assessed by the model, which "
            "drafts a broker email with pricing and data pre-completed for underwriter review, cutting the "
            "submission-to-quote time from three days to three minutes."
        ),
        "named_tool_or_model": "Google Cloud Gemini (within Hiscox AI Laboratories / Hailo)",
        "technology_partner": "Google Cloud",
        "proposed_evidence_strength": "3_strong",
        "evidence_strength_reason": (
            "Named, live generative-AI product (Gemini LLM) with a concrete task (lead underwriting quote "
            "generation), identifiable user group (underwriters/brokers) and a large quantified outcome "
            "(3 days -> 3 minutes) -- matches 3_strong."
        ),
        "proposed_confidence": "high",
        "confidence_reason": "Official company press release, explicit named LLM, live-launch confirmation and a specific quantified outcome leave little ambiguity.",
    },
    "HSX-OP-002": {  # Microsoft 365 Copilot for claims
        "evidence_quotation": (
            "Hiscox, the global specialist insurer, is rolling out the generative AI assistant Microsoft 365 "
            "Copilot to its 3,000+ employees across 14 countries...Identifying and recording the key "
            "information from a new claim now takes him as little as 10 minutes -- a task that previously "
            "took up to an hour."
        ),
        "use_case_name": "Microsoft 365 Copilot -- claims-handling productivity assistant",
        "use_case_description": (
            "Hiscox rolled out Microsoft 365 Copilot to its 3,000+ employees across 14 countries (up from an "
            "initial 300), including in the claims team, where it is used to extract and summarise "
            "information from emails, medical evidence and legal advice to support claims handling; a senior "
            "technical claims underwriter reported the time to identify and record key claim information "
            "falling from up to an hour to as little as 10 minutes."
        ),
        "named_tool_or_model": "Microsoft 365 Copilot",
        "technology_partner": "Microsoft",
        "proposed_evidence_strength": "3_strong",
        "evidence_strength_reason": (
            "Named, live generative-AI product rolled out company-wide (3,000+ employees, 14 countries) with "
            "a concrete task (claims handling/document summarisation) and a quantified time-saving outcome "
            "(up to an hour -> 10 minutes), corroborated with a named employee -- matches 3_strong for detail, "
            "though sourced from an official technology-partner case study rather than a company-primary "
            "document."
        ),
        "proposed_confidence": "medium",
        "confidence_reason": "Official Microsoft technology-partner case study naming Hiscox specifically and describing a live, specific, quantified deployment, but evidence_origin=technology_partner (not company-confirmed) warrants medium rather than high confidence, consistent with the project's standard treatment of partner-sourced findings.",
    },
    "INVP-OP-001": {  # Microsoft Copilot for Sales
        "evidence_quotation": (
            "Investec seized the opportunity to use the generative AI features of Copilot for Sales to save "
            "bankers time...Investec immediately recognized the promise of AI and was the very first customer "
            "to go live in production with Microsoft Copilot for Sales...Investec launched Microsoft Copilot "
            "for Sales in Outlook and Teams for 900 bankers in the UK...'We're estimating that we're making "
            "approximately 200 hours of savings a year across the bank.'"
        ),
        "use_case_name": "Microsoft Copilot for Sales -- banker productivity assistant",
        "use_case_description": (
            "Investec was the first Microsoft customer to go live in production with Copilot for Sales, "
            "launching it in Outlook and Teams for 900 UK bankers (rolling out to a further 700 bankers in "
            "South Africa). Copilot generates meeting-recap and email-chain summaries saved directly to client "
            "records, drafts client emails, and surfaces CRM insights within the flow of work; Investec "
            "estimates approximately 200 hours of colleague time saved per year across the bank."
        ),
        "named_tool_or_model": "Microsoft Copilot for Sales",
        "technology_partner": "Microsoft",
        "proposed_evidence_strength": "3_strong",
        "evidence_strength_reason": (
            "Named, live generative-AI product (first-customer production deployment) rolled out to 900 UK "
            "bankers with a further 700-banker rollout underway in South Africa, with a quantified time-saving "
            "estimate (~200 hours/year across the bank) -- matches 3_strong."
        ),
        "proposed_confidence": "medium",
        "confidence_reason": "Official Microsoft technology-partner case study naming Investec specifically and describing a live, specific, quantified deployment with named individual employees, but evidence_origin=technology_partner (not company-confirmed) warrants medium rather than high confidence, consistent with the project's standard treatment of partner-sourced findings.",
    },
    "SPX-OP-001": {  # MiM proprietary large language model
        "evidence_quotation": (
            "With a focus on enhancing sales engineer productivity, we have also continued to refine and "
            "develop our proprietary large language model-based training and solutions tool, MiM...During "
            "2025, MiM was piloted with 200 sales colleagues, with usage freeing up approximately four hours "
            "of their time per person, per week...MiM has now been rolled out to over 1,000 sales colleagues "
            "as we expand its sector-based content."
        ),
        "use_case_name": "MiM -- proprietary large language model for sales-engineer training and productivity",
        "use_case_description": (
            "Spirax Group developed 'MiM', a proprietary large language model built on the Group's technical, "
            "sector and application knowledge, to reduce training time for new sales engineers and improve "
            "the productivity of experienced ones. Piloted with 200 sales colleagues during 2025 (saving "
            "approximately four hours per person per week, redeployed into customer-facing activity), MiM has "
            "since been rolled out to over 1,000 sales colleagues as its sector-based content is expanded."
        ),
        "named_tool_or_model": "MiM",
        "technology_partner": "",
        "proposed_evidence_strength": "3_strong",
        "evidence_strength_reason": (
            "Company-primary source names a specific, self-developed large language model tool with a clear "
            "task (sales-engineer training/productivity), a measurable outcome (~4 hours/person/week freed "
            "up during the 2025 pilot), and evidence of scaling beyond pilot (pilot of 200 -> rolled out to "
            "over 1,000 sales colleagues) -- matches 3_strong."
        ),
        "proposed_confidence": "high",
        "confidence_reason": "Company-primary annual report describing its own internally developed tool in detail across two consecutive annual reports, with explicit 'large language model' and 'generative AI' language and a quantified benefit -- directly and unambiguously supported.",
    },
    "MTLN-OP-001": {  # Avokado CORTEX GenAI digital assistant
        "evidence_quotation": (
            "...d) a smart GenAI CORTEX digital assistant for B2B customers...Project Avokado CORTEX: "
            "creation of an Energy Assistant based on GenAI. The smart energy assistant CORTEX operates on "
            "top of the AVOX platform and acts as an assistant for B2B customers in matters of energy "
            "management and energy cost (budgeting)."
        ),
        "use_case_name": "Avokado CORTEX -- GenAI energy-management assistant for B2B customers",
        "use_case_description": (
            "METLEN's technology subsidiary Avokado (METLEN Group is sole shareholder) offers 'Avokado "
            "CORTEX', a named GenAI digital assistant operating on top of Avokado's AVOX platform, which "
            "assists B2B customers with energy management and energy cost budgeting. Described consistently "
            "across both the FY2024 and FY2025 annual reports as part of Avokado's product portfolio, with "
            "its creation described as an active project during 2025."
        ),
        "named_tool_or_model": "Avokado CORTEX",
        "technology_partner": "",
        "proposed_evidence_strength": "2_moderate",
        "evidence_strength_reason": (
            "Company-primary source names a specific GenAI product (Avokado CORTEX) with a clear task "
            "(energy-management/cost-budgeting assistant) and user group (B2B customers), but deployment "
            "stage is somewhat ambiguous (listed as an offered product while also described as 'underway' "
            "during 2025) and no quantified outcome or customer count is given -- matches 2_moderate."
        ),
        "proposed_confidence": "medium",
        "confidence_reason": "Company-primary annual report describing its own subsidiary's own named product with explicit 'GenAI' language across two consecutive annual reports, but some interpretive judgment is required to reconcile 'offers' (implying availability) with 'creation...underway' (implying still in development) into a single deployment stage.",
    },
    "BGEO-OP-001": {  # Georgian-language Generative AI chatbot
        "evidence_quotation": (
            "We have embedded AI across our operations -- from our GenAI chatbot that resolves 65% of queries "
            "without human intervention whilst achieving a 91% customer satisfaction score...We upgraded to a "
            "sophisticated Georgian-language Generative AI chatbot, delivering intelligent, personalised "
            "interactions."
        ),
        "use_case_name": "Georgian-language Generative AI customer-service chatbot",
        "use_case_description": (
            "Bank of Georgia's in-house-developed Generative AI chatbot -- the only such large-scale "
            "Georgian-language solution in the market -- resolves 65% of customer queries without human "
            "intervention, achieving a 91% customer satisfaction score (2025); the prior-generation chatbot "
            "offloaded 25% of Contact Center call volume (2024)."
        ),
        "named_tool_or_model": "In-house Georgian-language Generative AI chatbot",
        "technology_partner": "",
        "proposed_evidence_strength": "3_strong",
        "evidence_strength_reason": (
            "Company-primary source names a specific, self-developed generative-AI chatbot with a clear task "
            "(customer query resolution), broad customer-facing deployment, and quantified outcomes (65% "
            "autonomous resolution rate, 91% CSAT, 25% Contact Center volume offload) -- matches 3_strong."
        ),
        "proposed_confidence": "high",
        "confidence_reason": "Company-primary annual report describing its own in-house-developed product in detail across two consecutive annual reports, with explicit 'Generative AI' language and quantified outcomes -- directly and unambiguously supported.",
    },
    "BGEO-OP-002": {  # Enterprise AI platform / employee-built AI assistants
        "evidence_quotation": (
            "We enabled non-technical teams to automate tasks and unlock efficiencies through our enterprise "
            "AI platform...Employees built 300+ custom AI assistants, freeing up 6,600 hours per month for "
            "higher-value work. Weekly adoption rate increased from 10% to 56% in six months (80% in "
            "back-office roles). 310,000+ monthly interactions...40% reduction in document analysis time."
        ),
        "use_case_name": "Enterprise AI platform -- employee-built custom AI assistants",
        "use_case_description": (
            "An internal 'enterprise AI platform' enabling non-technical Bank of Georgia employees to build "
            "custom AI assistants; by 2025, employees had built over 300 custom assistants, freeing up "
            "approximately 6,600 hours per month, with weekly adoption rising from 10% to 56% within six "
            "months (80% in back-office roles), over 310,000 monthly interactions, and a 40% reduction in "
            "document analysis time. Tracked as a formal executive KPI ('GenAI engagement')."
        ),
        "named_tool_or_model": "Enterprise AI platform (unnamed proprietary internal platform)",
        "technology_partner": "",
        "proposed_evidence_strength": "3_strong",
        "evidence_strength_reason": (
            "Company-primary source describes a specific internal generative-AI-assistant-building platform "
            "with clear tasks, a defined user group (employees, especially back-office roles), and multiple "
            "quantified outcomes (300+ assistants built, ~6,600 hours/month freed, 10%->56% weekly adoption, "
            "310,000+ monthly interactions, 40% reduction in document analysis time), plus formal executive "
            "KPI tracking -- matches 3_strong."
        ),
        "proposed_confidence": "high",
        "confidence_reason": "Company-primary annual report describing its own internal platform in detail, with explicit AI/GenAI language, multiple quantified outcomes, and confirmation via a separate formal 'GenAI engagement' executive KPI disclosure -- directly and unambiguously supported.",
    },
    "SGRO-OP-001": {  # Microsoft Copilot company-wide rollout
        "evidence_quotation": (
            "Continuation of our digital transformation programme, including the rollout of Copilot to all "
            "employees with a structured training programme; and the introduction of a new facilities "
            "management system."
        ),
        "use_case_name": "Microsoft Copilot -- company-wide employee rollout",
        "use_case_description": (
            "SEGRO rolled out Microsoft Copilot to all employees as part of its digital transformation "
            "programme, supported by a structured training programme. No specific task, business function, "
            "or outcome is described for this initiative in the source."
        ),
        "named_tool_or_model": "Microsoft Copilot",
        "technology_partner": "Microsoft",
        "proposed_evidence_strength": "2_moderate",
        "evidence_strength_reason": (
            "Company-primary source names a specific, live, company-wide generative-AI product rollout "
            "(Copilot to all employees, with a structured training programme), but no task, business "
            "function, benefit, or outcome is described -- matches 2_moderate (specific use case/deployment "
            "stage clear, but detail on scale of use/outcome incomplete)."
        ),
        "proposed_confidence": "high",
        "confidence_reason": "Company-primary annual report directly and unambiguously naming Microsoft Copilot and describing a company-wide employee rollout with a structured training programme.",
    },
    "BA-OP-001": {  # LLM/generative-AI natural-language drone command
        "evidence_quotation": (
            "This year, we demonstrated the use of Large Language Models (LLMs) and generative AI to operate "
            "drones...non-expert users can command the drones using natural language, which drastically "
            "reduces training and operator workload...the drone can understand the intent of the operator "
            "and use generative AI to reconfigure itself to perform unexpected tasks like search and rescue "
            "or identifying specific enemy activities."
        ),
        "use_case_name": "LLM/generative-AI natural-language drone command and self-reconfiguration",
        "use_case_description": (
            "BAE Systems demonstrated the use of Large Language Models and generative AI to allow non-expert "
            "operators to command drones using natural language, and to let drones use generative AI to "
            "reconfigure themselves for unexpected tasks (e.g. search and rescue, identifying enemy "
            "activity), with operator oversight maintained throughout."
        ),
        "named_tool_or_model": "Unnamed LLM/generative-AI drone command capability",
        "technology_partner": "",
        "proposed_evidence_strength": "2_moderate",
        "evidence_strength_reason": (
            "Company-primary source explicitly names LLMs and generative AI for a specific task (natural-"
            "language drone command and self-reconfiguration) with a clear user group (drone operators), but "
            "deployment stage is a demonstration rather than a confirmed live/scaled rollout, and no "
            "quantified outcome is given -- matches 2_moderate."
        ),
        "proposed_confidence": "high",
        "confidence_reason": "Company-primary annual report directly and unambiguously naming both 'Large Language Models (LLMs)' and 'generative AI' for a specific, described capability.",
    },
    "BA-OP-002": {  # Typhoon AI maintenance assistant
        "evidence_quotation": (
            "We have now demonstrated a Typhoon AI assistant that can give clear answers to complex "
            "maintenance queries. The LLM it uses is generated from training manuals based on thousands of "
            "hours of real-world experience with the aircraft...step-by-step instructions along with "
            "references to exactly where it found the information...able to give answers in a number of "
            "languages, so would be useful for international teams working together."
        ),
        "use_case_name": "Typhoon AI maintenance assistant (LLM trained on maintenance manuals)",
        "use_case_description": (
            "BAE Systems demonstrated a Typhoon AI assistant using an LLM trained on aircraft maintenance "
            "manuals to answer complex maintenance queries with step-by-step, sourced instructions in "
            "multiple languages, aimed at faster support responses and increased aircraft uptime."
        ),
        "named_tool_or_model": "Typhoon AI assistant",
        "technology_partner": "",
        "proposed_evidence_strength": "2_moderate",
        "evidence_strength_reason": (
            "Company-primary source names a specific tool (Typhoon AI assistant) with an explicit LLM basis, "
            "a clear task (maintenance-query answering) and multi-language capability, but deployment stage "
            "is a demonstration rather than confirmed live/scaled, and the exact user population is not "
            "quantified -- matches 2_moderate."
        ),
        "proposed_confidence": "high",
        "confidence_reason": "Company-primary annual report directly and unambiguously naming the 'Typhoon AI assistant' and its LLM basis, with a detailed functional description.",
    },
    "BA-OP-003": {  # Operationalised AI cyber-threat-insight system
        "evidence_quotation": (
            "We have also operationalised an AI system to help our customers fight cyber threats. This again "
            "uses a LLM trained on nearly a decade of our expert analysis in cyber threats...The system is "
            "able to generate actionable insight for users and recommendations on how to proceed on a range "
            "of topics, from vulnerabilities in space systems through to mitigating specific tools used by "
            "criminal groups and hostile intelligence services."
        ),
        "use_case_name": "Operationalised AI cyber-threat-insight system for customers",
        "use_case_description": (
            "BAE Systems has operationalised an AI system, using an LLM trained on nearly a decade of its own "
            "cyber-threat expert analysis, to generate actionable insight and recommendations for customers "
            "on cyber-threat topics spanning space-systems vulnerabilities to criminal/hostile-actor tooling."
        ),
        "named_tool_or_model": "Unnamed operationalised AI cyber-threat-insight system",
        "technology_partner": "",
        "proposed_evidence_strength": "2_moderate",
        "evidence_strength_reason": (
            "Company-primary source explicitly states the system has been 'operationalised' (a stronger, "
            "live-status claim than 'demonstrated') with a clear LLM basis, task (cyber-threat insight "
            "generation) and user group (customers), but no user count, rollout scale, or quantified outcome "
            "is given -- matches 2_moderate."
        ),
        "proposed_confidence": "high",
        "confidence_reason": "Company-primary annual report directly and unambiguously stating the system is 'operationalised' with an explicit LLM basis and described function.",
    },
}


def build_operational_proposal(slug: str, ticker: str, company: str, sector: str, staging_rows: list[dict],
                                proposed_manifest_rows: list[dict], existing_uc_rows: list[dict],
                                problems: list[str]) -> list[dict]:
    existing_ids = {(r.get("record_id") or "").strip() for r in existing_uc_rows}
    id_prefix = ticker.split(".")[0]
    next_num = 1
    while f"{id_prefix}-UC-{next_num:03d}" in existing_ids:
        next_num += 1

    proposed: list[dict] = []
    for r in staging_rows:
        decision = (r.get("reviewer_decision") or "").strip()
        staging_id = r["staging_id"]
        if decision not in OPERATIONAL_PROMOTABLE_DECISIONS:
            pc.report(f"  [excluded] {staging_id}: reviewer_decision='{decision}' -- not eligible for promotion.")
            continue
        if already_promoted(staging_id, existing_uc_rows, "reviewer_notes"):
            pc.report(f"  [idempotent] {staging_id} already promoted -- skipping.")
            continue

        override = OPERATIONAL_OVERRIDES.get(staging_id)
        if override is None:
            problems.append(f"BLOCKED {staging_id}: no operational field-mapping override defined; would require inventing evidence_quotation/use_case fields.")
            continue

        local_filename = r["local_filename"]
        source_id = manifest_source_id_for(local_filename, proposed_manifest_rows)
        if not source_id:
            problems.append(f"BLOCKED {staging_id}: no source_id resolved for '{local_filename}' -- source_manifest promotion must run first.")
            continue

        for field, allowed in (
            ("provisional_primary_business_function", BUSINESS_FUNCTION_VALUES),
            ("provisional_secondary_business_function", BUSINESS_FUNCTION_VALUES),
            ("provisional_user_group", USER_GROUP_VALUES),
            ("provisional_orientation", ORIENTATION_VALUES),
            ("provisional_deployment_stage", DEPLOYMENT_STAGE_VALUES),
        ):
            value = (r.get(field) or "").strip()
            if value not in allowed:
                problems.append(f"BLOCKED {staging_id}: {field} value '{value}' not in controlled vocabulary.")
                continue

        claimed_benefits = [b.strip() for b in (r.get("provisional_claimed_benefits") or "").split(";") if b.strip()]
        invalid_benefits = [b for b in claimed_benefits if b not in CLAIMED_BENEFIT_VALUES]
        if invalid_benefits:
            problems.append(f"BLOCKED {staging_id}: claimed_benefits value(s) {invalid_benefits} not in controlled vocabulary.")
            continue

        manifest_row = next(m for m in proposed_manifest_rows if m["local_filename"] == local_filename)
        record_id = f"{id_prefix}-UC-{next_num:03d}"
        next_num += 1

        benefit_evidence = "observed_unquantified" if r["provisional_deployment_stage"] == "live_limited" else "expected"

        row = {
            "record_id": record_id,
            "company": company,
            "ticker": ticker,
            "sector": sector,
            "source_id": source_id,
            "document_title": manifest_row["document_title"],
            "document_category": r["document_category"],
            "evidence_origin": r["evidence_origin"],
            "publication_date": manifest_row["publication_date"],
            "url": manifest_row["url"],
            "local_filename": local_filename,
            "page_or_section": r["page_or_section"],
            "evidence_quotation": override["evidence_quotation"],
            "is_genai": "yes",
            "use_case_name": override["use_case_name"],
            "use_case_description": override["use_case_description"],
            "primary_business_function": r["provisional_primary_business_function"],
            "secondary_business_function": r["provisional_secondary_business_function"],
            "user_group": r["provisional_user_group"],
            "orientation": r["provisional_orientation"],
            "deployment_stage": r["provisional_deployment_stage"],
            "named_tool_or_model": override["named_tool_or_model"],
            "technology_partner": override["technology_partner"],
            "claimed_benefits": r["provisional_claimed_benefits"],
            "benefit_evidence": benefit_evidence,
            "quantified_metric": "not_applicable",
            "risk_or_limitation_discussed": r["provisional_risk_or_limitation"] if r["provisional_risk_or_limitation"] in RISK_YES_NO_UNCLEAR else "unclear",
            "human_review": "no",
            "privacy_control": "no",
            "security_control": "no",
            "accuracy_control": "no",
            "bias_fairness_control": "no",
            "employee_training": "no",
            "responsible_ai_framework": "no",
            "monitoring_audit": "no",
            "restricted_use_control": "no",
            "impact_assessment_control": "no",
            "evidence_strength": override["proposed_evidence_strength"],
            "confidence": override["proposed_confidence"],
            "review_status": "reviewed_confirmed",
            "reviewer_notes": (
                f"Promoted from staging {staging_id} (reviewer_decision={decision}). evidence_strength/confidence "
                f"explicitly approved by the human operator: {override['evidence_strength_reason']}"
            ),
            "supporting_source_ids": "",
            "duplicate_of_record_id": "",
            "coded_by": "human",  # staging rows received explicit human review/approval decisions; 'human' is an allowed value in 03_CODING_MANUAL.md field 6
            "model_version": "",
            "coded_date": today_date(),
        }
        proposed.append(row)
    return proposed


# ---------------------------------------------------------------------------
# Strategic -> strategic_capability_building_findings.csv
# ---------------------------------------------------------------------------
STRATEGIC_EVIDENCE_PROPOSALS = {
    "embedding_ai_into_operations": ("2_moderate", "medium",
        "Company-primary statement of embedding AI into operations with a clear (if broad) capability described, "
        "but no specific task, deployment stage, or measurable outcome -- matches 2_moderate/medium."),
    "data_and_ai_capability_building": ("2_moderate", "medium",
        "Names a specific internal team (TBS) building data-and-AI capability at scale, but no discrete task or "
        "deployment evidence -- matches 2_moderate/medium."),
    "technology_strategy": ("1_weak", "low",
        "Broad statement that AI is used to 'optimise operations', with no specific task, team, or deployment "
        "evidence described -- matches 1_weak/low."),
    "digital_transformation": ("2_moderate", "medium",
        "Concrete workforce/skills-training statement (2,500 colleagues trained; 30,000 learning hours) tied to "
        "AI/cloud/digital-transformation fundamentals -- specific quantified figures given, but no deployment-"
        "stage or discrete-task detail -- matches 2_moderate/medium."),
    "workforce_ai_readiness_planning": ("1_weak", "medium",
        "Company-primary statement that 'AI workforce readiness is also underway' with workforce-planning "
        "capability strengthened via forecasting to assess the impact of AI -- genuine but fairly general, no "
        "quantified figure or named programme -- matches 1_weak/medium (some judgment required to read this as "
        "substantive rather than vague, but no scale/outcome evidence)."),
    "workforce_ai_learning_platform_capability": ("2_moderate", "medium",
        "Specific, named platform (MyLeatro, 'our AI learning platform') with a quantified scale figure "
        "(991,196 learning hours delivered), but no outcome/effectiveness measure beyond volume -- matches "
        "2_moderate/medium."),
    "genai_product_rollout_planned": ("2_moderate", "medium",
        "Concrete, dated, quantifiable generative-AI product/rollout announcement (named connector or "
        "enterprise-wide tool access, with a specific target date or headcount) but explicitly described with "
        "future-tense/'expected'/'plans' language rather than confirmed live within the source document -- "
        "matches 2_moderate/medium (unusually concrete for a planned item, but excluded from the operational "
        "count per the rule against classifying planned deployments as operational)."),
}


def build_strategic_proposal(ticker: str, company: str, sector: str, staging_rows: list[dict],
                              proposed_manifest_rows: list[dict], existing_manifest_rows: list[dict],
                              existing_rows: list[dict], problems: list[str]) -> list[dict]:
    existing_ids = {(r.get("finding_id") or "").strip() for r in existing_rows}
    id_prefix = ticker.split(".")[0]
    next_num = 1
    while f"{id_prefix}-STR-{next_num:03d}" in existing_ids:
        next_num += 1

    all_manifest = {r["local_filename"]: r for r in proposed_manifest_rows}
    all_manifest.update({(r.get("local_filename") or ""): r for r in existing_manifest_rows})

    proposed: list[dict] = []
    for r in staging_rows:
        decision = (r.get("reviewer_decision") or "").strip()
        staging_id = r["staging_id"]
        if decision not in STRATEGIC_PROMOTABLE_DECISIONS:
            pc.report(f"  [excluded] {staging_id}: reviewer_decision='{decision}' -- not eligible for promotion.")
            continue
        if already_promoted(staging_id, existing_rows, "notes"):
            pc.report(f"  [idempotent] {staging_id} already promoted -- skipping.")
            continue

        finding_type = (r.get("provisional_finding_type") or "").strip()
        proposal = STRATEGIC_EVIDENCE_PROPOSALS.get(finding_type)
        if proposal is None:
            problems.append(f"BLOCKED {staging_id}: no evidence_strength/confidence proposal rule for finding_type '{finding_type}'.")
            continue
        evidence_strength, confidence, reason = proposal

        manifest_row = all_manifest.get(r["local_filename"])
        if manifest_row is None:
            problems.append(f"BLOCKED {staging_id}: source_id not resolvable for '{r['local_filename']}'.")
            continue
        source_id = manifest_row.get("source_id", "")

        finding_id = f"{id_prefix}-STR-{next_num:03d}"
        next_num += 1
        proposed.append({
            "finding_id": finding_id,
            "company": company, "ticker": ticker, "sector": sector,
            "source_id": source_id,
            "finding_name": f"{finding_type.replace('_', ' ').capitalize()} ({r['page_or_section']})",
            "finding_type": finding_type,
            "evidence_quotation": r["supporting_context"].split(" ||| ")[0],
            "page_or_section": r["page_or_section"],
            "evidence_strength": evidence_strength,
            "confidence": confidence,
            "reason_excluded_from_operational_count": (
                "Strategic/capability-building language with no discrete operational task, user group, or "
                "deployment stage evidenced -- does not meet the operational use-case bar."
            ),
            "coded_by": "human",  # staging rows received explicit human review/approval decisions
            "coded_date": today_date(),
            "notes": (
                f"Promoted from staging {staging_id} (reviewer_decision={decision}). {reason} "
                f"reviewer_notes at staging: {r.get('reviewer_notes', '')}"
            ),
        })
    return proposed


# ---------------------------------------------------------------------------
# Governance -> governance_and_enablement_findings.csv
# ---------------------------------------------------------------------------
def governance_flags(context: str) -> dict:
    lowered = context.lower()
    return {
        "employee_training": "yes" if "training" in lowered else "no",
        "responsible_ai_framework": "yes" if ("governance framework" in lowered or "responsible use" in lowered
                                               or "governance group" in lowered) else "no",
        "human_involvement_discussed": "unclear" if ("accountable" in lowered or "oversight" in lowered) else "no",
        "privacy_discussed": "no",
        "accuracy_or_hallucination_discussed": "unclear" if "explainable" in lowered else "no",
        "environmental_limitation_discussed": "unclear" if "sustainab" in lowered else "no",
    }


def build_governance_proposal(ticker: str, company: str, sector: str, staging_rows: list[dict],
                               proposed_manifest_rows: list[dict], existing_manifest_rows: list[dict],
                               existing_rows: list[dict], problems: list[str]) -> list[dict]:
    existing_ids = {(r.get("finding_id") or "").strip() for r in existing_rows}
    id_prefix = ticker.split(".")[0]
    next_num = 1
    while f"{id_prefix}-GOV-{next_num:03d}" in existing_ids:
        next_num += 1

    all_manifest = {r["local_filename"]: r for r in proposed_manifest_rows}
    all_manifest.update({(r.get("local_filename") or ""): r for r in existing_manifest_rows})

    proposed: list[dict] = []
    for r in staging_rows:
        decision = (r.get("reviewer_decision") or "").strip()
        staging_id = r["staging_id"]
        if decision not in GOVERNANCE_PROMOTABLE_DECISIONS:
            pc.report(f"  [excluded] {staging_id}: reviewer_decision='{decision}' -- not eligible for promotion.")
            continue
        if already_promoted(staging_id, existing_rows, "notes"):
            pc.report(f"  [idempotent] {staging_id} already promoted -- skipping.")
            continue

        theme = (r.get("provisional_governance_theme") or "").strip()
        manifest_row = all_manifest.get(r["local_filename"])
        if manifest_row is None:
            problems.append(f"BLOCKED {staging_id}: source_id not resolvable for '{r['local_filename']}'.")
            continue
        source_id = manifest_row.get("source_id", "")

        flags = governance_flags(r["supporting_context"])
        finding_id = f"{id_prefix}-GOV-{next_num:03d}"
        next_num += 1
        proposed.append({
            "finding_id": finding_id,
            "company": company, "ticker": ticker, "sector": sector,
            "source_ids": source_id,
            "finding_name": f"{theme.replace('_', ' ').capitalize()} ({r['page_or_section']})",
            "finding_type": "document_level_governance_discussion",
            "evidence_quotation_or_summary": r["supporting_context"].split(" ||| ")[0],
            "page_or_section": r["page_or_section"],
            **flags,
            "reason_excluded_from_operational_count": (
                "Governance/oversight framework discussion, not attributed to any individual use case -- not "
                "itself an operational deployment."
            ),
            "coded_by": "human",  # staging rows received explicit human review/approval decisions
            "coded_date": today_date(),
            "notes": (
                f"Promoted from staging {staging_id} (reviewer_decision={decision}). Boolean control fields "
                "(human_involvement_discussed/accuracy_or_hallucination_discussed/environmental_limitation_"
                "discussed) are PROPOSED from keyword-adjacent language ('accountable'/'explainable'/'sustainable') "
                "and flagged 'unclear' rather than guessed yes/no -- pending human confirmation. "
                f"reviewer_notes at staging: {r.get('reviewer_notes', '')}"
            ),
        })
    return proposed


# ---------------------------------------------------------------------------
# Rejected -> rejected_or_aspirational_findings.csv
# ---------------------------------------------------------------------------
def build_rejected_proposal(ticker: str, company: str, sector: str, staging_rows: list[dict],
                             proposed_manifest_rows: list[dict], existing_manifest_rows: list[dict],
                             existing_rows: list[dict], problems: list[str]) -> list[dict]:
    existing_ids = {(r.get("finding_id") or "").strip() for r in existing_rows}
    id_prefix = ticker.split(".")[0]
    next_num = 1
    while f"{id_prefix}-REJ-{next_num:03d}" in existing_ids:
        next_num += 1

    all_manifest = {r["local_filename"]: r for r in proposed_manifest_rows}
    all_manifest.update({(r.get("local_filename") or ""): r for r in existing_manifest_rows})

    proposed: list[dict] = []
    for r in staging_rows:
        decision = (r.get("reviewer_decision") or "").strip()
        staging_id = r["staging_id"]
        if decision not in REJECTED_PROMOTABLE_DECISIONS:
            pc.report(f"  [excluded] {staging_id}: reviewer_decision='{decision}' -- not eligible for promotion.")
            continue
        if already_promoted(staging_id, existing_rows, "notes"):
            pc.report(f"  [idempotent] {staging_id} already promoted -- skipping.")
            continue

        category = (r.get("provisional_rejection_category") or "").strip()
        rejection_category = REJECTION_CATEGORY_LABELS.get(category)
        item_name = REJECTION_ITEM_LABELS.get(category)
        if rejection_category is None or item_name is None:
            problems.append(f"BLOCKED {staging_id}: no rejection_category/item_name label mapping for '{category}'.")
            continue

        manifest_row = all_manifest.get(r["local_filename"])
        if manifest_row is None:
            problems.append(f"BLOCKED {staging_id}: source_id not resolvable for '{r['local_filename']}'.")
            continue
        source_id = manifest_row.get("source_id", "")

        finding_id = f"{id_prefix}-REJ-{next_num:03d}"
        next_num += 1
        proposed.append({
            "finding_id": finding_id,
            "company": company, "ticker": ticker, "sector": sector,
            "source_id": source_id,
            "item_name": f"{item_name} ({r['page_or_section']})",
            "evidence_quotation": r["supporting_context"].split(" ||| ")[0],
            "page_or_section": r["page_or_section"],
            "rejection_category": rejection_category,
            "reason_rejected": r.get("reviewer_notes", ""),
            "coded_by": "human",  # staging rows received explicit human review/approval decisions
            "coded_date": today_date(),
            "notes": f"Promoted from staging {staging_id} (reviewer_decision={decision}).",
        })
    return proposed


# ---------------------------------------------------------------------------
# Company summary
# ---------------------------------------------------------------------------
def compute_use_case_counts(uc_rows: list[dict]) -> tuple[int, int]:
    provisional = 0
    confirmed = 0
    for r in uc_rows:
        if (r.get("is_genai") or "").strip() != "yes":
            continue
        if (r.get("duplicate_of_record_id") or "").strip():
            continue
        strength = (r.get("evidence_strength") or "").strip()
        status = (r.get("review_status") or "").strip()
        if strength in {"1_weak", "2_moderate", "3_strong"} and status != "reviewed_excluded":
            provisional += 1
        if strength in {"2_moderate", "3_strong"} and status in {"reviewed_confirmed", "reviewed_corrected"}:
            confirmed += 1
    return provisional, confirmed


def build_company_summary_proposal(slug: str, company: str, ticker: str, sector: str,
                                    proposed_uc_rows: list[dict], existing_uc_rows_for_company: list[dict],
                                    proposed_manifest_rows: list[dict], existing_manifest_rows_for_company: list[dict],
                                    has_unresolved_review: bool) -> dict:
    all_uc_rows = existing_uc_rows_for_company + proposed_uc_rows
    provisional, confirmed = compute_use_case_counts(all_uc_rows)
    no_disclosure_confirmed = "disclosure_found" if confirmed >= 1 else "pending_sources"

    # Computed (not hardcoded) collected-document signal: the CUMULATIVE set of
    # already-promoted + newly-proposed manifest rows for this company -- using
    # only proposed_manifest_rows would wrongly reset these fields to
    # not_started on an idempotent rerun (already-promoted sources are never
    # re-proposed, so proposed_manifest_rows is empty by then).
    all_manifest_rows_for_company = existing_manifest_rows_for_company + proposed_manifest_rows
    categories_downloaded = {(r.get("document_category") or "").strip() for r in all_manifest_rows_for_company}
    annual_report_latest_collected = "collected" if "annual_report_current" in categories_downloaded else "not_started"
    annual_report_previous_collected = "collected" if "annual_report_previous" in categories_downloaded else "not_started"
    if "sustainability_or_esg_report" in categories_downloaded:
        separate_sustainability_report_collected = "collected"
    else:
        # No sustainability_or_esg_report source was ever found/approved for this
        # company. Do not assert "not_applicable" (that would claim knowledge --
        # that sustainability reporting is integrated elsewhere -- that hasn't
        # been verified); "not_started" honestly records that this collection
        # track was never specifically resolved either way.
        separate_sustainability_report_collected = "not_started"

    # manual_review_status: "pending_review" whenever any staging row for this
    # company is still needs_more_evidence, regardless of whether source
    # collection itself is complete -- distinguishes unresolved CONTENT review
    # from unresolved SOURCE collection.
    manual_review_status = "pending_review" if has_unresolved_review else "review_complete"

    # Computed (not hardcoded) search-completeness signal: any candidate row still
    # at approval_status=pending means that search/verification track isn't finished.
    _, candidates = pc.read_csv_rows(pc.INTERMEDIATE_DIR / f"{slug}_source_candidates.csv")
    pending_company_primary = [
        c for c in candidates
        if (c.get("approval_status") or "").strip() == "pending"
        and (c.get("evidence_origin") or "").strip() == "company_primary"
    ]
    pending_partner = [
        c for c in candidates
        if (c.get("approval_status") or "").strip() == "pending"
        and (c.get("evidence_origin") or "").strip() == "technology_partner"
    ]
    official_web_search_completed = "incomplete" if pending_company_primary else "complete"
    partner_search_completed = "incomplete" if pending_partner else "complete"

    confirmed_titles = [
        r["use_case_name"] for r in proposed_uc_rows
        if r.get("evidence_strength") in {"2_moderate", "3_strong"} and r.get("review_status") == "reviewed_confirmed"
    ]
    weak_titles = [r["use_case_name"] for r in proposed_uc_rows if r.get("evidence_strength") == "1_weak"]
    notes_parts = [
        f"{len(proposed_uc_rows)} operational use case(s) proposed for promotion, all with review_status="
        "reviewed_confirmed (evidence_strength/confidence explicitly approved by the human operator)."
    ]
    if confirmed_titles:
        notes_parts.append(f"Qualify for confirmed_use_case_count (evidence_strength 2_moderate/3_strong): {'; '.join(confirmed_titles)}.")
    if weak_titles:
        notes_parts.append(f"Count toward provisional_use_case_count only (evidence_strength=1_weak): {'; '.join(weak_titles)}.")
    if pending_company_primary:
        titles = "; ".join((c.get("candidate_title") or "").strip() for c in pending_company_primary)
        notes_parts.append(f"{len(pending_company_primary)} company-primary candidate source(s) remain approval_status=pending: {titles}.")
    if pending_partner:
        titles = "; ".join((c.get("candidate_title") or "").strip() for c in pending_partner)
        notes_parts.append(f"{len(pending_partner)} technology-partner candidate source(s) remain approval_status=pending: {titles}.")

    return {
        "company": company, "ticker": ticker, "sector": sector,
        "annual_report_latest_collected": annual_report_latest_collected,
        "annual_report_previous_collected": annual_report_previous_collected,
        "separate_sustainability_report_collected": separate_sustainability_report_collected,
        "official_web_search_completed": official_web_search_completed,
        "partner_search_completed": partner_search_completed,
        "provisional_use_case_count": str(provisional),
        "confirmed_use_case_count": str(confirmed),
        "no_disclosure_confirmed": no_disclosure_confirmed,
        "manual_review_status": manual_review_status,
        "notes": " ".join(notes_parts),
        "last_updated_date": today_date(),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
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
        sector = sector_lookup(company)
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1

    op_fields, op_rows = load_staging(slug, "operational_candidates")
    str_fields, str_rows = load_staging(slug, "strategic_candidates")
    gov_fields, gov_rows = load_staging(slug, "governance_candidates")
    rej_fields, rej_rows = load_staging(slug, "rejected_candidates")
    dup_fields, dup_rows = load_staging(slug, "duplicate_flags")
    for label, fields in (("operational", op_fields), ("strategic", str_fields),
                          ("governance", gov_fields), ("rejected", rej_fields), ("duplicate_flags", dup_fields)):
        if fields is None:
            print(f"ERROR: {slug}_{label}_staging.csv not found -- run 06_prepare_staging_candidates.py first.")
            return 1

    all_staging_rows = op_rows + str_rows + gov_rows + rej_rows
    problems: list[str] = []
    check_reviewer_decisions(all_staging_rows + dup_rows, problems)

    manifest_fields, manifest_rows = load_main_csv(pc.SOURCE_MANIFEST_CSV)
    uc_fields, uc_rows = load_main_csv(pc.PROJECT_ROOT / "use_case_dataset_template.csv")
    str_finding_fields, str_finding_rows = load_main_csv(pc.PROJECT_ROOT / "strategic_capability_building_findings.csv")
    gov_finding_fields, gov_finding_rows = load_main_csv(pc.PROJECT_ROOT / "governance_and_enablement_findings.csv")
    rej_finding_fields, rej_finding_rows = load_main_csv(pc.PROJECT_ROOT / "rejected_or_aspirational_findings.csv")
    summary_fields, summary_rows = load_main_csv(pc.PROJECT_ROOT / "company_summary_template.csv")

    proposed_manifest_rows = build_source_manifest_proposal(slug, ticker, company, sector, manifest_rows, problems)
    proposed_operational = build_operational_proposal(
        slug, ticker, company, sector, op_rows, proposed_manifest_rows, uc_rows, problems)
    proposed_strategic = build_strategic_proposal(
        ticker, company, sector, str_rows, proposed_manifest_rows, manifest_rows, str_finding_rows, problems)
    proposed_governance = build_governance_proposal(
        ticker, company, sector, gov_rows, proposed_manifest_rows, manifest_rows, gov_finding_rows, problems)
    proposed_rejected = build_rejected_proposal(
        ticker, company, sector, rej_rows, proposed_manifest_rows, manifest_rows, rej_finding_rows, problems)

    existing_uc_for_company = [r for r in uc_rows if (r.get("company") or "").strip() == company]
    existing_manifest_for_company = [r for r in manifest_rows if (r.get("company") or "").strip() == company]
    has_unresolved_review = any(
        (r.get("reviewer_decision") or "").strip() == "needs_more_evidence" for r in all_staging_rows
    )
    proposed_summary = build_company_summary_proposal(
        slug, company, ticker, sector, proposed_operational, existing_uc_for_company,
        proposed_manifest_rows, existing_manifest_for_company, has_unresolved_review)

    # ---- Cross-checks: duplicate source_id / url / filename against BOTH the
    # proposed set and the existing manifest.
    seen_ids, seen_urls, seen_files = set(), set(), set()
    for r in manifest_rows:
        seen_ids.add(r.get("source_id", ""))
        if r.get("url"):
            seen_urls.add(r.get("url"))
        seen_files.add(r.get("local_filename", ""))
    for r in proposed_manifest_rows:
        if r["source_id"] in seen_ids:
            problems.append(f"BLOCKED: duplicate source_id proposed: {r['source_id']}")
        if r["url"] and r["url"] in seen_urls:
            problems.append(f"BLOCKED: duplicate url proposed: {r['url']}")
        if r["local_filename"] in seen_files:
            problems.append(f"BLOCKED: duplicate local_filename proposed: {r['local_filename']}")
        seen_ids.add(r["source_id"])
        seen_urls.add(r["url"])
        seen_files.add(r["local_filename"])

    # ---- Report ----
    pc.report("")
    pc.report("=" * 70)
    pc.report("VALIDATION")
    pc.report("=" * 70)
    if problems:
        for p in problems:
            pc.report(p)
    else:
        pc.report("No blocking problems found.")

    pc.report("")
    pc.report("=" * 70)
    pc.report(f"PROPOSED source_manifest.csv rows ({len(proposed_manifest_rows)})")
    pc.report("=" * 70)
    for r in proposed_manifest_rows:
        pc.report(f"  {r['source_id']} | {r['document_title']} | {r['document_category']} | "
                  f"evidence_origin={r['evidence_origin']} | pub_date={r['publication_date']} | url={r['url'] or '(blank)'}")

    pc.report("")
    pc.report("=" * 70)
    pc.report(f"PROPOSED use_case_dataset_template.csv rows ({len(proposed_operational)})")
    pc.report("=" * 70)
    for r in proposed_operational:
        pc.report(f"  {r['record_id']} | {r['use_case_name']}")
        pc.report(f"    evidence_strength(proposed)={r['evidence_strength']} confidence(proposed)={r['confidence']} review_status={r['review_status']}")

    pc.report("")
    pc.report(f"PROPOSED strategic findings: {len(proposed_strategic)}  "
              f"governance findings: {len(proposed_governance)}  rejected findings: {len(proposed_rejected)}")

    pc.report("")
    pc.report("=" * 70)
    pc.report("PROPOSED company_summary_template.csv row")
    pc.report("=" * 70)
    for k, v in proposed_summary.items():
        pc.report(f"  {k}: {v}")

    if args.dry_run:
        pc.report("")
        pc.report("[dry-run] No file written. No checkpoint updated.")
        return 0

    if problems:
        print("ERROR: blocking problems found -- refusing to write. Resolve the BLOCKED items above first.")
        return 1

    # ---- Acceptance-test-style guard: abort (writing nothing) if the
    # promotion set doesn't match what a human has already reviewed and
    # approved for this company, even though no BLOCKED problem was raised
    # above. Each company's expected counts are set explicitly here only
    # after the operator has confirmed a matching dry-run report -- a
    # company with no entry below has no additional safety net beyond the
    # BLOCKED/problems checks already performed.
    EXPECTED_PROMOTION_COUNTS = {
        "Tesco": {"source_manifest": 5, "operational": 2, "strategic": 4, "governance": 6, "rejected": 16},
        "BT Group": {"source_manifest": 6, "operational": 4, "strategic": 2, "governance": 9, "rejected": 48},
        "Rolls-Royce Holdings": {"source_manifest": 4, "operational": 1, "strategic": 4, "governance": 1, "rejected": 25},
    }
    expected = EXPECTED_PROMOTION_COUNTS.get(company)
    if expected is None:
        pc.report(f"NOTE: no acceptance-test expected-counts entry for '{company}' -- skipping this extra guard "
                  f"(BLOCKED/problems checks above still apply).")
    else:
        actual_counts = {
            "source_manifest": len(proposed_manifest_rows), "operational": len(proposed_operational),
            "strategic": len(proposed_strategic), "governance": len(proposed_governance),
            "rejected": len(proposed_rejected),
        }
        for label, expected_count in expected.items():
            actual_count = actual_counts[label]
            if actual_count != expected_count:
                print(f"ERROR: acceptance test failed -- expected {expected_count} {label} rows, got {actual_count}. Refusing to write.")
                return 1

    # Real promotion (not reached by --dry-run). Every destination is written
    # to a .partial temp file and validated FIRST; only once every single
    # temp file has passed validation are any real files replaced -- so a
    # failure partway through never leaves some destinations updated and
    # others not. On any failure, all .partial files created this run are
    # removed and no destination file is touched.
    destinations = [
        (pc.SOURCE_MANIFEST_CSV, manifest_fields, manifest_rows + proposed_manifest_rows),
        (pc.PROJECT_ROOT / "use_case_dataset_template.csv", uc_fields, uc_rows + proposed_operational),
        (pc.PROJECT_ROOT / "strategic_capability_building_findings.csv", str_finding_fields,
         str_finding_rows + proposed_strategic),
        (pc.PROJECT_ROOT / "governance_and_enablement_findings.csv", gov_finding_fields,
         gov_finding_rows + proposed_governance),
        (pc.PROJECT_ROOT / "rejected_or_aspirational_findings.csv", rej_finding_fields,
         rej_finding_rows + proposed_rejected),
        (pc.PROJECT_ROOT / "company_summary_template.csv", summary_fields,
         [r for r in summary_rows if (r.get("company") or "").strip() != company] + [proposed_summary]),
    ]

    tmp_paths: list[Path] = []
    try:
        for path, fieldnames, rows in destinations:
            tmp_path = path.with_name(path.name + ".partial")
            pc.write_csv_rows(tmp_path, fieldnames, rows)
            tmp_fieldnames, written = pc.read_csv_rows(tmp_path)
            if tmp_fieldnames != fieldnames:
                raise RuntimeError(f"header mismatch validating {path.name}: column order was not preserved")
            if len(written) != len(rows):
                raise RuntimeError(f"validation failed writing {path.name}: wrote {len(rows)} but re-read {len(written)}")
            tmp_paths.append(tmp_path)
    except Exception as exc:
        for p in tmp_paths:
            p.unlink(missing_ok=True)
        print(f"ERROR: validation failed before any destination file was replaced -- nothing written. Detail: {exc}")
        return 1

    # Every temp file validated -- now replace all real destinations.
    for (path, _, _), tmp_path in zip(destinations, tmp_paths):
        tmp_path.replace(path)

    pc.save_checkpoint(slug, "promote_reviewed_staging", {
        "status": "complete",
        "manifest_rows_added": len(proposed_manifest_rows),
        "operational_rows_added": len(proposed_operational),
        "strategic_rows_added": len(proposed_strategic),
        "governance_rows_added": len(proposed_governance),
        "rejected_rows_added": len(proposed_rejected),
    }, dry_run=False)
    pc.report("Promotion complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
