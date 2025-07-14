#!/bin/bash
# chmod +x package-dev.sh   <-- Make sure this script is executable

zip -r JVH-YT-DLP-Tool.zip . \
  -x "venv/*" \
  -x ".venv/*" \
  -x ".git/*" \
  -x "*.pyc" \
  -x "__pycache__/*" \
  $(grep -v '^#' .gitignore | sed '/^\s*$/d' | sed 's|^| -x "|;s|$|"|')

echo "✔️  Zipped project to JVH-YT-DLP-Tool.zip (excluding .venv/ venv/ and .gitignore rules)"
