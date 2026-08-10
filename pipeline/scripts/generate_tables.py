import csv
import os
from collections import Counter, defaultdict
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from task_suitability import CLASSIFICATION

SNAP = r"c:\Users\rosie\OneDrive\university\extra stuff\2026 grad jobs prep\ftse_genai_research_pack\outputs\intermediate\analysis_snapshot_2026-08-08_final_closure"
ROOT = r"c:\Users\rosie\OneDrive\university\extra stuff\2026 grad jobs prep\ftse_genai_research_pack"
OUT = r"c:\Users\rosie\OneDrive\university\extra stuff\2026 grad jobs prep\ftse_genai_research_pack\outputs\analysis"


def load(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_table(filename, header, rows):
    path = f"{OUT}\\{filename}"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow(r)
    print(f"Wrote {path} ({len(rows)} rows)")


SECTOR_MERGE = {
    "Financial Services": "Financial services",
    "Investment Trusts": "Investment trusts",
}


def merged_sector(s):
    return SECTOR_MERGE.get(s, s)


companies = load(f"{SNAP}\\company_summary_template.csv")
usecases = load(f"{SNAP}\\use_case_dataset_template.csv")
strategic = load(f"{SNAP}\\strategic_capability_building_findings.csv")
governance = load(f"{SNAP}\\governance_and_enablement_findings.csv")
blocked_queue = load(f"{SNAP}\\manual_browser_resolution_queue_controller.csv")
constituents = load(f"{ROOT}\\ftse100_constituents_2026-06-19.csv")
sector_lookup = {c["company"]: merged_sector(c["sector"]) for c in constituents}
blocked_companies = sorted(set(r["company"] for r in blocked_queue))

confirmed = [r for r in usecases if r["review_status"] in ("reviewed_confirmed", "reviewed_corrected")
             and r["is_genai"] == "yes" and r["evidence_strength"] in ("2_moderate", "3_strong")
             and not r["duplicate_of_record_id"].strip()]

promoted = [c for c in companies if int(c["confirmed_use_case_count"]) >= 1]
null_result = [c for c in companies if int(c["confirmed_use_case_count"]) == 0]

# ---------------------------------------------------------------------------
# Table 1: coverage/status
# ---------------------------------------------------------------------------
write_table("table_1_coverage.csv",
            ["status", "definition", "company_count", "pct_of_100"],
            [
                ["confirmed_operational", "confirmed_use_case_count >= 1 in company_summary_template.csv", len(promoted), f"{len(promoted)/100:.1%}"],
                ["completed_null_result", "confirmed_use_case_count == 0, evidence-based final status reached", len(null_result), f"{len(null_result)/100:.1%}"],
                ["blocked_manual_browser", "source collection could not be completed with available tools", len(blocked_companies), f"{len(blocked_companies)/100:.1%}"],
                ["TOTAL", "sum (cross-checked against ftse100_constituents_2026-06-19.csv, no omissions/duplicates)", 100, "100.0%"],
            ])

# ---------------------------------------------------------------------------
# Table 2: adoption stats, two denominators
# ---------------------------------------------------------------------------
n_conf = len(promoted)
n_null = len(null_result)
n_blocked = len(blocked_companies)
total_confirmed_ucs = sum(int(c["confirmed_use_case_count"]) for c in companies)
total_provisional_ucs = sum(int(c["provisional_use_case_count"]) for c in companies)
dist = Counter(int(c["confirmed_use_case_count"]) for c in companies if int(c["confirmed_use_case_count"]) >= 1)

rows = [
    ["confirmed_operational_companies", n_conf, f"{n_conf/100:.1%}", f"{n_conf/87:.1%}"],
    ["null_result_companies", n_null, f"{n_null/100:.1%}", f"{n_null/87:.1%}"],
    ["blocked_companies", n_blocked, f"{n_blocked/100:.1%}", "n/a (excluded from denominator B)"],
    ["total_confirmed_use_cases", total_confirmed_ucs, "", ""],
    ["total_provisional_use_cases", total_provisional_ucs, "", ""],
]
write_table("table_2_adoption.csv",
            ["metric", "value", "pct_denominator_A_all100", "pct_denominator_B_87evidence"],
            rows)

# ---------------------------------------------------------------------------
# Table 3: use-case categories
# ---------------------------------------------------------------------------
rows = []
for field, label in [
    ("primary_business_function", "primary_business_function"),
    ("secondary_business_function", "secondary_business_function"),
    ("deployment_stage", "deployment_stage"),
    ("orientation", "orientation"),
    ("user_group", "user_group"),
]:
    counts = Counter(r[field] for r in confirmed)
    for val, n in counts.most_common():
        rows.append([label, val, n, f"{n/58:.1%}"])
benefit_counter = Counter()
for r in confirmed:
    for b in r["claimed_benefits"].split(";"):
        b = b.strip()
        if b:
            benefit_counter[b] += 1
for val, n in benefit_counter.most_common():
    rows.append(["claimed_benefits (multi-label)", val, n, f"{n/58:.1%}"])
for val, n in Counter(r["benefit_evidence"] for r in confirmed).most_common():
    rows.append(["benefit_evidence", val, n, f"{n/58:.1%}"])
write_table("table_3_use_case_categories.csv",
            ["dimension", "value", "count", "pct_of_58_confirmed"],
            rows)

# ---------------------------------------------------------------------------
# Table 3b: task suitability detail (row by row)
# ---------------------------------------------------------------------------
rows = []
for r in confirmed:
    rid = r["record_id"]
    cls = CLASSIFICATION.get(rid, ("", "", "", ""))
    rows.append([rid, r["company"], r["sector"], r["use_case_name"], r["primary_business_function"],
                 r["deployment_stage"], cls[0], cls[1], cls[2], cls[3]])
write_table("table_3b_task_suitability_detail.csv",
            ["record_id", "company", "sector", "use_case_name", "primary_business_function",
             "deployment_stage", "input_type", "output_type", "cost_of_error", "fit_judgement"],
            rows)

# ---------------------------------------------------------------------------
# Table 4: sector comparison (merged labels)
# ---------------------------------------------------------------------------
sector_stats = defaultdict(lambda: {"researched": 0, "confirmed_op": 0, "use_cases": 0, "null": 0, "blocked": 0})
for c in companies:
    sec = merged_sector(c["sector"])
    sector_stats[sec]["researched"] += 1
    n = int(c["confirmed_use_case_count"])
    if n >= 1:
        sector_stats[sec]["confirmed_op"] += 1
        sector_stats[sec]["use_cases"] += n
    else:
        sector_stats[sec]["null"] += 1
for name in blocked_companies:
    sec = sector_lookup.get(name, "UNKNOWN")
    sector_stats[sec]["blocked"] += 1

rows = []
for sec in sorted(sector_stats.keys()):
    s = sector_stats[sec]
    total = s["researched"] + s["blocked"]
    rate = f"{s['confirmed_op']/s['researched']:.0%}" if s["researched"] > 0 else "n/a"
    small_sample_flag = "YES - n<3" if total < 3 else ("caution - n<5" if total < 5 else "")
    rows.append([sec, s["researched"], s["confirmed_op"], rate, s["use_cases"], s["null"], s["blocked"], total, small_sample_flag])
write_table("table_4_sector_comparison.csv",
            ["sector", "researched", "confirmed_operational", "confirmed_op_rate_of_researched",
             "confirmed_use_cases", "null_result", "blocked", "total_in_sector_incl_blocked", "small_sample_flag"],
            rows)

# ---------------------------------------------------------------------------
# Table 5: strategic/governance vs operational
# ---------------------------------------------------------------------------
companies_with_strategic = set(r["company"] for r in strategic)
companies_with_governance = set(r["company"] for r in governance)
companies_with_confirmed_op = set(c["company"] for c in promoted)
company_names_summary = set(c["company"] for c in companies)
companies_with_any = companies_with_strategic | companies_with_governance | companies_with_confirmed_op
only_str_gov_no_op = (companies_with_strategic | companies_with_governance) - companies_with_confirmed_op
zero_evidence = company_names_summary - companies_with_any

rows = [
    ["confirmed_operational_use_case", len(companies_with_confirmed_op), f"{len(companies_with_confirmed_op)/87:.1%}"],
    ["strategic_finding_present", len(companies_with_strategic), f"{len(companies_with_strategic)/87:.1%}"],
    ["governance_finding_present", len(companies_with_governance), f"{len(companies_with_governance)/87:.1%}"],
    ["any_ai_evidence_strategic_gov_or_operational", len(companies_with_any), f"{len(companies_with_any)/87:.1%}"],
    ["strategic_or_governance_but_NO_confirmed_operational", len(only_str_gov_no_op), f"{len(only_str_gov_no_op)/87:.1%}"],
    ["zero_qualifying_evidence_of_any_kind", len(zero_evidence), f"{len(zero_evidence)/87:.1%}"],
]
write_table("table_5_strategic_governance_vs_operational.csv",
            ["group", "company_count", "pct_of_87_evidence_based"],
            rows)

# also write the company lists for the two key groups as a second small table
rows2 = [["strategic_or_governance_no_operational", c] for c in sorted(only_str_gov_no_op)] + \
        [["zero_qualifying_evidence", c] for c in sorted(zero_evidence)]
write_table("table_5b_company_lists.csv", ["group", "company"], rows2)

# ---------------------------------------------------------------------------
# Table 6: evidence quality
# ---------------------------------------------------------------------------
es_all = Counter(r["evidence_strength"] for r in usecases)
es_conf = Counter(r["evidence_strength"] for r in confirmed)
conf_conf = Counter(r["confidence"] for r in confirmed)
origin_conf = Counter(r["evidence_origin"] for r in confirmed)
benefit_conf = Counter(r["benefit_evidence"] for r in confirmed)

rows = []
for k, v in es_all.items():
    rows.append(["evidence_strength_all_63_rows", k, v, f"{v/63:.1%}"])
for k, v in es_conf.items():
    rows.append(["evidence_strength_58_confirmed", k, v, f"{v/58:.1%}"])
for k, v in conf_conf.items():
    rows.append(["confidence_58_confirmed", k, v, f"{v/58:.1%}"])
for k, v in origin_conf.items():
    rows.append(["evidence_origin_58_confirmed", k, v, f"{v/58:.1%}"])
for k, v in benefit_conf.items():
    rows.append(["benefit_evidence_58_confirmed", k, v, f"{v/58:.1%}"])
write_table("table_6_evidence_quality.csv",
            ["dimension", "value", "count", "pct"],
            rows)

# ---------------------------------------------------------------------------
# Table 7: blocked sensitivity
# ---------------------------------------------------------------------------
rows = []
for name in blocked_companies:
    sec = sector_lookup.get(name, "UNKNOWN")
    rows.append([name, sec])
write_table("table_7a_blocked_companies.csv", ["company", "sector"], rows)

rows = []
for n_hits in [0, 2, 4, 6, 8, 10, 13]:
    combined = n_conf + n_hits
    rows.append([n_hits, combined, f"{combined/100:.1%}"])
write_table("table_7b_blocked_sensitivity_bounds.csv",
            ["blocked_companies_assumed_to_qualify", "resulting_confirmed_total", "resulting_pct_of_100"],
            rows)

print("\nAll tables written.")
