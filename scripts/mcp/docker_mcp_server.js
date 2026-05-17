#!/usr/bin/env node
"use strict";

const { execFileSync } = require("node:child_process");
const path = require("node:path");

let inputBuffer = Buffer.alloc(0);

function writeMessage(message) {
  const body = Buffer.from(JSON.stringify(message), "utf8");
  process.stdout.write(`Content-Length: ${body.length}\r\n\r\n`);
  process.stdout.write(body);
}

function ok(id, result) {
  writeMessage({ jsonrpc: "2.0", id, result });
}

function fail(id, code, message, data) {
  writeMessage({ jsonrpc: "2.0", id, error: { code, message, data } });
}

function runDocker(args) {
  try {
    const stdout = execFileSync("docker", args, {
      encoding: "utf8",
      timeout: 15000,
      windowsHide: true,
      stdio: ["ignore", "pipe", "pipe"],
    });
    return { ok: true, stdout: stdout.trim(), stderr: "" };
  } catch (error) {
    return {
      ok: false,
      stdout: String(error.stdout || "").trim(),
      stderr: String(error.stderr || error.message || "").trim(),
      exitCode: error.status ?? null,
    };
  }
}

function allowedWorkspace(workspace) {
  const raw = String(workspace || "").trim();
  if (!raw) return false;
  const resolved = path.resolve(raw);
  const roots = String(process.env.TAC_DOCKER_ALLOWED_ROOTS || process.cwd())
    .split(path.delimiter)
    .map((root) => path.resolve(root.trim()))
    .filter(Boolean);
  return roots.some((root) => resolved === root || resolved.startsWith(root + path.sep));
}

function dockerRunPlan(args) {
  const workspace = String(args.workspace || "").trim();
  if (!allowedWorkspace(workspace)) {
    throw new Error("workspace is outside TAC_DOCKER_ALLOWED_ROOTS");
  }
  const image = String(args.image || "python:3.12-slim").trim();
  const command = Array.isArray(args.command) && args.command.length
    ? args.command.map(String)
    : ["python", "-m", "pytest", "-q"];
  const cpus = String(args.cpus || "1.0");
  const memory = String(args.memory || "1g");
  const network = args.network === "bridge" ? "bridge" : "none";
  const mountMode = args.readonly === true ? "ro" : "rw";
  return [
    "docker",
    "run",
    "--rm",
    "--network",
    network,
    "--cpus",
    cpus,
    "--memory",
    memory,
    "-v",
    `${path.resolve(workspace)}:/workspace:${mountMode}`,
    "-w",
    "/workspace",
    image,
    ...command,
  ];
}

const tools = [
  {
    name: "docker_status",
    description: "Check Docker client/daemon status without mutating containers.",
    inputSchema: { type: "object", properties: {}, additionalProperties: false },
  },
  {
    name: "docker_ps",
    description: "List Docker containers without changing runtime state.",
    inputSchema: {
      type: "object",
      properties: { all: { type: "boolean", default: false } },
      additionalProperties: false,
    },
  },
  {
    name: "docker_runner_plan",
    description: "Build a bounded docker run command for review; does not execute it.",
    inputSchema: {
      type: "object",
      properties: {
        workspace: { type: "string" },
        image: { type: "string", default: "python:3.12-slim" },
        command: { type: "array", items: { type: "string" } },
        cpus: { type: "string", default: "1.0" },
        memory: { type: "string", default: "1g" },
        network: { type: "string", enum: ["none", "bridge"], default: "none" },
        readonly: { type: "boolean", default: false },
      },
      required: ["workspace"],
      additionalProperties: false,
    },
  },
  {
    name: "docker_run_bounded",
    description: "Run a bounded container only when TAC_DOCKER_MCP_ALLOW_MUTATION=1.",
    inputSchema: {
      type: "object",
      properties: {
        workspace: { type: "string" },
        image: { type: "string", default: "python:3.12-slim" },
        command: { type: "array", items: { type: "string" } },
        cpus: { type: "string", default: "1.0" },
        memory: { type: "string", default: "1g" },
        network: { type: "string", enum: ["none", "bridge"], default: "none" },
        readonly: { type: "boolean", default: false },
      },
      required: ["workspace"],
      additionalProperties: false,
    },
  },
];

function textResult(value) {
  return { content: [{ type: "text", text: JSON.stringify(value, null, 2) }] };
}

function callTool(name, args) {
  if (name === "docker_status") {
    return textResult({
      client: runDocker(["version", "--format", "{{json .Client}}"]),
      server: runDocker(["version", "--format", "{{json .Server}}"]),
    });
  }
  if (name === "docker_ps") {
    const dockerArgs = ["ps", "--format", "{{json .}}"];
    if (args.all) dockerArgs.splice(1, 0, "--all");
    return textResult(runDocker(dockerArgs));
  }
  if (name === "docker_runner_plan") {
    return textResult({ command: dockerRunPlan(args) });
  }
  if (name === "docker_run_bounded") {
    if (process.env.TAC_DOCKER_MCP_ALLOW_MUTATION !== "1") {
      return textResult({
        ok: false,
        blocked: true,
        reason: "Docker mutation disabled. Set TAC_DOCKER_MCP_ALLOW_MUTATION=1 for an explicitly approved bounded run.",
        planned_command: dockerRunPlan(args),
      });
    }
    const command = dockerRunPlan(args);
    return textResult(runDocker(command.slice(1)));
  }
  throw new Error(`unknown tool: ${name}`);
}

function handle(message) {
  if (!message || message.jsonrpc !== "2.0") return;
  const { id, method, params = {} } = message;
  try {
    if (method === "initialize") {
      ok(id, {
        protocolVersion: params.protocolVersion || "2024-11-05",
        capabilities: { tools: {} },
        serverInfo: { name: "tac-docker-mcp", version: "0.1.0" },
      });
    } else if (method === "tools/list") {
      ok(id, { tools });
    } else if (method === "tools/call") {
      ok(id, callTool(params.name, params.arguments || {}));
    } else if (method === "ping") {
      ok(id, {});
    } else if (id !== undefined) {
      fail(id, -32601, `method not found: ${method}`);
    }
  } catch (error) {
    fail(id, -32000, String(error.message || error));
  }
}

function pump() {
  while (true) {
    let headerEnd = inputBuffer.indexOf("\r\n\r\n");
    let separatorLength = 4;
    if (headerEnd < 0) {
      headerEnd = inputBuffer.indexOf("\n\n");
      separatorLength = 2;
    }
    if (headerEnd < 0) return;
    const header = inputBuffer.slice(0, headerEnd).toString("utf8");
    const match = /^Content-Length:\s*(\d+)/im.exec(header);
    if (!match) {
      inputBuffer = inputBuffer.slice(headerEnd + separatorLength);
      continue;
    }
    const length = Number(match[1]);
    const bodyStart = headerEnd + separatorLength;
    const bodyEnd = bodyStart + length;
    if (inputBuffer.length < bodyEnd) return;
    const body = inputBuffer.slice(bodyStart, bodyEnd).toString("utf8");
    inputBuffer = inputBuffer.slice(bodyEnd);
    handle(JSON.parse(body));
  }
}

process.stdin.on("data", (chunk) => {
  inputBuffer = Buffer.concat([inputBuffer, chunk]);
  pump();
});
