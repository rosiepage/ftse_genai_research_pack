"""
Shared helpers for the FTSE 100 GenAI research pipeline scripts.

Plain-English summary
----------------------
This module holds the small pieces of logic that every pipeline script needs
(so we don't copy-paste them five times): finding the project's folders,
turning a company name into a safe folder name, reading/writing checkpoint
files, writing to a per-company error log, and the controlled-vocabulary
lists that come from 03_CODING_MANUAL.md.

Nothing in this file writes to any of the project's main dataset CSVs
(source_manifest.csv, use_case_dataset_template.csv,
company_summary_template.csv, or the three findings CSVs). It only ever
touches: sources/<company>/, pipeline/checkpoints/, and
outputs/intermediate/.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Project layout
# ---------------------------------------------------------------------------

# This file lives at <project_root>/pipeline/scripts/pipeline_common.py
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

SOURCES_DIR = PROJECT_ROOT / "sources"
INTERMEDIATE_DIR = PROJECT_ROOT / "outputs" / "intermediate"
CHECKPOINTS_DIR = PROJECT_ROOT / "pipeline" / "checkpoints"
PILOT_COMPANIES_CSV = PROJECT_ROOT / "pilot_companies.csv"
FTSE_CONSTITUENTS_CSV = PROJECT_ROOT / "ftse100_constituents_2026-06-19.csv"
SOURCE_MANIFEST_CSV = PROJECT_ROOT / "source_manifest.csv"


# ---------------------------------------------------------------------------
# Controlled vocabularies
# ---------------------------------------------------------------------------
# The document_category and evidence_origin lists below are copied verbatim
# from 03_CODING_MANUAL.md (the "Document category vocabulary" section and
# field 9, "evidence_origin"). If the manual is ever revised, update these
# two lists to match -- this file does not parse the manual automatically,
# so keeping them in sync is a manual step.

DOCUMENT_CATEGORY_VALUES = {
    "annual_report_current",
    "annual_report_previous",
    "sustainability_or_esg_report",
    "press_release",
    "investor_presentation",
    "results_presentation",
    "strategy_or_technology_webpage",
    "official_case_study",
    "governance_or_responsible_ai_policy",
    "executive_speech_or_interview",
    "partner_case_study",
    "regulatory_filing_or_rns",
    "earnings_call_transcript",
    "parliamentary_or_regulator_evidence",
    "third_party_interview",
    "vendor_conference_presentation",
    "other",
}

EVIDENCE_ORIGIN_VALUES = {
    "company_primary",
    "technology_partner",
    "third_party_named_executive",
    "other",
}

# These two vocabularies are pipeline-specific (they describe the state of a
# *candidate* source before it is ever logged in source_manifest.csv), so
# they are not in 03_CODING_MANUAL.md. They were defined in the approved v2
# pipeline design.
ACCESSIBILITY_STATUS_VALUES = {
    "not_yet_attempted",
    "fetched_ok",
    "blocked_403",
    "blocked_other",
    "manual_browser_required",
    "unavailable",
}

VERIFICATION_STATUS_VALUES = {
    "unresolved",
    "single_source_unverified",
    "landing_page_verified_download_link_unverified",
    "url_confirmed_cross_source",
    "verified",
}

APPROVAL_STATUS_VALUES = {"pending", "approved", "rejected"}

# Required columns for outputs/intermediate/<company>_source_candidates.csv,
# the file Claude Code's source-discovery step produces and a human then
# annotates with approval_status before 03_download_sources.py may act on it.
SOURCE_CANDIDATES_REQUIRED_COLUMNS = [
    "company",
    "ticker",
    "candidate_title",
    "url",
    "landing_page_url",
    "document_category",
    "evidence_origin",
    "accessibility_status",
    "verification_status",
    "publication_date_candidate",
    "approval_status",
    "notes",
]


# ---------------------------------------------------------------------------
# Company lookup / slugging
# ---------------------------------------------------------------------------

def slugify(name: str) -> str:
    """Turn a company name into a safe, lowercase folder-name slug.

    "AstraZeneca" -> "astrazeneca"; "BT Group" -> "bt-group";
    "Rolls-Royce Holdings" -> "rolls-royce-holdings".
    """
    slug = name.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug


def load_pilot_companies() -> list[dict]:
    """Read pilot_companies.csv into a list of plain dicts."""
    if not PILOT_COMPANIES_CSV.exists():
        raise FileNotFoundError(f"pilot_companies.csv not found at {PILOT_COMPANIES_CSV}")
    with PILOT_COMPANIES_CSV.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def find_company_row(identifier: str) -> dict | None:
    """Find a row in pilot_companies.csv by company name or ticker (case-insensitive)."""
    identifier_lower = identifier.strip().lower()
    for row in load_pilot_companies():
        if row.get("company", "").strip().lower() == identifier_lower:
            return row
        if row.get("ticker", "").strip().lower() == identifier_lower:
            return row
    return None


# ---------------------------------------------------------------------------
# CSV helpers
# ---------------------------------------------------------------------------

def read_csv_rows(path: Path) -> tuple[list[str] | None, list[dict]]:
    """Read a CSV file, returning (fieldnames, rows). (None, []) if the file is missing."""
    if not path.exists():
        return None, []
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        fieldnames = reader.fieldnames
    return fieldnames, rows


def write_csv_rows(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    """Write rows to a CSV file with a fixed column order. Creates parent dirs if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


