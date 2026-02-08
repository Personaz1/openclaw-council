#!/usr/bin/env python3
import argparse
import concurrent.futures as cf
import json
import os
import pathlib
import urllib.request
import urllib.error
import ssl
import time


def load_text(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def _ssl_context():
    # Prefer certifi CA bundle when available (fixes macOS local cert issues)
    try:
        import certifi  # type: ignore
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def chat_completion(base_url, api_key, model, messages, temperature=0.2, max_tokens=1200, timeout=90):
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    req = urllib.request.Request(url, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {api_key}")
    data = json.dumps(payload).encode("utf-8")
    with urllib.request.urlopen(req, data=data, timeout=timeout, context=_ssl_context()) as r:
        body = json.loads(r.read().decode("utf-8"))
    return body["choices"][0]["message"]["content"]


def mock_response(role_name, query):
    if role_name == "synthesizer":
        return json.dumps({
            "final_answer": "Запустить OpenClaw Council как OSS-проект через MVP + демо-кейсы + публичный roadmap.",
            "agreement_points": [
                "Нужен короткий time-to-wow",
                "Нужна прозрачность disagreement/risks",
                "Нужен plugin-формат ролей"
            ],
            "disagreement_points": [
                "Сколько ролей включать по умолчанию",
                "Делать ли critic round обязательным"
            ],
            "risks": [
                "429/квоты провайдеров",
                "шумные роли без строгих промптов"
            ],
            "open_questions": [
                "Дефолтный набор ролей для v1",
                "Целевые метрики качества ответа"
            ],
            "next_actions": [
                "Собрать 10 эталонных тест-запросов",
                "Добавить адаптивный выбор числа ролей",
                "Подготовить публичный README с примерами"
            ],
            "confidence": 0.68
        }, ensure_ascii=False)
    return (
        f"[MOCK:{role_name}]\n"
        f"Запрос: {query[:180]}\n"
        "- Гипотеза: нужен быстрый MVP с прозрачным output.\n"
        "- Риск: слабые данные/источники, переоценка confidence.\n"
        "- Следующий шаг: собрать 3-5 тест-кейсов и сравнить качество."
    )


def run_role(role_cfg, providers, query, runtime, base_dir):
    p = providers[role_cfg["provider"]]
    key = os.getenv(p["api_key_env"], "")
    if not key:
        return {
            "role": role_cfg["name"],
            "provider": role_cfg["provider"],
            "content": f"[ERROR] Missing env var {p['api_key_env']}"
        }
    system_prompt = load_text(base_dir / role_cfg["prompt_file"])

    retries = int(runtime.get("retries", 2))
    backoff = float(runtime.get("retry_backoff_sec", 1.5))
    last_err = None
    for attempt in range(retries + 1):
        try:
            content = chat_completion(
                p["base_url"], key, p["model"],
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=runtime.get("temperature", 0.2),
                max_tokens=runtime.get("max_tokens", 1200),
                timeout=runtime.get("timeout_sec", 90)
            )
            return {"role": role_cfg["name"], "provider": role_cfg["provider"], "content": content}
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8")[:500]
            except Exception:
                pass
            last_err = f"HTTP {e.code}: {body or e.reason}"
            if e.code == 429 and attempt < retries:
                time.sleep(backoff * (attempt + 1))
                continue
            break
        except Exception as e:
            last_err = f"{type(e).__name__}: {e}"
            break

    if runtime.get("allow_mock_fallback", False):
        return {"role": role_cfg["name"], "provider": role_cfg["provider"], "content": mock_response(role_cfg['name'], query)}

    return {"role": role_cfg["name"], "provider": role_cfg["provider"], "content": f"[ERROR] {last_err}"}


def run(config_path, query, out_path):
    base_dir = pathlib.Path(config_path).resolve().parent
    cfg = json.loads(pathlib.Path(config_path).read_text(encoding="utf-8"))
    providers = cfg["providers"]
    roles = cfg["roles"]
    synthesizer = cfg["synthesizer"]
    runtime = cfg.get("runtime", {})

    # Round 1: parallel roles
    with cf.ThreadPoolExecutor(max_workers=runtime.get("parallel_workers", 8)) as ex:
        futs = [ex.submit(run_role, r, providers, query, runtime, base_dir) for r in roles]
        round1 = []
        for role_cfg, fut in zip(roles, futs):
            try:
                round1.append(fut.result())
            except Exception as e:
                round1.append({
                    "role": role_cfg["name"],
                    "provider": role_cfg["provider"],
                    "content": f"[ERROR] {type(e).__name__}: {e}"
                })

    # Critic round: each role critiques all round1 outputs
    round1_blob = "\n\n".join([f"[{r['role']}]\n{r['content']}" for r in round1])
    critic_query = f"Original query:\n{query}\n\nRound1 outputs:\n{round1_blob}\n\nCritique weaknesses and contradictions."
    with cf.ThreadPoolExecutor(max_workers=runtime.get("parallel_workers", 8)) as ex:
        futs = [ex.submit(run_role, r, providers, critic_query, runtime, base_dir) for r in roles]
        critic_round = []
        for role_cfg, fut in zip(roles, futs):
            try:
                critic_round.append(fut.result())
            except Exception as e:
                critic_round.append({
                    "role": role_cfg["name"],
                    "provider": role_cfg["provider"],
                    "content": f"[ERROR] {type(e).__name__}: {e}"
                })

    # Synthesis
    synth_input = {
        "query": query,
        "round1": round1,
        "critic_round": critic_round,
    }
    synth_query = json.dumps(synth_input, ensure_ascii=False, indent=2)
    try:
        synthesis = run_role(synthesizer, providers, synth_query, runtime, base_dir)
    except Exception as e:
        synthesis = {
            "role": synthesizer["name"],
            "provider": synthesizer["provider"],
            "content": f"[ERROR] {type(e).__name__}: {e}"
        }

    out = {
        "query": query,
        "round1": round1,
        "critic_round": critic_round,
        "synthesis": synthesis,
    }
    pathlib.Path(out_path).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved: {out_path}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--query", required=True)
    r.add_argument("--config", required=True)
    r.add_argument("--out", default="council-run.json")
    args = ap.parse_args()

    if args.cmd == "run":
        run(args.config, args.query, args.out)


if __name__ == "__main__":
    main()
