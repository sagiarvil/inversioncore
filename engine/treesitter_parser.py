#!/usr/bin/env python3
import sys
import ast
from pathlib import Path
from typing import Dict, Any, List

class TreeSitterASTAnalyzer:
    def extract_enclosing_scope(self, file_path: str, target_line: int) -> Dict[str, Any]:
        p = Path(file_path).resolve()
        code = p.read_text(encoding="utf-8", errors="replace")
        lines = code.splitlines()
        try:
            tree = ast.parse(code, filename=str(p))
        except Exception:
            return self._fallback_scope(lines, target_line)

        best_func = None
        best_class = None

        class ScopeFinder(ast.NodeVisitor):
            def __init__(self, target_l):
                self.target_l = target_l
                self.current_class = None
                self.best_func = None
                self.best_class = None

            def visit_ClassDef(self, node):
                if node.lineno <= self.target_l <= getattr(node, "end_lineno", node.lineno):
                    prev = self.current_class
                    self.current_class = node.name
                    self.best_class = node.name
                    self.generic_visit(node)
                    self.current_class = prev
                else:
                    self.generic_visit(node)

            def visit_FunctionDef(self, node):
                if node.lineno <= self.target_l <= getattr(node, "end_lineno", node.lineno):
                    self.best_func = node
                    self.generic_visit(node)

            visit_AsyncFunctionDef = visit_FunctionDef

        finder = ScopeFinder(target_line)
        finder.visit(tree)

        if finder.best_func:
            fn = finder.best_func
            start_l = fn.lineno
            end_l = getattr(fn, "end_lineno", start_l)
            params = [a.arg for a in fn.args.args]
            local_vars = {n.id for n in ast.walk(fn) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)}
            scope_code = "\n".join(lines[start_l - 1:end_l])

            return {
                "status": "success",
                "enclosing_symbol": fn.name,
                "symbol_type": "function_definition",
                "enclosing_class": finder.best_class,
                "scope_range": {"start_line": start_l, "end_line": end_l, "line_count": end_l - start_l + 1},
                "parameters": params,
                "local_variables": sorted(list(local_vars)),
                "enclosing_code": scope_code
            }
        return self._fallback_scope(lines, target_line)

    def _fallback_scope(self, lines: List[str], target_line: int) -> Dict[str, Any]:
        start = max(1, target_line - 10)
        end = min(len(lines), target_line + 10)
        return {
            "status": "partial",
            "enclosing_symbol": "block",
            "scope_range": {"start_line": start, "end_line": end, "line_count": end - start + 1},
            "enclosing_code": "\n".join(lines[start - 1:end])
        }
