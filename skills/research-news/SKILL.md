# Research News

Validate high-ranking stories using official docs and trusted sources.

## When to use

- After `rank-news` wrote `output/rank.json`

## Inputs

- `output/rank.json`
- Items where `needs_research` is true (top N from config)

## Procedure

1. For each `needs_research` item, use Hermes browsing/search tools (when available) to check:
   - Official announcement or docs
   - Primary paper / GitHub / vendor blog
   - Whether claims in `claims_to_verify` hold
2. Prefer primary sources over secondary newsletters.
3. Attach:
   - `verified_claims` / `unverified_claims`
   - `context` (implementation notes, caveats)
   - `sources` (URLs used)
4. Non-research items pass through unchanged with `researched: false`.
5. Write `output/research.json`.

## Output schema

```json
{
  "items": [
    {
      "id": "string",
      "headline": "string",
      "summary": "string",
      "takeaways": ["string"],
      "scores": {},
      "researched": true,
      "verified_claims": ["string"],
      "unverified_claims": ["string"],
      "context": "string",
      "sources": ["https://..."],
      "links": ["https://..."]
    }
  ]
}
```

## Failure behavior

- If web tools are unavailable: mark `researched: false`, copy claims into `unverified_claims`, and continue.
- Never fabricate citations.