# ---------------------------------------------------------------------------
# Filename safety
# ---------------------------------------------------------------------------

def safe_pdf_filename(proposed_name: str) -> str:
    """Ensure a proposed filename ends in exactly one .pdf -- never .pdf.pdf.

    This is the forward-fix for the AstraZeneca .pdf.pdf issue: strip any
    number of trailing ".pdf" suffixes (case-insensitive) and add back
    exactly one.
    """
    name = proposed_name.strip()
    while name.lower().endswith(".pdf"):
        name = name[: -len(".pdf")]
    return f"{name}.pdf"


def txt_path_for_pdf(pdf_path: Path) -> Path:
    """Return the extracted-text path for a PDF, stripping *all* trailing .pdf
    suffixes first (so AZN_..._2025.pdf.pdf maps to AZN_..._2025.txt, matching
    the file that already exists on disk for AstraZeneca, not
    AZN_..._2025.pdf.txt).
    """
    name = pdf_path.name
    while name.lower().endswith(".pdf"):
        name = name[: -len(".pdf")]
    return pdf_path.with_name(name + ".txt")


# ---------------------------------------------------------------------------
# Checkpointing
# ---------------------------------------------------------------------------

def checkpoint_path(slug: str) -> Path:
    return CHECKPOINTS_DIR / f"{slug}_checkpoint.json"


def load_checkpoint(slug: str) -> dict:
    """Load a company's checkpoint file, or return a fresh empty structure."""
    path = checkpoint_path(slug)
    if not path.exists():
        return {"slug": slug, "stages": {}}
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    data.setdefault("stages", {})
    return data


def save_checkpoint(slug: str, stage_name: str, stage_data: dict, dry_run: bool = False) -> dict:
    """Merge a single stage's result into the company's checkpoint file.

    Only the named stage's entry is replaced -- every other stage already
    recorded is preserved untouched. In dry-run mode nothing is written; the
    merged result is returned so the caller can print/report it.
    """
    data = load_checkpoint(slug)
    stage_data = dict(stage_data)
    stage_data["timestamp"] = timestamp()
    data["stages"][stage_name] = stage_data
    if not dry_run:
        CHECKPOINTS_DIR.mkdir(parents=True, exist_ok=True)
        with checkpoint_path(slug).open("w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
    return data


# ---------------------------------------------------------------------------
# Error logging
# ---------------------------------------------------------------------------

def timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def error_log_path(slug: str) -> Path:
    return INTERMEDIATE_DIR / f"{slug}_pipeline_errors.log"


def log_error(slug: str, script_name: str, message: str, dry_run: bool = False) -> None:
    """Append one line to a company's error log without raising.

    Used so a single failed download/extraction/etc. is recorded and the
    script can continue with the next item, instead of stopping the batch.
    In dry-run mode the line is printed to stderr instead of being written.
    """
    line = f"{timestamp()} | {script_name} | {message}"
    if dry_run:
        print(f"[DRY-RUN error-log] {line}", file=sys.stderr)
        return
    INTERMEDIATE_DIR.mkdir(parents=True, exist_ok=True)
    with error_log_path(slug).open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


# ---------------------------------------------------------------------------
# Small shared reporting helper
# ---------------------------------------------------------------------------

def report(message: str) -> None:
    """Print a plain progress/result line. Kept as a single function so all
    scripts format their output the same way."""
    print(message)
