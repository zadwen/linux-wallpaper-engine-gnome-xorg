# Independent monitor controls

The customized full browser adds a monitor bar above the wallpaper gallery. Select **Monitor 1**, **Monitor 2**, or another saved screen. Gallery Apply/Stop actions target that monitor. **All connected monitors** is an explicit action for the connected screens.

Open **Customize Monitor…** or the Displays page to change each screen's:

- Wallpaper, including a different wallpaper on each screen.
- FPS, scaling, volume, mute, audio response, mouse interaction, parallax, and particles.
- Horizontal/vertical position and zoom, applied live.
- Wallpaper-specific properties such as colors, switches, sliders, and text.

Settings and wallpaper-specific properties are stored independently even when two monitors use the same wallpaper. The browser groups processes only when their complete settings match, so restarting or reapplying cannot merge different monitor settings. Individual monitor settings take precedence over shared wallpaper defaults.

Monitor numbers stay associated with connector IDs. Saved screens remain visible when disconnected, and their settings can be edited without starting a renderer. After reconnecting, select **Save and apply**, or restart the app to restore the saved selection. An explicit Stop clears restoration for that monitor while keeping its customization settings. Presets expose their underlying wallpaper's properties and preset defaults.

The integration's login restore helper also restores per-monitor settings and custom properties. Existing wallpaper selections, compatibility ratings, framing, and global preferences are preserved.

## Source and build

The UI/backend changes are in `patches/browser-monitor-controls.patch`, based on upstream browser commit `d14a70c87bd19bd6222d193a57e6507775629a90` (version 0.4.11). This patch is separate from the native renderer fixes. Use Node.js 22.12 or later; this build was checked with Node.js 24.

```sh
git clone https://github.com/jagrat7/linux-wallpaper-engine.git
cd linux-wallpaper-engine
git checkout d14a70c87bd19bd6222d193a57e6507775629a90
git apply /path/to/this/repository/patches/browser-monitor-controls.patch
npm ci --ignore-scripts --legacy-peer-deps
node scripts/build-monitors.mjs
node scripts/package-monitors.mjs /usr/lib/linux-wallpaper-engine "$HOME/.local/lib/linux-wallpaper-browser-monitors/custom"
```

The package command requires a **new directory**. It copies the existing Electron executable and preserves its fuses, retains native dependencies from the installed app, and packages the rebuilt application. Supporting runtime files refer to the original installation, so keep that installed. The system application is not overwritten.

Select the custom browser with the integration installer:

```sh
python3 /path/to/this/repository/install-browser-integration.py \
  --browser "$HOME/.local/lib/linux-wallpaper-browser-monitors/custom/linux-wallpaper-engine" \
  --backend /path/to/patched/linux-wallpaperengine
```

User data remains in the normal browser settings directory. Monitor preferences and stable display identities are stored in `wallpaper-engine/monitor-settings.json` and `wallpaper-engine/monitor-displays.json` under the configuration directory. Framing shares the existing `wallpaper-engine/positions.json` file with the position dialog.

## Verification

- TypeScript compilation and production builds passed.
- All 115 browser tests and 49 integration tests passed.
- Live UI checks showed both numbered screens; X11 reported HDMI-0 connected and DP-0 disconnected during this check.
- Temporarily set Monitor 1 to 24 FPS and Monitor 2 to 48 FPS; the running renderer used 24 FPS while the other screen retained its own saved setting. Those independent values survived an app restart.
- Saved a separate Wolf option and wallpaper selection for the disconnected monitor; switching wallpapers retained each wallpaper's customization.
- Changed Monitor 1's position and zoom through the UI; Monitor 2's framing remained unchanged.
- Restored the original wallpaper selections, 30 FPS, custom-property defaults, and framing after testing.

Actual simultaneous playback on both connected outputs was not retested while DP-0 was disconnected. Existing game pause/resume and renderer fixes remain in place. Test captures are kept locally; no desktop images or Workshop content are included in this repository.

## Monitor disconnects and layout changes

The GNOME adapter refreshes the XRandR layout once per second. Disconnecting
a screen stops its renderer; moving or resizing another screen recreates its
renderer at the new bounds. The supervisor retains the requested screen names
and restores their wallpaper on reconnection. The browser wrapper also waits
for saved screens that are disconnected at startup. Saved framing and per-screen
preferences remain unchanged. A layout change can briefly reload the wallpaper.

Verified on 2026-10-21: after DP-0 was turned off, HDMI-0 rendered once at
3840x2160+0+0, replacing two overlapping windows at obsolete coordinates.
All 54 integration tests passed, including a simulated two-screen disconnect,
origin change, and reconnect. Physical reconnection was not exercised while
the second display remained off.
