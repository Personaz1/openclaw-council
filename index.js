import { spawn } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { existsSync, readdirSync, readFileSync } from "node:fs";

const __dirname = dirname(fileURLToPath(import.meta.url));

function runProcess(command, args, cwd) {
  return new Promise((resolve) => {
    const child = spawn(command, args, { cwd, env: process.env });
    let stdout = "";
    let stderr = "";

    child.stdout.on("data", (d) => (stdout += d.toString()));
    child.stderr.on("data", (d) => (stderr += d.toString()));
    child.on("close", (code) => resolve({ code, stdout, stderr }));
    child.on("error", (err) => resolve({ code: 1, stdout, stderr: String(err) }));
  });
}

function getPaths() {
  const cwd = __dirname;
  return {
    cwd,
    config: join(cwd, "council.config.json"),
    runJson: join(cwd, "run.json"),
    reportMd: join(cwd, "report.md"),
    rolesDir: join(cwd, "roles"),
  };
}

async function runCouncil(query) {
  const p = getPaths();

  const runRes = await runProcess(
    "python3",
    ["council.py", "run", "--query", query, "--config", p.config, "--out", p.runJson],
    p.cwd,
  );

  if (runRes.code !== 0) {
    return {
      ok: false,
      text:
        "Council failed. Check your local config and API env vars.\n" +
        (runRes.stderr || runRes.stdout || "Unknown error"),
    };
  }

  const reportRes = await runProcess(
    "python3",
    ["render_report.py", "--infile", p.runJson, "--out", p.reportMd],
    p.cwd,
  );

  if (reportRes.code !== 0) {
    return {
      ok: false,
      text:
        "Council run completed but report rendering failed.\n" +
        (reportRes.stderr || reportRes.stdout || "Unknown error"),
    };
  }

  return {
    ok: true,
    text: [
      "✅ Council completed.",
      `Artifacts: ${p.runJson}, ${p.reportMd}`,
      "Tip: open report.md for the final synthesis.",
    ].join("\n"),
  };
}

async function statusText() {
  const p = getPaths();
  const py = await runProcess("python3", ["--version"], p.cwd);
  const hasCfg = existsSync(p.config);
  const hasRun = existsSync(p.runJson);
  const hasReport = existsSync(p.reportMd);

  return [
    "OpenClaw Council status",
    `- plugin: openclaw-council`,
    `- python: ${py.code === 0 ? (py.stdout || py.stderr).trim() : "not available"}`,
    `- config: ${hasCfg ? "present" : "missing (create from examples/council.config.example.json)"}`,
    `- last run.json: ${hasRun ? "present" : "missing"}`,
    `- last report.md: ${hasReport ? "present" : "missing"}`,
  ].join("\n");
}

function configCheckText() {
  const p = getPaths();
  if (!existsSync(p.config)) {
    return [
      "Config check: FAIL",
      "- council.config.json is missing",
      "- create it from: examples/council.config.example.json",
    ].join("\n");
  }

  try {
    const cfg = JSON.parse(readFileSync(p.config, "utf8"));
    const providersOk = !!cfg.providers && typeof cfg.providers === "object";
    const rolesOk = Array.isArray(cfg.roles) && cfg.roles.length > 0;
    const synthOk = !!cfg.synthesizer && typeof cfg.synthesizer === "object";

    const issues = [];
    if (!providersOk) issues.push("providers{} is missing or invalid");
    if (!rolesOk) issues.push("roles[] is missing or empty");
    if (!synthOk) issues.push("synthesizer is missing");

    if (issues.length) {
      return ["Config check: FAIL", ...issues.map((x) => `- ${x}`)].join("\n");
    }

    return [
      "Config check: OK",
      `- providers: ${Object.keys(cfg.providers).length}`,
      `- roles: ${cfg.roles.length}`,
      `- synthesizer: ${cfg.synthesizer.name || "set"}`,
    ].join("\n");
  } catch (e) {
    return ["Config check: FAIL", `- invalid JSON: ${String(e)}`].join("\n");
  }
}

function rolesListText() {
  const p = getPaths();
  if (!existsSync(p.rolesDir)) {
    return "Roles list: roles/ directory is missing.";
  }
  const files = readdirSync(p.rolesDir)
    .filter((f) => f.endsWith(".md"))
    .sort();
  if (!files.length) return "Roles list: no role files found.";
  return ["Roles", ...files.map((f) => `- ${f.replace(/\.md$/, "")}`)].join("\n");
}

function helpText() {
  return [
    "Usage:",
    "/council <query>",
    "/council status",
    "/council config-check",
    "/council roles list",
  ].join("\n");
}

export default function register(api) {
  api.logger?.info?.("[openclaw-council] plugin loaded");

  api.registerCommand({
    name: "council",
    description: "Run OpenClaw Council and utility subcommands",
    acceptsArgs: true,
    requireAuth: true,
    handler: async (ctx) => {
      const args = (ctx.args || "").trim();
      if (!args) return { text: helpText() };

      const lower = args.toLowerCase();
      if (lower === "status") return { text: await statusText() };
      if (lower === "config-check") return { text: configCheckText() };
      if (lower === "roles list") return { text: rolesListText() };

      const result = await runCouncil(args);
      return { text: result.text };
    },
  });
}
