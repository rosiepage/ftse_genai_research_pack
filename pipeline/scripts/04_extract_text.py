#!/usr/bin/env python3
"""
04_extract_text.py -- extract text from a company's downloaded PDFs and HTML pages.

Plain-English summary
----------------------
For every PDF in sources/<company-slug>/, this script writes a plain-text
file next to it (same name, .txt instead of .pdf), with page markers so a
later quotation can always be traced back to the page it came from --
exactly the convention already used for
sources/astrazeneca/AZN_company_sustainability_report_2025.txt.

It also extracts visible text from every .html/.htm file in the same
folder, using only Python's standard library (html.parser.HTMLParser --
no BeautifulSoup, lxml, readability, or trafilatura). Script, style,
noscript, template, svg and canvas content is never included, HTML
comments are ignored, and only visible text is kept -- markup attributes
are never treated as content. HTML has no page boundaries, so HTML output
uses a single "HTML DOCUMENT" header instead of PDF-style page markers.

For PDFs, it tries pypdf first. If pypdf produces no usable text at all
and PyMuPDF happens to already be installed, it tries that as a fallback --
it never installs PyMuPDF itself. Neither PDF nor HTML extraction ever uses
OCR, under any circumstance, even if extraction comes back empty.

If a .txt file already exists for a source (PDF or HTML), that source is
always skipped, in both normal and dry-run mode -- this script will never
overwrite an existing extraction. Every HTML write goes to a temporary
".partial" file first and is only renamed to the real .txt path after the
extracted text passes validation (not empty, not dominated by an
access-denied/login/bot-check/cookie-error/page-not-found/generic-error
page) -- validation always checks the extracted *visible* text, never the
raw whole HTML file, so a single incidental error-related phrase buried in
otherwise-substantive content (e.g. inside embedded JSON metadata) does not
cause a false rejection.

Examples
--------
    python 04_extract_text.py --company AstraZeneca
    python 04_extract_text.py --company Tesco --dry-run
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pipeline_common as pc  # noqa: E402

SCRIPT_NAME = "04_extract_text"

# Tags whose text content is never visible on the page and must be excluded.
SKIP_TEXT_TAGS = {"script", "style", "noscript", "template", "svg", "canvas"}

# Block-level tags: a line break is inserted around each one so extracted
# text keeps useful paragraph/row/list structure instead of running together.
BLOCK_TAGS = {
    "p", "div", "article", "section", "header", "footer", "main", "aside", "nav",
    "h1", "h2", "h3", "h4", "h5", "h6", "li", "ul", "ol", "table", "tr", "td", "th", "br",
}

MIN_VALID_HTML_LENGTH = 200
SHORT_PAGE_BLOCK_CHECK_THRESHOLD = 1000

# Checked against the extracted *visible* text only, never the raw HTML file.
HTML_ERROR_PAGE_MARKERS = [
    "access denied",
    "are you a robot",
    "captcha",
    "please verify you are human",
    "sign in to continue",
    "login required",
    "403 forbidden",
    "404 not found",
    "page not found",
    "just a moment",  # Cloudflare bot-check interstitial
    "enable cookies to continue",
    "cookies must be enabled",
    "something went wrong",
    "internal server error",
    "service unavailable",
]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extract text from every PDF and HTML/.htm file in sources/<company-slug>/ that "
            "doesn't already have a matching .txt file. PDFs use pypdf, with an optional PyMuPDF "
            "fallback if it is already installed. HTML files are parsed with Python's standard-"
            "library html.parser.HTMLParser only -- no third-party HTML libraries. Neither path "
            "ever uses OCR. Never overwrites an existing .txt file."
        ),
        epilog=(
            "Supports both PDF and HTML extraction. PDF text uses pypdf/PyMuPDF with page markers; "
            "HTML text uses only the Python standard library (html.parser), strips script/style/"
            "nav boilerplate down to visible text, and is written with a single HTML-document header "
            "instead of page markers (HTML has no page boundaries). No OCR is used for either format. "
            "An existing .txt file is always left untouched, in both real and --dry-run mode."
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
        help="Report what would be extracted (and page counts/character counts, where readable) "
             "without writing any .txt file, error log entry, or checkpoint update.",
    )
    return parser.parse_args(argv)


# ---------------------------------------------------------------------------
# PDF extraction (unchanged behaviour)
# ---------------------------------------------------------------------------

def extract_pages_with_pypdf(pdf_path: Path) -> list[str]:
    from pypdf import PdfReader  # imported here so --help works even if pypdf were ever missing

    reader = PdfReader(str(pdf_path))
    pages: list[str] = []
    for page in reader.pages:
        try:
            pages.append(page.extract_text() or "")
        except Exception:
            pages.append("")
    return pages


def extract_pages_with_pymupdf(pdf_path: Path) -> list[str]:
    import fitz  # PyMuPDF -- only used if already installed; never installed by this script

    doc = fitz.open(str(pdf_path))
    try:
        return [page.get_text() for page in doc]
    finally:
        doc.close()


def extract_pages(pdf_path: Path, slug: str) -> tuple[list[str], str | None, bool]:
    """Return (pages, engine_used, had_error). Tries pypdf, then an
    already-installed PyMuPDF only if pypdf yields nothing usable. Never
    raises -- all failures are logged and reflected in had_error.
    """
    had_error = False
    pages: list[str] = []
    engine: str | None = None

    try:
        pages = extract_pages_with_pypdf(pdf_path)
        engine = "pypdf"
    except Exception as exc:
        pc.log_error(slug, SCRIPT_NAME, f"{pdf_path.name}: pypdf could not open/read the file: {exc}")
        had_error = True

    if not any(p.strip() for p in pages):
        try:
            import fitz  # noqa: F401  -- presence check only
        except ImportError:
            if not pages:
                pc.log_error(slug, SCRIPT_NAME, f"{pdf_path.name}: pypdf produced no text and PyMuPDF is not installed (not installing it automatically).")
        else:
            try:
                fallback_pages = extract_pages_with_pymupdf(pdf_path)
                if any(p.strip() for p in fallback_pages):
                    pages = fallback_pages
                    engine = "pymupdf"
                    had_error = False
            except Exception as exc:
                pc.log_error(slug, SCRIPT_NAME, f"{pdf_path.name}: PyMuPDF fallback also failed: {exc}")
                had_error = True

    if not pages:
        had_error = True

    return pages, engine, had_error


def write_pdf_extraction(txt_path: Path, pages: list[str]) -> None:
    total = len(pages)
    parts = []
    for i, text in enumerate(pages, start=1):
        parts.append(f"\n\n===== PAGE {i} of {total} =====\n\n")
        parts.append(text)
    txt_path.write_text("".join(parts), encoding="utf-8")


# ---------------------------------------------------------------------------
# HTML extraction (new) -- standard library only
# ---------------------------------------------------------------------------

class _VisibleTextHTMLParser(HTMLParser):
    """Collects visible page text only: skips script/style/noscript/template/
    svg/canvas content and HTML comments, ignores markup attributes entirely
    (HTMLParser never calls handle_data for attribute values), and inserts a
    line break around block-level elements to preserve useful structure.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._skip_depth = 0
        self._in_title = False
        self.title = ""
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        tag = tag.lower()
        if tag in SKIP_TEXT_TAGS:
            self._skip_depth += 1
        if tag == "title":
            self._in_title = True
        if tag in BLOCK_TAGS:
            self._parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in SKIP_TEXT_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1
        if tag == "title":
            self._in_title = False
        if tag in BLOCK_TAGS:
            self._parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth > 0:
            return
        if self._in_title:
            self.title += data
            return
        self._parts.append(data)

    def handle_comment(self, data: str) -> None:
        pass  # HTML comments are never treated as visible content

    def get_text(self) -> str:
        return "".join(self._parts)


