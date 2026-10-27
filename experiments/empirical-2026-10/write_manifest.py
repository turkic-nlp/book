"""Freeze hashes after successful validation; excludes the manifest itself."""
from pathlib import Path
import json,hashlib
here=Path(__file__).parent
assert json.loads((here/'results/validation.json').read_text())['passed'],'Run validation successfully before freezing'
files=[*here.glob('*.py'),here/'README.md',*here.joinpath('inputs').glob('*'),*here.joinpath('results').glob('*')]
manifest={str(p.relative_to(here)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files) if p.is_file() and not p.name.endswith('.restored.conllu')}
(here/'reproducibility-manifest.json').write_text(json.dumps({'scope':'Final suite sources, frozen inputs and validated results; model weights are recorded in run manifests, not redistributed','sha256':manifest},indent=2)+'\n')
print(f'Frozen hashes for {len(manifest)} suite files')
