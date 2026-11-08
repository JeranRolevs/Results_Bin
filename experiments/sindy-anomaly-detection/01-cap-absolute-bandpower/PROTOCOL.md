# CAP absolute-bandpower pilot: published protocol description

This is a curated publication copy of the scientific design, not the original timestamped private freeze. The numerical evaluator was standalone, not a native Labton adapter. Execution ceiling: four CPU workers, 4 GiB summed RSS, 60 minutes, and at most 4 GiB raw EDF working set. No paid model calls were needed.

## Data and selection

Source: PhysioNet CAP Sleep Database **v1.0.0**, https://physionet.org/content/capslpdb/1.0.0/ and https://physionet.org/files/capslpdb/1.0.0/ . Dataset DOI **10.13026/C2VC79**. License: **Open Data Commons Attribution License v1.0**. Preserve source and Terzano et al. (2001) atlas/rules/scoring citation; follow source terms. This is not pathological anomaly detection: phase A is normal sleep microstructure, and excessive CAP may be associated with disorders.

First eight numerically ordered healthy-control records **n1..n8**, chosen before model outcomes; no patient replacement based on performance. Metadata audit found 8.2–12.3-hour records with hundreds of annotated phase-A events each. Raw EDF files total about 2.29 GB, not the full 40.1-GB database.

**Frozen split:** n1,n2 fit; n3 normal calibration; n4 development/model selection; n5,n6,n7,n8 untouched model-evaluation records. Metadata/annotation inventory has been inspected, but no signal-derived model results exist at freezing. This is a small exploratory holdout, not a preregistered independent clinical study or replication of published CAP scoring standards.

No exact EEG channel is common to all eight. Predeclare the physiologically related central-mastoid mapping **C4-A1 if present, otherwise C3-A2** (no other substitution). n1–n5 use C4-A1; n6–n8 use C3-A2. Rates are 512, 100 or 128 Hz. Units uV/mV convert using EDF physical/digital calibration, and mV->uV. This introduces lateral/montage/device shift, not a guaranteed identical observable. Expert CAP labels may have been scored on other/multiple EEG derivations; a single central channel may not contain every labeled event, a task-observability limitation shared by all comparators. Report n5 (same nominal montage/rate as fit) separately from n6–n8 as a predeclared descriptive stratum; never promote a stratum as the primary success after seeing results. Do not claim clinically generalizable transfer from this sample.

Fetch each full EDF once with an explicit size ceiling and verify the pinned upstream SHA256. Text annotations also retain SHA256. Do not reuse or execute upstream analysis scripts. Raw recordings/annotations are not sent to a provider or served in the dashboard.

## Label/clock audit

Parse REMlogic TSV event rows independently. Align 24-hour annotation clock to the EDF recording start, accounting for midnight. Stage epochs extending <=60 seconds beyond the physical record are marked/clipped to available data; entirely out-of-record portions receive no score. All other alignment errors stop the pilot. Retain original timing and audit warnings. Do not infer pathological status from CAP subtype.

Target: **any MCAP-A1/A2/A3 phase**, pooled, versus non-A EEG during annotated NREM (S1–S4). Score at one-second bin midpoints; retain A subtype/event counts for diagnostics. Expert NREM annotations define the evaluation domain: **oracle NREM gating**, not an automatic full-night clinical pipeline. Signals/features remain continuous/causal; expert stage labels are not predictive inputs. Other stages/unscored intervals are not negatives.

Normal fitting uses NREM non-A seconds, excluding a fixed 15-second buffer on both sides of phase-A intervals so feature history does not cross them. Label-assisted normal selection is disclosed; this is not label-free training. Calibration and test normal populations include NREM non-A seconds, including difficult transitions (no test-label cleanup).

## Causal features and permitted inputs

One central channel only, per frozen mapping. Same observed data for all primary models. Four second-order causal Butterworth bandpasses: delta 0.5–4 Hz, theta 4–8, alpha 8–12, beta 12–30. Use `scipy.signal.sosfilt` with state carried across chunks, never zero-phase filtering or future interpolation. Acquisition filters differ by source header and their delays are not known; report this limitation.

