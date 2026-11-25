# OECS: Paper experiment code

Observable-Evidence Conservative Selection (OECS) conservatively decides whether to replace the default retrieved failure memory using observable evidence. The paper studies **one recovery decision**, not a complete multi-step agent. Retrieval relevance, memory applicability, and recovery validity are different outcomes. Better selection does not establish that using memory is better than using none.

**Status:** this repository contains the paper experiment code and reduced per-target evaluation records. The E2/E3 tables can be independently recalculated; an end-to-end experiment rerun requires additional artifacts and has not been verified.

## A. Lightweight result verification

Requires Python 3.10+; no additional Python packages, model downloads, API, GPU, or inference are needed. From the package root:

```sh
python check_selector.py
python verify_results.py
```

The latter runs the original analysis logic on 8,656 retained rows, compares **every** descriptive and inference row with the frozen tables and prints the 403-target primary and 541-target sensitivity comparisons and the No Memory differences. Tests include exact two-sided McNemar, paired percentile bootstrap (10,000 replicates; recorded base seed 20260810 and comparison-specific derived seeds), and Holm adjustment within prespecified families. The bootstrap intervals are not Holm adjusted. Frozen invalid-output fallback outcomes remain included. Source identities and extraction rules are in `provenance/source_hashes.json`; `SHA256SUMS` checks packaged files. The original runner import was adapted for this self-contained entry point; its statistical logic was not changed.

`outputs/paper_2026/e2_e3_formal_analysis/tables.json` corresponds to the paper's main condition counts, paired comparisons and Appendix all-valid table; inference rows also provide the stratified comparisons. The accompanying E1, E4 and E5 files are frozen summaries, not regenerated here. **Figures, selection applicability, E4/E5 analyses, and the blind audit have not been independently reproduced**. No figure rendering command is claimed.

## B. Full experimental rerun: incomplete, not tested

Full reconstruction requires ToolMisuseBench release v0.2_large, dataset revision `98eb28718b0393e029088ce80604c48807216de4` from https://huggingface.co/datasets/sigdelakshey/ToolMisuseBench and benchmark code commit `b6ee3412f98d2058ee487e182a72b26c58046d51` from https://github.com/akgitrepos/toolmisusebench, plus the local failure extensions and frozen 100 development-source memories. Confirm the dataset license before redistributing or using its text. The benchmark code license in the original checkout says MIT; this does not establish the dataset license. No benchmark text or memory texts are distributed here. The 100-memory reconstruction scripts, precise source filtering and frozen card inputs have not been packaged, so a full rerun cannot currently be performed from this package. Target identifiers and stratum and union flags are in `data/paired_results.json`. The union is targets where any of dense, judge, OECS, no-gate, or no-contradiction differs from TF-IDF Rank-1 in memory identity; no-memory and oracle do not define it. Union flags are frozen evidence, not independently regenerated here.

Original project entry points, **included as source but not verified as standalone commands**, are `experiments/paper_2026/prepare_e1_selection_inputs.py`, `run_e1_dense_selection.py`, `run_e1_llm_judge_selection.py`, `build_agent_prompt_cache.py`, `run_agent_generation.py`, and `evaluate_agent_outputs.py`. They require additional project code, input artifacts, frozen configurations, model manifests and paths that are not all included. Do not interpret them as a tested end-to-end workflow. The original environment records Python 3.11.15, PyTorch 2.12.0, Transformers 5.8.1, CUDA 12.9 and one GPU per process (smoke tests used an RTX 5880 Ada). Actual GPU needs and model redistribution terms require confirmation. Qwen/Qwen3-8B is identified by a 15-file manifest SHA256 `aa3e07db476dac6f3af8ad14958cb6febee947243f4bc29d7f6c5eda5c92e4ba`, not a verified repository revision; Mistral-7B-Instruct-v0.3 revision is `c170c708c41dac9275d15a8fff4eca08d52bab71`. Greedy agent decoding uses seed 20260810, max 256 tokens, bfloat16, no quantization, one recovery decision, and Qwen thinking disabled.

## Selection and prompts

`src/failure_memory/paper_2026/selector.py` and its dependencies contain the unchanged selector and component ablations; `check_selector.py` checks imports only, not an experimental selection run. `src/failure_memory/paper_2026/llm_judge.py` records the complete judge prompt construction and strict parsing. Invalid judge output falls back to TF-IDF Rank-1 without repair. `experiments/proper_v1/agent_runtime.py` records agent prompt and parsing contract as reference code and is not a standalone runner. Reference configs in `config/reference/` omit private machine paths.

TF-IDF uses lowercase `[a-z0-9_]+` unigrams; TF=count/total, IDF=log((1+N)/(1+df))+1, unseen query terms IDF 1, cosine, lexical ID tie-break, same-source exclusion. The first ten form OECS/judge candidates. Dense uses `BAAI/bge-large-en-v1.5` revision `d4aa6901d3a41ba39fb536a557fa166f842b0e09`, CLS pooling, normalized embeddings, query prefix, length 512 and cosine ranking over the full bank; its exact options appear in the reference config.

## Scope and limitations

Analysis conditions include no-memory, TF-IDF, dense, judge, OECS, both ablations and oracle; Oracle is descriptive only. The 403 changed-target union is selected before generation and is not representative of all 541 valid targets. Qwen improves over no-memory on the primary population, but Mistral is worse; failure strata and component ablations differ. These results do not establish general deployment safety or universal benefit. Third-party data and model rights, source-code license selection, the memory bank, raw generation traces, full environment, plot reproduction and full rerun remain author review items. See `VALIDATION.md`.
