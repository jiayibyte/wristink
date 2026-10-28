# Official Garmin weather image sources

Source: https://support.garmin.com/en-US/?faq=kArcrtjkiE55MEYli4FtK9
Page: Status Icons on the inReach Mini 2. Retrieved 2026-10-28.

The thirteen JPGs are Garmin-published monochrome weather symbols, retained unchanged. `sources.json` records the original CDN URLs and SHA256 hashes. Rights remain with Garmin; no open-source license for these images is asserted. Review redistribution rights before a public store submission.

`tools/garmin_weather.py` crops source whitespace, fits the original aspect ratio, and converts coverage to a 1-bit 9px or 11px glyph. It does not use an Instinct firmware/private API and does not claim device-specific pixel identity. All processing happens at build time; the watch loads one small atlas, with no downloads or scaling at runtime.
