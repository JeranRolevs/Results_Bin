# CAP pilot findings

## Verdict

**NO-GO for demonstrated added value of this particular sparse quadratic/log-bandpower predictor.** This is a real held-out result, not another model-generated research recommendation. It does not establish that all SINDy methods or all EEG/MEG problems fail.

Eight fixed healthy-control nights were processed. n1–n2 fit; n3 calibrated normal thresholds; n4 selected model options; n5–n8 were held out for evaluation. The test domain contained approximately **23.37 hours of annotated NREM**, with **1,927 eligible phase-A events**. CAP phases are physiological sleep microstructure, not automatically pathological anomalies.

## Primary result

Equal-record mean **average precision (AP)** on unadjusted one-second A/non-A labels; higher is better:

| Model | Mean AP |
|---|---:|
| Persistence residual | 0.246 |
| Sparse quadratic dynamics residual | **0.311** |
| Linear VAR residual | **0.389** |
| Dense polynomial ridge residual | 0.383 |
| Static spectral-state Mahalanobis | **0.448** |
| Supervised spectral/lag LDA reference | 0.605 |

LDA uses additional positive/negative class-label supervision; it is a practical reference, not an identical normal-only training regime. Linear VAR and static spectral scores are the more important normal-only comparisons. The sparse model beat persistence on all four test records but beat the strongest primary normal-only comparator on **zero of four**.

At the frozen per-model calibration rule and two-second alarm rule, sparse new-event recall averaged **27.5%**, versus **66.2%** for linear VAR. Sparse had fewer new false alerts (about 30.4 versus 80.9 per non-A NREM hour), but this is accompanied by far lower event recall, not proof of better detection at matched test false-alarm rates. Primary AP does not depend on that single threshold choice. These alarm counts describe this oracle-NREM prototype, not clinical alarms per hour of full-night monitoring.

## Not merely a montage artifact

The predeclared nominally matched test night n5 also favored simpler models: sparse AP **0.304**, linear VAR **0.359**, static spectral AP **0.467**. However, one such night is not a controlled attribution study. n6–n8 change central-mastoid derivation/rate/device, so the overall sample also tests domain shift. No patient was removed or replaced after results.

## What this suggests—and what it does not

For this representation and dataset, ordinary power-state and linear-dynamics information was more useful than the tested sparse nonlinear residual. This is consistent with CAP scoring being strongly linked to spectral changes; it does **not** prove a causal explanation of CAP or general adequacy of linear models for brain dynamics.

The model sees four causal bandpower features, not full phase/cross-channel neural dynamics. It is discrete sparse nonlinear autoregression, not identified physical neural equations. The selected sparse option retained 315 of 612 coefficients across four outputs—only moderate sparsity. Its ridge strength was fixed at 0.001 while linear/dense ridge could select 0.001/0.1/1.0; this finite grid does not exhaust sparse-model possibilities. Stronger regularization or a different representation would require new development and untouched test records, not retuning this holdout and presenting it as confirmation.

Other limitations: one central channel despite labels scored on other/multiple derivations; expert NREM gating; label-assisted normal training; healthy subjects only; source analog filters differ; ADC clipping was retained and reported (about 2.46% of samples on n5). There is no validated pathology detector, official CAP-cycle/rate reconstruction, clinical utility or statistical-superiority claim.

## Resource and integrity evidence

- Completed in **19m 29s**, including downloads, preprocessing and modeling.
- Peak summed process RSS about **1.22 GiB**, below the 4-GiB limit; four-worker ceiling, below 60 minutes.
- Eight EDFs, **2,289,532,164 bytes**, each checked against official SHA256; annotation integrity checked too.
- Protocol, code and metadata hashes match the pre-fit freeze. The selected-model fingerprint matches the saved pre-test selection file. All four test records appear in every model's results.
- Five offline format/mathematical tests passed. These tests support implementation checks, not clinical validity.
- **Zero paid provider calls; no raw recordings sent to a provider.**
- This is a separate trusted local evaluator, not a native Labton domain adapter.

## Decision

Do not claim a useful SINDy advantage for this CAP variant or spend additional model calls merely to rephrase the negative result. The useful outcome is a measured boundary: beating persistence alone would have been misleading.

If pursuing CAP further, make a distinct, mechanistically motivated representation/regularization hypothesis and freeze a new independent split before testing it. Otherwise prefer a different problem with better-observed nonlinear dynamics and a practical endpoint. No additional fits, patients, provider calls or budget increases have been launched.

Data attribution: CAP Sleep Database v1.0.0, DOI **10.13026/C2VC79**, Open Data Commons Attribution License v1.0; cite Terzano et al. (2001), *Atlas, rules, and recording techniques for the scoring of cyclic alternating pattern (CAP) in human sleep*, Sleep Medicine 2(6):537–553. See DATA_ATTRIBUTION.md and the official PhysioNet page for source terms.

## Publication scope

This curated report is published with authorization. Original raw outputs, private freezes, audit records and research-agent trials remain outside this repository. The included evaluator directory contains computational kernels and offline fixtures, not the historical download/execution supervisor.
