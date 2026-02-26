# OpenClaw Council

Pluggable **Council mode** for OpenClaw: run multiple role prompts (and optionally multiple model providers) in parallel, then synthesize one final answer with explicit agreement/disagreement and risk mapping.

> This project is an **OpenClaw plugin/overlay**, not a fork of the OpenClaw core runtime.

## Why

Single-model answers can be fast but brittle. Council mode adds structured cross-checking:

- Parallel role perspectives (`analyst`, `skeptic`, `builder`, etc.)
- Critique round to expose weak assumptions
- Final synthesis into one actionable answer
- Transparent output (`agreement_points`, `disagreement_points`, `risks`, `confidence`)

## Features

- Unlimited pluggable roles (`roles/*.md`)
- Multi-provider support via OpenAI-compatible Chat Completions endpoints
- Parallel round-1 + critique round + synthesis round
- Structured JSON output + markdown report renderer
- Native slash command UX in OpenClaw
- Safe local config model (secrets only via env vars)

## Repository layout

- `council.py` — orchestration engine
- `render_report.py` — converts `run.json` to `report.md`
- `roles/` — role prompt packs
- `examples/council.config.example.json` — starter config template
- `schemas/council-output.schema.json` — output contract
- `openclaw.plugin.json` — plugin manifest
- `skills/openclaw-council/SKILL.md` — skill instructions

## Requirements

- Python 3.10+
- OpenClaw CLI installed and configured
- Provider API keys (for live mode)

## Install as OpenClaw plugin

```bash
git clone https://github.com/Personaz1/openclaw-council.git
cd openclaw-council
openclaw plugins install .
openclaw plugins enable openclaw-council
openclaw gateway restart
```

## Use native slash commands

```text
/council <query>
/council status
/council config-check
/council roles list
```

### Example queries

**Planning & Strategy:**
```text
/council Build a 14-day GTM plan for OpenClaw Council
/council Design a multi-provider LLM routing strategy for cost optimization
/council Plan a security audit process for our API infrastructure
```

**Code & Technical:**
```bash
# From CLI - review a pull request
python3 council.py run \
  --query "Review this PR for memory leaks and race conditions: https://github.com/user/repo/pull/123" \
  --config council.config.json \
  --out pr-review.json

# Debug production issue
python3 council.py run \
  --query "Analyze this error trace and suggest root cause: Connection timeout in pod auth-service after v2.3 deployment" \
  --config council.config.json \
  --out debug.json
```

**Decision Making:**
```text
/council Should we switch our vector database from Pinecone to pgvector? Consider cost, performance, and migration effort.
/council Evaluate three API providers: OpenAI, Anthropic, and local Llama3. Prioritize by latency and accuracy for a RAG workload.
```

## Quick start (local run)

```bash
cp examples/council.config.example.json council.config.json
# edit provider/model values if needed

python3 council.py run \
  --query "Build a 14-day go-to-market plan for an OpenClaw plugin" \
  --config council.config.json \
  --out run.json

python3 render_report.py --infile run.json --out report.md
```

## Understanding the output

Council returns structured JSON with transparency into the deliberation:

```json
{
  "query": "Should we switch to PostgreSQL?",
  "round1": [
    { "role": "analyst", "content": "PostgreSQL offers..." },
    { "role": "skeptic", "content": "Migration risks include..." }
  ],
  "critic_round": [
    { "role": "analyst", "content": "Weaknesses in my analysis:..." },
    { "role": "skeptic", "content": "Points I agree on:..."
  ],
  "synthesis": {
    "role": "synthesizer",
    "content": {
      "final_answer": "Yes, with a phased migration approach...",
      "agreement_points": ["Strong ACID compliance", "Active ecosystem"],
      "disagreement_points": ["Migration timeline estimates vary"],
      "risks": ["Data loss during migration", "Team learning curve"],
      "confidence": 0.82
    }
  }
}
```

Use `render_report.py` to convert this into a readable markdown report.

## One-command local install (skill-style copy)

```bash
bash install.sh
```

Installs into `~/.openclaw/skills/openclaw-council`.

## Security and secrets

- Keep API keys in environment variables only.
- Do **not** commit `council.config.json`, `run.json`, or `report.md`.
- Use `.env.example` as a template only.

## Add a new role

1. Create `roles/<role-name>.md`
2. Add it under `roles[]` in `council.config.json`

## Add a new provider

Add provider settings to `providers{}` in config:

- `base_url` (OpenAI-compatible endpoint)
- `api_key_env` (environment variable name)
- `model`

### Example: Adding Ollama (local models)

```json
{
  "providers": {
    "ollama": {
      "base_url": "http://localhost:11434",
      "api_key_env": "OLLAMA_API_KEY",
      "model": "llama3"
    }
  },
  "roles": [
    { "name": "analyst", "provider": "ollama", "prompt_file": "roles/analyst.md" }
  ]
}
```

Then set `OLLAMA_API_KEY=any` before running.

## License

MIT

## Troubleshooting

### API errors
- **429 (Rate Limit)**: Increase `runtime.retry_backoff_sec` in config or reduce parallel workers
- **401 (Auth Failed)**: Check your `api_key_env` variable is set correctly
- **Connection Timeout**: Increase `runtime.timeout_sec` for slow providers

### Common issues
- **Missing roles**: Ensure role `.md` files exist in `roles/` directory
- **Mock responses**: Set `runtime.allow_mock_fallback: true` for testing without API keys
- **SSL errors on macOS**: The script auto-fallbacks to certifi if available (`pip install certifi`)


## Roadmap and funding

See [`ROADMAP.md`](./ROADMAP.md).

> Note: the project is fully usable today, but progress on advanced quality features is slower without API funding.

If you want to sponsor development or fund specific milestones, open an issue/discussion in this repo.


## Work / hiring

I’m actively looking for work and available for funded collaboration.

I code from morning to night and focus on shipping practical AI products.

See [`WORK_AND_SPONSORSHIP.md`](./WORK_AND_SPONSORSHIP.md).
