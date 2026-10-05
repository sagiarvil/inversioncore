#!/usr/bin/env bash
# InversionCore - 100% Fiziksel Motor Derleme ve Kurulum Betiği (macOS & Linux Uyumlu)
# Resmi GitHub Repoları:
#   1. tree-sitter: https://github.com/tree-sitter/tree-sitter (Kararlı Tag: v0.24.4)
#   2. semgrep:     https://github.com/semgrep/semgrep
#   3. sandbox:     https://github.com/docker/cli
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BUILD_DIR="$PROJECT_ROOT/build"
BIN_DIR="$PROJECT_ROOT/bin"
VENV_DIR="$PROJECT_ROOT/venv"

mkdir -p "$BUILD_DIR" "$BIN_DIR"

echo "=========================================================="
echo "    InversionCore - GitHub Fiziksel Motor Kurulumu"
echo "    Hedef: https://github.com/sagiarvil/inversioncore"
echo "=========================================================="

# 0. Python Sanal Ortamı (macOS PEP 668 Uyumlu)
echo "[0/3] Python sanal ortamı (venv) hazırlanıyor..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
pip install --upgrade pip wheel setuptools >/dev/null 2>&1 || true

# 1. Tree-sitter (github.com/tree-sitter/tree-sitter)
echo "[1/3] Tree-sitter GitHub reposundan derleniyor..."
cd "$BUILD_DIR"
if [ ! -d "tree-sitter" ]; then
    git clone https://github.com/tree-sitter/tree-sitter.git
fi

cd "$BUILD_DIR/tree-sitter"
git fetch --tags --force
# rquickjs hatasını önlemek için resmi kararlı release tag'ine geçilir
echo "  -> Kararlı sürüme geçiliyor: v0.24.4..."
git checkout v0.24.4 >/dev/null 2>&1 || git checkout tags/v0.24.4 >/dev/null 2>&1 || true

if command -v cargo &>/dev/null; then
    echo "  -> Rust cargo ile tree-sitter-cli derleniyor..."
    cargo build --release -p tree-sitter-cli --locked || cargo build --release -p tree-sitter-cli
    if [ -f "target/release/tree-sitter" ]; then
        cp target/release/tree-sitter "$BIN_DIR/tree-sitter"
    fi
fi

# C çekirdek kütüphanesi derlemesi
make -j"$(sysctl -n hw.ncpu 2>/dev/null || nproc 2>/dev/null || echo 4)" >/dev/null 2>&1 || true
if [ -f "libtree-sitter.a" ]; then
    cp libtree-sitter.a "$BIN_DIR/" || true
fi

# 2. Semgrep (github.com/semgrep/semgrep)
echo "[2/3] Semgrep GitHub reposundan kuruluyor..."
cd "$BUILD_DIR"
if [ ! -d "semgrep" ]; then
    git clone --depth 1 https://github.com/semgrep/semgrep.git
else
    cd semgrep && git pull && cd ..
fi

cd "$BUILD_DIR/semgrep"
echo "  -> Semgrep CLI yerel ortama kuruluyor..."
pip install -e cli || pip install git+https://github.com/semgrep/semgrep.git#subdirectory=cli

SEMGREP_BIN="$VENV_DIR/bin/semgrep"
if [ -f "$SEMGREP_BIN" ]; then
    ln -sf "$SEMGREP_BIN" "$BIN_DIR/semgrep"
elif command -v semgrep &>/dev/null; then
    ln -sf "$(which semgrep)" "$BIN_DIR/semgrep"
fi

# 3. Docker CLI Sandbox (github.com/docker/cli)
echo "[3/3] Sandbox motoru (Docker) bağlanıyor..."
cd "$BUILD_DIR"
if [ ! -d "docker-cli" ]; then
    git clone --depth 1 https://github.com/docker/cli.git docker-cli
fi

DOCKER_BIN="$(which docker 2>/dev/null || echo "/usr/local/bin/docker")"
if [ -x "$DOCKER_BIN" ]; then
    ln -sf "$DOCKER_BIN" "$BIN_DIR/docker"
elif [ -x "/Applications/Docker.app/Contents/Resources/bin/docker" ]; then
    ln -sf "/Applications/Docker.app/Contents/Resources/bin/docker" "$BIN_DIR/docker"
fi

echo "=========================================================="
echo "    Kurulum Tamamlandı!"
echo "    Fiziksel İkili (Binary) Sürümleri:"
echo "=========================================================="
[ -x "$BIN_DIR/tree-sitter" ] && echo -n "  [+] Tree-sitter : " && "$BIN_DIR/tree-sitter" --version
[ -x "$BIN_DIR/semgrep" ]     && echo -n "  [+] Semgrep     : " && "$BIN_DIR/semgrep" --version
[ -x "$BIN_DIR/docker" ]      && echo -n "  [+] Docker      : " && "$BIN_DIR/docker" --version
echo "=========================================================="
