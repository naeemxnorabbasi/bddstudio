#!/usr/bin/env bash
set -euo pipefail

if ! command -v dot >/dev/null 2>&1; then
  echo "Graphviz 'dot' was not found."
  if command -v brew >/dev/null 2>&1; then
    echo "Installing Graphviz with Homebrew..."
    brew install graphviz
  else
    echo "Install Homebrew or install Graphviz manually, then rerun this script."
    exit 1
  fi
fi

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .

echo
echo "Setup complete."
echo "Run:"
echo "  source .venv/bin/activate"
echo "  bddstudio serve"
