import importlib.util
import os
from pathlib import Path
import signal
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('game_pause', Path(__file__).with_name('game-wallpaper-pause.py'))
pause = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pause)


class PauseTreeTests(unittest.TestCase):
    def test_web_helpers_are_included_without_suspending_other_apps(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for pid, parent, arguments in [
                (10, 1, ['/runtime/linux-wallpaperengine', '--bg', '/wallpaper']),
                (11, 10, ['/runtime/linux-wallpaperengine', '--type=zygote']),
                (12, 11, ['/runtime/linux-wallpaperengine', '--type=renderer']),
                (20, 1, ['/browser/electron', '--type=renderer']),
            ]:
                proc = root / str(pid)
                proc.mkdir()
                stat = ['0'] * 20
                stat[0], stat[1], stat[19] = 'S', str(parent), str(pid * 100)
                (proc / 'stat').write_text(f'{pid} (web helper) ' + ' '.join(stat))
                (proc / 'cmdline').write_bytes(b'\0'.join(os.fsencode(a) for a in arguments))
                (proc / 'comm').write_text('linux-wallpaper\n')
                (proc / 'environ').write_bytes(b'')
            with patch.object(pause, 'PROC', root):
                games, processes = pause.snapshot()
            self.assertEqual(games, set())
            self.assertEqual(processes, {10: '1000', 11: '1100', 12: '1200'})

    def test_service_recovery_resumes_its_orphaned_child(self):
        paused = {12: '1200'}
        with patch.object(pause, 'process_identity', return_value='1200'), patch.object(pause.os, 'kill') as kill:
            pause.resume(paused, {})
            kill.assert_called_once_with(12, signal.SIGCONT)
        self.assertEqual(paused, {})

    def test_reused_pid_is_not_resumed(self):
        with patch.object(pause, 'process_identity', return_value='9999'), patch.object(pause.os, 'kill') as kill:
            pause.resume({12: '1200'}, {})
            kill.assert_not_called()

    def test_descendant_cycles_cannot_loop_forever(self):
        self.assertEqual(pause.include_descendants({10: 'a'}, {10: (11, 'a'), 11: (10, 'b')}),
                         {10: 'a', 11: 'b'})


class PollingCostTests(unittest.TestCase):
    def test_unchanged_recovery_state_is_not_rewritten(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / 'paused.json'
            with patch.object(pause, 'STATE', state):
                pause.save_paused({10: '100'})
                before = state.stat().st_mtime_ns
                pause.save_paused({10: '100'})
                self.assertEqual(state.stat().st_mtime_ns, before)
                pause.save_paused({})
                self.assertEqual(state.read_text(), '{}')

    def test_native_game_marker_still_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for pid, comm in [(10, 'reaper'), (11, 'desktop')]:
                proc = root / str(pid)
                proc.mkdir()
                stat = ['0'] * 20
                stat[0], stat[1], stat[19] = 'S', '1', str(pid)
                (proc / 'stat').write_text(f'{pid} ({comm}) ' + ' '.join(stat))
                (proc / 'cmdline').write_bytes(comm.encode())
                (proc / 'comm').write_text(comm)
                # A normal desktop process has no readable environment here.
                if comm == 'reaper':
                    (proc / 'environ').write_bytes(b'SteamAppId=12345\0')
            with patch.object(pause, 'PROC', root):
                self.assertEqual(pause.snapshot()[0], {'12345'})
