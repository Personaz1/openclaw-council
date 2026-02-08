# Changelog

## 0.3.0 - 2026-02-08

### Added
- New `/council` subcommands:
  - `/council status`
  - `/council config-check`
  - `/council roles list`
- Improved command UX with integrated help text and operational checks.

### Changed
- `/council <query>` now shares one unified command surface with utility operations.
- Bumped plugin/package version to `0.3.0`.

## 0.2.0 - 2026-02-08

### Added
- Native plugin slash command: `/council <query>`
- In-plugin command execution flow (runs `council.py` + `render_report.py`)
- Improved user feedback for command usage and run completion

### Changed
- Bumped plugin/package version to `0.2.0`
- README updated with slash-command usage

## 0.1.0 - 2026-02-08

Initial public release.

### Added
- OpenClaw plugin packaging (`openclaw.plugin.json`, `index.js`, extension metadata)
- Pluggable council engine (`council.py`) with:
  - parallel round-1 role execution
  - critique round
  - synthesis round
- Role packs: analyst, skeptic, builder, startup, security, growth, synthesizer
- Structured output schema (`schemas/council-output.schema.json`)
- Markdown report renderer (`render_report.py`)
- Install helper (`install.sh`)
- Security defaults:
  - `.gitignore` excludes local config and outputs
  - `.env.example` template
  - no secrets in repository

### Notes
- This project is an OpenClaw overlay/plugin, not a fork of OpenClaw core.
