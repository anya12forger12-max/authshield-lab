#!/usr/bin/env bash
# check-defect-types.sh — ratchet gate for the *defect-shaped* slice of mypy.
#
# Why this exists
# ---------------
# `mypy --strict` is deliberately a SOFT CI step in every authshield repo: the
# codebase carries a few thousand annotation errors (`type-arg`, `no-untyped-def`,
# `no-any-return`, ...) that nobody intends to pay off, so hard-failing on raw
# mypy output would be red forever and would get ignored.
#
# That is the right call for annotation debt, but it left a real gap: the
# defect-shaped codes (`attr-defined`, `union-attr`, `operator`, `index`,
# `call-arg`, `arg-type`, `override`, `return-value`, `comparison-overlap`,
# `assignment`, `list-item`) are exactly the class that has produced every live
# crash found by static triage — repository methods missing from their ABCs,
# None-dereferences, wrong kwarg names, a handler-isolation path that raised from
# inside its own except block. Those are cheap to fix *at the moment they are
# written* and expensive to find later, and nothing in CI stopped them returning.
#
# So this gates only those codes, as a RATCHET: the current counts are recorded in
# backend/mypy-defect-baseline.txt and the job fails if any of them *increases*.
# Annotation debt is untouched and can only ever go down, never up.
#
# Usage: check-defect-types.sh [mypy-target] [baseline-file]
set -uo pipefail

TARGET="${1:-backend/}"
BASELINE="${2:-backend/mypy-defect-baseline.txt}"

# Defect-shaped codes: each of these has, at least once, been a real runtime bug
# in this codebase rather than an annotation preference.
# `name-defined` is here because of the collaboration/ecosystem class of bugs:
  # interface ABCs imported only under `if TYPE_CHECKING:` but used as *runtime*
  # base classes, so the module raised NameError on import. It is currently 0.
  # `misc` was the last unwatched code and it was not benign: the single
  # finding pointed at `TemplateStudioService.get_templates_by_type`, whose
  # annotation ("list[dict]") disagreed with a comprehension over a *paginated*
  # repository envelope. Following that disagreement found real silent data
  # loss -- the method filtered a single default page (20 of N) and returned []
  # for any template_type stored past it. A "misc" code is therefore not
  # automatically noise; it is currently 0 and worth keeping at 0.
  DEFECT_CODES='attr-defined|arg-type|assignment|call-arg|comparison-overlap|index|list-item|misc|name-defined|operator|override|return-value|union-attr'

if ! command -v mypy >/dev/null 2>&1; then
    echo "check-defect-types: mypy not on PATH" >&2
    exit 1
fi

out="$(mktemp)"
trap 'rm -f "$out"' EXIT

# Mirror CI's invocation. --no-error-summary keeps the output to bare
# "file:line: error: ... [code]" lines so the counts below are stable.
mypy --strict --no-error-summary "$TARGET" >"$out" 2>/dev/null || true

if [ ! -s "$out" ]; then
    echo "check-defect-types: mypy produced no output for '$TARGET' (unexpected)" >&2
    exit 1
fi

# Count the defect-shaped codes actually present in this run.
actual="$(grep -oE "\[($DEFECT_CODES)\]$" "$out" | tr -d '[]' | sort | uniq -c | awk '{print $2" "$1}')"

# Previous baseline, if any.
expected=""
if [ -f "$BASELINE" ]; then
    expected="$(grep -vE '^\s*(#|$)' "$BASELINE" | sort)"
fi

total_actual="$(printf '%s\n' "$actual" | awk '{s+=$2} END {print s+0}')"

echo "check-defect-types: defect-shaped findings in $TARGET = $total_actual"
printf '%s\n' "$actual" | sed 's/^/  /'

if [ -z "$expected" ]; then
    echo "check-defect-types: no baseline at $BASELINE — recording this run as the baseline."
    printf '%s\n' "$actual" > "$BASELINE"
    exit 0
fi

total_expected="$(printf '%s\n' "$expected" | awk '{s+=$2} END {print s+0}')"

# Compare per code: fail if any code's count went UP.
regressions=""
while read -r code count; do
    [ -z "$code" ] && continue
    before="$(printf '%s\n' "$expected" | awk -v c="$code" '$1==c {print $2}')"
    before="${before:-0}"
    if [ "$count" -gt "$before" ]; then
        regressions="${regressions}  ${code}: ${before} -> ${count}\n"
    fi
done <<EOF
$actual
EOF

if [ -n "$regressions" ]; then
    echo
    echo "check-defect-types: FAIL — defect-shaped type errors increased:" >&2
    printf "$regressions" >&2
    echo >&2
    echo "These codes mark code paths that have been real runtime crashes here." >&2
    echo "Fix the new findings (see $TARGET) rather than raising the baseline." >&2
    exit 1
fi

if [ "$total_actual" -lt "$total_expected" ]; then
    # A decrease is an improvement, not a reason to rewrite the file: the count
    # is not identical across environments (mypy under Python 3.12 reports a
    # few fewer `arg-type`/`attr-defined` findings than 3.11 does), so the
    # committed baseline is kept at the highest count any environment produces
    # and every environment compares against that. Rewriting it here would make
    # the checked-in value depend on which interpreter ran, and CI cannot commit
    # the change anyway.
    echo "check-defect-types: PASS ($total_actual < baseline $total_expected) — baseline left at the recorded maximum."
    exit 0
fi

echo "check-defect-types: PASS ($total_actual == baseline $total_expected, no regression)"