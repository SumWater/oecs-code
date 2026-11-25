# OECS: Paper experiment code

Observable-Evidence Conservative Selection (OECS) conservatively decides whether to replace the default retrieved failure memory using observable evidence. The paper studies **one recovery decision**, not a complete multi-step agent. Retrieval relevance, memory applicability, and recovery validity are different outcomes. Better selection does not establish that using memory is better than using none.

**Status:** this repository contains the paper experiment code and reduced per-target evaluation records. The E2/E3 tables can be independently recalculated; an end-to-end experiment rerun requires additional artifacts and has not been verified.

## A. Lightweight result verification

Requires Python 3.10+; no additional Python packages, model downloads, API, GPU, or inference are needed. From the package root:

```sh
python check_selector.py
python verify_selector.py
python verify_results.py
python manuscript/scripts/generate_formal_figures.py
```

The latter runs the original analysis logic on 8,656 retained rows, compares **every** descriptive and inference row with the frozen tables and prints the 403-target primary and 541-target sensitivity comparisons and the No Memory differences. Tests include exact two-sided McNemar, paired percentile bootstrap (10,000 replicates; recorded base seed 20260810 and comparison-specific derived seeds), and Holm adjustment within prespecified families. The bootstrap intervals are not Holm adjusted. Frozen invalid-output fallback outcomes remain included. Source identities and extraction rules are in `provenance/source_hashes.json`; `SHA256SUMS` checks packaged files. The original runner import was adapted for this self-contained entry point; its statistical logic was not changed.

`outputs/paper_2026/e2_e3_formal_analysis/tables.json` corresponds to the paper's main condition counts, paired comparisons and Appendix all-valid table; inference rows also provide the stratified comparisons. The accompanying E1, E4 and E5 files are frozen summaries, not regenerated here. The formal figure script creates SVG files under `manuscript/figures/formal/`; it uses the included frozen tables and E4 summary and checks their hashes. SVG output was generated successfully, but it was not byte-identical to the archived figure assets; PDF/PNG conversion and visual equivalence have not been verified. Selection applicability, E4/E5 analyses, and the blind audit have not been independently reproduced.

## B. Full experimental rerun: incomplete, not tested

Full reconstruction requires ToolMisuseBench release v0.2_large, dataset revision `98eb28718b0393e029088ce80604c48807216de4` from https://huggingface.co/datasets/sigdelakshey/ToolMisuseBench and benchmark code commit `b6ee3412f98d2058ee487e182a72b26c58046d51` from https://github.com/akgitrepos/toolmisusebench, plus the local failure extensions and frozen 100 development-source memories. Confirm the dataset license before redistributing or using its text. The benchmark code license in the original checkout says MIT; this does not establish the dataset license. No benchmark text or memory texts are distributed here. A local builder and 100 frozen source identities are included; see the memory reconstruction section below. A full rerun cannot currently be performed from this package. Target identifiers and stratum and union flags are in `data/paired_results.json`. The union is targets where any of dense, judge, OECS, no-gate, or no-contradiction differs from TF-IDF Rank-1 in memory identity; no-memory and oracle do not define it. `verify_selector.py` rebuilds these flags from the frozen per-method selection identities and matches all 541 recorded flags.

Original project entry points, **included as source but not verified as standalone commands**, are `experiments/paper_2026/prepare_e1_selection_inputs.py`, `run_e1_dense_selection.py`, `run_e1_llm_judge_selection.py`, `build_agent_prompt_cache.py`, `run_agent_generation.py`, and `evaluate_agent_outputs.py`. They require additional project code, input artifacts, frozen configurations, model manifests and paths that are not all included. Do not interpret them as a tested end-to-end workflow. The original environment records Python 3.11.15, PyTorch 2.12.0, Transformers 5.8.1, CUDA 12.9 and one GPU per process (smoke tests used an RTX 5880 Ada). Actual GPU needs and model redistribution terms require confirmation. Qwen/Qwen3-8B is identified by a 15-file manifest SHA256 `aa3e07db476dac6f3af8ad14958cb6febee947243f4bc29d7f6c5eda5c92e4ba`, not a verified repository revision; Mistral-7B-Instruct-v0.3 revision is `c170c708c41dac9275d15a8fff4eca08d52bab71`. Greedy agent decoding uses seed 20260810, max 256 tokens, bfloat16, no quantization, one recovery decision, and Qwen thinking disabled.

