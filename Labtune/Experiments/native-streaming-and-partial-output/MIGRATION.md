# Deferred migration into Labtune

## Exact compatibility target

Baseline repository: https://github.com/JeranRolevs/labtune

Baseline revision: `d0f462a28bcc4267f8767316d8c73c3c72201063` (Labtune rename; package version 0.5.0).

This is a proposed source patch, not a dependency on the withdrawn experimental commit. It intentionally lives in Results_Bin until the user decides there is enough testing. There is no automatic installation or promotion.

## Isolated application

Clone both repositories, then use a new Labtune test checkout/worktree. The following shell commands assume a POSIX shell and that the paths are adjusted to the two local clones:

```sh
RESULTS_BIN=/absolute/path/to/Results_Bin
EXPERIMENT="$RESULTS_BIN/Labtune/Experiments/native-streaming-and-partial-output"

git clone https://github.com/JeranRolevs/labtune.git labtune-experiment
cd labtune-experiment
git switch -c test/native-streaming d0f462a28bcc4267f8767316d8c73c3c72201063
git apply --check "$EXPERIMENT/patches/labtune-streaming.patch"
git apply "$EXPERIMENT/patches/labtune-streaming.patch"

python3 -m venv .venv
. .venv/bin/activate
python -m pip install '.[memory,bayesian]'
python -m unittest discover -s tests -v
python -m unittest discover -s examples/memory_retention/tests -v
python tools/sync_starter.py --check
python tools/check_release.py
```

Dependency installation may download ordinary packages. These checks themselves must not make paid provider calls. Preserve LICENSE, LICENSING.md, copyright and author notices. Source snapshots are provided for inspection; the patch is the complete application unit.

## If upstream has advanced

Do not force-apply or overwrite newer source files. Work on a separate branch, inspect conflicts and reimplement/rebase the intended changes against the new source. Re-run all regression, portability and package-export checks. Regenerate starter resources with `tools/sync_starter.py` after canonical documentation changes; do not edit generated resources alone.

## Promotion checklist

1. Review TESTING.md and close or explicitly accept remaining risks.
2. Keep user choices explicit: provider, model, streaming, communication, statistics, delegation and budgets. No silent defaults or automatic model/budget changes.
3. Confirm that usage, partial failures, privacy, cancellation and finite deadlines remain honest and bounded.
4. Verify native workflow completion separately from scientific evaluation; text proposals remain not_evaluated.
5. Record the new baseline, changes and fresh test results in a curated update here. Keep raw trials and audit records private.
6. Obtain explicit user approval to commit/push the accepted implementation into Labtune. Do not merge merely because one live workflow succeeded.
7. Once approved, create a new reviewable Labtune commit/PR, link it from this folder, and mark this experiment migrated with any limitations that remain. Do not treat the withdrawn commit as an approved release.

For an uncommitted test application, prefer discarding the isolated checkout/worktree after preserving any authorized work. Do not reset a shared branch or delete unrelated changes as a cleanup shortcut.
