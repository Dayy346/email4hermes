# Categorize News

Classify collected newsletter items into topics and extract entities.

## When to use

- After `collect-emails` produced `output/collect.json` with `count > 0`

## Inputs

- `output/collect.json`

## Procedure

1. Read each item's `subject`, `body`, and `links`.
2. Assign one or more topic tags from:
   - `llms`, `rag`, `agents`, `security`, `infra`, `devtools`, `research`, `product`, `other`
3. Extract entities: organizations, model names, products, technologies.
4. Write `output/categorize.json`.

## Output schema

```json
{
  "items": [
    {
      "id": "string",
      "topics": ["agents"],
      "organizations": ["OpenAI"],
      "models": ["GPT-x"],
      "technologies": ["RAG"],
      "notes": "optional short note"
    }
  ]
}
```

## Failure behavior

- If an item is too short to classify: use `topics: ["other"]` and continue.
- Never drop items here; preserve every collected `id`.
