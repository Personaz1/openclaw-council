# OpenClaw Council (pluggable)

Council-движок с **подключаемыми ролями** и **произвольным числом моделей/API**.

## Что умеет
- Любое число ролей (файлы в `roles/*.md`)
- Любое число провайдеров/моделей (конфиг `council.config.json`)
- Параллельный 1-й раунд (все роли)
- Раунд критики (каждая роль критикует агрегированный черновик)
- Финальный синтез (отдельная роль `synthesizer`)
- Прозрачный JSON-вывод: agree/disagree/risks/confidence

## Быстрый старт
```bash
cd ideas/openclaw-council
cp examples/council.config.example.json council.config.json
python3 council.py run --query "Сделай план запуска продукта за 14 дней" --config council.config.json --out run.json
```

## Подключение новых ролей
1. Добавь файл `roles/<name>.md` (инструкция роли).
2. Добавь роль в `council.config.json`.

## Подключение новых API
Поддержан OpenAI-compatible Chat Completions endpoint:
- OpenAI
- OpenRouter
- локальные шлюзы (vLLM, LM Studio, etc.)

Просто добавь новый provider в конфиг.

## Формат вывода
См. `schemas/council-output.schema.json`


## Security / secrets
- Ключи храним только в env-переменных.
- Файл `council.config.json` локальный и в git не коммитится.
- Перед пушем проверь: `git status` и что нет файлов с ключами.

## Install as OpenClaw skill (local)
```bash
# положить папку в ваш каталог skills и запускать команды из SKILL.md
```


## One-command local install
```bash
bash install.sh
```
Installs into `~/.openclaw/skills/openclaw-council`.


## Install as OpenClaw plugin (recommended)
```bash
# after cloning this repo
openclaw plugins install .
openclaw plugins enable openclaw-council
openclaw gateway restart
```

Then run the council skill from:
`skills/openclaw-council/SKILL.md`

## Install directly from GitHub source
```bash
git clone https://github.com/Personaz1/openclaw-council.git
cd openclaw-council
openclaw plugins install .
```
