# Manual task-suitability classification of the 58 confirmed operational GenAI use cases,
# applied by the analyst after reading each record_id's full description/quotation from the
# read-only snapshot. Three axes, matching the criteria given by the user:
#   input_type: unstructured_language | structured_or_nonlanguage | mixed
#   output_type: generative_interpretive | classification_or_analytics_leaning | mixed
#   cost_of_error: low | medium | high
# "fit" is a holistic judgement: good | partial | mixed_bundle (row bundles >1 sub-use with
# differing stakes) -- not a re-derivation of evidence_strength/confidence, which are separate.

CLASSIFICATION = {
    "AZN-UC-002": ("unstructured_language", "generative_interpretive", "low", "good"),
    "AZN-UC-003": ("unstructured_language", "generative_interpretive", "medium", "good"),
    "AZN-UC-004C": ("structured_or_nonlanguage", "generative_interpretive", "low", "partial"),
    "TSCO-UC-002": ("structured_or_nonlanguage", "generative_interpretive", "low", "good"),
    "BT-UC-001": ("unstructured_language", "generative_interpretive", "low", "good"),
    "BT-UC-002": ("unstructured_language", "generative_interpretive", "medium", "good"),
    "BT-UC-003": ("unstructured_language", "generative_interpretive", "medium", "good"),
    "BT-UC-004": ("unstructured_language", "generative_interpretive", "low", "good"),
    "RR-UC-001": ("structured_or_nonlanguage", "generative_interpretive", "low", "partial"),
    "EXPN-UC-001": ("unstructured_language", "generative_interpretive", "medium", "good"),
    "RIO-UC-001": ("unstructured_language", "generative_interpretive", "low", "good"),
    "DGE-UC-001": ("structured_or_nonlanguage", "generative_interpretive", "low", "partial"),
    "DGE-UC-002": ("unstructured_language", "generative_interpretive", "low", "good"),
    "DGE-UC-003": ("structured_or_nonlanguage", "generative_interpretive", "low", "partial"),
    "VOD-UC-001": ("unstructured_language", "generative_interpretive", "medium", "good"),
    "VOD-UC-002": ("unstructured_language", "generative_interpretive", "low", "good"),
    "LGEN-UC-001": ("mixed", "mixed", "medium", "mixed_bundle"),
    "RKT-UC-001": ("unstructured_language", "generative_interpretive", "low", "good"),
    "SHEL-UC-001": ("structured_or_nonlanguage", "generative_interpretive", "high", "partial"),
    "HSBA-UC-001": ("mixed", "mixed", "high", "mixed_bundle"),
    "HSBA-UC-002": ("unstructured_language", "generative_interpretive", "medium", "good"),
    "GSK-UC-001": ("unstructured_language", "generative_interpretive", "medium", "good"),
    "REL-UC-001": ("unstructured_language", "generative_interpretive", "high", "good"),
    "REL-UC-002": ("unstructured_language", "generative_interpretive", "high", "good"),
    "REL-UC-003": ("unstructured_language", "generative_interpretive", "high", "good"),
    "REL-UC-004": ("unstructured_language", "generative_interpretive", "medium", "good"),
    "LSEG-UC-001": ("mixed", "generative_interpretive", "medium", "good"),
    "BARC-UC-001": ("unstructured_language", "generative_interpretive", "low", "good"),
    "AV-UC-001": ("unstructured_language", "generative_interpretive", "medium", "good"),
    "AV-UC-002": ("unstructured_language", "generative_interpretive", "high", "good"),
    "AV-UC-003": ("unstructured_language", "generative_interpretive", "low", "good"),
    "SVT-UC-001": ("unstructured_language", "generative_interpretive", "low", "good"),
    "MKS-UC-001": ("unstructured_language", "generative_interpretive", "low", "good"),
    "STAN-UC-001": ("unstructured_language", "generative_interpretive", "low", "good"),
    "STAN-UC-002": ("unstructured_language", "generative_interpretive", "low", "good"),
    "NWG-UC-001": ("unstructured_language", "generative_interpretive", "low", "good"),
    "SSE-UC-001": ("unstructured_language", "generative_interpretive", "medium", "good"),
    "AUTO-UC-001": ("structured_or_nonlanguage", "generative_interpretive", "low", "good"),
    "ITRK-UC-001": ("structured_or_nonlanguage", "generative_interpretive", "low", "good"),
    "CTEC-UC-001": ("unstructured_language", "generative_interpretive", "low", "good"),
    "ENT-UC-001": ("unstructured_language", "generative_interpretive", "medium", "good"),
    "SDR-UC-001": ("unstructured_language", "generative_interpretive", "high", "good"),
    "SDR-UC-002": ("unstructured_language", "generative_interpretive", "low", "good"),
    "PSON-UC-001": ("unstructured_language", "generative_interpretive", "low", "good"),
    "CNA-UC-001": ("unstructured_language", "classification_or_analytics_leaning", "medium", "partial"),
    "KGF-UC-001": ("unstructured_language", "generative_interpretive", "medium", "good"),
    "RTO-UC-001": ("unstructured_language", "generative_interpretive", "low", "good"),
    "HSX-UC-001": ("unstructured_language", "generative_interpretive", "high", "good"),
    "HSX-UC-002": ("unstructured_language", "generative_interpretive", "medium", "good"),
    "INVP-UC-001": ("unstructured_language", "generative_interpretive", "low", "good"),
    "SPX-UC-001": ("unstructured_language", "generative_interpretive", "low", "good"),
    "MTLN-UC-001": ("unstructured_language", "generative_interpretive", "medium", "good"),
    "BGEO-UC-001": ("unstructured_language", "generative_interpretive", "medium", "good"),
    "BGEO-UC-002": ("unstructured_language", "generative_interpretive", "low", "good"),
    "SGRO-UC-001": ("unstructured_language", "generative_interpretive", "low", "good"),
    "BA-UC-001": ("unstructured_language", "mixed", "high", "mixed_bundle"),
    "BA-UC-002": ("unstructured_language", "generative_interpretive", "high", "good"),
    "BA-UC-003": ("unstructured_language", "generative_interpretive", "high", "good"),
}

