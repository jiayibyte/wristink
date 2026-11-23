"""Phone settings share their product names, IDs and defaults with the app."""
from xml.etree import ElementTree as ET

from themes import THEME_NAMES

METRICS = ("Off", "Heart rate", "Battery", "Steps", "Calories", "Distance",
           "Temperature", "Notifications", "Elevation", "Floors climbed", "Seconds")
OUTSIDE_METRICS = METRICS[:-1]
STATUS_OPTIONS = ("Off", "Tones off", "Phone connected", "Alarm set", "Do not disturb",
                  "Active notifications", "Battery 20% or lower", "Vibration off",
                  "Phone disconnected", "Charging cable connected")
FIELDS = {
    "Theme": ("Color theme", 1, THEME_NAMES),
    "Typeface": ("Time font", 0, ("Segment", "Contour", "Matrix")),
    "TimeFormat": ("Time format", 0, ("Watch setting", "12 hours", "24 hours")),
    "DateStyle": ("Date display", 0, ("Weekday, year, month and day", "Weekday, month / day", "Day / month", "Off")),
    "ClockSeconds": ("Small seconds", 0, ("Off", "On wrist raise")),
    "Gauge": ("Progress bar", 0, ("Step goal", "Battery", "Off", "Day elapsed",
                                  "Floors climbed goal", "Weekly intensity goal")),
    "BatteryDisplay": ("Battery display", 0, ("Percent", "Estimated days")),
    "StatusText": ("Status above date", 1, STATUS_OPTIONS),
    "StatusLeft": ("Left icon above seconds", 2, STATUS_OPTIONS),
    "StatusRight": ("Right icon above seconds", 3, STATUS_OPTIONS),
    "Window": ("Upper-right field / Instinct window", 1, METRICS),
    "TopLeft": ("Upper left", 3, OUTSIDE_METRICS),
    "TopRight": ("Upper right", 2, OUTSIDE_METRICS),
    "TopThird": ("Second row left", 6, OUTSIDE_METRICS),
    "TopFourth": ("Second row right", 9, OUTSIDE_METRICS),
    "BottomLeft": ("Lower left", 4, OUTSIDE_METRICS),
    "BottomMiddle": ("Lower center", 6, OUTSIDE_METRICS),
    "BottomRight": ("Lower right", 7, OUTSIDE_METRICS),
}


def generate(dest, overrides, name, window_default, mono=False):
    strings = ET.Element("strings")
    ET.SubElement(strings, "string", id="AppName").text = name
    # Titles and choices are read only by the phone's settings page. Scoped
    # strings stay out of the watch's resource table and the installed PRG.
    scoped = {"scope": "settings"}
    properties = ET.Element("properties")
    settings = ET.Element("settings")
    options = {}
    for key, (title, default, choices) in FIELDS.items():
        if window_default and key.startswith("Bottom"):
            continue
        if not window_default and key in ("TopThird","TopFourth"):
            continue
        if key == "Window":
            if not window_default:
                continue
            default = window_default
        entries = dict(enumerate(choices))
        if key == "Theme" and mono:
            entries = {1:"Black LCD", 5:"White LCD"}
        value = overrides.get(key, default)
        if value not in entries:
            raise ValueError(f"{key}={value} is outside its setting range")
        ET.SubElement(strings, "string", id=key, **scoped).text = title
        ET.SubElement(properties, "property", id=key, type="number").text = str(value)
        setting = ET.SubElement(settings, "setting", propertyKey=f"@Properties.{key}", title=f"@Strings.{key}")
        menu = ET.SubElement(setting, "settingConfig", type="list")
        for i, label in entries.items():
            if label not in options:
                options[label] = f"Option{len(options)}"
                ET.SubElement(strings, "string", id=options[label], **scoped).text = label
            ET.SubElement(menu, "listEntry", value=str(i)).text = f"@Strings.{options[label]}"
    for xml in (strings, properties, settings):
        ET.indent(xml)
        ET.ElementTree(xml).write(dest/f"{xml.tag}.xml", encoding="utf-8", xml_declaration=True)
