# Compatibility verification — 21 October 2026

Retested all 48 wallpapers previously marked red or yellow in this PC’s browser. All 48 produced nonblank frames with the installed patched renderer. 37 had no recorded diagnostic; 11 retained warnings or unsupported-feature diagnostics after the orange-entry follow-up. The browser ratings were refreshed from these results.

These were 640×360 previews observed over several seconds, with process-lifetime and changing-frame checks. Two X11 enumeration races were retried successfully. This does not verify every effect at full desktop resolution or establish visual parity with Windows. A synthetic gradient verified live horizontal/vertical framing at 200% zoom. A scene fixture verified property values and timer callbacks.

## Previously broken entries

| Wallpaper | Result |
|---|---|
| [Black & White Tree](https://steamcommunity.com/sharedfiles/filedetails/?id=3387640151) | Displays; diagnostics remain |
| [A Solitary Reflection [4K]](https://steamcommunity.com/sharedfiles/filedetails/?id=3644280276) | Displays without recorded diagnostics |
| [Black and White](https://steamcommunity.com/sharedfiles/filedetails/?id=3042527971) | Displays without recorded diagnostics |
| [Colorful Fluid Animation [Audio Responsive]](https://steamcommunity.com/sharedfiles/filedetails/?id=1748506393) | Displays; diagnostics remain |
| [Evangelion asuka langley soryu vol.1](https://steamcommunity.com/sharedfiles/filedetails/?id=2051445900) | Displays without recorded diagnostics |
| [Jujutsu Kaisen: Gojo x Sukuna \| Anime Quotes \| 両面宿儺 x  五条悟 \|](https://steamcommunity.com/sharedfiles/filedetails/?id=3277650572) | Displays; diagnostics remain |
| [Mount Fuji and Lake Kawaguchi \| Japan](https://steamcommunity.com/sharedfiles/filedetails/?id=3618078338) | Displays; diagnostics remain |
| [Toji \| jujutsu kaisen](https://steamcommunity.com/sharedfiles/filedetails/?id=3173180645) | Displays without recorded diagnostics |
| [White Tree - Snow](https://steamcommunity.com/sharedfiles/filedetails/?id=1789171537) | Displays; diagnostics remain |
| [剑来·剑灵 \| 4K](https://steamcommunity.com/sharedfiles/filedetails/?id=3748682389) | Displays; diagnostics remain |

## Remaining limitations

The renderer now reads MDLV0013/0016 compact puppet vertices and MDLV0019 meshes, and text layers can import native WEMath/WEColor modules. Some wallpapers still report unsupported light/volume-light layers or custom shader metadata/effects. Web wallpapers can also report GTK/OpenGL and NSS diagnostics, and authored JavaScript dependencies may be incomplete. These diagnostics remain visible; they were not suppressed to turn a rating green.

The web audio bridge currently mirrors the native recorder’s single spectrum into two channels. The fluid wallpaper is interactive and can fade toward black without mouse movement or audio.

The installed runtime is kept separate from the build tree so later compilation cannot overwrite libraries in running wallpapers. Source changes are reproducible using `patches/backend-base.txt` and `patches/backend-fixes.patch`. Workshop downloads and user selections are preserved.

## Desktop/session validation

48 integration tests and 17 native test cases (45 assertions) passed. Live checks verified game
pause at 0% renderer CPU and resumed changing frames after Hollow Knight exited,
repeated restoration without duplicate players, and parent-death cleanup even
when a child is suspended. The position dialog was rendered and inspected.
At final desktop validation only HDMI-0 was active; the saved DP-0 selection was
retained and disconnected-monitor startup was covered by a regression test.

## Orange-entry follow-up

Concrete fixes:

- Virtual files now return independent read streams. Previously, reading a built-in copy shader for one layer exhausted the shared stream and broke subsequent layers in **Ender Goku**.
- Read the correct 52-byte vertex layout for MDLV0013/0016 and 80-byte layout for MDLV0019. **Bubbles**, **Giyu – Dead Calm**, **Black Mask**, and **Red Gojo** load their puppet meshes without the previous unsupported-format errors. This verifies mesh rendering, not complete skeletal-animation parity.
- Keep imports at module scope when creating isolated text-layer closures. **Frozen Coffee** no longer fails on its WEMath import.
- Serve legacy JSON import assertions using current import attributes, while preserving strings and comments. Workshop source files are unchanged.
- Web wallpapers now receive native MPRIS playback, metadata, timeline, and artwork events. Timeline microseconds become seconds; artwork is encoded for the web listener with a sampled color and contrasting text color. Media callbacks fire when their event values change.
- Complete synchronous web asset requests using CEF's synchronous response path, without also invoking its asynchronous continuation.

The controlled fixture in `tests/fixtures/web-media` verifies legacy JSON module loading, playback state, track/artist data, timeline units, PNG artwork, and cover color. Run it while no other MPRIS media players are open:

```sh
python3 verify-web-media.py --backend /path/to/linux-wallpaperengine --assets /path/to/wallpaper_engine/assets --output /tmp/we-media-test
```

The event shape follows the [official web media API](https://docs.wallpaperengine.io/en/web/audio/media.html). The artwork color is a single downsampled average, rather than the Windows implementation's color extraction algorithm.

Remaining orange groups: White Tree / Black & White Tree and Fluid retain GTK/CEF/NSS diagnostics (Tree also has an authored missing Tether dependency); Gojo Quotes retains GTK/NSS diagnostics; Gojo Satoru, Solo Leveling, Simon, and Sky Pirate require light/volume-light support; both Mount Fuji variants and 剑来·剑灵 still have shader/effect failures. Their ratings remain orange.

A trial context-release change caused GL errors and was reverted before deployment. No warning suppression was added. The installed runtime is versioned separately from the previous working copy, preserving rollback.

The final installed-runtime retest covered the same 48 wallpapers: **48/48** produced nonblank previews and stayed running; **37** had no recorded diagnostic and **11** retained orange ratings. These counts describe the tested subset, not every Workshop wallpaper or every feature.

Game pause now includes renderer descendants (CEF renderer/GPU/utility processes), rather than suspending only the parent. Recovery checks saved start times even for orphaned children, and never resumes a reused PID. A live Hollow Knight run stopped all **18** processes belonging to the two active web wallpapers, with zero CPU-tick changes during the pause measurement; all resumed on exit. Both monitor windows displayed changing frames afterward. Current per-monitor choices, 30 FPS, and framing settings were preserved. The one-time follow-up automation remains paused.