## Selection and prompts

`src/failure_memory/paper_2026/selector.py` and its dependencies contain the unchanged selector and component ablations. `check_selector.py` checks imports only. `verify_selector.py` replays the real typed target and candidate features for all 541 targets and three variants and compares all 1,623 complete decision records with frozen outputs. To avoid redistributing benchmark text, natural memory texts are replaced with `[omitted]`, and instructions and raw argument values are redacted. Before export all 1,623 redacted decisions were compared with their original unredacted inputs and found identical. TF-IDF rankings are frozen, not recalculated by this check. `src/failure_memory/paper_2026/llm_judge.py` records the complete judge prompt construction and strict parsing. Invalid judge output falls back to TF-IDF Rank-1 without repair. `experiments/proper_v1/agent_runtime.py` records agent prompt and parsing contract as reference code and is not a standalone runner. Reference configs in `config/reference/` omit private machine paths.

TF-IDF uses lowercase `[a-z0-9_]+` unigrams; TF=count/total, IDF=log((1+N)/(1+df))+1, unseen query terms IDF 1, cosine, lexical ID tie-break, same-source exclusion. The first ten form OECS/judge candidates. Dense uses `BAAI/bge-large-en-v1.5` revision `d4aa6901d3a41ba39fb536a557fa166f842b0e09`, CLS pooling, normalized embeddings, query prefix, length 512 and cosine ranking over the full bank; its exact options appear in the reference config.

## Scope and limitations

Analysis conditions include no-memory, TF-IDF, dense, judge, OECS, both ablations and oracle; Oracle is descriptive only. The 403 changed-target union is selected before generation and is not representative of all 541 valid targets. Qwen improves over no-memory on the primary population, but Mistral is worse; failure strata and component ablations differ. These results do not establish general deployment safety or universal benefit. Third-party data and model rights, source-code licensing, redistribution rights, raw generation traces, full environment and full rerun remain author review items. See `VALIDATION.md`.

## Rebuild the fixed 100-memory bank locally

The code implements the recorded development-source filters, SHA256 ordering seed `confirmatory-v2-20260721`, source exclusions, one-source rule and five 20-source quotas. Install Python 3.10+ and PyYAML (`python -m pip install -r requirements.txt`). Obtain the `dev` split from the official [ToolMisuseBench dataset](https://huggingface.co/datasets/sigdelakshey/ToolMisuseBench) at revision `98eb28718b0393e029088ce80604c48807216de4`, after checking its terms. Place the downloaded file at a local path named `dev.jsonl`. Its required SHA256 is `a5a2b49b28c66f01bdbac37966c00cca9c6a1027a6d4b5b3a8c1d1d359db27e3`.

```sh
python rebuild_memory.py --dev /path/to/dev.jsonl --output /path/to/private/rebuilt_memories.json
```

The builder refuses a different dataset hash, reconstructs the memories and checks all 100 experience IDs and individual text hashes against `data/memory_sources.json` before writing the output. This was tested using the project's existing frozen development file; download and installation were not tested. The output contains benchmark-derived text; review its license before redistributing it.

## Configurations and full runs

`configs/` contains experiment configurations and the missing timeout-capacity source is included. Configurations are reference copies: machine-specific path lines have been omitted, and serialization may differ, so original frozen hash checks can fail. `config/path_redactions.json` identifies files with removed host paths. Full selection preparation and model generation still need the original frozen manifests, cohort artifacts, model files and runtime environment; these entry points have not been validated end-to-end. Never interpret `requirements.txt` as a complete GPU environment.

## License

The original project metadata declares `license = {text = "MIT"}`, but no project-level LICENSE was found and the authors have not confirmed that this declaration applies to this release. No license has been inferred for OECS; contact the authors for permission. ToolMisuseBench code included under `external/toolmisusebench/` retains its own MIT license.
