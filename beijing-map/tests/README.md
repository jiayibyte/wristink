# Validation scope

- test_geometry.py: generic clipping, coordinate coding and preservation of bends.
- tools/validate_map.py: every packed map record and all 16 district browse centres.
- tools/validate_navigation.py: every fine-node parent, portal connectivity, search-index decoding and fixed-route reference cases against the source graph.
- native/Harness.mc: checks tab wrapping, GPS quality/stale-fix bars, timer formatting, missing-value placeholders and daily-distance units; offers synthetic metrics for layout inspection, clearly marked SIM. Also supports interactive search → result → destination → route UI. Coordinates are public, synthetic test coordinates; screen is marked SIM. This does not validate satellite reception.
- native-batch/Batch.mc: the production router runs on the official Instinct 3 Solar SDK VM for Tiananmen → Temple of Heaven / Summer Palace / Yanqing / Miyun; it also injects 2600 fixes into the production trail recorder, checks simplification and storage round-trip, and exercises the native FIT start/stop/save API.

Native manifests have distinct app IDs and are not shipped as installable production binaries. A successful FIT save API result does not prove that a real watch records accurate GPS samples or syncs them correctly. Real-device GPS, compass, FIT contents, battery usage and long-duration behaviour still need a physical-device test.

- v0.3 native batch additionally verifies elapsed time is retained through save/restore and cleared by starting a new recording.
