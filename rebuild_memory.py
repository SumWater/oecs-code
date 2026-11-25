import argparse, hashlib, json, sys
from pathlib import Path
root = Path(__file__).resolve().parent
sys.path[:0] = [str(root/'src'), str(root/'external/toolmisusebench'), str(root/'experiments/proper_v1')]
from gate_dataset import load_config, load_exclusions, resolve_root_path, build_memory_sources, as_experience
from toolmisusebench.dataset import load_tasks
p = argparse.ArgumentParser(description='Rebuild the 100 frozen source memories from the pinned local development split.')
p.add_argument('--dev', type=Path, required=True, help='path to pinned dev.jsonl')
p.add_argument('--output', type=Path, required=True, help='destination for rebuilt private/local memory texts')
a = p.parse_args()
hash_file = hashlib.sha256(a.dev.read_bytes()).hexdigest()
expected = 'a5a2b49b28c66f01bdbac37966c00cca9c6a1027a6d4b5b3a8c1d1d359db27e3'
if hash_file != expected: raise ValueError('development split SHA256 differs from frozen split')
config = load_config()
exclusions, _ = load_exclusions(resolve_root_path(config['pilot_exclusions']))
tasks = load_tasks(a.dev.parent, 'dev')
sources = build_memory_sources(tasks, config, exclusions)
experiences = [as_experience(x) for x in sources]
declared = json.loads((root/'data/memory_sources.json').read_text(encoding='utf8'))['memory_sources']
actual = {x.experience_id: hashlib.sha256(x.natural_text.encode('utf8')).hexdigest() for x in experiences}
wanted = {x['experience_id']: x['natural_text_sha256'] for x in declared}
if actual != wanted or len(actual) != 100: raise ValueError('rebuilt memories differ from frozen identities')
a.output.parent.mkdir(parents=True, exist_ok=True)
a.output.write_text(json.dumps([{'experience_id':x.experience_id, 'source_instance_id':x.source_instance_id, 'natural_text':x.natural_text} for x in experiences],ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('PASS: all 100 frozen memory identities and text hashes match; local output:',a.output)
