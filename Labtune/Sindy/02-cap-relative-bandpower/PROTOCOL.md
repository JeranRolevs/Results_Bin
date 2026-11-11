# CAP relative-bandpower comparison: published protocol description

Curated publication copy, not the original timestamped private freeze. All models use dimensionless relative features because some source files have unknown voltage units; no missing unit is assigned. Relative normalization does not remove all acquisition/reference differences. Execution was a trusted standalone evaluator, not a native Labton adapter. Ceiling: four CPU workers, 4 GiB summed RSS, 60 minutes cumulatively including the failed attempt, and at most 4 GiB raw EDF working set. No paid model calls.

## Frozen data roles

- **Fit:** n1,n2, unchanged from the prior pilot.
- **Normal calibration:** n3, unchanged from the prior pilot.
- **Development/model selection:** n9,n10,n11,n12, equal-record aggregation.
- **Confirmation:** n13,n14,n15,n16, untouched model outcomes at protocol freezing.
- Prior n4–n8 are not refit/retested or reused as new confirmation. They informed the research design only.

No subject replacement based on performance, file size or desired outcome. Metadata, annotation inventory and montage availability have been inspected before fitting, not signal-derived model outcomes. Cached n1–n3 EDF files are reused only after checksum verification; n9–n16 are new downloads with official SHA256 verification. Expected new raw bytes: 1,526,194,336. Cached+new raw working set must remain <=4 GiB.

Use the same central-mastoid selection rule for all models: normalized punctuation aliases C4A1/C4-A1 first, otherwise C3A2/C3-A2. n9 uses C3-A2; n10–n16 use C4-A1/C4A1. Sample rates include 100,128,200,512 Hz. Different acquisition setups remain a limitation. Unknown EDF record count -1 is resolved exactly from full-file length and channel sample layout; a nonintegral resolution fails the run.

## Labels and causal representation

Same task and evaluation population as the prior pilot: pooled MCAP-A1/A2/A3 versus non-A during **expert-annotated NREM S1–S4**. This is physiological event detection with oracle NREM gating, not pathological anomaly diagnosis or automatic full-night clinical scoring. Normal fitting excludes a fixed 15-second buffer around A events; this label-assisted normal selection is disclosed. Calibration/test normal includes difficult transitions, without outcome-based cleanup.

Independent TSV clock parsing uses EDF start time and midnight rollover. Stage annotations extending <=60 seconds beyond the record are flagged and clipped to recorded time; clipped A events get no new-onset credit. Other alignment errors stop the study.

Representation for **every** model:

1. EDF digital->physical numerical calibration; preserve the raw unit label but do not assume missing units or convert them to uV. A constant unknown multiplicative voltage gain is permitted because it cancels below.
2. Same four second-order causal Butterworth bandpasses: 0.5–4, 4–8, 8–12, 12–30 Hz. Carry filter state across chunks; no zero-phase filtering or future interpolation.
3. Per second compute trailing-two-second band energy E_b. Form r_b = E_b / sum(E_b), then log(max(r_b,1e-10)). The floor is **dimensionless**, never an absolute voltage floor. If total energy is nonpositive/nonfinite, mark the feature invalid for all models; no label-based exclusions.
4. Four log-relative-power states at 1 Hz, same lags 1,2,4,8 seconds. Burn first 60 seconds and invalid lag histories; no whole-test-record normalization or patient-specific adaptation. State standardization uses fit-normal n1,n2 only.

Relative powers discard absolute amplitude and have a compositional constraint. This may help or hurt CAP detection; no benefit is assumed. One central channel also cannot represent every event scored on other/multiple derivations. ADC clipping is retained/reported, not used to select successful test segments.

## Fixed model families and grids

Same data and inputs for all matched primary models. All train on the identical fit-normal rows, except the separately labeled supervised reference. Ridge objective is Gram/n + alpha*I, with an unpenalized intercept where present. All polynomial columns scale using training-only mean/std. Max 10 monotonic prune/refit steps.

**Shared ridge grid:** alpha in {0.001,0.1,1,10}. **Sparsity cutoff grid:** {0.01,0.05,0.1,0.2}. No added polynomial degree, phase feature, learned representation, regime switching or ensemble.

Controls:

- persistence;
- linear ridge VAR, 4 options;
- dense quadratic ridge/NARX, 4 options;
- static spectral-state Mahalanobis, fixed 0.1 covariance shrinkage;
- supervised spectral/lag LDA, fixed 0.1 covariance shrinkage, same state/lags plus A/non-A labels on n1,n2 (extra supervision disclosed);
- legacy sparse recipe: fixed alpha=0.001 and cutoff=0.01, retrained on the **new relative representation**. This is a recipe control, not the original saved absolute-power model or its old AP score.

