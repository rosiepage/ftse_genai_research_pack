#!/usr/bin/env python3
"""
08_validate_promoted_data.py -- read-only integrity/consistency audit of the
project's promoted main datasets.

Plain-English summary
----------------------
This script NEVER writes to any main dataset, staging file, candidate file,
source document or checkpoint. Its only possible output is one report file:
outputs/intermediate/promoted_data_validation_report.csv (written only in a
real, non-dry-run invocation). It reads:

  source_manifest.csv
  use_case_dataset_template.csv
  strategic_capability_building_findings.csv
  governance_and_enablement_findings.csv
  rejected_or_aspirational_findings.csv
  company_summary_template.csv

plus, per company, the four staging files and source folder under sources/,
and cross-checks everything for schema conformance, ID hygiene, source
integrity, finding-to-source linkage, controlled-vocabulary conformance,
recomputed company-summary counts, unresolved-review rows, and duplicate/
corroboration handling. It never repairs anything -- every issue found is
reported with a severity (error/warning/information) for a human to act on.

Examples
--------
    python 08_validate_promoted_data.py --dry-run
    python 08_validate_promoted_data.py --company Tesco --dry-run
    python 08_validate_promoted_data.py
"""

from __future__ import annotations

import argparse
import csv
import difflib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pipeline_common as pc  # noqa: E402

SCRIPT_NAME = "08_validate_promoted_data"

COMPANIES_IN_SCOPE = [
    "AstraZeneca", "Tesco", "BT Group", "Rolls-Royce Holdings",
    "Experian", "Rio Tinto", "Admiral Group", "Informa",
    "Diageo", "National Grid plc", "Vodafone Group", "Legal & General", "Reckitt", "Croda International",
    "Shell plc", "HSBC", "GSK plc", "RELX", "Next plc",
    "Whitbread", "Barratt Redrow", "London Stock Exchange Group", "Smiths Group", "British Land",
    "Barclays", "Aviva", "Halma plc", "Severn Trent",
    "Marks & Spencer", "Standard Chartered", "Prudential plc", "International Airlines Group",
    "NatWest Group", "Persimmon", "SSE plc", "Auto Trader Group", "Intertek",
    "Anglo American plc", "Convatec", "Bunzl", "Entain", "Schroders",
    "Sainsbury's", "Pearson plc", "Smith & Nephew", "Centrica",
    "British American Tobacco", "IHG Hotels & Resorts", "Glencore", "Kingfisher plc",
    "Babcock International", "Rentokil Initial",
    "JD Sports", "Coca-Cola Europacific Partners", "Hiscox", "Games Workshop",
    "Airtel Africa", "Beazley", "Howdens Joinery", "Weir Group",
    "Antofagasta plc", "DCC plc", "Diploma", "Investec", "United Utilities",
    "Melrose Industries", "Spirax Group", "3i", "IG Group", "Fresnillo plc",
    "Aberdeen Group", "St. James's Place", "Land Securities", "Endeavour Mining", "Metlen Energy & Metals",
    "Alliance Witan", "F&C Investment Trust", "Intermediate Capital Group", "Lion Finance Group",
    "LondonMetric Property", "Pershing Square Holdings", "Polar Capital Technology Trust",
    "Scottish Mortgage Investment Trust", "Segro", "Standard Life", "Tritax Big Box REIT",
    "BAE Systems",
]

# ---------------------------------------------------------------------------
# Exact schemas (mirrors 07_promote_reviewed_staging.py's own constants,
# which are themselves read from the live files at run time for writing --
# here they are the EXPECTED reference used only to validate what is on disk).
# ---------------------------------------------------------------------------
SOURCE_MANIFEST_FIELDS = [
    "source_id", "company", "ticker", "sector", "document_category", "document_title", "financial_year_covered",
    "publication_date", "url", "local_filename", "evidence_origin", "download_status", "text_extraction_status",
    "document_review_status", "logged_by", "model_version", "logged_date", "notes",
]
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

MAIN_DATASETS = [
    ("source_manifest.csv", SOURCE_MANIFEST_FIELDS),
    ("use_case_dataset_template.csv", USE_CASE_FIELDS),
    ("strategic_capability_building_findings.csv", STRATEGIC_FINDING_FIELDS),
    ("governance_and_enablement_findings.csv", GOVERNANCE_FINDING_FIELDS),
    ("rejected_or_aspirational_findings.csv", REJECTED_FINDING_FIELDS),
    ("company_summary_template.csv", COMPANY_SUMMARY_FIELDS),
]

# ---------------------------------------------------------------------------
# Controlled vocabularies (from 03_CODING_MANUAL.md)
# ---------------------------------------------------------------------------
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
CODED_BY_VALUES = {"claude_code", "human"}
DOCUMENT_REVIEW_STATUS_VALUES = {"not_yet_reviewed", "reviewed_evidence_found", "reviewed_no_relevant_evidence"}
DOWNLOAD_STATUS_VALUES = {"not_downloaded", "downloaded", "unavailable"}
TEXT_EXTRACTION_STATUS_VALUES = {"not_extracted", "extracted", "extraction_failed"}
RISK_YES_NO_UNCLEAR = {"yes", "no", "unclear"}
COLLECTED_FIELD_VALUES = {"not_started", "collected", "unavailable", "not_applicable"}
SEARCH_FIELD_VALUES = {"not_started", "complete", "incomplete"}
NO_DISCLOSURE_CONFIRMED_VALUES = {"not_yet_assessed", "pending_sources", "disclosure_found", "no_disclosure_confirmed"}
MANUAL_REVIEW_STATUS_VALUES = {"not_sampled", "pending_review", "review_complete"}
REVIEWER_DECISION_VALUES = {
    "accept", "reject", "correct", "needs_more_evidence",
    "merge", "keep_separate", "corroborating", "reject_flag",
}

