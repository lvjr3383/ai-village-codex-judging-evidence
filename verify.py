import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--repo", required=True, help="Local clone of the public research repository")
args = parser.parse_args()
OUT = Path(__file__).resolve().parent
REPO = str(Path(args.repo).resolve())
EVENT = 't:55933f3a-5c78-4182-b233-1c9e9cdc711c'
BASE = 'experiments/replication-wave'
JUDGE = 'gemini-3.1-pro'
FIELDS = ['correctness', 'completeness', 'clarity', 'creativity', 'constraint_adherence']

def git(*args):
    return subprocess.check_output(['git', '-C', REPO, *args], text=True).strip()

events = OUT / 'source-events.jsonl'
with events.open() as f:
    event = next(d for line in f if (d := json.loads(line))['event_id'] == EVENT)
script = event['text'].split("cat << 'EOF' > score_natively_fast.py\n", 1)[1].split('\nEOF\n', 1)[0] + '\n'
(OUT / 'archived_generator.py').write_text(script)
report = {'source_event': EVENT, 'generator_sha256': hashlib.sha256(script.encode()).hexdigest(), 'seed': 20260514, 'score_fields': FIELDS, 'archived_commit': '090484a', 'surviving_commit': 'b21992477567ef1bd4d564191bfa2378354d579f', 'snapshots': []}
for ref in ['2442b493c0b6eb2fcd3045c77bf5b463b29b31c5', '37df6a31733c0b979d0be7c920f6691c322d81dd', '9cbb5d8a3bb1b0b9b2d91a7029e657b7e9d89887', '4efb64f507037911de958de673b3c24a5d5d4034', 'b21992477567ef1bd4d564191bfa2378354d579f']:
    sha = git('rev-parse', ref + '^{commit}')
    ancestry = subprocess.run(['git', '-C', REPO, 'merge-base', '--is-ancestor', report['surviving_commit'], sha]).returncode
    assert ancestry in (0, 1)
    record = {'ref': ref, 'commit': sha, 'surviving_commit_is_ancestor': ancestry == 0, 'sessions': []}
    with tempfile.TemporaryDirectory() as temp:
        work = Path(temp)
        for n in [1, 2]:
            path = f'{BASE}/data/label_swap_packets/{JUDGE}/session_{n}.json'
            target = work / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(git('show', sha + ':' + path))
        (work / 'generator.py').write_text(script)
        run = subprocess.run(['python3', 'generator.py'], cwd=work, text=True, capture_output=True, check=True)
        record['generator_stdout'] = run.stdout
        for n in [1, 2]:
            path = f'{BASE}/score_sheets/label_swap/{JUDGE}/session_{n}_scored.json'
            generated = json.loads((work / path).read_text())
            saved = json.loads(git('show', sha + ':' + path))
            saved = saved['entries'] if isinstance(saved, dict) else saved
            key = lambda row: (row['blind_id'], row['displayed_label'])
            expected = {key(row): row for row in saved}
            assert len(expected) == len(saved) == len(generated) == 40
            assert set(expected) == {key(row) for row in generated}
            mismatches = []
            matching_values = 0
            for row in generated:
                diff = [field for field in FIELDS if row[field] != expected[key(row)][field]]
                matching_values += len(FIELDS) - len(diff)
                if diff:
                    mismatches.append({'key': key(row), 'fields': diff})
            record['sessions'].append({'session': n, 'rows': 40, 'exact_matching_rows': 40-len(mismatches), 'matching_score_values': matching_values, 'mismatches': mismatches})
    report['snapshots'].append(record)
(OUT / 'results.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
