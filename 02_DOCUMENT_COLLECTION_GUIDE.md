# Documents to collect

Create one folder per company inside `sources/company_documents/`.

## Required documents for every company

### A. Latest annual report
Collect the latest annual report available by 14 July 2026. Prefer the full annual report PDF rather than a webpage summary.

Purpose: official discussion of strategy, operations, risks, investment and material deployments.

Filename:
`TICKER_company_annual_report_FY2025.pdf`

Adjust the financial year in the filename where required.

### B. Previous annual report
Collect the immediately preceding annual report.

Purpose: identifies changes over time and captures earlier pilots that may have developed into deployments.

Filename:
`TICKER_company_annual_report_FY2024.pdf`

### C. Latest sustainability, ESG or responsible-business report
Collect this only where it is a separate substantive report.

Purpose: workforce, responsible-AI, governance, environmental and social disclosures.

Filename:
`TICKER_company_sustainability_report_2025.pdf`

If the content is fully integrated into the annual report, mark it as not separate in the manifest rather than downloading duplicates.

## Required web evidence search for every company
Save qualifying pages as PDF, HTML or plain text and record their URLs in `source_manifest.csv`.

Search the official company website for:
- generative AI
- GenAI
- large language model
- LLM
- foundation model
- copilot
- ChatGPT
- Claude
- Gemini
- Microsoft 365 Copilot
- GitHub Copilot
- Amazon Bedrock
- Azure OpenAI
- Google Vertex AI

Collect relevant:
- company press releases;
- investor presentations;
- results presentations;
- strategy or technology webpages;
- official case studies;
- governance or responsible-AI policies;
- speeches or interviews published by the company.

Filename:
`TICKER_company_document-type_YYYY-MM-DD_short-title.pdf`

## Partner evidence
Search major technology-provider case-study libraries for the company name. Likely sources include Microsoft, Google Cloud, AWS, IBM, Salesforce, ServiceNow, Adobe, SAP, Oracle, NVIDIA and model providers.

Partner case studies may contain operational detail absent from annual reports. Code their evidence origin as `technology_partner`, not `company_primary`.

Only retain a partner source when it names the FTSE company and describes a specific generative-AI activity.

## Optional sources
Use selectively:
- regulatory filings and RNS announcements;
- earnings-call transcripts, where legally accessible;
- parliamentary or regulator evidence submitted by the company;
- reputable interviews quoting a named company executive;
- vendor conference presentations featuring a named company representative.

## Sources not suitable as final evidence
Do not rely on:
- search snippets;
- unsourced blogs;
- generic news summaries;
- social posts without substantive detail;
- automatically generated stock-market pages;
- Wikipedia as evidence of a use case.

News can help locate a primary source but should usually not be the final citation.

## Minimum viable corpus
For each company, aim for:
- two annual reports;
- one separate sustainability/governance report where available;
- all qualifying official company webpages in the evidence window;
- all clearly relevant partner case studies.

Do not impose a fixed number of AI sources per company. A company with no qualifying disclosure is a valid finding.

## PDF handling
Keep original PDFs unchanged. Extract text into a parallel `sources/extracted_text/` directory. Retain page boundaries so quotations can be traced back to their page.
