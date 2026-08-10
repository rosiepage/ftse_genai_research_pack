#!/usr/bin/env python3
"""
03_download_sources.py -- download only the sources a human has approved.

Plain-English summary
----------------------
This script reads outputs/intermediate/<company>_source_candidates.csv and
downloads exactly the rows where a human has already set
approval_status = approved. It never guesses which sources are worth
downloading, never retries a blocked site with different headers to get
around a block, and never re-downloads a file that is already sitting in
sources/<company-slug>/.

Effective download URL
-----------------------
Each row may carry both a human-facing `url`/`landing_page_url` (often a
report's landing page, not the report itself) and a `direct_download_url`
(the actual document link, where known). This script always prefers
`direct_download_url` when it is non-empty; only falls back to `url` when
`direct_download_url` is blank. Both the landing page and the selected
"effective" download URL are always shown in the report and the log, so a
human can see exactly which one was used.

File type / extension
----------------------
This script never assumes every source is a PDF. For a real download, it
inspects the HTTP Content-Type of the response (and the final URL after any
redirects) and chooses the file extension accordingly: application/pdf ->
.pdf, text/html or application/xhtml+xml -> .html, text/plain -> .txt,
otherwise a recognised extension from the final URL, otherwise .bin (with a
warning logged). In dry-run mode -- which makes no network request at all
-- the same extension is only *guessed* from the URL itself, and every
dry-run report line says so explicitly.

Content validation
-------------------
Before a real download is accepted, the response is checked: a file destined
for .pdf must start with the "%PDF-" signature; a file destined for .html
must look like actual HTML and must not look like a login page, access-
denied page, bot/CAPTCHA challenge, or generic error page. Anything that
fails this check is recorded as `manual_collection_required`, not silently
accepted. Downloads are written to a temporary ".partial" file first and
only renamed to the final filename after validation passes, so a failed
download never leaves a half-written file at the real path.

Duplicate detection
---------------------
Rows are deduplicated on the normalised *effective* download URL, not the
landing page. Two different reports that happen to share one landing-page
URL (e.g. an annual-report archive index covering several years) are
correctly treated as distinct documents as long as their direct download
URLs differ. If two rows really do resolve to the same effective download
URL, both candidate titles are reported so nothing is silently discarded.

If the candidates file doesn't exist yet (source discovery hasn't run for
this company), this script does not treat that as an error: it scans
sources/<company-slug>/ and reports whatever is already there, makes no
network requests, makes no file changes, and returns a distinct exit code
so a caller can tell "not started yet" apart from a genuine failure.

Exit codes
----------
    0 = completed successfully (including "ran fine, 0 approved rows to download")
    1 = processing ran and found a genuine error (e.g. unknown company)
    2 = prerequisite not yet available (the candidates file doesn't exist
        yet) -- this means "not started yet", not "failed"

Examples
--------
    python 03_download_sources.py --company AstraZeneca
    python 03_download_sources.py --company Tesco --dry-run
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pipeline_common as pc  # noqa: E402

SCRIPT_NAME = "03_download_sources"

USER_AGENT = "FTSE100-GenAI-Research-Pipeline/1.0 (academic research project; contact via project owner)"
REQUEST_TIMEOUT_SECONDS = 20

DOWNLOAD_LOG_FIELDS = [
    "company",
    "ticker",
    "candidate_title",
    "landing_page_url",
    "direct_download_url",
    "effective_download_url",
    "final_redirected_url",
    "http_status",
    "content_type",
    "filename",
    "result",
    "reason",
]

# Content-Type (main type, ignoring charset etc.) -> file extension.
CONTENT_TYPE_TO_EXTENSION = {
    "application/pdf": ".pdf",
    "text/html": ".html",
    "application/xhtml+xml": ".html",
    "text/plain": ".txt",
}

# Recognised extensions we're willing to trust straight off a URL path.
RECOGNISED_URL_EXTENSIONS = {".pdf", ".html", ".htm", ".txt"}

# Substrings (checked case-insensitively) that indicate an HTML response is
# actually a login wall, bot-check, or generic error page rather than the
# real content.
ERROR_PAGE_MARKERS = [
    b"access denied",
    b"are you a robot",
    b"captcha",
    b"please verify you are human",
    b"sign in to continue",
    b"login required",
    b"403 forbidden",
    b"404 not found",
    b"page not found",
    b"just a moment",  # Cloudflare bot-check interstitial
    b"incapsula",  # Incapsula bot-check interstitial (e.g. "_Incapsula_Resource" iframe stub)
    b"request unsuccessful",  # Incapsula's generic incident-ID error text
]

# Characters not allowed in Windows filenames, plus control characters.
WINDOWS_UNSAFE_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Download only the rows in outputs/intermediate/<company>_source_candidates.csv "
            "marked approval_status = approved. Prefers each row's direct_download_url over its "
            "landing-page url. Determines the saved file's extension from the actual HTTP "
            "Content-Type (falling back to the final URL, then .bin) rather than assuming "
            "everything is a PDF -- HTML webpages are saved as .html, never mislabelled .pdf. "
            "Validates content before accepting it, skips files already on disk, records "
            "duplicate/manual-collection-required/failed outcomes, and never bypasses access controls."
        ),
        epilog=(
            "Exit codes: 0 = completed (including 0 approved rows); 1 = genuine error (e.g. unknown "
            "company); 2 = prerequisite not available yet (candidates file missing -- 'not started "
            "yet', not a failure). Key behaviour: direct_download_url is always preferred over the "
            "landing-page url when present; the saved extension is decided by the real Content-Type "
            "of the response (HTML pages get .html, not .pdf); in --dry-run mode no network request "
            "of any kind is made -- the reported extension is only a heuristic guess from the URL, "
            "clearly labelled as such."
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
        help="Report what would be downloaded, its expected content type/extension, and where it "
             "would be saved -- no network requests of any kind, no file writes.",
    )
    return parser.parse_args(argv)


# ---------------------------------------------------------------------------
# URL selection and deduplication
# ---------------------------------------------------------------------------

def select_effective_download_url(row: dict) -> str:
    """direct_download_url wins whenever it's non-empty; otherwise fall back to url."""
    direct = (row.get("direct_download_url") or "").strip()
    if direct:
        return direct
    return (row.get("url") or "").strip()