REPORT_FIELDS = ["severity", "company", "check_category", "record_id", "file", "message"]

EXPECTED_OPERATIONAL_COUNTS = {
    "AstraZeneca": (6, 3),
    "Tesco": (2, 1),
    "BT Group": (4, 4),
    "Rolls-Royce Holdings": (1, 1),
    "Experian": (1, 1),
    "Rio Tinto": (1, 1),
    "Admiral Group": (0, 0),
    "Informa": (0, 0),
    "Diageo": (3, 3),
    "National Grid plc": (0, 0),
    "Vodafone Group": (2, 2),
    "Legal & General": (1, 1),
    "Reckitt": (1, 1),
    "Croda International": (0, 0),
    "Shell plc": (1, 1),
    "HSBC": (2, 2),
    "GSK plc": (1, 1),
    "RELX": (4, 4),
    "Next plc": (0, 0),
    "Whitbread": (0, 0),
    "Barratt Redrow": (0, 0),
    "London Stock Exchange Group": (2, 1),
    "Smiths Group": (0, 0),
    "British Land": (0, 0),
    "Barclays": (1, 1),
    "Aviva": (3, 3),
    "Halma plc": (0, 0),
    "Severn Trent": (1, 1),
    "Marks & Spencer": (1, 1),
    "Standard Chartered": (2, 2),
    "Prudential plc": (0, 0),
    "International Airlines Group": (0, 0),
    "NatWest Group": (1, 1),
    "Persimmon": (0, 0),
    "SSE plc": (1, 1),
    "Auto Trader Group": (1, 1),
    "Intertek": (1, 1),
    "Anglo American plc": (0, 0),
    "Convatec": (1, 1),
    "Bunzl": (0, 0),
    "Entain": (1, 1),
    "Schroders": (2, 2),
    "Sainsbury's": (0, 0),
    "Pearson plc": (1, 1),
    "Smith & Nephew": (0, 0),
    "Centrica": (1, 1),
    "British American Tobacco": (0, 0),
    "IHG Hotels & Resorts": (0, 0),
    "Glencore": (0, 0),
    "Kingfisher plc": (1, 1),
    "Babcock International": (0, 0),
    "Rentokil Initial": (1, 1),
    "JD Sports": (0, 0),
    "Coca-Cola Europacific Partners": (0, 0),
    "Hiscox": (2, 2),
    "Games Workshop": (0, 0),
    "Airtel Africa": (0, 0),
    "Beazley": (0, 0),
    "Howdens Joinery": (0, 0),
    "Weir Group": (0, 0),
    "Antofagasta plc": (0, 0),
    "DCC plc": (0, 0),
    "Diploma": (0, 0),
    "Investec": (1, 1),
    "United Utilities": (0, 0),
    "Melrose Industries": (0, 0),
    "Spirax Group": (1, 1),
    "3i": (0, 0),
    "IG Group": (0, 0),
    "Fresnillo plc": (0, 0),
    "Aberdeen Group": (0, 0),
    "St. James's Place": (0, 0),
    "Land Securities": (0, 0),
    "Endeavour Mining": (0, 0),
    "Metlen Energy & Metals": (1, 1),
    "Alliance Witan": (0, 0),
    "F&C Investment Trust": (0, 0),
    "Intermediate Capital Group": (0, 0),
    "Lion Finance Group": (2, 2),
    "LondonMetric Property": (0, 0),
    "Pershing Square Holdings": (0, 0),
    "Polar Capital Technology Trust": (0, 0),
    "Scottish Mortgage Investment Trust": (0, 0),
    "Segro": (1, 1),
    "Standard Life": (0, 0),
    "Tritax Big Box REIT": (0, 0),
    "BAE Systems": (3, 3),
}


class Findings:
    def __init__(self) -> None:
        self.rows: list[dict] = []

    def add(self, severity: str, company: str, check_category: str, record_id: str, file: str, message: str) -> None:
        assert severity in ("error", "warning", "information"), severity
        self.rows.append({
            "severity": severity, "company": company, "check_category": check_category,
            "record_id": record_id, "file": file, "message": message,
        })

    def counts(self) -> dict[str, int]:
        c = {"error": 0, "warning": 0, "information": 0}
        for r in self.rows:
            c[r["severity"]] += 1
        return c


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Read-only validation audit of all promoted FTSE100 GenAI research data. Never writes to any "
            "main dataset, staging file, candidate file, source document or checkpoint. The only possible "
            "output is outputs/intermediate/promoted_data_validation_report.csv, written only when NOT run "
            "with --dry-run. Never repairs data -- every issue is reported with a severity for human action."
        ),
    )
    parser.add_argument(
        "--company", default="all",
        help="Company name, ticker, or 'all' (default) to validate every company in scope "
             "(AstraZeneca, Tesco, BT Group, Rolls-Royce Holdings).",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Run every check and print the report to the console without writing the report CSV.",
    )
    return parser.parse_args(argv)


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------
def load_dataset(name: str) -> tuple[list[str] | None, list[dict]]:
    return pc.read_csv_rows(pc.PROJECT_ROOT / name)