def normalize_extracted_html_text(text: str) -> str:
    """Collapse repeated whitespace/blank lines and resolve any residual
    character references (convert_charrefs already handles most of this
    during parsing; html.unescape is a harmless extra safety pass).
    """
    text = html.unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_text_from_html(html_path: Path) -> tuple[str, str]:
    """Return (visible_text, title). HTMLParser is lenient with malformed
    markup, so this does not raise for ordinary bad HTML.
    """
    raw = html_path.read_text(encoding="utf-8", errors="replace")
    parser = _VisibleTextHTMLParser()
    parser.feed(raw)
    parser.close()
    return normalize_extracted_html_text(parser.get_text()), parser.title.strip()


def validate_html_extraction(text: str) -> str | None:
    """Return a problem description if the extracted *visible* text should
    be rejected, or None if it passes. Never inspects the raw HTML file.
    """
    if len(text) < MIN_VALID_HTML_LENGTH:
        return f"extracted visible text is near-empty ({len(text)} characters, minimum {MIN_VALID_HTML_LENGTH})"
    lowered = text.lower()
    hits = [m for m in HTML_ERROR_PAGE_MARKERS if m in lowered]
    if hits and len(text) < SHORT_PAGE_BLOCK_CHECK_THRESHOLD:
        return (
            f"extracted visible text is short ({len(text)} characters) and contains blocking/error "
            f"marker(s) {hits} -- likely a genuine access-denied/login/bot-check/error page, not real content"
        )
    return None


def build_html_output(source_filename: str, title: str, visible_text: str) -> str:
    title_line = title if title else "(no <title> found)"
    return (
        "===== HTML DOCUMENT =====\n"
        f"Source file: {source_filename}\n"
        f"Title: {title_line}\n\n"
        f"{visible_text}\n"
    )


