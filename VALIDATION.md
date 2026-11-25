# Local validation report — 2026-11-25

## Passed

- Original E2/E3 evaluation data, evaluation lock, analysis runner and statistics source matched their frozen SHA256 identities before extraction; E1, E4 and E5 summaries matched their result locks. The reduced 8,656 records retain all rows in source order.
- In a fresh directory, `verify_results.py` reproduced every frozen E2/E3 table row including 18 comparisons, exact two-sided McNemar tests, 10,000 paired bootstrap replicates and Holm adjustments. Primary Qwen: 366 vs 351, 15/0, +3.7221 pp; Mistral: 180 vs 158, 30/8, +5.4591 pp. On all 541 targets, the respective differences are +2.7726 and +4.0665 pp. OECS versus No Memory is +24.3176 pp and −3.7221 pp, respectively.
- Original typed selection inputs were reconstructed locally. The original E1 preparation verified 60 of 61 P0 source hashes; `docs/paper_2026/experiment_plan.md` did not match its frozen hash. For this reconstruction only, that documentation mismatch was explicitly waived; the remaining source checks and full comparison with the frozen selector audit remained active. No original files were modified.
- Before export, removing the instruction and raw argument values and replacing natural memory text preserved all 1,623 complete decisions across 541 targets and three variants. In a new directory, `verify_selector.py` matched those decisions and rebuilt the changed-target union as 403/541 from frozen selection identities. This does not regenerate TF-IDF ranks.
- In a fresh directory with the original frozen development file, `rebuild_memory.py` recreated the 100 source identities and natural-text hashes. Third-party data and rebuilt texts are not included. PyYAML from the locally bundled development environment was used; installation and data download were not tested.
- `generate_formal_figures.py` generated five SVGs from hash-verified frozen tables and diagnostics. These SVG hashes differ from the archived project SVGs; exact figure reproduction, visual equivalence and PDF/PNG conversion are not verified.
- An automated scan found no common private-key blocks, API-token patterns, private home paths or sensitive configuration filenames. The only email-shaped string was the corresponding author's email in CITATION.cff. This bounded scan is not proof of absence of all sensitive content.

## Not tested or unresolved

- TF-IDF retrieval from raw targets, full E1 finalization, independent E1 applicability, E4/E5 calculations, blind-audit results, raw-generation trace reconstruction, end-to-end cohort reconstruction, model setup or inference. No model, remote service or GPU was used.
- Full experiment scripts need more input artifacts and environment dependencies. Some configuration copies have machine paths removed or modified line endings; frozen source hashes can fail.
- Dataset and derived text redistribution rights and the OECS license require author confirmation. The original project metadata says MIT but no project-level license file was found. ToolMisuseBench code retains its own MIT license.
