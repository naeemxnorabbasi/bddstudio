#!/usr/bin/env bash
set -e
python -m pip install pyinstaller
pyinstaller --onefile --name bddstudio bddstudio/cli/main.py
