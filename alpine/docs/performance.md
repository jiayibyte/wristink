# Alpine performance and power policy

This is a software/runtime policy audit. Simulator timings and font-mask pixel counts are not physical-watch battery measurements.

| State | Rendering | Data / resource work |
| --- | --- | --- |
| Full minute, wake, settings change | Full current landscape and selected fields | Load only the current background; refresh visible data / automatic-scene inputs; cached weather/location at most every five minutes; sky calculations cached by minute and inputs |
| Same-minute active tick, seconds disabled | No seconds erase or draw | No full-clock/device-settings read; heart-rate source only when a visible slot needs it, at most every five seconds |
| Heart-rate change | Repaint only heart-rate value boxes; circle if configured; full scene only for a sky header needing it | Keep the same row-wide fitting rule; do not repaint other labels, decorations or step progress |
| MIP sleep | Normal minute updates; no continuous seconds | Same-minute callbacks return without reading clock/settings, sensors or painting |
| AMOLED always-on | Dim clock only; four vertically separated positions rotated by minute | Release active landscape and face fonts; load only AOD font; no weather, location, sky or health refresh |
| Hidden / settings menu | No face painting | Release face fonts/background before constructing the menu; reload on return |

The previous same-minute seconds-disabled path still restored the seconds rectangle. That operation is now absent. Device settings are no longer fetched on every active tick. Manual skins no longer trigger unused altitude/stress/activity/battery inputs solely for disabled automatic effects.

Moon illumination sine/cosine values are computed once per body rather than per pixel. Foreground clouds on monochrome screens stay above the ridge using a bounded span check, without a second foreground bitmap.

The logical background restoration area for one changed heart-rate footer value is 35×12 instead of 176×29 on monochrome, and 43×21 instead of 260×40 on colour. This is a drawing-area comparison, not a battery-saving percentage. Label/panel/progress redraws are omitted on this path.

Offline AOD font-mask audit covers all 12/24-hour combinations (2,880 frames). The conservative maximum is 1,722 nonzero-alpha pixels, 0.995% of a 416×416 canvas. Adjacent minute positions do not overlap in the 34px font height. This is not a device framebuffer or burn-in certification; native low-power validation is still a separate check.

New native regressions cover disabled-seconds and sleeping ticks, AOD resource release/minute-only work, and heart-rate-only value patches. An SDK 9.2 optimizer error on conditional array constants was diagnosed with local compiler logs; equidistant footer coordinates and explicit lightning branches remove that trigger without changing the layout. Type checking and regional runtime API guards remain enabled.
