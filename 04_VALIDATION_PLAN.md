# Validation plan

## Purpose
The project should evaluate Claude's research performance rather than assume its classifications are correct.

## Manual validation sample
Manually review:
- all records classed as `unclear`;
- all records based only on partner evidence;
- a random 20% of included use cases;
- a random sample of excluded candidate passages;
- at least five companies for which Claude finds no use cases.

## Variables to validate
1. Is this genuinely generative AI?
2. Does the quotation support the claimed use case?
3. Is the deployment stage correct?
4. Is the business function correct?
5. Is the evidence origin correct?
6. Is it a duplicate?
7. Are the page number, URL and date correct?

## Metrics
Calculate:
- precision of included use cases;
- recall using the manually reviewed company subset;
- exact agreement for deployment stage;
- exact agreement for business function;
- citation accuracy;
- duplicate rate;
- percentage of records requiring correction.

## Error taxonomy
Label errors as:
- ordinary AI mistaken for generative AI;
- future intention mistaken for live deployment;
- vendor claim treated as company confirmation;
- unsupported benefit inferred;
- wrong business function;
- missing use case;
- duplicate use case;
- incorrect citation or page;
- ambiguous passage coded too confidently;
- other.

## Reliability improvement
After the first validation round:
1. revise ambiguous category definitions;
2. add positive and negative examples to the prompt;
3. rerun the same validation sample;
4. report changes transparently rather than hiding the first-round errors.
