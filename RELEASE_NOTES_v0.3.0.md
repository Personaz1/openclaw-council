# OpenClaw Council v0.3.0

This release upgrades Council UX into a practical operator command set.

## What's new

- Added `/council status` for runtime diagnostics
- Added `/council config-check` for fast config validation
- Added `/council roles list` to inspect installed role packs
- Kept `/council <query>` as the primary execution command

## Usage

```text
/council status
/council config-check
/council roles list
/council Build a 14-day GTM plan for OpenClaw Council
```

## Upgrade

```bash
cd openclaw-council
git pull
openclaw plugins install .
openclaw plugins enable openclaw-council
openclaw gateway restart
```

## Notes

- Plugin overlay architecture is unchanged (no OpenClaw core patching).
- Secrets remain environment-only.
