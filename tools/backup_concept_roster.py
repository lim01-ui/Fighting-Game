"""Archive the eight active designs before their concept-art replacements."""
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from characters import character_data

KEYS = ('rook', 'vex', 'sable', 'chib', 'golem', 'sanya', 'soldier', 'choom')


def main():
    source = ROOT / 'assets/characters/style-v2'
    backup = ROOT / 'assets/characters/backups/pre-concept-integration'
    if (backup / 'manifest.json').exists():
        print('Existing archive preserved.')
        return
    backup.mkdir(parents=True, exist_ok=True)
    filenames = set()
    for key in KEYS:
        filenames.add(f'{key}.json')
        manifest = json.loads((source / f'{key}.json').read_text(encoding='utf-8'))
        filenames.add(manifest['image'])
        filenames.add(manifest['idle_animation']['image'])
    digests = {}
    for filename in sorted(filenames):
        shutil.copy2(source / filename, backup / filename)
        digests[filename] = hashlib.sha256((backup / filename).read_bytes()).hexdigest()
    (backup / 'manifest.json').write_text(json.dumps({
        'fighters': {key: character_data.get(key) for key in KEYS},
        'sha256': digests,
    }, indent=2) + '\n', encoding='utf-8')
    print(f'Archived {len(filenames)} files for {len(KEYS)} fighters.')


if __name__ == '__main__':
    main()
