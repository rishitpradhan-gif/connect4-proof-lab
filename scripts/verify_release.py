#!/usr/bin/env python3
"""Build and independently check the released evidence without long searches."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skip-build', action='store_true')
    args = parser.parse_args()
    output = ROOT / 'build' / 'verification'
    output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    records = []

    def run(label, command, cwd):
        result = subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=300)
        (output / (label + '.log')).write_text(result.stdout)
        if result.returncode:
            raise RuntimeError(f'{label} failed ({result.returncode}):\n{result.stdout}')
        print(f'PASS {label}', flush=True)
        records.append(label)
        return result.stdout

    ET.parse(ROOT / 'assets' / 'research-banner.svg')
    note = ROOT / 'latex-development-note'
    published = json.loads((note / 'verification.json').read_text())
    for name, expected in published['sha256'].items():
        if sha(note / name) != expected:
            raise RuntimeError(f'Published paper identity mismatch: {name}')
    results = json.loads((ROOT / 'continuation' / 'results.json').read_text())
    for name, expected in results['code_sha256'].items():
        if sha(ROOT / name) != expected:
            raise RuntimeError(f'Research source identity mismatch: {name}')
    assert results['empty_board_value'] == 'UNKNOWN'
    assert not results['ultra_weak_solution_achieved']
    print('PASS released source/PDF identities and explicit research scope', flush=True)
    records.append('released-identities')

    if not args.skip_build:
        run('build', ['sh', 'build.sh'], ROOT)

    with tempfile.TemporaryDirectory(prefix='connect4-proof-lab-') as directory:
        work = Path(directory)
        (work / 'data').mkdir()
        (work / 'continuation').mkdir()
        for name in ['certificate.py', 'pairing-proof.py', 'pairing-refutations.py',
                     'fixtures-9x9.jsonl', 'endgame-certificate.json']:
            shutil.copy2(ROOT / name, work / name)
        shutil.copy2(ROOT / 'continuation/check-pairing-classification.py',
                     work / 'continuation/check-pairing-classification.py')
        shutil.copy2(note / 'audit_note.py', work / 'audit_note.py')

        run('independent-bitboard-endgames', [str(ROOT / 'validate')], work)
        reference = [json.loads(x) for x in (ROOT / 'fixtures-9x9.jsonl').read_text().splitlines()]
        generated = [json.loads(x) for x in (work / 'fixtures-9x9.jsonl').read_text().splitlines()]
        assert generated == reference, 'Deterministic endgame fixture mismatch'
        run('horizon-endgames', [str(ROOT / 'validate-horizon')], work)
        run('proof-number-endgames', [str(ROOT / 'dfpn'), '--validate',
            str(ROOT / 'continuation/merged-bounds.csv')], work)
        run('strategy-tree', [sys.executable, 'certificate.py', 'endgame-certificate.json'], work)
        run('midgame-pairing-certificates', [sys.executable, 'pairing-proof.py'], work)
        run('classified-counterattacks', [sys.executable, 'pairing-refutations.py'], work)
        run('small-board-classification', [sys.executable,
            'continuation/check-pairing-classification.py'], work)
        run('manuscript-witnesses', [sys.executable, 'audit_note.py'], work)

        negative_checks = r"""
import copy, importlib.util, json
from pathlib import Path
import certificate as tree

def reject(label, fn):
    try:
        fn()
    except AssertionError:
        print('REJECTED_AS_EXPECTED', label)
    else:
        raise RuntimeError('Malformed certificate accepted: ' + label)

original = json.loads(Path('endgame-certificate.json').read_text())
history = original['opening_moves_1_based']; turn = len(history) % 2
state = tree.replay(history)
mutant = copy.deepcopy(original); mutant['proof']['moves'][0]['child']['moves'].pop()
reject('missing opponent reply', lambda: tree.verify(*state, mutant['proof'], turn, turn))
mutant = copy.deepcopy(original); mutant['proof'] = {'terminal': 'root_player_wins'}
reject('false terminal win', lambda: tree.verify(*state, mutant['proof'], turn, turn))
mutant = copy.deepcopy(original); mutant['proof']['moves'][0]['column'] = 0
reject('illegal move', lambda: tree.verify(*state, mutant['proof'], turn, turn))
spec = importlib.util.spec_from_file_location('pairing_proof', 'pairing-proof.py')
pairing = importlib.util.module_from_spec(spec); spec.loader.exec_module(pairing)
proofs = json.loads(Path('continuation/midgame-pairing-certificates.json').read_text())
mutant = copy.deepcopy(proofs[0]); mutant['vertical_pairs'].pop()
reject('missing pair', lambda: pairing.verify(mutant))
mutant = copy.deepcopy(proofs[0]); mutant['vertical_pairs'][0].reverse()
reject('reversed vertical reply', lambda: pairing.verify(mutant))
mutant = copy.deepcopy(next(x for x in proofs if x['side_to_move_upper_bound'] == 0))
mutant['side_to_move_upper_bound'] = -1
reject('unjustified forced win', lambda: pairing.verify(mutant))
"""
        run('malformed-certificate-rejection', [sys.executable, '-c', negative_checks], work)

        proofs = json.loads((work / 'continuation/midgame-pairing-verification.json').read_text())
        assert proofs['certificates'] == 21 and proofs['forced_losses'] == 9
        obstruction = json.loads((work / 'continuation/pairing-refutation-result.json').read_text())
        assert obstruction['classified_strategy_types'] == 328125
        assert obstruction['max_counterattack_game_plies'] <= 16
        audit = json.loads((work / 'audit_results.json').read_text())
        assert [x['configurations'] for x in audit['generalized_obstruction_checks']] == [42525, 134400]

    report = {'status': 'PASS', 'checks': records,
              'wall_seconds': round(time.monotonic() - started, 3),
              'opening_value': 'UNKNOWN', 'long_opening_searches_run': False}
    (output / 'results.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
