#!/usr/bin/env bash
set -euo pipefail

# Resolve the project even when invoked from another directory.
cd "$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"

quarto render --to html --no-clean
