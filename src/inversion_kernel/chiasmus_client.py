# -*- coding: utf-8 -*-
"""
InversionCore Chiasmus Neurosymbolic Formal Verification Client
MCP JSON-RPC Integration for Formal Reasoning with Z3 (WASM / In-Process)
"""

import subprocess
import json
import os
from typing import Dict, Any, Optional


class ChiasmusClient:
    """Chiasmus MCP Formal Doğrulama İstemcisi."""

    CHIASMUS_BIN = "/Users/macair1/.nvm/versions/node/v22.23.2/bin/chiasmus"

    def __init__(self, binary_path: Optional[str] = None):
        self.binary_path = binary_path or self.CHIASMUS_BIN

    def is_available(self) -> bool:
        """Chiasmus ikilisinin sistemde var olup olmadığını doğrular."""
        return os.path.exists(self.binary_path) and os.access(self.binary_path, os.X_OK)

    def verify_smt(self, smt_input: str, solver: str = "z3") -> Dict[str, Any]:
        """
        Chiasmus MCP üzerinden SMT-LIB2 spesifikasyonunu WASM Z3 motoruyla doğrular.
        """
        if not self.is_available():
            return {"status": "unavailable", "error": "Chiasmus binary not found"}

        env = os.environ.copy()
        # Chiasmus harici embeddings API hatası vermemesi için bağımsız çalıştırılır
        env.pop("DEEPSEEK_API_KEY", None)

        try:
            proc = subprocess.Popen(
                [self.binary_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )

            # 1. MCP Initialize
            init_req = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "inversioncore", "version": "3.3"}
                }
            }
            proc.stdin.write(json.dumps(init_req) + "\n")
            proc.stdin.flush()
            _ = proc.stdout.readline()

            # 2. Tools Call: chiasmus_verify
            verify_req = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "chiasmus_verify",
                    "arguments": {
                        "input": smt_input,
                        "solver": solver
                    }
                }
            }
            proc.stdin.write(json.dumps(verify_req) + "\n")
            proc.stdin.flush()

            raw_res = proc.stdout.readline()
            proc.terminate()

            data = json.loads(raw_res)
            if "result" in data and "content" in data["result"]:
                text_content = data["result"]["content"][0].get("text", "{}")
                inner = json.loads(text_content)
                return {
                    "status": inner.get("status", "unknown").upper(),
                    "details": inner,
                    "engine": "CHIASMUS_MCP_Z3"
                }
            elif "error" in data:
                return {"status": "ERROR", "error": data["error"]}
            return {"status": "UNKNOWN", "raw": raw_res}

        except Exception as e:
            return {"status": "EXCEPTION", "error": str(e)}
