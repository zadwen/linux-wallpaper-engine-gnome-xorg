import dbus,dbus.service,dbus.mainloop.glib
from gi.repository import GLib
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus=dbus.SessionBus();name=dbus.service.BusName('org.mpris.MediaPlayer2.wallpapertest',bus)
class Player(dbus.service.Object):
 @dbus.service.method('org.freedesktop.DBus.Properties',in_signature='ss',out_signature='v')
 def Get(self,interface,prop):
  return {'PlaybackStatus':dbus.String('Playing'),'Position':dbus.Int64(30000000),'Metadata':dbus.Dictionary({'xesam:title':'Wallpaper test song','xesam:artist':dbus.Array(['Test artist'],signature='s'),'xesam:album':'Test album','mpris:length':dbus.Int64(120000000),'mpris:artUrl':(HERE/'cover.png').as_uri()},signature='sv')}[prop]
player=Player(bus,'/org/mpris/MediaPlayer2')
Path(sys.argv[1]).touch()
GLib.MainLoop().run()
