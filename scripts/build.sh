#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)" \
  || { echo "Python 3.12+ is required." >&2; exit 1; }

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

pip install -q -r requirements.txt

mkdir -p .generated output

python scripts/json_to_rendercv.py \
  --input resume.json \
  --design build/design.yaml \
  --output .generated/cv.yaml

rendercv render .generated/cv.yaml

GENERATED_PDF="$(find .generated/rendercv_output -maxdepth 1 -name '*.pdf' | head -n 1)"
if [ -z "$GENERATED_PDF" ]; then
  echo "RenderCV did not produce a PDF." >&2
  exit 1
fi

cp "$GENERATED_PDF" output/resume.pdf
echo "✓ output/resume.pdf"
