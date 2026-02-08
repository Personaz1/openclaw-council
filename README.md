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

Example:

```text
/council Build a 14-day GTM plan for OpenClaw Council
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

## License

MIT


## Roadmap and funding

See [`ROADMAP.md`](./ROADMAP.md).

> Note: the project is fully usable today, but progress on advanced quality features is slower without API funding.

If you want to sponsor development or fund specific milestones, open an issue/discussion in this repo.


## Work / hiring

I’m actively looking for work and available for funded collaboration.

I code from morning to night and focus on shipping practical AI products.

See [`WORK_AND_SPONSORSHIP.md`](./WORK_AND_SPONSORSHIP.md).
