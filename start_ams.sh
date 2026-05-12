#!/usr/bin/env bash
set -euo pipefail

echo ""
echo "============================================================"
echo "  AMS JobAssist -- Startvorgang"
echo "============================================================"
echo ""

if ! command -v python3 &>/dev/null; then
    echo "Python 3 nicht gefunden. Bitte unter https://python.org herunterladen."
    exit 1
fi

cd "$(dirname "$0")"

python3 launcher.py