At 1 Hz form log mean-square band energies over the trailing two seconds, giving **four log-bandpower state variables**. No test-record normalization. Exclude first 60 seconds of each record and missing/non-finite values. ADC clipping is reported, not used for outcome-based test exclusions. Lags **1,2,4,8 seconds**, same across dynamics models. Standardize states on fit-normal data only. This is a **sparse discrete polynomial NARX/SINDy-style predictor**, not a recovered continuous neural governing equation.

## Models

1. Persistence: previous feature state.
2. Multivariate linear ridge VAR on the same four lags.
3. Dense quadratic polynomial ridge/NARX on the same lag representation.
4. Sparse quadratic predictor with independently implemented sequential thresholded ridge least squares; no PySINDy/upstream implementation imported.
5. Normal-only static spectral-state Mahalanobis score (regularized fit-normal covariance).
6. **Supervised spectral/lag LDA reference:** linear classifier on current and same lagged features using fit-record A/non-A labels. Additional class-label supervision is disclosed; this is a useful practical reference, not an identical normal-only training regime. Do not hide it if it defeats the unsupervised residual approach.

Ridge strengths **0.001, 0.1, 1.0**, objective Gram divided by fit sample count, unpenalized intercept. Sparse base ridge **0.001**, standardized-coefficient cutoffs **0.01, 0.05, 0.1**, at most 10 prune/refit iterations; intercept retained. Feature column scaling is learned on fit data only. Dynamics scores are mean squared residuals scaled by fit-normal per-output residual RMS (floor 0.001 standardized units). Static covariance and LDA shrinkage fixed at **0.1**, no test tuning.

Every model uses its **own 95th percentile** of n3 normal scores, i.e. same calibration rule, not an arbitrary shared numeric residual threshold. Require at least 1000 fit-normal and 1000 calibration-normal seconds (temporally correlated seconds are not claimed independent trials). For ridge/sparsity options choose best **n4 development average precision**, ties by declared option order; write the selected parameters and source/code fingerprints before computing any test metrics. Thresholds never tune to n4/test labels. LDA/static/persistence have no selected hyperparameter.

## Metrics and stopping interpretation

Primary descriptive metric: **equal-record mean average precision (AP)** for A/non-A one-second bins on n5–n8, with per-record prevalence and per-record results. Group tied scores for AP; report ROC-AUC as secondary. Correlated bins are not independent samples and no formal superiority test or CI is claimed.

Alarm rule: above calibrated threshold on **two consecutive eligible NREM seconds**. Report ordinary unadjusted time-bin precision/recall/F1, normal false-positive time fraction, new false-alert episodes per scored non-A NREM hour, and one-to-one phase-A event recall from an alarm **rising edge inside** the event. An alarm already active before A begins does not receive new-onset credit. Median delay only among newly detected events, accompanied by event recall; do not compare conditional delays alone. No point adjustment or retrospective expansion over an entire annotated event. Do not report clinical false alarms per hour of full-night independent normal monitoring.

A cautious **GO for a larger study** requires sparse mean AP at least **0.05** above every primary normal-only comparator, AP exceeding the best primary comparator in at least **3/4** test records, no worse equal-record normal false-alert burden than the strongest primary comparator (chosen on n4), and no claim of practical advantage if the supervised spectral/lag reference meets or exceeds sparse mean AP. Otherwise report **NO-GO for demonstrated added value in this pilot**, not proof SINDy can never work. Metadata insufficiency/domain-shift failure is reported explicitly; no new patients, channels, thresholds, libraries or subgroups are tried after confirmation.

CAP rate can be reported only as a rough A-time summary, not official CAP-cycle reconstruction, since this prototype does not implement the full Terzano cycle/sequence rules. No pathological-CAP diagnosis, sleep-quality endpoint validation or clinical utility claim.


Private runtime records are not distributed. See FINDINGS.md for limitations and observed outcomes.