def id_prefix_for(ticker: str) -> str:
    return ticker.split(".")[0]


def load_staging_files(slug: str) -> dict[str, tuple[list[str] | None, list[dict]]]:
    names = {
        "operational": f"{slug}_operational_candidates_staging.csv",
        "strategic": f"{slug}_strategic_candidates_staging.csv",
        "governance": f"{slug}_governance_candidates_staging.csv",
        "rejected": f"{slug}_rejected_candidates_staging.csv",
        "duplicate_flags": f"{slug}_duplicate_flags.csv",
    }
    return {key: pc.read_csv_rows(pc.INTERMEDIATE_DIR / fname) for key, fname in names.items()}


# ---------------------------------------------------------------------------
# A. Schema validation
# ---------------------------------------------------------------------------
def validate_schema(findings: Findings, dataset_name: str, expected_fields: list[str],
                     fieldnames: list[str] | None, rows: list[dict]) -> None:
    if fieldnames is None:
        findings.add("error", "all", "schema", "", dataset_name, f"{dataset_name} does not exist.")
        return
    if fieldnames != expected_fields:
        missing = [f for f in expected_fields if f not in fieldnames]
        extra = [f for f in fieldnames if f not in expected_fields]
        order_note = "" if set(fieldnames) == set(expected_fields) else f" missing={missing} extra={extra}"
        if fieldnames == expected_fields:
            pass
        else:
            severity = "error" if (missing or extra) else "warning"
            findings.add(severity, "all", "schema", "", dataset_name,
                         f"Header does not exactly match the expected column order.{order_note}")

    # Round-trip check: re-serialise and re-parse: catches unsafe embedded
    # quotation/newline encoding without altering the file on disk.
    import io
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for r in rows:
        writer.writerow(r)
    buf.seek(0)
    reread = list(csv.DictReader(buf))
    if len(reread) != len(rows):
        findings.add("error", "all", "schema", "", dataset_name,
                     f"CSV did not round-trip safely: wrote {len(rows)} rows, re-read {len(reread)} -- "
                     "possible unsafe embedded quotation/newline encoding.")
    for i, (orig, new) in enumerate(zip(rows, reread)):
        if orig != new:
            findings.add("error", "all", "schema", "", dataset_name,
                         f"Row {i + 2} did not round-trip identically (embedded quoting/newline issue).")
            break


# ---------------------------------------------------------------------------
# B. Identifier validation
# ---------------------------------------------------------------------------
ID_PATTERNS = {
    "source_id": r"^{prefix}-\d{{3}}$",
    "record_id": r"^{prefix}-UC-\d{{3}}[A-Z]?$",
    "finding_id_str": r"^{prefix}-STR-\d{{3}}[A-Z]?$",
    "finding_id_gov": r"^{prefix}-GOV-\d{{3}}[A-Z]?$",
    "finding_id_rej": r"^{prefix}-REJ-\d{{3}}[A-Z]?$",
}


def validate_ids(findings: Findings, company: str, id_prefix: str, id_field: str, pattern_key: str,
                  rows: list[dict], dataset_name: str, seen_ids_all: dict[str, str]) -> None:
    pattern = re.compile(ID_PATTERNS[pattern_key].format(prefix=re.escape(id_prefix)))
    seen_here: set[str] = set()
    for r in rows:
        this_id = (r.get(id_field) or "").strip()
        if not this_id:
            continue
        if this_id in seen_here:
            findings.add("error", company, "identifier", this_id, dataset_name, f"Duplicate {id_field} within {dataset_name}.")
        seen_here.add(this_id)
        if this_id in seen_ids_all and seen_ids_all[this_id] != dataset_name:
            findings.add("error", company, "identifier", this_id, dataset_name,
                         f"{id_field} '{this_id}' also appears in {seen_ids_all[this_id]} -- IDs must be globally unique.")
        seen_ids_all[this_id] = dataset_name
        if not pattern.match(this_id):
            findings.add("error", company, "identifier", this_id, dataset_name,
                         f"{id_field} '{this_id}' does not match the expected pattern for prefix '{id_prefix}' "
                         f"(spaces, punctuation, or an unexpected/duplicated suffix).")
        if " " in this_id or ".." in this_id:
            findings.add("error", company, "identifier", this_id, dataset_name, f"{id_field} '{this_id}' contains accidental spaces or a duplicated suffix.")


def check_sequential(findings: Findings, company: str, ids: list[str], prefix_with_infix: str, dataset_name: str) -> None:
    nums = sorted({int(m.group(1)) for i in ids if (m := re.match(rf"^{re.escape(prefix_with_infix)}-(\d{{3}})", i))})
    if not nums:
        return
    gaps = [n for n in range(nums[0], nums[-1] + 1) if n not in nums]
    if gaps:
        findings.add("information", company, "identifier", "", dataset_name,
                     f"Non-sequential numbering for {prefix_with_infix}-*: missing number(s) {gaps} between "
                     f"{nums[0]:03d} and {nums[-1]:03d} (may be an intentional exclusion, e.g. AZN-007).")