def normalize_url_for_dedup(url: str) -> str:
    return url.strip().lower().rstrip("/")


# ---------------------------------------------------------------------------
# Extension / content-type handling
# ---------------------------------------------------------------------------

def extension_from_content_type(content_type: str) -> str | None:
    if not content_type:
        return None
    main_type = content_type.split(";")[0].strip().lower()
    return CONTENT_TYPE_TO_EXTENSION.get(main_type)


def extension_from_url(url: str) -> str | None:
    path = urllib.parse.urlparse(url).path
    suffix = Path(path).suffix.lower()
    if suffix == ".htm":
        return ".html"
    if suffix in RECOGNISED_URL_EXTENSIONS:
        return suffix
    return None


def guess_expected_content_type_and_extension(url: str) -> tuple[str, str]:
    """Heuristic only -- makes no network request. Used for dry-run reporting
    and as a pre-fetch existing-file check before a real download.
    """
    ext = extension_from_url(url)
    if ext == ".pdf":
        return "application/pdf (guessed from URL)", ".pdf"
    if ext == ".html":
        return "text/html (guessed from URL)", ".html"
    if ext == ".txt":
        return "text/plain (guessed from URL)", ".txt"
    return "text/html (assumed -- no recognised file extension in URL; dry-run heuristic only)", ".html"


# ---------------------------------------------------------------------------
# Filename safety
# ---------------------------------------------------------------------------

def safe_extension_filename(base: str, extension: str) -> str:
    """Windows-safe, deterministic filename ending in exactly one of the
    given extension. Generalises pc.safe_pdf_filename() to any extension --
    this script is currently the only consumer of multi-extension filenames,
    so the helper lives here rather than in pipeline_common.py.
    """
    base = WINDOWS_UNSAFE_CHARS.sub("", base).strip().rstrip(". ")
    ext = extension if extension.startswith(".") else f".{extension}"
    while base.lower().endswith(ext.lower()):
        base = base[: -len(ext)]
    return f"{base}{ext}"


def build_local_filename(ticker: str, evidence_origin: str, document_category: str,
                          candidate_title: str, publication_date_candidate: str,
                          financial_year_covered: str, extension: str) -> str:
    """Build a local filename from ticker, evidence origin, document category, a
    short sanitised title (or financial year, when a real one is known -- much
    shorter and more meaningful for annual/sustainability reports), the
    publication date where confirmed, and the actual extension.
    """
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
    return safe_extension_filename(base, extension)


# ---------------------------------------------------------------------------
# Content validation
# ---------------------------------------------------------------------------

def looks_like_pdf(content: bytes) -> bool:
    return content[:5] == b"%PDF-"


def looks_like_html(content: bytes) -> bool:
    head = content[:2048].lower()
    return b"<html" in head or b"<!doctype html" in head


def looks_like_error_or_blocked_page(content: bytes) -> bool:
    head = content[:4096].lower()
    return any(marker in head for marker in ERROR_PAGE_MARKERS)