if __name__ == "__main__":
    from collections import Counter
    print("Total classified:", len(CLASSIFICATION))
    print("\ninput_type distribution:")
    for k, v in Counter(x[0] for x in CLASSIFICATION.values()).most_common():
        print(f"  {k}: {v}")
    print("\noutput_type distribution:")
    for k, v in Counter(x[1] for x in CLASSIFICATION.values()).most_common():
        print(f"  {k}: {v}")
    print("\ncost_of_error distribution:")
    for k, v in Counter(x[2] for x in CLASSIFICATION.values()).most_common():
        print(f"  {k}: {v}")
    print("\nfit distribution:")
    for k, v in Counter(x[3] for x in CLASSIFICATION.values()).most_common():
        print(f"  {k}: {v}")

    # Cross-tab: how many meet ALL THREE "classic good fit" criteria simultaneously
    # (unstructured input + generative output + low/medium cost of error)?
    classic_fit = [k for k, v in CLASSIFICATION.items()
                   if v[0] == "unstructured_language" and v[1] == "generative_interpretive" and v[2] in ("low", "medium")]
    print(f"\nClassic strong-fit (unstructured input + generative output + low/medium cost of error): {len(classic_fit)} / {len(CLASSIFICATION)}")

    high_stakes = [k for k, v in CLASSIFICATION.items() if v[2] == "high"]
    print(f"High cost-of-error use cases: {len(high_stakes)} / {len(CLASSIFICATION)}")
    print(" ", high_stakes)

    non_language_input = [k for k, v in CLASSIFICATION.items() if v[0] == "structured_or_nonlanguage"]
    print(f"\nNon-language/structured-input use cases (weaker fit to 'unstructured LANGUAGE input' criterion): {len(non_language_input)}")
    print(" ", non_language_input)

    mixed_bundles = [k for k, v in CLASSIFICATION.items() if v[3] == "mixed_bundle"]
    print(f"\nMixed-bundle rows (combine sub-uses of differing task type/stakes in one record): {len(mixed_bundles)}")
    print(" ", mixed_bundles)