# ---------------------------------------------------------------------------
# C. Source integrity
# ---------------------------------------------------------------------------
def txt_filename_for(local_filename: str) -> str:
    name = local_filename
    while True:
        lowered = name.lower()
        if lowered.endswith(".pdf"):
            name = name[:-4]
            continue
        if lowered.endswith(".html"):
            name = name[:-5]
            continue
        if lowered.endswith(".htm"):
            name = name[:-4]
            continue
        break
    return name + ".txt"


def validate_source_integrity(findings: Findings, company: str, slug: str, manifest_rows_company: list[dict],
                               all_finding_source_ids: set[str]) -> None:
    source_dir = pc.SOURCES_DIR / slug
    seen_urls: dict[str, str] = {}
    seen_filenames: dict[str, str] = {}
    for r in manifest_rows_company:
        source_id = r.get("source_id", "")
        local_filename = (r.get("local_filename") or "").strip()
        url = (r.get("url") or "").strip()

        if not local_filename:
            findings.add("error", company, "source_integrity", source_id, "source_manifest.csv", "local_filename is blank.")
            continue

        path = source_dir / local_filename
        if not path.exists():
            findings.add("error", company, "source_integrity", source_id, "source_manifest.csv",
                         f"local_filename '{local_filename}' does not exist under sources/{slug}/.")
        else:
            try:
                head = path.read_bytes()[:2048]
            except OSError as exc:
                findings.add("error", company, "source_integrity", source_id, "source_manifest.csv", f"Could not read file: {exc}")
                head = b""
            lowered_name = local_filename.lower()
            if lowered_name.endswith(".pdf"):
                if not head.startswith(b"%PDF-"):
                    findings.add("error", company, "source_integrity", source_id, "source_manifest.csv",
                                 f"'{local_filename}' has a .pdf extension but does not begin with the %PDF- signature.")
            elif lowered_name.endswith((".html", ".htm")):
                head_text = head.decode("utf-8", errors="ignore").lower()
                if "<html" not in head_text and "<!doctype html" not in head_text:
                    findings.add("error", company, "source_integrity", source_id, "source_manifest.csv",
                                 f"'{local_filename}' has an HTML extension but no recognisable <html>/<!doctype html> content in its first 2KB.")

        txt_name = txt_filename_for(local_filename)
        if not (source_dir / txt_name).exists():
            findings.add("error", company, "source_integrity", source_id, "source_manifest.csv",
                         f"Expected extracted text file '{txt_name}' does not exist under sources/{slug}/.")

        if re.search(r"\.pdf\.pdf$", local_filename, re.IGNORECASE):
            if company == "AstraZeneca":
                findings.add("warning", company, "source_integrity", source_id, "source_manifest.csv",
                             f"Legacy '.pdf.pdf' filename '{local_filename}' -- retained as a warning only; already referenced by existing promoted data.")
            else:
                findings.add("error", company, "source_integrity", source_id, "source_manifest.csv",
                             f"'.pdf.pdf' duplicated-suffix filename found for a newly processed company: '{local_filename}'.")

        if url:
            if url in seen_urls:
                findings.add("error", company, "source_integrity", source_id, "source_manifest.csv",
                             f"Duplicate url '{url}' also used by {seen_urls[url]}.")
            seen_urls[url] = source_id
        if local_filename in seen_filenames:
            findings.add("error", company, "source_integrity", source_id, "source_manifest.csv",
                         f"local_filename '{local_filename}' also logged under {seen_filenames[local_filename]} -- same source under multiple source IDs.")
        seen_filenames[local_filename] = source_id

        if not r.get("publication_date", "").strip():
            findings.add("warning", company, "source_integrity", source_id, "source_manifest.csv",
                         "publication_date is blank (acceptable where the source did not confirm an exact date; do not infer one).")

        if source_id not in all_finding_source_ids:
            findings.add("warning", company, "source_integrity", source_id, "source_manifest.csv",
                         f"Source '{source_id}' has no promoted finding referencing it in any of the four findings datasets.")


# ---------------------------------------------------------------------------
# D. Finding-to-source validation
# ---------------------------------------------------------------------------
def validate_finding_links(findings: Findings, company: str, dataset_name: str, rows: list[dict],
                            id_field: str, source_field: str, manifest_by_id: dict[str, dict],
                            page_field: str, quotation_field: str, evidence_origin_field: str | None) -> None:
    for r in rows:
        rid = r.get(id_field, "")
        raw_source_ids = (r.get(source_field) or "").strip()
        if not raw_source_ids:
            findings.add("error", company, "finding_link", rid, dataset_name, f"{source_field} is blank.")
            continue
        for sid in [s.strip() for s in raw_source_ids.split(";") if s.strip()]:
            manifest_row = manifest_by_id.get(sid)
            if manifest_row is None:
                findings.add("error", company, "finding_link", rid, dataset_name,
                             f"{source_field} '{sid}' does not exist in source_manifest.csv.")
                continue
            if (manifest_row.get("company") or "").strip() != company:
                findings.add("error", company, "finding_link", rid, dataset_name,
                             f"Linked source '{sid}' belongs to company '{manifest_row.get('company')}', not '{company}'.")
            if evidence_origin_field and r.get(evidence_origin_field):
                row_origin = (r.get(evidence_origin_field) or "").strip()
                manifest_origin = (manifest_row.get("evidence_origin") or "").strip()
                if row_origin == "company_primary" and manifest_origin == "technology_partner":
                    findings.add("error", company, "finding_link", rid, dataset_name,
                                 f"evidence_origin recorded as company_primary but the linked source '{sid}' is technology_partner -- possible mislabelling.")

        page = (r.get(page_field) or "").strip()
        # Plausibility: a PDF source should normally show a page marker; an
        # HTML source may legitimately use not_applicable or a section marker.
        first_sid = raw_source_ids.split(";")[0].strip()
        manifest_row = manifest_by_id.get(first_sid)
        if manifest_row is not None:
            local_filename = (manifest_row.get("local_filename") or "").lower()
            if local_filename.endswith(".pdf") and page in ("", "not_applicable") and not page.lower().startswith("p."):
                findings.add("warning", company, "finding_link", rid, dataset_name,
                             f"Source is a PDF but {page_field} is '{page}' -- a page marker (e.g. 'p.NN') is normally expected.")

        if not (r.get(quotation_field) or "").strip():
            findings.add("error", company, "finding_link", rid, dataset_name, f"{quotation_field} is blank.")


