#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BIN_DIR="$PROJECT_ROOT/bin"
VENV_DIR="$PROJECT_ROOT/venv"

echo "=========================================================="
echo "    Semgrep-Core Fiziksel Motor Bağlantısı"
echo "=========================================================="

# 1. macOS Homebrew üzerinden yerel derlenmiş fiziksel motoru bağla
if command -v brew &>/dev/null; then
    echo "[1/2] Homebrew ile resmi fiziksel semgrep kuruluyor/bağlanıyor..."
    brew install semgrep || brew upgrade semgrep || true
    BREW_SEMGREP="$(which semgrep 2>/dev/null || echo "/opt/homebrew/bin/semgrep")"
    if [ -x "$BREW_SEMGREP" ]; then
        ln -sf "$BREW_SEMGREP" "$BIN_DIR/semgrep"
        BREW_CORE="$(which semgrep-core 2>/dev/null || echo "/opt/homebrew/bin/semgrep-core")"
        [ -x "$BREW_CORE" ] && ln -sf "$BREW_CORE" "$BIN_DIR/semgrep-core"
    fi
fi

# 2. Alternatif: Resmi GitHub Release'den doğrudan semgrep-core çekme
if ! "$BIN_DIR/semgrep" --version &>/dev/null; then
    echo "[2/2] GitHub Releases üzerinden semgrep-core indiriliyor..."
    TMP_ZIP="/tmp/semgrep-dist.zip"
    TMP_DIR="/tmp/semgrep-unpack"
    rm -rf "$TMP_ZIP" "$TMP_DIR" && mkdir -p "$TMP_DIR"
    
    curl -fL -o "$TMP_ZIP" "https://github.com/semgrep/semgrep/releases/download/v1.178.0/semgrep-v1.178.0-osx.zip" || \
    curl -fL -o "$TMP_ZIP" "https://github.com/semgrep/semgrep/releases/latest/download/semgrep-osx.zip"
    
    unzip -q "$TMP_ZIP" -d "$TMP_DIR"
    find "$TMP_DIR" -name "semgrep-core" -exec cp {} "$BIN_DIR/semgrep-core" \;
    find "$TMP_DIR" -name "semgrep" -type f -exec cp {} "$BIN_DIR/semgrep" \;
    chmod +x "$BIN_DIR"/semgrep*
    [ -d "$VENV_DIR/bin" ] && cp -f "$BIN_DIR/semgrep-core" "$VENV_DIR/bin/" || true
fi

echo "=========================================================="
echo -n "  [+] Semgrep Doğrulama: "
"$BIN_DIR/semgrep" --version
echo "=========================================================="