def txt_path_for_html(html_path: Path) -> Path:
    name = html_path.name
    for suffix in (".html", ".htm"):
        if name.lower().endswith(suffix):
            name = name[: -len(suffix)]
            break
    return html_path.with_name(name + ".txt")


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
    slug = pc.slugify(company)
    company_dir = pc.SOURCES_DIR / slug

    pc.report(f"Company: {company}  ->  slug: {slug}")

    if not company_dir.exists():
        print(f"ERROR: {company_dir} does not exist yet. Run 01_setup_company.py (and download sources) first.")
        return 1

    pdf_paths = sorted(company_dir.glob("*.pdf"))
    html_paths = sorted(set(company_dir.glob("*.html")) | set(company_dir.glob("*.htm")))
    pc.report(f"PDFs found: {len(pdf_paths)}")
    pc.report(f"HTML files found: {len(html_paths)}")

    counts = {"extracted_pdf": 0, "extracted_html": 0, "skipped_existing": 0, "failed": 0, "unsupported": 0}
    any_failed = False

    # --- PDFs ---------------------------------------------------------
    for pdf_path in pdf_paths:
        txt_path = pc.txt_path_for_pdf(pdf_path)

        if txt_path.exists():
            counts["skipped_existing"] += 1
            pc.report(f"  [skipped_existing] {pdf_path.name} | type=PDF | output={txt_path.name} | reason=extraction already exists")
            continue

        if args.dry_run:
            try:
                from pypdf import PdfReader

                reader = PdfReader(str(pdf_path))
                pc.report(f"  [would_extract] {pdf_path.name} | type=PDF | output={txt_path.name} | pages={len(reader.pages)}")
            except Exception as exc:
                pc.report(f"  [would_extract] {pdf_path.name} | type=PDF | output={txt_path.name} | pages=unknown (could not open for a page count: {exc})")
            continue

        pages, engine, had_error = extract_pages(pdf_path, slug)
        non_empty_pages = sum(1 for p in pages if p.strip())
        total_chars = sum(len(p) for p in pages)

        if had_error or not pages or non_empty_pages == 0:
            counts["failed"] += 1
            any_failed = True
            reason = f"extraction produced {non_empty_pages}/{len(pages)} non-empty pages (engine={engine})"
            pc.log_error(slug, SCRIPT_NAME, f"{pdf_path.name}: {reason}")
            pc.report(f"  [failed] {pdf_path.name} | type=PDF | output={txt_path.name} | engine={engine} | pages={len(pages)} | chars={total_chars} | reason={reason}")
        else:
            write_pdf_extraction(txt_path, pages)
            counts["extracted_pdf"] += 1
            pc.report(
                f"  [extracted] {pdf_path.name} | type=PDF | output={txt_path.name} | engine={engine} | "
                f"pages={len(pages)} | chars={total_chars} | reason={non_empty_pages}/{len(pages)} non-empty pages"
            )

    # --- HTML -----------------------------------------------------------
    for html_path in html_paths:
        txt_path = txt_path_for_html(html_path)

        if txt_path.exists():
            counts["skipped_existing"] += 1
            pc.report(f"  [skipped_existing] {html_path.name} | type=HTML | output={txt_path.name} | reason=extraction already exists")
            continue

        if args.dry_run:
            pc.report(f"  [would_extract] {html_path.name} | type=HTML document | output={txt_path.name}")
            continue

        try:
            visible_text, title = extract_text_from_html(html_path)
        except Exception as exc:
            counts["failed"] += 1
            any_failed = True
            pc.log_error(slug, SCRIPT_NAME, f"{html_path.name}: HTML parsing raised: {exc}")
            pc.report(f"  [failed] {html_path.name} | type=HTML document | output={txt_path.name} | chars=0 | reason=parsing error: {exc}")
            continue

        problem = validate_html_extraction(visible_text)
        if problem:
            counts["failed"] += 1
            any_failed = True
            pc.log_error(slug, SCRIPT_NAME, f"{html_path.name}: {problem}")
            pc.report(f"  [failed] {html_path.name} | type=HTML document | output={txt_path.name} | chars={len(visible_text)} | reason={problem}")
            continue

        output_text = build_html_output(html_path.name, title, visible_text)
        tmp_path = txt_path.with_name(txt_path.name + ".partial")
        tmp_path.write_text(output_text, encoding="utf-8")
        tmp_path.rename(txt_path)
        counts["extracted_html"] += 1
        pc.report(
            f"  [extracted] {html_path.name} | type=HTML document | output={txt_path.name} | "
            f"chars={len(visible_text)} | reason=title={title or '(none)'!r}"
        )

    pc.report(f"Summary: {counts}")

    if args.dry_run:
        pc.report("[dry-run] Checkpoint not updated. No files written. No error log written.")
    else:
        stage_status = "failed" if any_failed else "complete"
        pc.save_checkpoint(slug, "extract_text", {"status": stage_status, **counts}, dry_run=False)
        if any_failed:
            pc.report("[warning] extract_text checkpoint stage recorded as 'failed' -- at least one supported source did not extract successfully.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
