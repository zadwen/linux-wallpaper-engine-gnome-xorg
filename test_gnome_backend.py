import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('bridge',str(Path(__file__).resolve().parent / 'gnome-backend.py'))
bridge=importlib.util.module_from_spec(spec);spec.loader.exec_module(bridge)
class PlacementTests(unittest.TestCase):
 def test_monitor_coordinates(self):
  layout='HDMI-0 connected primary 1920x1080+1920+0 (normal)\nHDMI-1-2 connected 1920x1080+0+0 (normal)\nDP-0 disconnected\n'
  with patch.object(bridge.subprocess,'check_output',return_value=layout) as query:
   self.assertEqual(bridge.monitors(),{'HDMI-0':('1920','0','1920','1080'),'HDMI-1-2':('0','0','1920','1080')})
   query.assert_called_once_with(['xrandr','--current'],text=True,timeout=3)
 def test_negative_monitor_coordinates(self):
  layout='DP-0 connected primary 1920x1080-1920+0 (normal)\nHDMI-0 connected 1080x1920+0-540 (normal)\n'
  with patch.object(bridge.subprocess,'check_output',return_value=layout):
   self.assertEqual(bridge.monitors(),{'DP-0':('-1920','0','1920','1080'),'HDMI-0':('0','-540','1080','1920')})
 def test_desktop_type_precedes_position_and_below(self):
  with patch.object(bridge.subprocess,'run') as run, patch.object(bridge,'lower_desktop') as lower:
   bridge.pin('0x123',('1920','0','1920','1080'))
  lower.assert_called_once_with('0x123')
  commands=[c.args[0] for c in run.call_args_list]
  self.assertEqual(commands[0][-1], '_NET_WM_WINDOW_TYPE_DESKTOP')
  self.assertIn(['wmctrl','-i','-r','0x123','-b','remove,above,below'],commands)
  self.assertIn(['wmctrl','-i','-r','0x123','-b','remove,fullscreen'],commands)
  self.assertIn(['wmctrl','-i','-r','0x123','-b','add,sticky'],commands)
  self.assertEqual(commands[-1][-1],'0,1920,0,1920,1080')
 def test_parent_death_kills_even_a_suspended_renderer(self):
  from unittest.mock import MagicMock
  libc=MagicMock();libc.prctl.return_value=0
  with patch.object(bridge.ctypes,'CDLL',return_value=libc),patch.object(bridge.os,'getppid',return_value=123):
   bridge.renderer_lifetime()
  libc.prctl.assert_called_once_with(1,bridge.signal.SIGKILL,0,0,0)
 def test_disconnected_monitor_does_not_block_an_active_monitor(self):
  from unittest.mock import MagicMock
  child=MagicMock();child.pid=321;child.poll.side_effect=[None,0,0]
  geometry=('0','0','1920','1080')
  with patch.object(bridge.sys,'argv',['bridge','/backend','--screen-root','missing','--screen-root','main']),patch.object(bridge,'monitors',return_value={'main':geometry}),patch.object(bridge.subprocess,'Popen',return_value=child) as spawn,patch.object(bridge.subprocess,'check_output',return_value='0x123 0 321 host wallpaper'),patch.object(bridge,'pin') as pin,patch.object(bridge.time,'sleep',side_effect=KeyboardInterrupt):
   with self.assertRaises(KeyboardInterrupt): bridge.main()
  self.assertEqual(spawn.call_count,1)
  pin.assert_called_once_with('0x123',geometry)
 def test_disconnect_stops_only_removed_output(self):
  from unittest.mock import MagicMock
  main=MagicMock(); main.poll.return_value=None; other=MagicMock(); other.poll.return_value=None
  geometry=('0','0','3840','2160')
  children={'main':(main,geometry),'other':(other,('3840','0','1080','1920'))}
  bridge.reconcile(children,{'main':geometry})
  self.assertEqual(list(children),['main'])
  other.kill.assert_called_once(); other.wait.assert_called_once()
  main.kill.assert_not_called()
 def test_layout_origin_change_moves_existing_renderer(self):
  from unittest.mock import MagicMock
  child=MagicMock(); child.pid=321; child.poll.return_value=None
  children={'main':(child,('1080','0','3840','2160'))}
  with patch.object(bridge.subprocess,'check_output',return_value='0x123 0 321 host wallpaper'),patch.object(bridge,'pin') as pin:
   bridge.reconcile(children,{'main':('0','0','3840','2160')})
  self.assertEqual(children['main'][1],('0','0','3840','2160'))
  pin.assert_called_once_with('0x123',('0','0','3840','2160'))
  child.kill.assert_not_called()
 def test_unchanged_layout_keeps_renderer(self):
  from unittest.mock import MagicMock
  child=MagicMock(); child.poll.return_value=None; geometry=('0','0','3840','2160')
  children={'main':(child,geometry)}
  bridge.reconcile(children,{'main':geometry})
  self.assertIn('main',children); child.kill.assert_not_called()
 def test_disconnect_and_reconnect_supervisor(self):
  from unittest.mock import MagicMock
  child=MagicMock(); child.pid=321; child.poll.return_value=None
  first={'main':('1080','0','3840','2160'),'other':('0','540','1080','1920')}
  single={'main':('0','0','3840','2160')}
  with patch.object(bridge.sys,'argv',['bridge','/backend','--screen-root','main','--screen-root','other']),patch.object(bridge,'monitors',side_effect=[first,single,first]),patch.object(bridge.subprocess,'Popen',return_value=child) as spawn,patch.object(bridge.subprocess,'check_output',return_value='0x123 0 321 host wallpaper'),patch.object(bridge,'pin'),patch.object(bridge.time,'sleep',side_effect=[None,None,KeyboardInterrupt]):
   with self.assertRaises(KeyboardInterrupt): bridge.main()
  geometries=[call.args[0][2] for call in spawn.call_args_list]
  self.assertEqual(geometries,['1080x0x3840x2160','0x540x1080x1920','0x540x1080x1920'])
 def test_exited_renderer_is_retired_for_restart(self):
  from unittest.mock import MagicMock
  child=MagicMock(); child.poll.return_value=1
  geometry=('0','0','3840','2160'); children={'main':(child,geometry)}
  bridge.reconcile(children,{'main':geometry})
  self.assertEqual(children,{})
  child.wait.assert_called_once(); child.kill.assert_not_called()
 def test_transient_window_listing_error_is_retried(self):
  from unittest.mock import MagicMock
  child=MagicMock(); child.pid=321; child.poll.return_value=None
  geometry=('0','0','1920','1080')
  error=bridge.subprocess.CalledProcessError(1,['wmctrl','-lp'])
  with patch.object(bridge.sys,'argv',['bridge','/backend','--screen-root','main']),patch.object(bridge,'monitors',return_value={'main':geometry}),patch.object(bridge.subprocess,'Popen',return_value=child),patch.object(bridge.subprocess,'check_output',side_effect=[error,'0x123 0 321 host wallpaper']),patch.object(bridge,'pin') as pin,patch.object(bridge.time,'sleep',side_effect=[None,KeyboardInterrupt]):
   with self.assertRaises(KeyboardInterrupt): bridge.main()
  pin.assert_called_once_with('0x123',geometry)
 def test_invalid_monitor_does_not_launch(self):
  with patch.object(bridge.sys,'argv',['bridge','/backend','--screen-root','missing']),patch.object(bridge,'monitors',return_value={}),patch.object(bridge.subprocess,'Popen') as spawn:
   with self.assertRaises(ValueError): bridge.main()
   spawn.assert_not_called()
if __name__ == '__main__':
 unittest.main()
