#!/usr/bin/env python3
"""
02_validate_source_candidates.py -- structural validation of a company's
source-candidates file.

Plain-English summary
----------------------
Claude Code's own source-discovery step (web search / fetch, or a manual
browser check where a site blocks automated access) produces
outputs/intermediate/<company>_source_candidates.csv. This script checks
that file's *shape*, not its *truth*:

  - are all the required columns present?
  - does every URL look like a real http/https URL?
  - are there duplicate URLs?
  - are document_category / evidence_origin from the controlled lists in
    03_CODING_MANUAL.md?
  - are accessibility_status / verification_status / approval_status from
    the approved staging vocabularies?

It deliberately does NOT decide that a candidate is a genuine, usable
source just because its URL is well-formed -- that judgement belongs to
source discovery and human review, never to this script. It also never
writes to source_manifest.csv or any other main dataset file.

Exit codes
----------
    0 = completed successfully (structurally valid -- no errors found)
    1 = validation ran and found genuine errors in the candidates file
    2 = prerequisite not yet available (the candidates file doesn't exist
        yet) -- this means "not started yet", not "failed"

Examples
--------
    python 02_validate_source_candidates.py --company AstraZeneca
    python 02_validate_source_candidates.py --company Tesco --dry-run
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pipeline_common as pc  # noqa: E402

SCRIPT_NAME = "02_validate_source_candidates"

URL_PATTERN = re.compile(r"^https?://\S+$", re.IGNORECASE)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the structure of outputs/intermediate/<company>_source_candidates.csv: "
            "required columns, well-formed URLs, duplicate URLs, and controlled-vocabulary values. "
            "Never judges whether a source is genuine, and never edits source_manifest.csv."
        ),
        epilog=(
            "Exit codes: 0 = passed structurally; 1 = ran and found genuine errors; "
            "2 = prerequisite not available yet (candidates file missing -- 'not started yet', not a failure)."
        ),
    )
    parser.add_argument(
        "--company",
        required=True,
        help="Company name or ticker exactly as it appears in pilot_companies.csv.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the validation report only -- do not write the report file or update the checkpoint.",
    )
    return parser.parse_args(argv)


def validate_rows(rows: list[dict], fieldnames: list[str]) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) for the given candidate rows."""
    errors: list[str] = []
    warnings: list[str] = []

    missing_columns = [c for c in pc.SOURCE_CANDIDATES_REQUIRED_COLUMNS if c not in fieldnames]
    if missing_columns:
        errors.append(f"Missing required column(s): {', '.join(missing_columns)}")
        # Column-level checks below assume the columns exist, so stop here.
        return errors, warnings

    seen_urls: dict[str, int] = {}
    for i, row in enumerate(rows, start=2):  # row 2 = first data row (row 1 is the header)
        url = (row.get("url") or "").strip()
        if not url:
            errors.append(f"Row {i}: 'url' is blank.")
        elif not URL_PATTERN.match(url):
            errors.append(f"Row {i}: 'url' does not look like a complete http/https URL: {url!r}")
        else:
            key = url.lower().rstrip("/")
            if key in seen_urls:
                warnings.append(f"Row {i}: duplicate URL, also seen at row {seen_urls[key]}: {url}")
            else:
                seen_urls[key] = i

        doc_cat = (row.get("document_category") or "").strip()
        if not doc_cat:
            warnings.append(f"Row {i}: 'document_category' is blank.")
        elif doc_cat not in pc.DOCUMENT_CATEGORY_VALUES:
            errors.append(f"Row {i}: 'document_category' value not in the controlled list: {doc_cat!r}")

        evidence_origin = (row.get("evidence_origin") or "").strip()
        if not evidence_origin:
            warnings.append(f"Row {i}: 'evidence_origin' is blank.")
        elif evidence_origin not in pc.EVIDENCE_ORIGIN_VALUES:
            errors.append(f"Row {i}: 'evidence_origin' value not in the controlled list: {evidence_origin!r}")

        accessibility = (row.get("accessibility_status") or "").strip()
        if not accessibility:
            warnings.append(f"Row {i}: 'accessibility_status' is blank.")
        elif accessibility not in pc.ACCESSIBILITY_STATUS_VALUES:
            errors.append(f"Row {i}: 'accessibility_status' value not in the approved staging vocabulary: {accessibility!r}")

        verification = (row.get("verification_status") or "").strip()
        if not verification:
            warnings.append(f"Row {i}: 'verification_status' is blank.")
        elif verification not in pc.VERIFICATION_STATUS_VALUES:
            errors.append(f"Row {i}: 'verification_status' value not in the approved staging vocabulary: {verification!r}")

        approval = (row.get("approval_status") or "").strip()
        if not approval:
            warnings.append(f"Row {i}: 'approval_status' is blank (treated as not yet reviewed by a human).")
        elif approval not in pc.APPROVAL_STATUS_VALUES:
            errors.append(f"Row {i}: 'approval_status' value not in {sorted(pc.APPROVAL_STATUS_VALUES)}: {approval!r}")

    return errors, warnings


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    row = pc.find_company_row(args.company)
    if row is None:
        print(f"ERROR: '{args.company}' was not found in pilot_companies.csv.")
        return 1

    company = row["company"]
    slug = pc.slugify(company)
    candidates_path = pc.INTERMEDIATE_DIR / f"{slug}_source_candidates.csv"

    pc.report(f"Company: {company}  ->  slug: {slug}")
    pc.report(f"Validating: {candidates_path}")

    fieldnames, rows = pc.read_csv_rows(candidates_path)
    if fieldnames is None:
        pc.report(
            f"Not started yet: {candidates_path} does not exist. Run Claude Code's source-discovery "
            "step first (this script only validates structure -- it does not perform discovery). "
            "This is a missing prerequisite, not a validation failure."
        )
        return 2

    errors, warnings = validate_rows(rows, fieldnames)

    pc.report(f"Rows checked: {len(rows)}")
    pc.report(f"Errors: {len(errors)}")
    for e in errors:
        pc.report(f"  ERROR: {e}")
    pc.report(f"Warnings: {len(warnings)}")
    for w in warnings:
        pc.report(f"  WARNING: {w}")

    if errors:
        pc.report(
            "Result: FAIL -- fix the errors above (or have a human correct the candidate rows) "
            "before running 03_download_sources.py."
        )
    else:
        pc.report(
            "Result: PASS (structurally) -- this does NOT mean the sources are genuine or "
            "approved. A human still decides approval_status for each row."
        )

    stage_data = {
        "status": "fail" if errors else "pass",
        "rows_checked": len(rows),
        "error_count": len(errors),
        "warning_count": len(warnings),
    }
    if args.dry_run:
        pc.report("[dry-run] Checkpoint not updated.")
    else:
        pc.save_checkpoint(slug, "validate_source_candidates", stage_data, dry_run=False)

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
