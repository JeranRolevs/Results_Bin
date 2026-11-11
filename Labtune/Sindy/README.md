# SINDy research hub — Labtune

Labtune (formerly Labton) is the research system for this programme. This directory is the central hub for its SINDy-related research, tests and curated findings. Every study must distinguish Labtune scientist research from externally executed numerical evaluation.

**Two completed negative studies, with the simpler controls retained.** These exploratory studies ask whether sparse nonlinear autoregressive residuals add value for physiological CAP phase-A event detection in healthy-control sleep EEG. They do not diagnose pathology or identify physical neural equations.

| Study | Sparse candidate AP | Linear VAR AP | Static spectral AP | Supervised reference AP | Outcome |
|---|---:|---:|---:|---:|---|
| [01: Absolute bandpower](01-cap-absolute-bandpower/FINDINGS.md) | 0.3107 | 0.3894 | 0.4484 | 0.6046 | No demonstrated added value |
| [02: Relative bandpower](02-cap-relative-bandpower/FINDINGS.md) | 0.4162 | 0.4172 | 0.4097 | 0.4868 | No demonstrated nonlinear added value |

**Do not compare AP across these rows as an improvement estimate:** representation and confirmation subjects changed. The matched relative-feature legacy recipe scored **0.2921** on the second study's same confirmation records. Tuning increased AP to **0.4162**, but deleted every lagged and nonlinear coefficient, leaving a static spectral-distance score. The linear-plus-sparse-residual family selected **zero correction**, exactly matching VAR at **0.4172**.

## Contents

- `01-cap-absolute-bandpower/`: published scientific protocol, curated findings, independently implemented evaluator kernels and five offline tests.
- `02-cap-relative-bandpower/`: published protocol including the pre-fitting calibration amendment, curated findings, final evaluator kernels and sixteen offline tests.
- `DATA_ATTRIBUTION.md`: dataset source, license and required citation.
- `LICENSE` and `LICENSING.md`: unchanged Labton license and notices.

The protocol documents are publication descriptions, **not original timestamped freezes or external preregistration**. No raw EDF, annotations, extracted features, raw trial results, trained-model coefficients, credentials, private seed panels, researcher prompts, audit archives or historical logs are included. The earlier scientist-organization/private-manual-baseline studies are outside this export. Original private records are retained separately, not committed here.

## Run the offline tests

Use Python 3.11+ with NumPy and SciPy (the test modules use only the standard library otherwise):

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r Labtune/Sindy/requirements.txt
python Labtune/Sindy/run_offline_tests.py
```

Installation uses ordinary dependency downloads; **the tests themselves make no network or paid provider calls**. The historical numerical environment reported Python 3.14.4, NumPy 2.5.4 and SciPy 1.18.1. These are recorded observations, not a dependency lock or a claim that other environments reproduce bit-identical scores.

The test runner isolates the two module versions in separate processes. Tests cover EDF demultiplexing, annotation midnight/record edges, causal chunking, tied AP/AUC, event-onset credit, sparse regression, residual null identity, synthetic nonlinear recovery, gain/polarity invariance, missing-unit handling, and cached/direct fitting equivalence. Passing these tests does not validate clinical performance.

## Reproduction boundary

The evaluator directories contain computational kernels and synthetic offline fixtures, **not a turnkey rerun of the historical experiment**. Running the tests does not reproduce the reported dataset AP. A full independent replication requires acquiring CAP data from its official source under its terms, verifying upstream checksums, reconstructing the published feature/split/selection protocol, and writing a bounded execution harness. Private historical freezes, data and supervisors are deliberately not bundled. Importing the modules does not initiate downloads; executing the metadata auditor directly can fetch public metadata, so it is not part of setup/testing.

All scientific implementation here was independently written for these studies; no upstream SINDy/CAP research implementation was copied or executed. NumPy/SciPy are general-purpose dependencies, not vendored research code.

## Interpretation and execution

Both studies use expert NREM gating, label-assisted normal fitting/calibration, one central-mastoid derivation and four confirmation records. Correlated one-second bins are not independent trials. No formal superiority statistics, clinical utility or universal SINDy-failure conclusion is claimed. Confirmation records must not be retuned and described as untouched again.

Labton supported the preceding scientist workflows/proposals. **These numerical evaluations used a trusted standalone evaluator, not a native Labton adapter.** Both made zero paid model calls and sent no raw EEG to providers. No new dataset experiment is included or launched by this publication.

## Licensing

Copyright (c) 2026 Pioneertown B.V.; author: Goran Mitevski. Code and documentation preserve the **Labton Academic Research License 2.0**, not MIT/Apache or unrestricted open-source terms. See the full [LICENSE](LICENSE) and [LICENSING.md](LICENSING.md) for eligibility, exclusions and permission requirements. Dataset licensing is separate: CAP Sleep Database v1.0.0, ODC Attribution 1.0; see [DATA_ATTRIBUTION.md](DATA_ATTRIBUTION.md). NumPy/SciPy retain their own licenses; neither dependency nor the dataset is redistributed here.

## Naming and publication policy

The project was renamed from Labton to [Labtune](https://github.com/JeranRolevs/labtune). Historical files, implementation snapshots and their original license notices retain the names under which they were created; they are not rewritten as native Labtune experiment executions. New lab research will identify the Labtune revision, user-approved organization/model/budget, independently checked sources, limitations, and whether conclusions are proposals or measured results. Only curated, authorized publication material belongs here; private trials and raw artifacts stay outside Git.