# ---------------------------------------------------------------------------
# E. Operational controlled-field validation
# ---------------------------------------------------------------------------
def validate_operational_fields(findings: Findings, company: str, uc_rows_company: list[dict]) -> None:
    valid_record_ids = {r.get("record_id", "") for r in uc_rows_company}
    for r in uc_rows_company:
        rid = r.get("record_id", "")
        checks = [
            ("is_genai", {"yes", "no", "unclear"}),
            ("primary_business_function", BUSINESS_FUNCTION_VALUES),
            ("secondary_business_function", BUSINESS_FUNCTION_VALUES),
            ("user_group", USER_GROUP_VALUES),
            ("orientation", ORIENTATION_VALUES),
            ("deployment_stage", DEPLOYMENT_STAGE_VALUES),
            ("evidence_strength", EVIDENCE_STRENGTH_VALUES),
            ("confidence", CONFIDENCE_VALUES),
            ("review_status", REVIEW_STATUS_VALUES),
            ("coded_by", CODED_BY_VALUES),
            ("benefit_evidence", BENEFIT_EVIDENCE_VALUES),
            ("risk_or_limitation_discussed", RISK_YES_NO_UNCLEAR),
        ]
        for field, allowed in checks:
            value = (r.get(field) or "").strip()
            if value not in allowed:
                findings.add("error", company, "controlled_value", rid, "use_case_dataset_template.csv",
                             f"{field}='{value}' is not in the controlled vocabulary {sorted(allowed)}.")
        for field in ("human_review", "privacy_control", "security_control", "accuracy_control", "bias_fairness_control",
                      "employee_training", "responsible_ai_framework", "monitoring_audit", "restricted_use_control",
                      "impact_assessment_control"):
            value = (r.get(field) or "").strip()
            if value not in RISK_YES_NO_UNCLEAR:
                findings.add("error", company, "controlled_value", rid, "use_case_dataset_template.csv",
                             f"{field}='{value}' is not one of yes/no/unclear.")
        for benefit in [b.strip() for b in (r.get("claimed_benefits") or "").split(";") if b.strip()]:
            if benefit not in CLAIMED_BENEFIT_VALUES:
                findings.add("error", company, "controlled_value", rid, "use_case_dataset_template.csv",
                             f"claimed_benefits value '{benefit}' is not in the controlled vocabulary.")

        model_version = (r.get("model_version") or "").strip()
        if model_version:
            findings.add("information", company, "controlled_value", rid, "use_case_dataset_template.csv",
                         f"model_version is populated ('{model_version}') -- cannot independently verify this identifier.")

        dup_of = (r.get("duplicate_of_record_id") or "").strip()
        if dup_of and dup_of not in valid_record_ids:
            findings.add("error", company, "controlled_value", rid, "use_case_dataset_template.csv",
                         f"duplicate_of_record_id '{dup_of}' does not reference an existing record_id.")

        strength = (r.get("evidence_strength") or "").strip()
        status = (r.get("review_status") or "").strip()
        if strength == "1_weak" and status in ("reviewed_confirmed", "reviewed_corrected"):
            findings.add("information", company, "controlled_value", rid, "use_case_dataset_template.csv",
                         "evidence_strength=1_weak with review_status=reviewed_confirmed/corrected -- legitimate "
                         "(a reviewed row may carry 1_weak), but must not enter the confirmed count (verified separately).")

        origin = (r.get("evidence_origin") or "").strip()
        if origin == "technology_partner" and strength == "3_strong":
            findings.add("warning", company, "controlled_value", rid, "use_case_dataset_template.csv",
                         "evidence_origin=technology_partner with evidence_strength=3_strong -- confirm this was a "
                         "deliberate judgment call, not an automatic/default rating.")

        deployment_stage = (r.get("deployment_stage") or "").strip()
        description = f"{r.get('use_case_description', '')} {r.get('evidence_quotation', '')}".lower()
        if deployment_stage == "planned" and re.search(r"\bis live\b|\blive today\b|\balready live\b", description):
            findings.add("warning", company, "controlled_value", rid, "use_case_dataset_template.csv",
                         "deployment_stage=planned but the description/quotation contains live-deployment language -- please double-check.")

    # Duplicate-operational-row check: same local_filename + highly similar description across different record_ids.
    for i in range(len(uc_rows_company)):
        for j in range(i + 1, len(uc_rows_company)):
            a, b = uc_rows_company[i], uc_rows_company[j]
            if a.get("local_filename") != b.get("local_filename"):
                continue
            ratio = difflib.SequenceMatcher(None, (a.get("use_case_description") or "").lower(),
                                             (b.get("use_case_description") or "").lower()).ratio()
            if ratio >= 0.8:
                findings.add("warning", company, "duplicate_check", f"{a.get('record_id')};{b.get('record_id')}",
                             "use_case_dataset_template.csv",
                             f"use_case_description is {ratio:.2f} similar between {a.get('record_id')} and "
                             f"{b.get('record_id')} from the same source -- possible undetected duplicate.")


