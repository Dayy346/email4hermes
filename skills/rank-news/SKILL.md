# Rank News

Score stories, deduplicate across newsletters, and select what matters.

## When to use

- After `summarize-news` wrote `output/summarize.json`

## Inputs

- `output/summarize.json`
- `config/newsletter.yaml` → `top_n_research`, `profile`

## Procedure

1. Deduplicate near-identical stories (same product launch / paper / model across sources). Keep the best source and list `duplicate_of` / `merged_from` ids.
2. Score each unique story 0–100 on:
   - `relevance` (to AI/engineering + profile)
   - `novelty`
   - `engineering_impact`
   - `confidence` (source quality)
3. `total = weighted average` (impact and novelty slightly higher for senior; relevance/explainability higher for junior).
4. Sort by `total` desc. Keep all ranked items; mark top `top_n_research` with `needs_research: true`.
5. Write `output/rank.json`.

## Output schema

```json
{
  "items": [
    {
      "id": "string",
      "merged_from": ["id2"],
      "headline": "string",
      "summary": "string",
      "takeaways": ["string"],
      "claims_to_verify": ["string"],
      "links": ["https://..."],
      "scores": {
        "relevance": 0,
        "novelty": 0,
        "engineering_impact": 0,
        "confidence": 0,
        "total": 0
      },
      "needs_research": true
    }
  ]
}
```

## Failure behavior

- If only one source exists for a story, still score it.
- Do not invent scores without reading the summary.
