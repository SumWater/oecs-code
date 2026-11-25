import json,sys,importlib.util
from pathlib import Path
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'src'))
spec=importlib.util.spec_from_file_location('formal_analysis',R/'experiments/paper_2026/analyze_e2_e3.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
c=json.loads((R/'config/analysis.json').read_text(encoding='utf8'))
a,t,audit=m.analyze(c,{})
frozen=json.loads((R/'outputs/paper_2026/e2_e3_formal_analysis/tables.json').read_text(encoding='utf8'))
assert t==frozen, 'Recomputed tables differ from frozen tables'
print('PASS: all descriptive and inference rows match frozen tables, including CIs and adjusted p values.')
for row in t['inference_rows']:
 if row['family'] in ('primary_proper_vs_tfidf','all_valid_sensitivity'):
  print(row['population'],row['model_name'],'n',row['pair_count'],'baseline',row['baseline_successes'],'OECS',row['treatment_successes'],'discordant',row['positive_discordant'],row['negative_discordant'],'difference_pp',round(100*row['paired_risk_difference'],4),'CI',row['paired_bootstrap_ci']['lower'],row['paired_bootstrap_ci']['upper'],'Holm p',row['holm_adjusted_p'])
for model in c['models']:
 rows=[x for x in t['descriptive_rows'] if x['model_name']==model and x['population']=='changed_target_union' and x['stratum']=='all_strata']
 d={x['condition']:x for x in rows}; print(model,'OECS minus no memory (pp)',round(100*(d['proper']['recovery_validity_rate']-d['no_memory']['recovery_validity_rate']),4))