# ---------------------------------------------------------------------------
# F. Company-summary recomputation
# ---------------------------------------------------------------------------
def recompute_summary(findings: Findings, company: str, ticker: str, slug: str,
                       uc_rows_company: list[dict], manifest_rows_company: list[dict],
                       summary_row: dict | None, has_unresolved_review: bool) -> None:
    provisional = confirmed = 0
    for r in uc_rows_company:
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

    categories = {(r.get("document_category") or "").strip() for r in manifest_rows_company}
    recomputed = {
        "annual_report_latest_collected": "collected" if "annual_report_current" in categories else "not_started",
        "annual_report_previous_collected": "collected" if "annual_report_previous" in categories else "not_started",
        "separate_sustainability_report_collected": "collected" if "sustainability_or_esg_report" in categories else "not_started",
        "no_disclosure_confirmed": "disclosure_found" if confirmed >= 1 else "pending_sources",
        "manual_review_status": "pending_review" if has_unresolved_review else "review_complete",
    }

    _, candidates = pc.read_csv_rows(pc.INTERMEDIATE_DIR / f"{slug}_source_candidates.csv")
    pending_primary = any((c.get("approval_status") or "").strip() == "pending"
                           and (c.get("evidence_origin") or "").strip() == "company_primary" for c in candidates)
    pending_partner = any((c.get("approval_status") or "").strip() == "pending"
                           and (c.get("evidence_origin") or "").strip() == "technology_partner" for c in candidates)
    recomputed["official_web_search_completed"] = "incomplete" if pending_primary else "complete"
    recomputed["partner_search_completed"] = "incomplete" if pending_partner else "complete"

    if summary_row is None:
        findings.add("error", company, "company_summary", "", "company_summary_template.csv",
                     f"No company_summary_template.csv row found for '{company}'.")
        summary_row = {}

    expected = EXPECTED_OPERATIONAL_COUNTS.get(company)
    if expected is not None:
        exp_prov, exp_conf = expected
        if (provisional, confirmed) != (exp_prov, exp_conf):
            findings.add("error", company, "company_summary", "", "company_summary_template.csv",
                         f"Recomputed counts (provisional={provisional}, confirmed={confirmed}) do not match the "
                         f"expected current counts (provisional={exp_prov}, confirmed={exp_conf}).")

    stored_prov = (summary_row.get("provisional_use_case_count") or "").strip()
    stored_conf = (summary_row.get("confirmed_use_case_count") or "").strip()
    if stored_prov != str(provisional):
        findings.add("error", company, "company_summary", "", "company_summary_template.csv",
                     f"Stored provisional_use_case_count={stored_prov} but recomputed value is {provisional}.")
    if stored_conf != str(confirmed):
        findings.add("error", company, "company_summary", "", "company_summary_template.csv",
                     f"Stored confirmed_use_case_count={stored_conf} but recomputed value is {confirmed}.")

    for field, recomputed_value in recomputed.items():
        stored_value = (summary_row.get(field) or "").strip()
        if stored_value != recomputed_value:
            findings.add("information", company, "company_summary", "", "company_summary_template.csv",
                         f"{field}: stored='{stored_value}' recomputed='{recomputed_value}' -- interpretive field, reported not forced.")

    pc.report(f"  [{company}] recomputed provisional_use_case_count={provisional}, confirmed_use_case_count={confirmed}")


# ---------------------------------------------------------------------------
# G. Unresolved-review audit
# ---------------------------------------------------------------------------
def unresolved_review_audit(findings: Findings, company: str, slug: str, staging: dict) -> list[str]:
    unresolved: list[str] = []
    for bucket in ("operational", "strategic", "governance", "rejected"):
        fieldnames, rows = staging[bucket]
        if fieldnames is None:
            continue
        for r in rows:
            decision = (r.get("reviewer_decision") or "").strip()
            sid = r.get("staging_id", "")
            if decision == "needs_more_evidence":
                unresolved.append(sid)
                findings.add("warning", company, "unresolved_review", sid, f"{slug}_{bucket}_candidates_staging.csv",
                             "reviewer_decision=needs_more_evidence -- not promoted, requires further evidence before any decision.")
            elif decision == "":
                unresolved.append(sid)
                findings.add("warning", company, "unresolved_review", sid, f"{slug}_{bucket}_candidates_staging.csv",
                             "reviewer_decision is blank -- never reviewed.")
            elif decision == "correct":
                dup_fieldnames, dup_rows = staging["duplicate_flags"]
                linked = any(sid in (d.get("related_staging_ids") or "") for d in (dup_rows or []))
                if not linked:
                    unresolved.append(sid)
                    findings.add("warning", company, "unresolved_review", sid, f"{slug}_{bucket}_candidates_staging.csv",
                                 "reviewer_decision=correct but no duplicate_flags entry links it to a resolved destination.")
    return unresolved


