# openclaw-council (local skill draft)

## Purpose
Запуск multi-role council с произвольным количеством ролей/провайдеров и синтез финального решения.

## Run
```bash
cd /Users/stefan/.openclaw/workspace/ideas/openclaw-council
cp examples/council.config.example.json council.config.json
python3 council.py run --query "<your query>" --config council.config.json --out run.json
python3 render_report.py --infile run.json --out report.md
```

## Add role
1. Создай `roles/<name>.md`
2. Добавь объект в `roles[]` конфига.

## Add provider
Добавь в `providers{}` OpenAI-compatible endpoint + `api_key_env`.

## Output
- `run.json` — сырой протокол раундов
- `report.md` — человекочитаемый итог