def validate_content(extension: str, content: bytes) -> str | None:
    """Return a human-readable problem description if content fails
    validation for its determined extension, or None if it passes.
    """
    if extension == ".pdf":
        if not looks_like_pdf(content):
            return "expected a PDF (Content-Type/URL indicated .pdf) but the response body does not start with the %PDF- signature"
        return None
    if extension == ".html":
        if looks_like_error_or_blocked_page(content):
            return "response looks like an access-denied/login/bot-check/error page, not the real content"
        if not looks_like_html(content):
            return "expected HTML (Content-Type/URL indicated .html) but the response body does not look like HTML"
        return None
    return None  # .txt and .bin: no strict signature check is defined


# ---------------------------------------------------------------------------
# Network
# ---------------------------------------------------------------------------

def fetch_url(url: str) -> dict:
    """Perform the network request only -- does not write to disk or validate
    content. Never retries with spoofed headers or proxies if blocked; a 403
    is reported and left for a human to resolve, exactly like the
    AstraZeneca MANUAL_DOWNLOAD_CHECKLIST.md precedent.
    """
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            content = response.read()
            return {
                "ok": True,
                "content": content,
                "http_status": response.status,
                "content_type": response.headers.get("Content-Type", ""),
                "final_url": response.geturl(),
            }
    except urllib.error.HTTPError as exc:
        return {
            "ok": False, "http_status": exc.code, "content_type": "", "final_url": url,
            "reason": f"HTTP {exc.code} -- {exc.reason}",
        }
    except urllib.error.URLError as exc:
        return {
            "ok": False, "http_status": None, "content_type": "", "final_url": url,
            "reason": f"network error -- {exc.reason}",
        }
    except OSError as exc:
        return {
            "ok": False, "http_status": None, "content_type": "", "final_url": url,
            "reason": f"local file error -- {exc}",
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

    company = row["company"]
    ticker = row["ticker"]
    slug = pc.slugify(company)
    company_dir = pc.SOURCES_DIR / slug
    candidates_path = pc.INTERMEDIATE_DIR / f"{slug}_source_candidates.csv"
    log_path = pc.INTERMEDIATE_DIR / f"{slug}_download_log.csv"

    pc.report(f"Company: {company} ({ticker})  ->  slug: {slug}")

    fieldnames, rows = pc.read_csv_rows(candidates_path)
    if fieldnames is None:
        pc.report(
            f"Not started yet: {candidates_path} does not exist. Run Claude Code's source-discovery "
            "step and 02_validate_source_candidates.py first. This is a missing prerequisite, not a failure."
        )
        if company_dir.exists():
            existing_files = sorted(
                p for pattern in ("*.pdf", "*.html", "*.htm", "*.txt") for p in company_dir.glob(pattern)
            )
            pc.report(f"Existing source files already present in {company_dir}: {len(existing_files)}")
            for existing_path in existing_files:
                pc.report(f"  [existing] {existing_path.name}")
        else:
            pc.report(f"{company_dir} does not exist yet -- 0 existing source files.")
        pc.report("Approved candidates to process: 0 (candidates file missing).")
        pc.report("No network requests made. No file changes made.")
        return 2

    approved_rows = [r for r in rows if (r.get("approval_status") or "").strip() == "approved"]
    pc.report(f"Approved rows: {len(approved_rows)} of {len(rows)} total candidates")

    if not approved_rows:
        pc.report("Nothing to download -- no rows are marked approval_status = approved yet.")
        return 0

    if not company_dir.exists() and not args.dry_run:
        company_dir.mkdir(parents=True, exist_ok=True)

    seen_effective_urls: dict[str, str] = {}  # normalised effective URL -> candidate_title already seen
    log_rows: list[dict] = []
    counts = {"downloaded": 0, "skipped_existing": 0, "duplicate": 0, "manual_collection_required": 0, "failed": 0}

    for r in approved_rows:
        candidate_title = (r.get("candidate_title") or "").strip()
        landing_page_url = (r.get("landing_page_url") or "").strip()
        direct_download_url = (r.get("direct_download_url") or "").strip()
        document_category = (r.get("document_category") or "").strip()
        evidence_origin = (r.get("evidence_origin") or "").strip()
        publication_date_candidate = (r.get("publication_date_candidate") or "").strip()
        financial_year_covered = (r.get("financial_year_covered") or "").strip()
        accessibility_status = (r.get("accessibility_status") or "").strip()
        verification_status = (r.get("verification_status") or "").strip()

        effective_url = select_effective_download_url(r)
        dedup_key = normalize_url_for_dedup(effective_url)

        manual_warning = None
        if accessibility_status not in ("fetched_ok",) or verification_status not in ("verified", "url_confirmed_cross_source"):
            manual_warning = (
                f"source_candidates.csv still shows accessibility_status={accessibility_status!r}, "
                f"verification_status={verification_status!r} -- re-check manually if this download "
                "doesn't look right."
            )

        if dedup_key in seen_effective_urls:
            result, reason, http_status, content_type, final_url, filename = (
                "duplicate",
                f"same effective_download_url as candidate {seen_effective_urls[dedup_key]!r}",
                "", "", "", "",
            )
            counts["duplicate"] += 1
            pc.report(f"  [duplicate] {candidate_title!r} duplicates {seen_effective_urls[dedup_key]!r} (same effective_download_url: {effective_url})")
            log_rows.append({
                "company": company, "ticker": ticker, "candidate_title": candidate_title,
                "landing_page_url": landing_page_url, "direct_download_url": direct_download_url,
                "effective_download_url": effective_url, "final_redirected_url": final_url,
                "http_status": http_status, "content_type": content_type, "filename": filename,
                "result": result, "reason": reason,
            })
            continue

        seen_effective_urls[dedup_key] = candidate_title
        expected_content_type, guessed_ext = guess_expected_content_type_and_extension(effective_url)
        guessed_filename = build_local_filename(
            ticker, evidence_origin, document_category, candidate_title,
            publication_date_candidate, financial_year_covered, guessed_ext,
        )
        guessed_path = company_dir / guessed_filename

        if args.dry_run:
            action = "skipped_existing (already present)" if guessed_path.exists() else "would_download"
            pc.report(
                f"  [{action}] {candidate_title}\n"
                f"      landing_page_url:        {landing_page_url}\n"
                f"      effective_download_url:  {effective_url}\n"
                f"      expected content type:   {expected_content_type}\n"
                f"      proposed extension:      {guessed_ext}\n"
                f"      proposed filename:       {guessed_filename}"
                + (f"\n      warning: {manual_warning}" if manual_warning else "")
            )
            continue

        # --- Real run from here -----------------------------------------
        if guessed_path.exists():
            result, reason = "skipped_existing", f"file already present: {guessed_path}"
            http_status, content_type, final_url, filename = "", "", "", guessed_filename
        else:
            fetch = fetch_url(effective_url)
            if not fetch["ok"]:
                if fetch.get("http_status") in (404, 410):
                    result = "failed"
                else:
                    # 403s and other blocked/unexpected responses need a human, not a retry.
                    result = "manual_collection_required"
                reason = fetch["reason"]
                http_status, content_type, final_url, filename = fetch.get("http_status", ""), "", fetch["final_url"], ""
                pc.log_error(slug, SCRIPT_NAME, f"{result} downloading {effective_url}: {reason}")
            else:
                content = fetch["content"]
                content_type = fetch["content_type"]
                final_url = fetch["final_url"]
                http_status = fetch["http_status"]

                real_ext = extension_from_content_type(content_type) or extension_from_url(final_url)
                if real_ext is None:
                    real_ext = ".bin"
                    pc.log_error(slug, SCRIPT_NAME, f"{effective_url}: could not determine a safe extension from Content-Type ({content_type!r}) or final URL ({final_url}); using .bin")

                filename = build_local_filename(
                    ticker, evidence_origin, document_category, candidate_title,
                    publication_date_candidate, financial_year_covered, real_ext,
                )
                real_path = company_dir / filename

                if real_path.exists():
                    result, reason = "skipped_existing", f"file already present: {real_path}"
                else:
                    problem = validate_content(real_ext, content)
                    if problem:
                        result, reason = "manual_collection_required", problem
                        pc.log_error(slug, SCRIPT_NAME, f"{effective_url}: {problem}")
                    else:
                        tmp_path = real_path.with_name(real_path.name + ".partial")
                        tmp_path.write_bytes(content)
                        tmp_path.rename(real_path)
                        result, reason = "downloaded", f"{len(content)} bytes, content_type={content_type}"

        counts[result] = counts.get(result, 0) + 1
        pc.report(f"  [{result}] {candidate_title} -> {filename or '(no file)'} ({reason})" + (f" | {manual_warning}" if manual_warning else ""))

        log_rows.append({
            "company": company, "ticker": ticker, "candidate_title": candidate_title,
            "landing_page_url": landing_page_url, "direct_download_url": direct_download_url,
            "effective_download_url": effective_url, "final_redirected_url": final_url,
            "http_status": http_status, "content_type": content_type, "filename": filename,
            "result": result, "reason": reason,
        })

    pc.report(f"Summary: {counts}")

    if args.dry_run:
        pc.report(f"[dry-run] Would write download log to: {log_path}")
        pc.report("[dry-run] Checkpoint not updated.")
        pc.report("[dry-run] No network requests were made.")
    else:
        _, existing_log_rows = pc.read_csv_rows(log_path)
        pc.write_csv_rows(log_path, DOWNLOAD_LOG_FIELDS, existing_log_rows + log_rows)
        pc.report(f"Download log written: {log_path}")
        pc.save_checkpoint(slug, "download_sources", {"status": "complete", **counts}, dry_run=False)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
