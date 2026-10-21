#!/usr/bin/env python3
"""Check legacy JSON imports and native web media events against a mock MPRIS player."""
import argparse
import json
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--backend', required=True)
    parser.add_argument('--assets', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    # The temporary player must not displace an existing user's media session.
    names = subprocess.check_output(['/usr/bin/python3', '-c',
        "import dbus,json;print(json.dumps([str(n) for n in dbus.SessionBus().list_names() if n.startswith('org.mpris.MediaPlayer2.')]))"], text=True)
    if json.loads(names):
        raise SystemExit('Close media players before running this controlled media test.')
    args.output.mkdir(parents=True, exist_ok=True)
    fixture = HERE / 'tests/fixtures/web-media'
    checker = runpy.run_path(str(HERE / 'check-wallpaper-compatibility.py'))['check']
    with tempfile.TemporaryDirectory(prefix='we-media-ready-') as temporary:
        ready = Path(temporary) / 'ready'
        mock = subprocess.Popen(['/usr/bin/python3', str(fixture / 'mock.py'), str(ready)])
        try:
            for _ in range(50):
                if ready.exists():
                    break
                if mock.poll() is not None:
                    raise RuntimeError('Mock media player failed to start')
                time.sleep(.1)
            if not ready.exists():
                raise RuntimeError('Mock media player did not become ready')
            report = checker((str(fixture), {}), args.backend, args.assets, args.output, 10)
            (args.output / 'results.json').write_text(json.dumps(report, indent=2) + '\n')
            log = (args.output / 'web-media.log').read_text()
            if 'TEST_MEDIA_BRIDGE_PASS' not in log or 'Web wallpaper: Uncaught' in log:
                raise RuntimeError('Media fixture assertions did not pass; inspect web-media.log')
            print('Web media and legacy JSON import assertions passed')
        finally:
            mock.terminate()
            mock.wait(timeout=5)

if __name__ == '__main__':
    main()
