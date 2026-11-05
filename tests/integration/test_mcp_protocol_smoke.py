"""Live subprocess MCP JSON-RPC protocol smoke test.

Verifies:
1. `revisi-mudah-mcp` starts up cleanly over stdio.
2. Client can send an `initialize` JSON-RPC request and receive a valid handshake.
3. Client can send `notifications/initialized`.
4. Client can send `tools/list` and receives all 6 registered academic tools.
5. Stdout contains purely valid JSON-RPC framing (no unformatted debug prints).
6. Clean process shutdown.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


def _read_json_line(process: subprocess.Popen) -> dict:
    """Read one non-empty line from process stdout and parse as JSON."""
    line = process.stdout.readline()
    if not line:
        err = process.stderr.read()
        raise RuntimeError(f"EOF reached while reading MCP response. Stderr: {err}")
    line_str = line.decode("utf-8").strip()
    return json.loads(line_str)


def test_mcp_server_protocol_handshake_and_tools():
    # Run the MCP server executable via uv
    cmd = ["uv", "run", "revisi-mudah-mcp"]
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(Path(__file__).resolve().parent.parent.parent),
    )

    try:
        # Step 1: Send initialize request
        init_req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "audit-client", "version": "1.0"},
            },
        }
        proc.stdin.write((json.dumps(init_req) + "\n").encode("utf-8"))
        proc.stdin.flush()

        init_resp = _read_json_line(proc)
        assert init_resp.get("jsonrpc") == "2.0"
        assert init_resp.get("id") == 1
        assert "result" in init_resp
        server_info = init_resp["result"].get("serverInfo", {})
        assert server_info.get("name") == "revisi-mudah"

        # Step 2: Send initialized notification
        init_notif = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
        }
        proc.stdin.write((json.dumps(init_notif) + "\n").encode("utf-8"))
        proc.stdin.flush()

        # Step 3: Send tools/list request
        tools_req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {},
        }
        proc.stdin.write((json.dumps(tools_req) + "\n").encode("utf-8"))
        proc.stdin.flush()

        tools_resp = _read_json_line(proc)
        assert tools_resp.get("jsonrpc") == "2.0"
        assert tools_resp.get("id") == 2
        assert "result" in tools_resp

        tools_list = tools_resp["result"].get("tools", [])
        tool_names = {t["name"] for t in tools_list}

        expected_tools = {
            "audio_inspect",
            "audio_transcribe",
            "academic_extract_feedback",
            "academic_adjudicate",
            "academic_build_roadmap",
            "academic_export_ars",
        }
        assert expected_tools.issubset(tool_names), (
            f"Missing tools: {expected_tools - tool_names}"
        )

    finally:
        proc.stdin.close()
        proc.terminate()
        proc.wait(timeout=5)


def test_legacy_mcp_alias_protocol_handshake():
    """Verify legacy mentorspec-mcp alias completes MCP handshake without stdout pollution."""
    cmd = ["uv", "run", "mentorspec-mcp"]
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(Path(__file__).resolve().parent.parent.parent),
    )

    try:
        init_req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "legacy-audit-client", "version": "1.0"},
            },
        }
        proc.stdin.write((json.dumps(init_req) + "\n").encode("utf-8"))
        proc.stdin.flush()

        init_resp = _read_json_line(proc)
        assert init_resp.get("jsonrpc") == "2.0"
        assert init_resp.get("id") == 1
        assert "result" in init_resp
    finally:
        proc.stdin.close()
        proc.terminate()
        proc.wait(timeout=5)
