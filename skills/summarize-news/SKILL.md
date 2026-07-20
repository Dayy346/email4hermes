# Summarize News

Produce concise structured summaries and flag claims that need verification.

## When to use

- After `categorize-news` wrote `output/categorize.json`

## Inputs

- `output/collect.json`
- `output/categorize.json`

## Procedure

1. Join collect + categorize by `id`.
2. For each item, write:
   - `headline` (one line)
   - `summary` (3–5 sentences max)
   - `takeaways` (1–3 bullets, technical)
   - `claims_to_verify` (statements that research should check)
3. Write `output/summarize.json`.

## Output schema

```json
{
  "items": [
    {
      "id": "string",
      "headline": "string",
      "summary": "string",
      "takeaways": ["string"],
      "claims_to_verify": ["string"],
      "topics": ["agents"],
      "links": ["https://..."]
    }
  ]
}
```

## Failure behavior

- Prefer source text over speculation.
- If body is truncated, summarize what is present and add a claim flag: "source body incomplete".
