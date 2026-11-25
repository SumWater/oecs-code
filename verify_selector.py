import json, sys
from pathlib import Path
root = Path(__file__).resolve().parent
sys.path.insert(0, str(root / 'src'))
from failure_memory.paper_2026.selector import select_from_mappings
from failure_memory.paper_2026.contracts import SelectorVariant
cases = json.loads((root / 'data/selector_inputs_redacted.json').read_text(encoding='utf8'))['records']
ids = {x['target_key']: x for x in json.loads((root / 'data/selection_identities.json').read_text(encoding='utf8'))['records']}
rows = json.loads((root / 'data/paired_results.json').read_text(encoding='utf8'))['records']
unions = {x['target_key']: x['changed_target_union_member'] for x in rows}
assert len(cases) == len(ids) == len(unions) == 541
n = 0
for case in cases:
    for variant, expected in case['decisions'].items():
        observed = select_from_mappings(case['target'], case['candidates'], variant=SelectorVariant(variant), minimum_extraction_confidence=0.75).to_mapping()
        if observed != expected:
            raise AssertionError(f"selection mismatch: {case['target_key']} {variant}")
        n += 1
    x = ids[case['target_key']]
    values = [x['dense'], x['llm_judge'], *x['proper_variants'].values()]
    assert x['top10'][0] == x['tfidf']
    assert any(v != x['tfidf'] for v in values) == unions[case['target_key']]
assert sum(unions.values()) == 403
print(f'PASS: {n} frozen selector decisions across {len(cases)} real target feature sets; union 403/541')
print('Natural texts, instruction and raw argument values are redacted; TF-IDF ordering itself was not recomputed.')
