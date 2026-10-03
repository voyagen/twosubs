"""Run: python tests/smoke.py [--visual /tmp/twosubs.png]. Requires mpv + ffmpeg."""
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time

visual = len(sys.argv) == 3 and sys.argv[1] == '--visual'
script = Path(__file__).resolve().parents[1] / 'scripts' / 'twosubs.lua'
with tempfile.TemporaryDirectory(prefix='twosubs-') as folder:
    root = Path(folder)
    video = root / 'clip.mkv'
    subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i',
                    'color=c=0x202838:s=960x540:r=10:d=8', '-c:v', 'ffv1',
                    str(video)], check=True)
    for name, text in [('en', 'Primary line one\nPrimary line two'),
                       ('es', 'Secondary subtitle')]:
        (root / f'{name}.srt').write_text(
            f'1\n00:00:00,000 --> 00:00:03,000\n{text}\n', encoding='utf-8')
    ipc = root / 'ipc'
    player = subprocess.Popen([
        'mpv', '--no-config', '--load-scripts=no', f'--script={script}',
        '--vo=gpu' if visual else '--vo=null', '--ao=null', '--osc=no',
        '--osd-level=0', '--pause', '--keep-open=yes', '--sid=1',
        '--secondary-sid=2', f'--input-ipc-server={ipc}',
        f'--sub-file={root / "en.srt"}', f'--sub-file={root / "es.srt"}',
        str(video)], stdout=subprocess.DEVNULL)
    try:
        deadline = time.monotonic() + 10
        while not ipc.exists():
            if player.poll() is not None or time.monotonic() > deadline:
                raise RuntimeError('mpv did not start')
            time.sleep(0.05)
        with socket.socket(socket.AF_UNIX) as client:
            client.settimeout(10)
            client.connect(str(ipc))
            stream = client.makefile('rwb', buffering=0)
            request = 0

            def command(*args):
                global request
                request += 1
                stream.write((json.dumps({'command': args, 'request_id': request}) + '\n').encode())
                while True:
                    reply = json.loads(stream.readline())
                    if reply.get('request_id') == request:
                        if args[0] == 'get_property' and reply['error'] == 'property unavailable':
                            return None
                        assert reply['error'] == 'success', reply
                        return reply.get('data')

            def get(name):
                return command('get_property', name)

            def expect(name, value):
                deadline = time.monotonic() + 5
                while get(name) != value:
                    if time.monotonic() > deadline:
                        raise AssertionError(f'{name}: expected {value!r}, got {get(name)!r}')
                    time.sleep(0.05)

            expect('sub-text', 'Primary line one\nPrimary line two')
            expect('secondary-sub-text', 'Secondary subtitle')
            secondary_pos = get('secondary-sub-pos')
            if visual:
                command('screenshot-to-file', str(Path(sys.argv[2]).resolve()), 'window')
            command('script-binding', 'twosubs/swap')
            expect('sid', 2)
            expect('secondary-sid', 1)
            expect('sub-text', 'Secondary subtitle')
            expect('secondary-sub-text', 'Primary line one\nPrimary line two')
            command('script-binding', 'twosubs/secondary-next')
            expect('secondary-sid', False)
            command('script-binding', 'twosubs/secondary-prev')
            expect('secondary-sid', 1)
            command('script-binding', 'twosubs/secondary-up')
            expect('secondary-sub-pos', secondary_pos - 1)
            command('script-binding', 'twosubs/secondary-down')
            expect('secondary-sub-pos', secondary_pos)
            command('seek', 4, 'absolute+exact')
            expect('sub-text', '')
            expect('secondary-sub-text', '')
            command('seek', 1, 'absolute+exact')
            expect('sub-text', 'Secondary subtitle')
            expect('secondary-sub-text', 'Primary line one\nPrimary line two')
            command('quit')
        player.wait(timeout=10)
        assert player.returncode == 0
        print('PASS: two tracks, swap, cycling, spacing, cue expiry, and seeking')
    finally:
        if player.poll() is None:
            player.terminate()
            player.wait(timeout=10)
