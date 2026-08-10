#!/usr/bin/env python3
"""
01_setup_company.py -- create the folder scaffold for one pilot company.

Plain-English summary
----------------------
This script does the boring, mechanical first step for a new company: make
its folder under sources/, drop in a blank source-checklist file (only if
one doesn't already exist), and start its checkpoint file. It never decides
anything about what the company's generative-AI use is -- that's for later,
human-reviewed stages.

It is idempotent: running it twice for the same company does nothing the
second time except confirm that everything is already in place.

Examples
--------
    python 01_setup_company.py --company AstraZeneca
    python 01_setup_company.py --company Tesco --dry-run
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pipeline_common as pc  # noqa: E402

SCRIPT_NAME = "01_setup_company"

CHECKLIST_SCAFFOLD_TEMPLATE = """# {company} ({ticker}) -- Manual Download Checklist

Status: source collection not yet started. This checklist prepares sources
for discovery and manual/automated retrieval. It does not itself constitute
logged evidence -- none of these rows exist in `source_manifest.csv` until a
human explicitly approves and promotes them.

Fill in candidate sources here as they are found (by Claude Code's
source-discovery step), following the same structure used for AstraZeneca's
checklist: title, landing_page_url, direct_download_url,
url_verification_status, publication_date, document_category,
evidence_origin, required_or_optional, manual_action_required, status.

## Core sources

(none logged yet)

## Optional sources

(none logged yet)
"""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create sources/<company-slug>/, a blank MANUAL_DOWNLOAD_CHECKLIST.md "
            "(only if missing), and initialise the company's checkpoint file. "
            "Never overwrites an existing checklist or folder."
        ),
        epilog="This script never edits pilot_companies.csv or any main dataset CSV.",
    )
    parser.add_argument(
        "--company",
        required=True,
        help="Company name or ticker exactly as it appears in pilot_companies.csv (e.g. 'Tesco' or 'TSCO').",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would be created, without creating or writing anything.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    row = pc.find_company_row(args.company)
    if row is None:
        print(f"ERROR: '{args.company}' was not found in pilot_companies.csv (checked company and ticker columns).")
        return 1

    company = row["company"]
    ticker = row["ticker"]
    slug = pc.slugify(company)
    company_dir = pc.SOURCES_DIR / slug
    checklist_path = company_dir / "MANUAL_DOWNLOAD_CHECKLIST.md"

    pc.report(f"Company: {company} ({ticker})  ->  slug: {slug}")

    # --- Folder ------------------------------------------------------------
    if company_dir.exists():
        pc.report(f"[skip] Folder already exists: {company_dir}")
    elif args.dry_run:
        pc.report(f"[dry-run] Would create folder: {company_dir}")
    else:
        company_dir.mkdir(parents=True, exist_ok=True)
        pc.report(f"[created] Folder: {company_dir}")

    # --- Checklist -----------------------------------------------------------
    if checklist_path.exists():
        pc.report(f"[skip] Checklist already exists, not overwriting: {checklist_path}")
    elif args.dry_run:
        pc.report(f"[dry-run] Would create checklist scaffold: {checklist_path}")
    else:
        # The folder must exist before we can write into it.
        company_dir.mkdir(parents=True, exist_ok=True)
        checklist_path.write_text(
            CHECKLIST_SCAFFOLD_TEMPLATE.format(company=company, ticker=ticker),
            encoding="utf-8",
        )
        pc.report(f"[created] Checklist scaffold: {checklist_path}")

    # --- Checkpoint ----------------------------------------------------------
    existing = pc.load_checkpoint(slug)
    already_recorded = "setup_company" in existing.get("stages", {})
    stage_data = {
        "status": "complete",
        "company": company,
        "ticker": ticker,
        "folder_created_or_present": True,
        "checklist_created_or_present": True,
    }
    if args.dry_run:
        pc.report(
            f"[dry-run] Would {'update' if already_recorded else 'record'} checkpoint stage "
            f"'setup_company' in {pc.checkpoint_path(slug)}"
        )
    else:
        pc.save_checkpoint(slug, "setup_company", stage_data, dry_run=False)
        pc.report(f"[{'updated' if already_recorded else 'recorded'}] Checkpoint stage 'setup_company'")

    pc.report("Done." if not args.dry_run else "Dry run complete -- nothing was written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