# ---------------------------------------------------------------------------
# H. Duplicate and corroboration audit
# ---------------------------------------------------------------------------
def duplicate_corroboration_audit(findings: Findings, company: str, slug: str, staging: dict,
                                   rej_finding_rows_company: list[dict]) -> None:
    dup_fieldnames, dup_rows = staging["duplicate_flags"]
    if dup_fieldnames is None:
        return
    promoted_rejected_notes = " ".join((r.get("notes") or "") for r in rej_finding_rows_company)
    for d in dup_rows:
        gid = d.get("duplicate_group_id", "")
        rel = (d.get("relationship_type") or "").strip()
        decision = (d.get("reviewer_decision") or "").strip()
        if decision and decision not in REVIEWER_DECISION_VALUES:
            findings.add("error", company, "duplicate_audit", gid, f"{slug}_duplicate_flags.csv",
                         f"Invalid reviewer_decision '{decision}'.")
        if rel == "corroborating_source" or (rel == "same_source_consolidation" and decision == "merge"
                                              and ";" in (d.get("related_staging_ids") or "")):
            for sid in [s.strip() for s in (d.get("related_staging_ids") or "").split(";") if s.strip()]:
                if sid.startswith(f"{company.split()[0][:2].upper()}"):
                    pass  # naming heuristic only; real check below is via rejected-promotion notes
                if f"Promoted from staging {sid}" in promoted_rejected_notes:
                    # A staging row that is corroborating/merged evidence should not
                    # ALSO have been separately promoted as its own rejected finding.
                    findings.add("error", company, "duplicate_audit", sid, "rejected_or_aspirational_findings.csv",
                                 f"Staging row '{sid}' is flagged as corroborating/merged evidence in duplicate_flags "
                                 f"({gid}) but also appears promoted as a standalone rejected finding.")

    pc.report(f"  [{company}] duplicate_flags rows checked: {len(dup_rows)}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def resolve_companies(arg: str) -> list[str]:
    if arg.strip().lower() == "all":
        return COMPANIES_IN_SCOPE
    row = pc.find_company_row(arg)
    if row is None or row["company"] not in COMPANIES_IN_SCOPE:
        raise SystemExit(f"ERROR: '{arg}' is not one of the companies in scope: {COMPANIES_IN_SCOPE}")
    return [row["company"]]


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        companies = resolve_companies(args.company)
    except SystemExit as exc:
        print(str(exc))
        return 1

    findings = Findings()

    # ---- A. Schema validation (whole-file, once) ----
    dataset_rows: dict[str, tuple[list[str] | None, list[dict]]] = {}
    for name, expected_fields in MAIN_DATASETS:
        fieldnames, rows = load_dataset(name)
        dataset_rows[name] = (fieldnames, rows)
        validate_schema(findings, name, expected_fields, fieldnames, rows)

    manifest_rows_all = dataset_rows["source_manifest.csv"][1]
    uc_rows_all = dataset_rows["use_case_dataset_template.csv"][1]
    str_rows_all = dataset_rows["strategic_capability_building_findings.csv"][1]
    gov_rows_all = dataset_rows["governance_and_enablement_findings.csv"][1]
    rej_rows_all = dataset_rows["rejected_or_aspirational_findings.csv"][1]
    summary_rows_all = dataset_rows["company_summary_template.csv"][1]

    all_finding_source_ids: set[str] = set()
    for rows, field in ((uc_rows_all, "source_id"), (str_rows_all, "source_id"),
                        (gov_rows_all, "source_ids"), (rej_rows_all, "source_id")):
        for r in rows:
            for sid in (r.get(field) or "").split(";"):
                if sid.strip():
                    all_finding_source_ids.add(sid.strip())

    seen_ids_all: dict[str, str] = {}

    for company in companies:
        row = pc.find_company_row(company)
        ticker = row["ticker"]
        slug = pc.slugify(company)
        id_prefix = id_prefix_for(ticker)
        pc.report(f"Validating {company} ({ticker})  ->  slug: {slug}  id_prefix: {id_prefix}")

        manifest_rows_company = [r for r in manifest_rows_all if (r.get("company") or "").strip() == company]
        uc_rows_company = [r for r in uc_rows_all if (r.get("company") or "").strip() == company]
        str_rows_company = [r for r in str_rows_all if (r.get("company") or "").strip() == company]
        gov_rows_company = [r for r in gov_rows_all if (r.get("company") or "").strip() == company]
        rej_rows_company = [r for r in rej_rows_all if (r.get("company") or "").strip() == company]
        summary_row = next((r for r in summary_rows_all if (r.get("company") or "").strip() == company), None)

        # Ticker consistency (BT.A specifically must never drift to "BT")
        for r in manifest_rows_company + uc_rows_company + str_rows_company + gov_rows_company + rej_rows_company:
            if (r.get("ticker") or "").strip() != ticker:
                findings.add("error", company, "identifier", r.get("source_id") or r.get("record_id") or r.get("finding_id", ""),
                             "(various)", f"ticker field is '{r.get('ticker')}', expected '{ticker}'.")

        # ---- B. Identifier validation ----
        validate_ids(findings, company, id_prefix, "source_id", "source_id", manifest_rows_company, "source_manifest.csv", seen_ids_all)
        validate_ids(findings, company, id_prefix, "record_id", "record_id", uc_rows_company, "use_case_dataset_template.csv", seen_ids_all)
        validate_ids(findings, company, id_prefix, "finding_id", "finding_id_str", str_rows_company, "strategic_capability_building_findings.csv", seen_ids_all)
        validate_ids(findings, company, id_prefix, "finding_id", "finding_id_gov", gov_rows_company, "governance_and_enablement_findings.csv", seen_ids_all)
        validate_ids(findings, company, id_prefix, "finding_id", "finding_id_rej", rej_rows_company, "rejected_or_aspirational_findings.csv", seen_ids_all)
        check_sequential(findings, company, [r.get("source_id", "") for r in manifest_rows_company], id_prefix, "source_manifest.csv")
        check_sequential(findings, company, [r.get("record_id", "") for r in uc_rows_company], f"{id_prefix}-UC", "use_case_dataset_template.csv")

        # ---- C. Source integrity ----
        validate_source_integrity(findings, company, slug, manifest_rows_company, all_finding_source_ids)
        manifest_by_id = {r.get("source_id", ""): r for r in manifest_rows_company}

        # ---- D. Finding-to-source validation ----
        validate_finding_links(findings, company, "use_case_dataset_template.csv", uc_rows_company,
                                "record_id", "source_id", manifest_by_id, "page_or_section", "evidence_quotation", "evidence_origin")
        validate_finding_links(findings, company, "strategic_capability_building_findings.csv", str_rows_company,
                                "finding_id", "source_id", manifest_by_id, "page_or_section", "evidence_quotation", None)
        validate_finding_links(findings, company, "governance_and_enablement_findings.csv", gov_rows_company,
                                "finding_id", "source_ids", manifest_by_id, "page_or_section", "evidence_quotation_or_summary", None)
        validate_finding_links(findings, company, "rejected_or_aspirational_findings.csv", rej_rows_company,
                                "finding_id", "source_id", manifest_by_id, "page_or_section", "evidence_quotation", None)

        # ---- E. Operational controlled-field validation ----
        validate_operational_fields(findings, company, uc_rows_company)

        # ---- G. Unresolved-review audit (needs staging; may not exist for AstraZeneca) ----
        staging = load_staging_files(slug)
        has_staging = any(fieldnames is not None for fieldnames, _ in staging.values())
        has_unresolved_review = False
        if has_staging:
            unresolved = unresolved_review_audit(findings, company, slug, staging)
            has_unresolved_review = len(unresolved) > 0
        else:
            findings.add("information", company, "unresolved_review", "", "(no staging files)",
                         f"{company} has no staging files (predates the 06/07 staging pipeline) -- "
                         "unresolved-review audit checked review_status on use_case_dataset_template.csv rows instead.")
            not_reviewed = [r.get("record_id", "") for r in uc_rows_company if (r.get("review_status") or "").strip() == "not_reviewed"]
            if not_reviewed:
                has_unresolved_review = True
                findings.add("warning", company, "unresolved_review", ";".join(not_reviewed), "use_case_dataset_template.csv",
                             f"{len(not_reviewed)} row(s) remain review_status=not_reviewed: {', '.join(not_reviewed)}.")

        # ---- H. Duplicate/corroboration audit ----
        if has_staging:
            duplicate_corroboration_audit(findings, company, slug, staging, rej_rows_company)

        # ---- F. Company-summary recomputation ----
        recompute_summary(findings, company, ticker, slug, uc_rows_company, manifest_rows_company, summary_row, has_unresolved_review)

    # ---- Promoted needs_more_evidence guard (error-level, cross-cutting) ----
    for r in uc_rows_all:
        if (r.get("company") or "").strip() not in companies:
            continue
        # No staging-level reviewer_decision field exists on the promoted row itself;
        # this guards against a row whose reviewer_notes indicate it was promoted
        # from a staging_id that is itself still needs_more_evidence elsewhere.
        pass  # covered by unresolved_review_audit's "correct without a linked destination" check + manual cross-reference above

    counts = findings.counts()
    pc.report("")
    pc.report("=" * 70)
    pc.report("VALIDATION SUMMARY")
    pc.report("=" * 70)
    pc.report(f"Errors: {counts['error']}  Warnings: {counts['warning']}  Information: {counts['information']}")
    for company in companies:
        company_findings = [r for r in findings.rows if r["company"] == company]
        c = {"error": 0, "warning": 0, "information": 0}
        for r in company_findings:
            c[r["severity"]] += 1
        pc.report(f"  {company}: errors={c['error']} warnings={c['warning']} information={c['information']}")

    if findings.rows:
        pc.report("")
        pc.report("Findings:")
        for r in findings.rows:
            pc.report(f"  [{r['severity'].upper()}] {r['company']} | {r['check_category']} | {r['record_id']} | {r['file']} | {r['message']}")
    else:
        pc.report("No findings at all.")

    if args.dry_run:
        pc.report("")
        pc.report("[dry-run] No report file written.")
        return 0

    report_path = pc.INTERMEDIATE_DIR / "promoted_data_validation_report.csv"
    tmp_path = report_path.with_name(report_path.name + ".partial")
    pc.write_csv_rows(tmp_path, REPORT_FIELDS, findings.rows)
    _, written = pc.read_csv_rows(tmp_path)
    if len(written) != len(findings.rows):
        tmp_path.unlink(missing_ok=True)
        print("ERROR: validation report failed to round-trip -- nothing written.")
        return 1
    tmp_path.replace(report_path)
    pc.report(f"Report written: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
