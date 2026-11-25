# Local validation report — 2026-11-25

## Passed

- Frozen E2/E3 evaluation results, evaluation lock, statistics source and analysis runner matched their pre-existing configuration SHA-256 values before extraction. E1 analysis, E4 diagnostics, E5 concentration matched their respective result locks. The exact comparisons and original hashes are recorded in `provenance/source_hashes.json` for E2/E3.
- Export retained all 8,656 input records, in source order, with only documented fields and no row filter. Exact equality of every recalculated E2/E3 descriptive and inference row with frozen `tables.json` verifies the numerical effects of this extraction.
- A fresh directory outside the project was used to run `check_selector.py` and `verify_results.py` with bundled Python and no project path. Both passed. This import check is not a behavioral test of OECS.
- Primary 403: Qwen TF-IDF 351, OECS 366, discordance 15/0, +3.7221 pp; Mistral 158, 180, 30/8, +5.4591 pp. OECS versus No Memory is +24.3176 pp Qwen and −3.7221 pp Mistral.
- All 541: Qwen 469 versus 484, 15/0, +2.7726 pp; Mistral 226 versus 248, 30/8, +4.0665 pp. All 18 inferential rows including 10,000-replicate paired percentile bootstrap intervals, exact two-sided McNemar p values and within-family Holm adjusted p values matched frozen tables.
- Automated scan found no common private-key blocks, common API-token patterns, obvious private home paths, or sensitive configuration filenames. Excluded raw chat, audit participant records, model weights, caches and model output text. This is a bounded scan, not proof of absence of all sensitive content.

## Not tested

- Selector decisions against all original candidates; original target-to-memory selections and the changed-union construction.
- Recalculation of E1 applicability, E4 diagnostics, E5 concentration, blind-audit findings, or figures. The corresponding retained aggregate files are reference outputs only.
- Full inference, environment setup, original model hashes, GPU operation, and the original generation pipeline. No model, remote service, or GPU was used.

## Blocked / author review before release

- Dataset licensing and permission to redistribute derived 100-memory texts are unconfirmed. The frozen memory bank, its complete construction dependencies, local benchmark extensions, original selection inputs, model outputs and exact complete rerun environment are not packaged. The A workflow verifies E2/E3 statistics, not all figures and results in the paper; B is not runnable from this export.
- Authors must select a project license, review third-party/model terms and permissions, and inspect the package for private or sensitive information. The paper Data Availability Statement remains a draft and must be updated only when the actual release status is known.

## Experiment-code export follow-up

The source tree and additional experiment entry points were added for code sharing. The selector import and E2/E3 statistics checks passed again in a fresh external directory. The extra entry points have not been executed or verified for complete dependencies; full experiments remain untested. A common credential and private-path pattern scan found no matches.
