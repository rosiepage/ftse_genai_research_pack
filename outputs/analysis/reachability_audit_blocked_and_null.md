# Reachability audit: 13 blocked + 49 null-result companies

OCR is never invoked anywhere in this pipeline, for any company, regardless of format -- confirmed directly in `pipeline/scripts/04_extract_text.py` ("Neither PDF nor HTML extraction ever uses OCR, under any circumstance, even if extraction comes back empty"). The `ocr_attempted` column below is therefore uniformly "No"; it is included for completeness, not because any row differs.

`possible_scanned_image_pdf` for null-result companies is an inferred proxy, not a recorded field: it flags any PDF whose extracted `.txt` file on disk is under 500 bytes, which is the only available signal (this pipeline records no scanned/image-PDF detection of its own).

## Null-result companies (49)

| Company | Sector | Document format(s) encountered | Possible scanned-image PDF | OCR attempted |
|---|---|---|---|---|
| 3i | Financial services | native_pdf | none flagged | No |
| Aberdeen Group | Financial Services | native_pdf | none flagged | No |
| Admiral Group | Insurance | clean_html | none flagged | No |
| Airtel Africa | Telecommunications services | native_pdf | none flagged | No |
| Alliance Witan | Investment Trusts | native_pdf | none flagged | No |
| Anglo American plc | Mining | native_pdf | none flagged | No |
| Antofagasta plc | Mining | native_pdf | none flagged | No |
| Babcock International | Aerospace & defence | native_pdf | none flagged | No |
| Barratt Redrow | Household goods & home construction | native_pdf | none flagged | No |
| Beazley | Insurance | native_pdf | none flagged | No |
| British American Tobacco | Tobacco | native_pdf | none flagged | No |
| British Land | Real estate | native_pdf | none flagged | No |
| Bunzl | Support services | native_pdf | none flagged | No |
| Coca-Cola Europacific Partners | Beverages | native_pdf | none flagged | No |
| Croda International | Chemicals | native_pdf | none flagged | No |
| DCC plc | Support services | native_pdf | none flagged | No |
| Diploma | Industrial support services | native_pdf | none flagged | No |
| Endeavour Mining | Mining | native_pdf | none flagged | No |
| F&C Investment Trust | Collective investments | native_pdf | none flagged | No |
| Fresnillo plc | Mining | native_pdf | none flagged | No |
| Games Workshop | Leisure goods | native_pdf | none flagged | No |
| Glencore | Mining | native_pdf | none flagged | No |
| Halma plc | Electronic equipment & parts | native_pdf | none flagged | No |
| Howdens Joinery | Homebuilding & construction supplies | native_pdf | none flagged | No |
| IG Group | Financial services | native_pdf | none flagged | No |
| IHG Hotels & Resorts | Travel & leisure | clean_html;native_pdf | none flagged | No |
| Informa | Media | native_pdf | none flagged | No |
| Intermediate Capital Group | Financial services | native_pdf | none flagged | No |
| International Airlines Group | Travel & leisure | native_pdf | none flagged | No |
| JD Sports | General retailers | native_pdf | none flagged | No |
| Land Securities | Real estate investment trusts | native_pdf | none flagged | No |
| LondonMetric Property | Real estate investment trusts | native_pdf | none flagged | No |
| Melrose Industries | Aerospace & defence | native_pdf | none flagged | No |
| National Grid plc | Multiline utilities | native_pdf | none flagged | No |
| Next plc | General retailers | native_pdf | none flagged | No |
| Pershing Square Holdings | Financial services | native_pdf | none flagged | No |
| Persimmon | Household goods & home construction | native_pdf | none flagged | No |
| Polar Capital Technology Trust | Investment trusts | native_pdf | none flagged | No |
| Prudential plc | Life insurance | clean_html;native_pdf | none flagged | No |
| Sainsbury's | Food & drug retailing | native_pdf | none flagged | No |
| Scottish Mortgage Investment Trust | Collective investments | native_pdf | none flagged | No |
| Smith & Nephew | Health care equipment & supplies | clean_html | none flagged | No |
| Smiths Group | General industrials | native_pdf | none flagged | No |
| St. James's Place | Financial services | native_pdf | none flagged | No |
| Standard Life | Life insurance | native_pdf | none flagged | No |
| Tritax Big Box REIT | Real estate investment trusts | native_pdf | none flagged | No |
| United Utilities | Multiline utilities | native_pdf | none flagged | No |
| Weir Group | Industrial goods and services | native_pdf | none flagged | No |
| Whitbread | Retail hospitality | native_pdf | none flagged | No |

## Blocked companies (13)

**Correction (2026-09-04):** the two rows below marked with an asterisk were originally populated
by mechanically concatenating each company's raw `blocker_type` field values from
`manual_browser_resolution_queue_controller.csv`, which is imprecise where a company has multiple
queue rows with differently-worded (but consistent) `blocker_type` labels. Re-read directly
against each row's own `notes` text (the actual retry-attempt record, and the more reliable
source): **Lloyds Banking Group**'s three queue rows all describe the same Cloudflare "Error 1007"
block page, not a generic application error; **Sage Group**'s three queue rows all describe a
persistent HTTP 403, including the one row whose `blocker_type` field says
`document_location_only` (its own notes read "HTTP 403 Forbidden retrying the main sustainability
landing page"). Sage Group therefore belongs with the other nine plain-403 companies below, not
grouped with Lloyds.

| Company | Sector | Blocker type | Document format encountered | OCR attempted |
|---|---|---|---|---|
| Associated British Foods | Food & tobacco | 403_domain_wide | unknown - blocked before any document was ever opened | No |
| BP | Oil & gas producers | 403_domain_wide | unknown - blocked before any document was ever opened | No |
| Burberry Group | Personal goods | 403_domain_wide | unknown - blocked before any document was ever opened | No |
| Coca-Cola HBC | Beverages | 403_domain_wide | unknown - blocked before any document was ever opened | No |
| Compass Group | Support services | 403_domain_wide | unknown - blocked before any document was ever opened | No |
| Computacenter | Software & computer services | timeout_domain_wide | unknown - blocked before any document was ever opened | No |
| Haleon | Pharmaceuticals & biotechnology | 403_domain_wide | unknown - blocked before any document was ever opened | No |
| IMI | Industrial engineering | 403_domain_wide | unknown - blocked before any document was ever opened | No |
| Imperial Brands | Tobacco | 403_domain_wide | unknown - blocked before any document was ever opened | No |
| Lloyds Banking Group | Banks | *cloudflare_error_1007 (corrected 2026-09-04, was application_error_domain_wide;document_location_only) | unknown - blocked before any document was ever opened | No |
| M&G | Financial services | encrypted_pdf_extraction_blocked | native_pdf (downloaded, but AES-encrypted -- extraction blocked) | No |
| Sage Group | Software & computer services | *403_domain_wide (corrected 2026-09-04, was 403_domain_wide;document_location_only) | unknown - blocked before any document was ever opened | No |
| Unilever | Personal goods | 403_domain_wide | unknown - blocked before any document was ever opened | No |
