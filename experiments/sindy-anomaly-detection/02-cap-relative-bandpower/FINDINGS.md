# Relative-bandpower CAP comparison: reviewed findings

## Bottom line

**NO-GO for demonstrated nonlinear added value in this tested configuration.** Joint regularization improves on the legacy sparse recipe under the same new representation and confirmation subjects, but does so by deleting every lagged and nonlinear predictor coefficient. The selected sparse predictor is intercept-only: it reduces to a static diagonal spectral-distance detector, not learned dynamics. The sparse residual family selects a null correction and is exactly the selected VAR, including coefficients, residual scaling and all confirmation metrics.

## Frozen comparison

All models use the same four causal log-relative bandpower coordinates and available 1/2/4/8-second lags. Fit n1–n2; normal calibration n3; development n9–n12; confirmation n13–n16. Each option uses its own n3-normal 95th-percentile score threshold. The 96-option grid and family selection were frozen before confirmation scoring; joint sparse was the preselected primary revised family. Equal-record means below cover 22.447 scored NREM hours and 1,867 eligible phase-A events. These are physiological sleep microstructure events in healthy-control recordings, not pathological anomalies.

| Family | Confirmation mean AP | Quadratic predictor coefficients |
|---|---:|---:|
| Persistence | 0.2562 | — |
| Legacy sparse recipe | 0.2921 | 320 |
| Dense polynomial ridge | 0.3816 | 544 |
| Static spectral full-covariance distance | 0.4097 | — |
| Jointly tuned sparse predictor | **0.4162** | **0; also zero lagged linear coefficients** |
| Linear VAR | **0.4172** | 0 |
| VAR + sparse quadratic residual | **0.4172** | **0: null correction selected** |
| Supervised spectral/lag LDA reference | 0.4868 | — |

The tuned sparse candidate used ridge 1.0 and cutoff 0.2. Its only four numerically nonzero coefficients are intercepts of order 1e-14 or smaller; every non-intercept coefficient is exactly zero. VAR selected ridge 10.0. The selected residual option is its exact uncorrected counterpart. The legacy recipe remains ridge 0.001, cutoff 0.01.

Matched new-data AP change over the legacy recipe: **+0.1241**. This is a descriptive improvement in the search/regularization recipe, not a demonstration of nonlinear dynamics. Do not compare the new 0.4162 directly against the previous absolute-bandpower study's approximately 0.311: both representation and confirmation subjects changed. The representation change itself was not isolated against an absolute-power comparator because some new records have unknown physical units.

## Per-record AP (no test-driven reselection)

| Record | Legacy sparse | Preselected tuned sparse | VAR / null residual | Static full covariance | Supervised LDA |
|---|---:|---:|---:|---:|---:|
| n13 | 0.2920 | 0.4812 | 0.4633 | 0.4555 | 0.5072 |
| n14 | 0.3082 | 0.3914 | 0.4069 | 0.4172 | 0.4419 |
| n15 | 0.2887 | 0.4795 | 0.4664 | 0.4780 | 0.5456 |
| n16 | 0.2793 | 0.3125 | 0.3322 | 0.2880 | 0.4526 |

## Prespecified decision checks

- AP at least 0.05 above every primary normal-only control: **fail**; selected sparse is 0.0011 below VAR.
- Beat every primary control on at least 3/4 records: **fail**, 2/4.
- No worse new false-alert rate than development-selected strongest normal-only control: **pass**, 53.51 versus VAR 57.13 per non-A NREM hour. This is still high and is not clinical utility.
- Exceed supervised reference AP: **fail**. Supervised LDA uses extra class-label supervision.
- Retain nonlinear terms: **fail**.

## Execution and pre-fitting calibration repair

The initial attempt downloaded and SHA256-verified all 11 EDFs, then stopped before model fitting on n12's reversed digital endpoints (410, -410, paired with physical -50, 50). No model-selection artifact or confirmation scores existed. The failed attempt was preserved privately; those archives are not part of this export.

The manual continuation preserved the declared signed affine endpoint mapping, flagged the irregularity and sorted endpoint bounds only for the clipping diagnostic. This is not silent header repair or a claim of full EDF conformance. Squared band-energy ratios are invariant to polarity and uniform gain. Synthetic EDF fixtures verify exact polarity invariance, gain invariance, causal future independence and correct clipping bounds. Nonfinite/equal endpoints still fail. The technical amendment and code were refrozen before fitting; no grid, split or scoring rule changed. Unknown units remain unknown, especially n13–n15; no uV imputation.

Sixteen offline tests passed. The cumulative observed execution time, including the failed attempt, was **613.925 seconds (10m14s)**. Observed peak summed process RSS was **1.295 GiB**; CPU affinity was four slots and raw working set **2.744 GiB**. The continuation had only 3,038 seconds available, preserving the original 60-minute cumulative budget. No automatic retry/restart, new download or paid provider call was used for the continuation.

This is a **trusted standalone evaluator, not a native Labton experiment adapter**. Raw recordings were not sent to a model. Code, metadata, protocol and selection hashes were reviewed; original absolute-study code/protocol remain unchanged. Git tracked files are unchanged.

## Limitations and stopping point

Four confirmation subjects, oracle expert NREM gating and label-assisted normal fitting/calibration are not a clinical deployment evaluation. Relative power removes uniform gain, not montage, reference, hardware frequency response or all recording shifts. No formal superiority statistics, universal SINDy-failure conclusion or physical neural-equation identification is claimed. Do not retune on these confirmation records and reuse them as untouched confirmation. No further study, cohort, model call or budget increase is launched by these findings.

Data: CAP Sleep Database v1.0.0, DOI 10.13026/C2VC79; ODC Attribution License 1.0; Terzano et al. (2001). See [data attribution](../DATA_ATTRIBUTION.md).

## Publication scope

Curated findings are published with authorization. Original raw results, private freezes, audit records, model coefficients and research-agent trials remain outside this repository. The included source is the final amended computational kernels and offline fixtures, not a turnkey historical replay.
