import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def frame(payload):
    body = json.dumps(payload).encode("utf-8")
    return b"Content-Length: " + str(len(body)).encode("ascii") + b"\r\n\r\n" + body


def read_framed(stdout):
    header = b""
    while b"\r\n\r\n" not in header:
        chunk = stdout.read(1)
        if not chunk:
            raise AssertionError("process closed before header")
        header += chunk
    head, rest = header.split(b"\r\n\r\n", 1)
    length = None
    for line in head.decode("utf-8").splitlines():
        if line.lower().startswith("content-length:"):
            length = int(line.split(":", 1)[1].strip())
            break
    if length is None:
        raise AssertionError(f"missing content-length: {head!r}")
    body = rest + stdout.read(length - len(rest))
    return json.loads(body.decode("utf-8"))


class McpServerTests(unittest.TestCase):
    def call_once(self, argv, payload, env=None):
        proc = subprocess.Popen(
            argv,
            cwd=ROOT,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )
        try:
            proc.stdin.write(frame(payload))
            proc.stdin.flush()
            return read_framed(proc.stdout)
        finally:
            proc.kill()
            proc.wait(timeout=5)
            proc.stdin.close()
            proc.stdout.close()
            proc.stderr.close()

    def test_docker_mcp_lists_tools(self):
        response = self.call_once(
            ["node", str(ROOT / "scripts" / "mcp" / "docker_mcp_server.js")],
            {"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
        )
        names = {tool["name"] for tool in response["result"]["tools"]}
        self.assertIn("docker_status", names)
        self.assertIn("docker_runner_plan", names)
        self.assertIn("docker_run_bounded", names)

    def test_state_db_mcp_initializes_sqlite(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = os.environ.copy()
            env["TAC_STATE_ROOT"] = tmp
            env["TAC_STATE_DB"] = str(Path(tmp) / "state.sqlite3")
            response = self.call_once(
                [sys.executable, str(ROOT / "scripts" / "mcp" / "state_db_mcp_server.py")],
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {"name": "init_state_db", "arguments": {}},
                },
                env=env,
            )
            payload = json.loads(response["result"]["content"][0]["text"])
            self.assertTrue(payload["ok"])
            self.assertTrue(Path(payload["db_path"]).exists())

    def test_state_db_mcp_records_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = os.environ.copy()
            env["TAC_STATE_ROOT"] = tmp
            env["TAC_STATE_DB"] = str(Path(tmp) / "state.sqlite3")
            proc = subprocess.Popen(
                [sys.executable, str(ROOT / "scripts" / "mcp" / "state_db_mcp_server.py")],
                cwd=ROOT,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
            )
            try:
                proc.stdin.write(
                    frame(
                        {
                            "jsonrpc": "2.0",
                            "id": 1,
                            "method": "tools/call",
                            "params": {
                                "name": "record_task",
                                "arguments": {"task_id": "tac-test", "source": "unit", "status": "PASS"},
                            },
                        }
                    )
                )
                proc.stdin.flush()
                first = read_framed(proc.stdout)
                self.assertTrue(json.loads(first["result"]["content"][0]["text"])["ok"])

                proc.stdin.write(
                    frame(
                        {
                            "jsonrpc": "2.0",
                            "id": 2,
                            "method": "tools/call",
                            "params": {"name": "get_task", "arguments": {"task_id": "tac-test"}},
                        }
                    )
                )
                proc.stdin.flush()
                second = read_framed(proc.stdout)
                task = json.loads(second["result"]["content"][0]["text"])["task"]
                self.assertEqual(task["task_id"], "tac-test")
                self.assertEqual(task["status"], "PASS")
            finally:
                proc.kill()
                proc.wait(timeout=5)
                proc.stdin.close()
                proc.stdout.close()
                proc.stderr.close()


if __name__ == "__main__":
    unittest.main()