Revisions:

- **Jointly regularized sparse quadratic predictor:** 4 ridge × 4 cutoff = 16 options, otherwise the existing STLSQ-style model.
- **Linear backbone + sparse quadratic residual:** fit a linear VAR for each of the 4 ridge strengths; hold that backbone fixed while fitting only quadratic interactions to its training residual. Nonlinear ridge uses the same 4 strengths, cutoff the same 4 values. Include a separate **zero correction** for each backbone: 4 × (16+1) = 68 options. No nonlinear intercept/linear terms in the correction. Null correction exactly recovers its linear predictor and score normalization.

This yields 96 scored options across all eight families (including fixed controls). Cache equivalent Gram/cross-products only for computational efficiency; unit tests must compare cached fits with the independently tested direct prototype. More selection opportunities exist for nonlinear families; untouched confirmation is necessary and a single small study still cannot establish reliable superiority.

## Selection and lock before confirmation

Use each candidate's own **95th percentile of n3 non-A NREM scores** as the fixed threshold. Residual models scale each target error by fit-normal residual RMS (floor 0.001 in training-standardized units). Static/LDA use their native scores with the same quantile rule. No threshold tuning on development/test event labels.

Select each family's option by highest equal-record **development AP over n9–n12**. Ties within 1e-12 prefer fewer nonlinear nonzeros, then fixed grid order. Select one **primary revised candidate** across the two revised families with the same rule **before** test metrics. Preserve both families' results as secondary. Select strongest primary normal-only comparator on development AP, not confirmation.

Write selected models, thresholds, parameters, counts, code/protocol fingerprints and timestamp to a local model-selection record before calculating any n13–n16 scores/metrics. Require >=1000 fit-normal and calibration-normal seconds, and both classes in each development/confirmation record. If data are insufficient or any model has nonfinite predictions, report failure/infeasibility, never silently omit failing records or change the split.

## Metrics and predeclared interpretation

Primary descriptive metric: equal-record mean **average precision** on unadjusted one-second A/non-A bins. Group tied scores; report per-record prevalence and AP/ROC-AUC. Correlated windows are not independent experiments; no formal superiority hypothesis test/CI is claimed with four confirmation records.

At the frozen threshold require two consecutive eligible above-threshold seconds. Report ordinary bin precision/recall/F1, non-A false-positive time fraction, new false alerts per non-A NREM hour, and phase-A event recall from an alarm rising edge timestamped inside the event. Already-active pre-onset alarms earn no new-onset credit. Delays are conditional on new detection and must accompany event recall. No point adjustment, event expansion or clinical-monitoring alarm-rate claim.

A **GO for a larger study** requires the preselected revised candidate to:

- have confirmation mean AP >=0.05 above every primary normal-only comparator (persistence, current VAR, dense polynomial ridge, static spectral);
- beat every such comparator in at least 3/4 confirmation records;
- have no greater mean normal false-alert burden than the comparator preselected on development;
- exceed the supervised spectral-reference mean AP for a practical-advantage claim;
- retain at least one nonlinear correction/term if claiming nonlinear added value.

Otherwise report **NO-GO for demonstrated added value in this tested configuration**, not that all SINDy/EEG methods fail. If the zero correction wins, report convergence to linear VAR. Show the comparison to the legacy recipe **on the same new representation and confirmation records**; do not compare fresh scores directly to the old 0.311 on different data/features.

No post-confirmation patient selection, refitting, grid expansion, calibration changes or retuning. Negative and mixed outcomes are retained. No clinical diagnosis, physical neural-equation identification or official CAP-cycle-rate claim.


## Pre-fitting technical amendment

The first execution stopped before model fitting because n12 declares reversed digital calibration endpoints (410, -410) paired with physical endpoints (-50, 50). No model-selection or confirmation scores existed at that point. The amended extractor preserves this signed affine mapping, explicitly flags reversed endpoints, and sorts the bounds only for the clipping diagnostic. Squared band-energy ratios are invariant to waveform polarity and uniform gain; synthetic EDF fixtures verify this. Nonfinite/equal endpoints still fail. This does not claim full EDF conformance or resolve acquisition differences.

The amendment did not change splits, grids, thresholds, selection or GO rules. The manually authorized continuation used only the remaining original cumulative 60-minute execution allowance. Historical freezes, raw data and audit records are not distributed. The final amended computational kernels and offline tests are included.
