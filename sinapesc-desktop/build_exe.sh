#!/usr/bin/env bash
# Gera o executável no Linux (teste). No notebook Windows use build_exe.bat.
set -euo pipefail
cd "$(dirname "$0")"
python3 -m pip install -r requirements.txt
python3 -m PyInstaller --noconfirm build_exe.spec
echo "Gerado em: dist/SinapescREAP"
