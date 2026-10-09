#!/usr/bin/env bash
# Full test suite: exact solid self-checks, geometry kernel (distances, penetration, gradients), tightening Jacobian,
# and the checkers on known-good and deliberately broken claim files. Exits nonzero on any failure.
set -euo pipefail
cd "$(dirname "$0")/.."
echo "== exact solids (solids.py)"; python3 solids.py
echo "== geometry kernel (src/geom.js)"; node test/test_geom.js
echo "== tightening Jacobian + checkers"; python3 test/test_checkers.py
echo "ALL TESTS PASSED"
