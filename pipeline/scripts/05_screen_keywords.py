#!/usr/bin/env python3
"""
05_screen_keywords.py -- mechanical keyword screening of extracted text.

Plain-English summary
----------------------
This script reads every .txt file already produced by 04_extract_text.py for
a company and looks for two tiers of generative-AI-related terms:

  Stage A (high-precision): generative AI, GenAI, large language model, LLM,
  foundation model, GPT, Copilot, Claude, Gemini, Bedrock,
  retrieval-augmented generation, RAG, agentic AI, text generation,
  code generation.

  Stage B (broader recall): AI, artificial intelligence, machine learning,
  intelligent assistant, automation, synthetic data, digital assistant.

Every Stage A hit is provisionally tagged "likely_genai" -- but this is
still just a mechanical keyword match, not a confirmed classification; a
human (or Claude Code's later, judgement-based staging step) still has to
read it and decide. Every Stage B hit is tagged "uncertain" and is NEVER
auto-tagged "likely_genai", because a bare "AI"/"automation"/"machine
learning" mention says nothing on its own about generative AI.

Original source filename resolution
------------------------------------
Each .txt file's `local_filename` is resolved back to its original source
document -- checked in order: matching .pdf, then matching .html, then
matching .htm -- so a webpage-derived .txt always reports the real .html
filename, not the .txt filename. Only if no original file can be found at
all does it fall back to the .txt filename itself, with a warning logged.

Extraction-artifact flagging (conservative, mechanical only)
--------------------------------------------------------------
pypdf's text extraction occasionally splits a word with a spurious space
(e.g. "Aiming" -> "Ai ming"), which can make the short Stage B term "AI"
match a fragment of an unrelated word rather than a genuine AI mention.
This script never deletes or silently recodes such a hit -- it adds a
`possible_extraction_artifact` column (yes/no) using a narrow, conservative
rule: only a Stage B "AI" hit whose *actual on-page casing* is Title-case
("Ai", not "AI" or "ai") and which is immediately followed by a single
space and a lowercase letter-run that looks like the rest of a word is
flagged. Ordinary "AI"/"ai" mentions, and every Stage A hit, are never
flagged by this rule.

Output goes to outputs/intermediate/<company>_candidate_passages.csv -- a
holding pen, not a dataset. This script never writes to
use_case_dataset_template.csv or any other main dataset file.

Examples
--------
    python 05_screen_keywords.py --company AstraZeneca
    python 05_screen_keywords.py --company Tesco --dry-run
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pipeline_common as pc  # noqa: E402

SCRIPT_NAME = "05_screen_keywords"

STAGE_A_KEYWORDS = [
    "generative AI",
    "GenAI",
    "large language model",
    "LLM",
    "foundation model",
    "GPT",
    "Copilot",
    "Claude",
    "Gemini",
    "Bedrock",
    "retrieval-augmented generation",
    "RAG",
    "agentic AI",
    "text generation",
    "code generation",
]

STAGE_B_KEYWORDS = [
    "AI",
    "artificial intelligence",
    "machine learning",
    "intelligent assistant",
    "automation",
    "synthetic data",
    "digital assistant",
]

CANDIDATE_PASSAGES_FIELDS = [
    "company",
    "ticker",
    "source_id",
    "local_filename",
    "page_or_section",
    "matched_keyword",
    "stage",
    "surrounding_context",
    "provisional_classification",
    "confidence",
    "reason",
    "possible_extraction_artifact",
]

PAGE_MARKER_PATTERN = re.compile(r"=====\s*PAGE\s+(\d+)\s+of\s+(\d+)\s*=====")
CONTEXT_CHARS = 150


def build_keyword_patterns(keywords: list[str]) -> list[tuple[str, re.Pattern]]:
    """Compile each keyword into a case-insensitive, whole-word regex.

    Multi-word phrases allow flexible whitespace between words (PDF text
    extraction sometimes inserts line breaks mid-phrase), and every pattern
    is word-boundary-anchored so short terms like "AI" or "RAG" never match
    as a substring inside an unrelated word.
    """
    patterns = []
    for kw in keywords:
        tokens = [re.escape(t) for t in kw.split()]
        pattern_str = r"\s+".join(tokens)
        patterns.append((kw, re.compile(rf"\b{pattern_str}\b", re.IGNORECASE)))
    return patterns


STAGE_A_PATTERNS = build_keyword_patterns(STAGE_A_KEYWORDS)
STAGE_B_PATTERNS = build_keyword_patterns(STAGE_B_KEYWORDS)


def split_into_pages(text: str) -> list[tuple[str, str]]:
    """Split extracted text into (page_label, page_text) using the
    '===== PAGE N of TOTAL =====' markers written by 04_extract_text.py.
    Falls back to a single 'not_applicable' page if no markers are found
    (this is also what happens for HTML-derived text, which has no page
    markers by design).
    """
    matches = list(PAGE_MARKER_PATTERN.finditer(text))
    if not matches:
        return [("not_applicable", text)]
    pages = []
    for idx, m in enumerate(matches):
        start = m.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        pages.append((f"p.{m.group(1)}", text[start:end]))
    return pages


def find_hits(page_text: str, patterns: list[tuple[str, re.Pattern]], stage_label: str,
              claimed: list[tuple[int, int]]) -> list[dict]:
    """Find keyword matches in page_text, skipping any whose surrounding
    context window overlaps a span already claimed by an earlier hit (Stage
    A hits are found first, so Stage B never duplicates a passage Stage A
    already captured). Extends `claimed` in place. Records the raw matched
    substring and its span so artifact-detection can inspect the exact
    on-page casing and adjacent characters.
    """
    hits = []
    for kw, pattern in patterns:
        for m in pattern.finditer(page_text):
            start, end = m.span()
            overlaps = any(not (end + CONTEXT_CHARS < s or start - CONTEXT_CHARS > e) for s, e in claimed)
            if overlaps:
                continue
            claimed.append((start, end))
            ctx_start = max(0, start - CONTEXT_CHARS)
            ctx_end = min(len(page_text), end + CONTEXT_CHARS)
            context = " ".join(page_text[ctx_start:ctx_end].split())
            hits.append({
                "keyword": kw,
                "stage": stage_label,
                "context": context,
                "matched_text": m.group(0),
                "start": start,
                "end": end,
            })
    return hits


def classify_hit(stage_label: str, keyword: str) -> tuple[str, str, str]:
    """Return (provisional_classification, confidence, reason) for a hit.
    Stage B is never auto-classified likely_genai -- that is the whole
    point of the two-stage design.
    """
    if stage_label == "A":
        return (
            "likely_genai",
            "medium",
            f"Stage A high-precision generative-AI term '{keyword}' matched; still requires human "
            "confirmation of is_genai, deployment_stage and evidence_strength.",
        )
    return (
        "uncertain",
        "low",
        f"Stage B broader-recall term '{keyword}' matched only; broader AI/automation terms are never "
        "auto-classified as generative AI and need further reading to confirm relevance.",
    )


def looks_like_extraction_artifact(stage_label: str, keyword: str, matched_text: str,
                                    page_text: str, match_end: int) -> bool:
    """Conservative, mechanical check for one specific pypdf kerning/word-
    splitting artifact: a short Stage B "AI" hit whose actual on-page
    casing is Title-case ('Ai', not 'AI' or 'ai') and which is immediately
    followed by exactly one space and a lowercase letter-run that looks
    like the remainder of an ordinary word (e.g. 'Ai ming' -> 'Aiming').

    Never flags Stage A hits, never flags the multi-word Stage B terms, and
    never flags a genuine all-caps 'AI' or all-lowercase 'ai' mention --
    only this specific mixed-case adjacency pattern.

    The separator between the two halves of a split word is not always a
    plain space -- pypdf sometimes emits a line break (CRLF or LF) at the
    split point (e.g. "Ai\\r\\nming"). Up to two whitespace characters
    (covering a lone space, a lone \\n, or a \\r\\n pair) are skipped before
    looking for the completing lowercase run; three or more whitespace
    characters is treated as a genuine word/sentence gap, not a split word.
    """
    if stage_label != "B" or keyword.lower() != "ai":
        return False
    if len(matched_text) != 2 or not (matched_text[0].isupper() and matched_text[1].islower()):
        return False
    j = match_end
    whitespace_seen = 0
    while j < len(page_text) and page_text[j].isspace() and whitespace_seen < 2:
        j += 1
        whitespace_seen += 1
    if whitespace_seen == 0:
        return False
    k = j
    while k < len(page_text) and page_text[k].isalpha() and page_text[k].islower():
        k += 1
    next_token = page_text[j:k]
    return len(next_token) >= 2


def find_original_source_name(company_dir: Path, txt_path: Path, slug: str) -> str:
    """Resolve the original source file a .txt file was extracted from,
    preserving its exact original filename and extension. Checked in order:
    matching .pdf, matching .html, matching .htm. Falls back to the .txt
    filename itself (with a logged warning) only if none is found.
    """
    for pdf_path in company_dir.glob("*.pdf"):
        if pc.txt_path_for_pdf(pdf_path) == txt_path:
            return pdf_path.name

    for pattern in ("*.html", "*.htm"):
        for candidate in company_dir.glob(pattern):
            name = candidate.name
            stem = name
            for suffix in (".html", ".htm"):
                if name.lower().endswith(suffix):
                    stem = name[: -len(suffix)]
                    break
            if stem == txt_path.stem:
                return candidate.name

    pc.log_error(
        slug, SCRIPT_NAME,
        f"{txt_path.name}: could not resolve an original .pdf/.html/.htm source file; falling back to the .txt filename.",
    )
    return txt_path.name


def load_manifest_lookup() -> dict[str, str]:
    """Map an already-logged source's local_filename (stripped of any .pdf
    suffixes, lower-cased) to its source_id, read-only from
    source_manifest.csv. Returns {} if the manifest doesn't exist or a
    company has no rows in it yet -- source_id is simply left blank for
    those hits.
    """
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


def write_candidate_passages_safely(output_path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    """Write the candidate-passages CSV to a temporary file first, validate
    it round-trips to the expected row count, then atomically replace any
    existing output file. Never leaves a half-written file at output_path.
    """
    tmp_path = output_path.with_name(output_path.name + ".partial")
    pc.write_csv_rows(tmp_path, fieldnames, rows)
    _, written_rows = pc.read_csv_rows(tmp_path)
    if len(written_rows) != len(rows):
        raise RuntimeError(
            f"validation failed writing {output_path.name}: wrote {len(rows)} rows but re-read {len(written_rows)}"
        )
    tmp_path.replace(output_path)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Screen a company's extracted .txt files for Stage A (high-precision) and Stage B "
            "(broader-recall) generative-AI keywords, writing candidate passages to "
            "outputs/intermediate/<company>_candidate_passages.csv. Purely mechanical string "
            "matching -- never decides is_genai, and never writes to any main dataset file. Each "
            "row's local_filename resolves to the real original source file (.pdf/.html/.htm), and "
            "a conservative possible_extraction_artifact flag marks (without removing) short 'AI' "
            "hits that look like a pypdf word-splitting artifact rather than a genuine AI mention."
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
        help="Report hit counts, resolved source filenames, and possible-extraction-artifact counts "
             "without writing the candidate-passages CSV or updating the checkpoint.",
    )
    return parser.parse_args(argv)


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

    pc.report(f"Company: {company} ({ticker})  ->  slug: {slug}")

    if not company_dir.exists():
        print(f"ERROR: {company_dir} does not exist yet. Run earlier pipeline stages first.")
        return 1

    txt_paths = sorted(company_dir.glob("*.txt"))
    if not txt_paths:
        pc.report("No extracted .txt files found -- nothing to screen. Run 04_extract_text.py first.")
        return 0

    manifest_lookup = load_manifest_lookup()
    output_rows: list[dict] = []
    counts = {"files_screened": 0, "stage_a_hits": 0, "stage_b_hits": 0, "possible_extraction_artifacts": 0}

    for txt_path in txt_paths:
        try:
            text = txt_path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            pc.log_error(slug, SCRIPT_NAME, f"{txt_path.name}: could not be read: {exc}", dry_run=args.dry_run)
            continue

        source_id = manifest_lookup.get(txt_path.stem.lower(), "")
        local_filename = find_original_source_name(company_dir, txt_path, slug)

        file_hit_count = 0
        for page_label, page_text in split_into_pages(text):
            claimed: list[tuple[int, int]] = []
            hits = find_hits(page_text, STAGE_A_PATTERNS, "A", claimed)
            hits += find_hits(page_text, STAGE_B_PATTERNS, "B", claimed)

            for hit in hits:
                classification, confidence, reason = classify_hit(hit["stage"], hit["keyword"])
                is_artifact = looks_like_extraction_artifact(
                    hit["stage"], hit["keyword"], hit["matched_text"], page_text, hit["end"]
                )
                output_rows.append({
                    "company": company,
                    "ticker": ticker,
                    "source_id": source_id,
                    "local_filename": local_filename,
                    "page_or_section": page_label,
                    "matched_keyword": hit["keyword"],
                    "stage": hit["stage"],
                    "surrounding_context": hit["context"],
                    "provisional_classification": classification,
                    "confidence": confidence,
                    "reason": reason,
                    "possible_extraction_artifact": "yes" if is_artifact else "no",
                })
                file_hit_count += 1
                if hit["stage"] == "A":
                    counts["stage_a_hits"] += 1
                else:
                    counts["stage_b_hits"] += 1
                if is_artifact:
                    counts["possible_extraction_artifacts"] += 1

        counts["files_screened"] += 1
        pc.report(f"  [screened] {txt_path.name} | resolved original source: {local_filename} | {file_hit_count} hit(s)")

    pc.report(f"Summary: {counts}")

    output_path = pc.INTERMEDIATE_DIR / f"{slug}_candidate_passages.csv"

    if args.dry_run:
        pc.report(f"[dry-run] Would write {len(output_rows)} candidate passage row(s) to: {output_path}")
        pc.report(f"[dry-run] Would flag {counts['possible_extraction_artifacts']} row(s) as possible_extraction_artifact=yes")
        for sample_row in output_rows[:5]:
            pc.report(f"  sample: {sample_row['stage']} / {sample_row['provisional_classification']} / "
                      f"{sample_row['matched_keyword']!r} / {sample_row['page_or_section']} / "
                      f"artifact={sample_row['possible_extraction_artifact']}")
        pc.report("[dry-run] Checkpoint not updated. No CSV written.")
    else:
        write_candidate_passages_safely(output_path, CANDIDATE_PASSAGES_FIELDS, output_rows)
        pc.report(f"Candidate passages written: {output_path} ({len(output_rows)} row(s))")
        pc.save_checkpoint(slug, "screen_keywords", {"status": "complete", **counts}, dry_run=False)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
