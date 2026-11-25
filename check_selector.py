import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'src'))
from failure_memory.paper_2026.selector import select_from_mappings
print('PASS: OECS selector and dependencies imported; callable:', select_from_mappings.__name__)
